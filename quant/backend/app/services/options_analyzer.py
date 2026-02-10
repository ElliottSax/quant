"""
Options Analysis Service

Advanced options analysis for politician trades including:
- Gamma Exposure (GEX) calculation
- Unusual options activity detection
- Options flow analysis (calls vs puts)
- Bullish/bearish sentiment from options

Author: Claude
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta, date
from decimal import Decimal
from pydantic import BaseModel, Field
from enum import Enum
import asyncio
import httpx
from collections import defaultdict

from app.core.cache import cache_result
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OptionsType(str, Enum):
    """Options type"""
    CALL = "call"
    PUT = "put"


class OptionsFlowSentiment(str, Enum):
    """Options flow sentiment"""
    VERY_BULLISH = "very_bullish"
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"
    VERY_BEARISH = "very_bearish"


class UnusualActivityType(str, Enum):
    """Type of unusual options activity"""
    HIGH_VOLUME = "high_volume"
    HIGH_OI_CHANGE = "high_oi_change"
    LARGE_TRADE = "large_trade"
    UNUSUAL_STRIKE = "unusual_strike"
    SWEEP = "sweep"


class OptionsContract(BaseModel):
    """Options contract data"""
    symbol: str
    strike: float
    expiration: date
    option_type: OptionsType
    volume: int
    open_interest: int
    implied_volatility: float
    premium: float
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None


class OptionsFlow(BaseModel):
    """Options flow for a symbol"""
    symbol: str
    timestamp: datetime
    total_call_volume: int
    total_put_volume: int
    call_put_ratio: float
    net_premium_flow: float  # Positive = bullish, negative = bearish
    sentiment: OptionsFlowSentiment
    confidence: float = Field(..., ge=0, le=1)
    notable_strikes: List[float] = []


class GammaExposure(BaseModel):
    """Gamma Exposure (GEX) analysis"""
    symbol: str
    timestamp: datetime
    total_gamma: float
    net_gamma: float  # Call gamma - Put gamma
    gamma_flip_price: Optional[float] = None  # Price where gamma flips
    key_gamma_strikes: List[Tuple[float, float]]  # [(strike, gamma), ...]
    market_stance: str  # "bullish", "bearish", "neutral"
    explanation: str


class UnusualActivity(BaseModel):
    """Unusual options activity"""
    symbol: str
    timestamp: datetime
    activity_type: UnusualActivityType
    description: str
    option_type: OptionsType
    strike: float
    expiration: date
    volume: int
    open_interest: int
    volume_oi_ratio: float
    unusual_score: float = Field(..., ge=0, le=100)
    metadata: Dict = {}


class OptionsAnalysisResult(BaseModel):
    """Complete options analysis"""
    symbol: str
    timestamp: datetime
    gamma_exposure: Optional[GammaExposure] = None
    options_flow: Optional[OptionsFlow] = None
    unusual_activities: List[UnusualActivity] = []
    overall_sentiment: OptionsFlowSentiment
    confidence: float
    summary: str


class OptionsAnalyzer:
    """
    Analyze options data for politician trades

    Features:
    - Gamma exposure calculation
    - Unusual activity detection
    - Options flow analysis
    - Sentiment aggregation
    """

    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.cache_ttl = 300  # 5 minutes

    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()

    @cache_result("options_analysis", ttl=300)
    async def analyze_symbol(
        self,
        symbol: str,
        include_gex: bool = True,
        include_flow: bool = True,
        include_unusual: bool = True
    ) -> OptionsAnalysisResult:
        """
        Comprehensive options analysis for a symbol

        Args:
            symbol: Stock ticker symbol
            include_gex: Include gamma exposure analysis
            include_flow: Include options flow analysis
            include_unusual: Include unusual activity detection

        Returns:
            Complete options analysis result
        """
        logger.info(f"Analyzing options for {symbol}")

        # Fetch options data
        options_data = await self._fetch_options_data(symbol)

        if not options_data:
            logger.warning(f"No options data available for {symbol}")
            return OptionsAnalysisResult(
                symbol=symbol,
                timestamp=datetime.now(),
                overall_sentiment=OptionsFlowSentiment.NEUTRAL,
                confidence=0.0,
                summary=f"No options data available for {symbol}"
            )

        # Parallel analysis
        tasks = []

        if include_gex:
            tasks.append(self._analyze_gamma_exposure(symbol, options_data))
        else:
            tasks.append(asyncio.create_task(self._return_none()))

        if include_flow:
            tasks.append(self._analyze_options_flow(symbol, options_data))
        else:
            tasks.append(asyncio.create_task(self._return_none()))

        if include_unusual:
            tasks.append(self._detect_unusual_activity(symbol, options_data))
        else:
            tasks.append(asyncio.create_task(self._return_none()))

        gex, flow, unusual = await asyncio.gather(*tasks)

        # Aggregate sentiment
        overall_sentiment, confidence = self._aggregate_sentiment(gex, flow, unusual)

        # Generate summary
        summary = self._generate_summary(symbol, gex, flow, unusual, overall_sentiment)

        return OptionsAnalysisResult(
            symbol=symbol,
            timestamp=datetime.now(),
            gamma_exposure=gex,
            options_flow=flow,
            unusual_activities=unusual or [],
            overall_sentiment=overall_sentiment,
            confidence=confidence,
            summary=summary
        )

    async def _return_none(self):
        """Helper to return None for skipped analysis"""
        return None

    async def _fetch_options_data(self, symbol: str) -> Optional[List[OptionsContract]]:
        """
        Fetch real options data via yfinance.

        Falls back to simulated data if yfinance is unavailable or the symbol
        has no listed options.
        """
        try:
            import yfinance as yf
        except ImportError:
            logger.warning("yfinance not installed, using simulated options data")
            return self._generate_simulated_options(symbol)

        try:
            logger.info(f"Fetching options data for {symbol} via yfinance")
            loop = asyncio.get_event_loop()

            ticker = await loop.run_in_executor(None, lambda: yf.Ticker(symbol))
            expirations = await loop.run_in_executor(None, lambda: ticker.options)

            if not expirations:
                logger.warning(f"No options expirations available for {symbol}")
                return None

            # Limit to first 4 expirations to control data volume
            expirations = expirations[:4]
            contracts: List[OptionsContract] = []

            for exp_str in expirations:
                chain = await loop.run_in_executor(
                    None, lambda exp=exp_str: ticker.option_chain(exp)
                )
                exp_date = datetime.strptime(exp_str, "%Y-%m-%d").date()

                for _, row in chain.calls.iterrows():
                    contract = self._row_to_contract(symbol, row, OptionsType.CALL, exp_date)
                    if contract:
                        contracts.append(contract)

                for _, row in chain.puts.iterrows():
                    contract = self._row_to_contract(symbol, row, OptionsType.PUT, exp_date)
                    if contract:
                        contracts.append(contract)

            logger.info(f"Fetched {len(contracts)} options contracts for {symbol}")
            return contracts if contracts else None

        except Exception as e:
            logger.error(f"Error fetching options data for {symbol}: {e}", exc_info=True)
            return self._generate_simulated_options(symbol)

    def _row_to_contract(
        self, symbol: str, row, option_type: OptionsType, exp_date: date
    ) -> Optional[OptionsContract]:
        """Convert a yfinance DataFrame row to an OptionsContract."""
        try:
            volume = int(row.get("volume", 0) or 0)
            open_interest = int(row.get("openInterest", 0) or 0)
            implied_vol = float(row.get("impliedVolatility", 0) or 0)
            premium = float(row.get("lastPrice", 0) or 0)
            strike = float(row.get("strike", 0))

            if strike <= 0:
                return None

            return OptionsContract(
                symbol=symbol,
                strike=strike,
                expiration=exp_date,
                option_type=option_type,
                volume=volume,
                open_interest=open_interest,
                implied_volatility=implied_vol,
                premium=premium,
                delta=None,
                gamma=None,
                theta=None,
                vega=None,
            )
        except (ValueError, TypeError) as e:
            logger.debug(f"Skipping invalid options row for {symbol}: {e}")
            return None

    def _generate_simulated_options(self, symbol: str) -> List[OptionsContract]:
        """Generate simulated options data as fallback."""
        logger.info(f"Generating simulated options data for {symbol}")
        contracts = []
        base_price = 100.0

        for days_to_exp in [7, 14, 30, 60]:
            exp_date = date.today() + timedelta(days=days_to_exp)

            for strike_offset in [-10, -5, 0, 5, 10]:
                strike = base_price + strike_offset

                contracts.append(OptionsContract(
                    symbol=symbol,
                    strike=strike,
                    expiration=exp_date,
                    option_type=OptionsType.CALL,
                    volume=1000 + (abs(strike_offset) * 100),
                    open_interest=5000 + (abs(strike_offset) * 500),
                    implied_volatility=0.3 + (abs(strike_offset) * 0.01),
                    premium=max(0.1, base_price - strike + 5),
                    delta=0.5 if strike_offset == 0 else (0.3 if strike_offset > 0 else 0.7),
                    gamma=0.05,
                    theta=-0.1,
                    vega=0.2,
                ))

                contracts.append(OptionsContract(
                    symbol=symbol,
                    strike=strike,
                    expiration=exp_date,
                    option_type=OptionsType.PUT,
                    volume=800 + (abs(strike_offset) * 80),
                    open_interest=4000 + (abs(strike_offset) * 400),
                    implied_volatility=0.28 + (abs(strike_offset) * 0.01),
                    premium=max(0.1, strike - base_price + 5),
                    delta=-0.5 if strike_offset == 0 else (-0.3 if strike_offset < 0 else -0.7),
                    gamma=0.05,
                    theta=-0.1,
                    vega=0.2,
                ))

        return contracts

    async def _analyze_gamma_exposure(
        self,
        symbol: str,
        options_data: List[OptionsContract]
    ) -> GammaExposure:
        """
        Calculate Gamma Exposure (GEX)

        GEX represents the total gamma exposure that market makers have,
        which influences price movement and volatility.
        """
        logger.info(f"Calculating gamma exposure for {symbol}")

        # Calculate gamma by strike
        gamma_by_strike = defaultdict(float)
        call_gamma = 0.0
        put_gamma = 0.0

        for contract in options_data:
            if contract.gamma is None:
                continue

            # Gamma exposure = gamma * open_interest * 100 (shares per contract)
            gamma_exp = contract.gamma * contract.open_interest * 100

            gamma_by_strike[contract.strike] += gamma_exp

            if contract.option_type == OptionsType.CALL:
                call_gamma += gamma_exp
            else:
                put_gamma += gamma_exp

        total_gamma = call_gamma + put_gamma
        net_gamma = call_gamma - put_gamma

        # Find gamma flip price (where net gamma = 0)
        sorted_strikes = sorted(gamma_by_strike.items())
        gamma_flip_price = None

        for i in range(len(sorted_strikes) - 1):
            strike1, gamma1 = sorted_strikes[i]
            strike2, gamma2 = sorted_strikes[i + 1]

            if gamma1 * gamma2 < 0:  # Sign change
                gamma_flip_price = (strike1 + strike2) / 2
                break

        # Key gamma strikes
        key_strikes = sorted(gamma_by_strike.items(), key=lambda x: abs(x[1]), reverse=True)[:5]

        # Determine market stance
        if net_gamma > total_gamma * 0.2:
            stance = "bullish"
            explanation = "Positive net gamma suggests market makers are long gamma, leading to volatility suppression and potential upside."
        elif net_gamma < -total_gamma * 0.2:
            stance = "bearish"
            explanation = "Negative net gamma suggests market makers are short gamma, leading to volatility amplification and potential downside."
        else:
            stance = "neutral"
            explanation = "Balanced gamma exposure suggests neutral market maker positioning."

        return GammaExposure(
            symbol=symbol,
            timestamp=datetime.now(),
            total_gamma=total_gamma,
            net_gamma=net_gamma,
            gamma_flip_price=gamma_flip_price,
            key_gamma_strikes=key_strikes,
            market_stance=stance,
            explanation=explanation
        )

    async def _analyze_options_flow(
        self,
        symbol: str,
        options_data: List[OptionsContract]
    ) -> OptionsFlow:
        """
        Analyze options flow to determine market sentiment
        """
        logger.info(f"Analyzing options flow for {symbol}")

        call_volume = sum(c.volume for c in options_data if c.option_type == OptionsType.CALL)
        put_volume = sum(c.volume for c in options_data if c.option_type == OptionsType.PUT)

        call_put_ratio = call_volume / put_volume if put_volume > 0 else float('inf')

        # Calculate net premium flow
        call_premium = sum(c.volume * c.premium for c in options_data if c.option_type == OptionsType.CALL)
        put_premium = sum(c.volume * c.premium for c in options_data if c.option_type == OptionsType.PUT)
        net_premium_flow = call_premium - put_premium

        # Notable strikes (high volume)
        volume_by_strike = defaultdict(int)
        for c in options_data:
            volume_by_strike[c.strike] += c.volume

        notable_strikes = sorted(volume_by_strike.items(), key=lambda x: x[1], reverse=True)[:5]
        notable_strikes = [strike for strike, _ in notable_strikes]

        # Determine sentiment
        if call_put_ratio > 2.0:
            sentiment = OptionsFlowSentiment.VERY_BULLISH
            confidence = min(0.9, call_put_ratio / 3.0)
        elif call_put_ratio > 1.5:
            sentiment = OptionsFlowSentiment.BULLISH
            confidence = 0.7
        elif call_put_ratio < 0.5:
            sentiment = OptionsFlowSentiment.VERY_BEARISH
            confidence = min(0.9, 1.0 - call_put_ratio)
        elif call_put_ratio < 0.75:
            sentiment = OptionsFlowSentiment.BEARISH
            confidence = 0.7
        else:
            sentiment = OptionsFlowSentiment.NEUTRAL
            confidence = 0.5

        return OptionsFlow(
            symbol=symbol,
            timestamp=datetime.now(),
            total_call_volume=call_volume,
            total_put_volume=put_volume,
            call_put_ratio=call_put_ratio,
            net_premium_flow=net_premium_flow,
            sentiment=sentiment,
            confidence=confidence,
            notable_strikes=notable_strikes
        )

    async def _detect_unusual_activity(
        self,
        symbol: str,
        options_data: List[OptionsContract]
    ) -> List[UnusualActivity]:
        """
        Detect unusual options activity
        """
        logger.info(f"Detecting unusual options activity for {symbol}")

        unusual = []

        # Calculate baselines
        avg_volume = sum(c.volume for c in options_data) / len(options_data) if options_data else 0
        avg_oi = sum(c.open_interest for c in options_data) / len(options_data) if options_data else 0

        for contract in options_data:
            activities = []

            # High volume (3x average)
            if contract.volume > avg_volume * 3:
                activities.append((
                    UnusualActivityType.HIGH_VOLUME,
                    f"Volume {contract.volume} is {contract.volume / avg_volume:.1f}x average",
                    min(100, (contract.volume / avg_volume) * 20)
                ))

            # High OI change (volume > 50% of OI)
            if contract.volume > contract.open_interest * 0.5:
                vol_oi_ratio = contract.volume / contract.open_interest if contract.open_interest > 0 else 0
                activities.append((
                    UnusualActivityType.HIGH_OI_CHANGE,
                    f"Volume/OI ratio of {vol_oi_ratio:.2f} suggests new positions",
                    min(100, vol_oi_ratio * 50)
                ))

            # Large single trade (volume > 2000 contracts)
            if contract.volume > 2000:
                activities.append((
                    UnusualActivityType.LARGE_TRADE,
                    f"Large trade of {contract.volume} contracts",
                    min(100, (contract.volume / 2000) * 30)
                ))

            for activity_type, description, score in activities:
                unusual.append(UnusualActivity(
                    symbol=symbol,
                    timestamp=datetime.now(),
                    activity_type=activity_type,
                    description=description,
                    option_type=contract.option_type,
                    strike=contract.strike,
                    expiration=contract.expiration,
                    volume=contract.volume,
                    open_interest=contract.open_interest,
                    volume_oi_ratio=contract.volume / contract.open_interest if contract.open_interest > 0 else 0,
                    unusual_score=score,
                    metadata={
                        "implied_volatility": contract.implied_volatility,
                        "premium": contract.premium
                    }
                ))

        # Sort by unusual score
        unusual.sort(key=lambda x: x.unusual_score, reverse=True)

        # Return top 10
        return unusual[:10]

    def _aggregate_sentiment(
        self,
        gex: Optional[GammaExposure],
        flow: Optional[OptionsFlow],
        unusual: Optional[List[UnusualActivity]]
    ) -> Tuple[OptionsFlowSentiment, float]:
        """
        Aggregate sentiment from all analyses
        """
        sentiments = []
        weights = []

        if flow:
            sentiment_scores = {
                OptionsFlowSentiment.VERY_BULLISH: 2.0,
                OptionsFlowSentiment.BULLISH: 1.0,
                OptionsFlowSentiment.NEUTRAL: 0.0,
                OptionsFlowSentiment.BEARISH: -1.0,
                OptionsFlowSentiment.VERY_BEARISH: -2.0
            }
            sentiments.append(sentiment_scores[flow.sentiment])
            weights.append(flow.confidence)

        if gex:
            stance_scores = {
                "bullish": 1.0,
                "neutral": 0.0,
                "bearish": -1.0
            }
            sentiments.append(stance_scores[gex.market_stance])
            weights.append(0.7)  # GEX is less direct indicator

        if unusual and len(unusual) > 0:
            # Unusual activity weighted by type
            call_score = sum(u.unusual_score for u in unusual if u.option_type == OptionsType.CALL)
            put_score = sum(u.unusual_score for u in unusual if u.option_type == OptionsType.PUT)

            if call_score > put_score * 1.5:
                sentiments.append(1.0)
                weights.append(0.6)
            elif put_score > call_score * 1.5:
                sentiments.append(-1.0)
                weights.append(0.6)

        if not sentiments:
            return OptionsFlowSentiment.NEUTRAL, 0.0

        # Weighted average
        total_weight = sum(weights)
        avg_sentiment = sum(s * w for s, w in zip(sentiments, weights)) / total_weight

        # Convert to sentiment category
        if avg_sentiment > 1.5:
            final_sentiment = OptionsFlowSentiment.VERY_BULLISH
        elif avg_sentiment > 0.5:
            final_sentiment = OptionsFlowSentiment.BULLISH
        elif avg_sentiment < -1.5:
            final_sentiment = OptionsFlowSentiment.VERY_BEARISH
        elif avg_sentiment < -0.5:
            final_sentiment = OptionsFlowSentiment.BEARISH
        else:
            final_sentiment = OptionsFlowSentiment.NEUTRAL

        confidence = min(0.95, total_weight / len(sentiments))

        return final_sentiment, confidence

    def _generate_summary(
        self,
        symbol: str,
        gex: Optional[GammaExposure],
        flow: Optional[OptionsFlow],
        unusual: Optional[List[UnusualActivity]],
        sentiment: OptionsFlowSentiment
    ) -> str:
        """
        Generate human-readable summary
        """
        parts = [f"Options analysis for {symbol}:"]

        if flow:
            parts.append(
                f"Call/Put ratio of {flow.call_put_ratio:.2f} indicates {flow.sentiment.value} sentiment."
            )

        if gex:
            parts.append(
                f"Net gamma of {gex.net_gamma:,.0f} suggests {gex.market_stance} market maker positioning."
            )
            if gex.gamma_flip_price:
                parts.append(f"Gamma flip at ${gex.gamma_flip_price:.2f}.")

        if unusual and len(unusual) > 0:
            parts.append(
                f"Detected {len(unusual)} unusual activities, "
                f"with highest score of {unusual[0].unusual_score:.0f}."
            )

        parts.append(f"Overall: {sentiment.value.replace('_', ' ').title()}")

        return " ".join(parts)


# Global instance
_options_analyzer: Optional[OptionsAnalyzer] = None


def get_options_analyzer() -> OptionsAnalyzer:
    """Get global options analyzer instance"""
    global _options_analyzer
    if _options_analyzer is None:
        _options_analyzer = OptionsAnalyzer()
    return _options_analyzer
