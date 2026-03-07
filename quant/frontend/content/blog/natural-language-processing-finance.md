---
title: "NLP for Finance: Sentiment Analysis from News and Filings"
description: "Apply NLP to financial data for sentiment analysis, news classification, and SEC filing analysis. FinBERT, topic modeling, and event detection with Python."
date: "2026-03-21"
author: "Dr. James Chen"
category: "Machine Learning"
tags: ["NLP", "sentiment analysis", "FinBERT", "text mining", "financial news"]
keywords: ["NLP finance", "financial sentiment analysis", "FinBERT trading"]
---

# NLP for Finance: Sentiment Analysis from News and Filings

Natural language processing transforms the vast ocean of unstructured financial text -- news articles, earnings calls, SEC filings, analyst reports, and social media -- into quantitative trading signals. While prices reflect all public information eventually, NLP provides the ability to process text faster and more consistently than human analysts, capturing sentiment shifts before they are fully priced in.

This guide covers the practical implementation of financial NLP pipelines, from preprocessing raw text through sentiment scoring with FinBERT to constructing tradable signals from multiple text sources.

## Key Takeaways

- **FinBERT outperforms general-purpose models** on financial text by 10-15% accuracy due to domain-specific pre-training.
- **News sentiment is a short-lived alpha source.** The predictive window is typically 1-3 days for news and 1-5 days for earnings calls.
- **SEC filings contain structural alpha** in tone changes, unusual language patterns, and readability shifts between filings.
- **Ensemble multiple text sources** for more robust signals: news + social + filings outperform any single source.

## Financial Text Preprocessing

Financial text requires domain-specific preprocessing that differs from general NLP.

```python
import re
import pandas as pd
import numpy as np
from typing import Optional

class FinancialTextPreprocessor:
    """
    Preprocessing pipeline for financial text.
    Handles tickers, numbers, financial jargon, and noise removal.
    """

    # Financial stop words to remove
    FINANCIAL_STOPWORDS = {
        "inc", "corp", "ltd", "llc", "plc", "co", "company",
        "nasdaq", "nyse", "sec", "reuters", "associated press",
    }

    # Patterns that indicate boilerplate
    BOILERPLATE_PATTERNS = [
        r"forward.looking\s+statements?",
        r"safe\s+harbor",
        r"risk\s+factors?",
        r"this\s+press\s+release\s+contains",
    ]

    def clean(self, text: str) -> str:
        """Full preprocessing pipeline."""
        text = self._normalize_whitespace(text)
        text = self._handle_financial_numbers(text)
        text = self._handle_tickers(text)
        text = self._remove_boilerplate(text)
        text = self._clean_special_chars(text)
        return text.strip()

    def _normalize_whitespace(self, text: str) -> str:
        return re.sub(r"\s+", " ", text)

    def _handle_financial_numbers(self, text: str) -> str:
        """Normalize financial numbers to categories."""
        # $1.2 billion -> LARGE_AMOUNT
        text = re.sub(
            r"\$[\d,.]+\s*(billion|trillion)", " LARGE_AMOUNT ", text, flags=re.I
        )
        # $1.2 million -> MEDIUM_AMOUNT
        text = re.sub(
            r"\$[\d,.]+\s*million", " MEDIUM_AMOUNT ", text, flags=re.I
        )
        # Percentages
        text = re.sub(r"[\d,.]+\s*%", " PERCENTAGE ", text)
        return text

    def _handle_tickers(self, text: str) -> str:
        """Normalize stock tickers."""
        # (NASDAQ: AAPL) -> TICKER_MENTION
        text = re.sub(
            r"\((?:NASDAQ|NYSE|AMEX)\s*:\s*[A-Z]{1,5}\)", " TICKER_MENTION ", text
        )
        return text

    def _remove_boilerplate(self, text: str) -> str:
        """Remove forward-looking statement disclaimers."""
        for pattern in self.BOILERPLATE_PATTERNS:
            # Remove everything after the boilerplate marker
            match = re.search(pattern, text, re.I)
            if match:
                text = text[:match.start()]
        return text

    def _clean_special_chars(self, text: str) -> str:
        """Remove HTML, URLs, and excessive punctuation."""
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"https?://\S+", " URL ", text)
        text = re.sub(r"[^\w\s.,!?;:\-'\"()]", " ", text)
        return text
```

## Sentiment Analysis with FinBERT

FinBERT is a BERT model fine-tuned on financial text, providing significantly better sentiment classification than general-purpose models.

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class FinBERTSentiment:
    """
    Financial sentiment analysis using FinBERT.
    Returns sentiment scores: positive, negative, neutral.
    """

    def __init__(self, model_name: str = "ProsusAI/finbert"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()

        self.labels = ["positive", "negative", "neutral"]

    def analyze(self, text: str) -> dict:
        """Analyze sentiment of a single text."""
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            max_length=512,
            truncation=True,
            padding=True,
        )

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)

        scores = probs[0].numpy()
        result = {label: float(score) for label, score in zip(self.labels, scores)}
        result["compound"] = result["positive"] - result["negative"]
        result["label"] = self.labels[scores.argmax()]

        return result

    def analyze_batch(
        self, texts: list[str], batch_size: int = 16
    ) -> list[dict]:
        """Analyze sentiment for multiple texts efficiently."""
        all_results = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            inputs = self.tokenizer(
                batch,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True,
            )

            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)

            for j in range(len(batch)):
                scores = probs[j].numpy()
                result = {
                    label: float(score)
                    for label, score in zip(self.labels, scores)
                }
                result["compound"] = result["positive"] - result["negative"]
                result["label"] = self.labels[scores.argmax()]
                all_results.append(result)

        return all_results

# Usage
# analyzer = FinBERTSentiment()
# result = analyzer.analyze(
#     "Apple reported record quarterly revenue of $124 billion, "
#     "exceeding analyst expectations by 5%."
# )
# print(result)
# {'positive': 0.92, 'negative': 0.03, 'neutral': 0.05, 'compound': 0.89}
```

## News Sentiment Aggregation

Individual article sentiments must be aggregated into tradable signals.

```python
class NewsSentimentAggregator:
    """
    Aggregate news sentiment into ticker-level trading signals.
    Handles recency weighting, source reliability, and volume normalization.
    """

    def __init__(
        self,
        decay_half_life_hours: float = 24,
        min_articles: int = 3,
    ):
        self.decay_half_life = decay_half_life_hours
        self.min_articles = min_articles

    def aggregate(
        self,
        articles: pd.DataFrame,
        current_time: pd.Timestamp,
    ) -> pd.DataFrame:
        """
        Aggregate article-level sentiment to ticker-level signals.

        Args:
            articles: DataFrame with columns:
                - ticker, timestamp, compound_sentiment, source
            current_time: reference time for recency weighting

        Returns:
            DataFrame with ticker-level sentiment signals
        """
        results = []

        for ticker, group in articles.groupby("ticker"):
            if len(group) < self.min_articles:
                continue

            # Recency weighting (exponential decay)
            hours_ago = (
                current_time - group["timestamp"]
            ).dt.total_seconds() / 3600
            weights = np.exp(-np.log(2) * hours_ago / self.decay_half_life)
            weights = weights / weights.sum()

            # Weighted sentiment
            weighted_sentiment = (
                group["compound_sentiment"] * weights
            ).sum()

            # Sentiment momentum (change over time)
            if len(group) >= 5:
                recent = group.nlargest(len(group) // 2, "timestamp")
                older = group.nsmallest(len(group) // 2, "timestamp")
                momentum = (
                    recent["compound_sentiment"].mean()
                    - older["compound_sentiment"].mean()
                )
            else:
                momentum = 0

            # Consensus (agreement among articles)
            consensus = 1 - group["compound_sentiment"].std()

            # Article volume (unusual volume = more significant)
            volume_z = (len(group) - 5) / 3  # Normalize around typical volume

            results.append({
                "ticker": ticker,
                "weighted_sentiment": weighted_sentiment,
                "raw_sentiment": group["compound_sentiment"].mean(),
                "sentiment_momentum": momentum,
                "consensus": consensus,
                "article_count": len(group),
                "volume_zscore": volume_z,
                "signal": weighted_sentiment * (1 + abs(volume_z) * 0.2),
            })

        return pd.DataFrame(results)
```

## SEC Filing Analysis

10-K and 10-Q filings contain subtle signals in tone changes and readability shifts.

```python
import re
from collections import Counter

class SECFilingAnalyzer:
    """
    Analyze SEC filings for sentiment and structural changes.
    """

    # Loughran-McDonald financial sentiment dictionaries (subset)
    POSITIVE_WORDS = {
        "achieve", "attain", "benefit", "better", "boost", "enhance",
        "exceed", "favorable", "gain", "growth", "improve", "increase",
        "opportunities", "positive", "profit", "progress", "recovery",
        "strength", "strong", "success", "surpass", "upturn",
    }
    NEGATIVE_WORDS = {
        "adverse", "against", "closure", "decline", "decrease", "deficit",
        "deteriorate", "difficult", "downturn", "fail", "impair", "inability",
        "litigation", "loss", "negative", "penalty", "restructuring", "risk",
        "shortage", "sluggish", "threat", "unfavorable", "weak", "worsen",
    }
    UNCERTAINTY_WORDS = {
        "approximate", "believe", "contingent", "depend", "estimate",
        "expect", "fluctuate", "indefinite", "likelihood", "may", "might",
        "possible", "predict", "probable", "risk", "uncertain", "unpredictable",
        "variable",
    }

    def analyze_filing(self, text: str) -> dict:
        """Compute filing-level metrics."""
        words = re.findall(r"\b[a-z]+\b", text.lower())
        word_count = len(words)
        word_freq = Counter(words)

        if word_count == 0:
            return {"error": "Empty document"}

        # Sentiment counts
        pos_count = sum(word_freq.get(w, 0) for w in self.POSITIVE_WORDS)
        neg_count = sum(word_freq.get(w, 0) for w in self.NEGATIVE_WORDS)
        unc_count = sum(word_freq.get(w, 0) for w in self.UNCERTAINTY_WORDS)

        # Tone metric (Loughran-McDonald)
        tone = (pos_count - neg_count) / word_count

        # Readability (Fog Index approximation)
        sentences = re.split(r"[.!?]+", text)
        n_sentences = max(len(sentences), 1)
        avg_sentence_length = word_count / n_sentences
        complex_words = sum(1 for w in words if len(w) > 6)
        fog_index = 0.4 * (avg_sentence_length + 100 * complex_words / word_count)

        return {
            "word_count": word_count,
            "positive_pct": pos_count / word_count,
            "negative_pct": neg_count / word_count,
            "uncertainty_pct": unc_count / word_count,
            "tone": tone,
            "fog_index": fog_index,
            "avg_sentence_length": avg_sentence_length,
            "n_sentences": n_sentences,
        }

    def compare_filings(
        self, current: dict, previous: dict
    ) -> dict:
        """
        Compare current filing to previous period.
        Changes in tone and complexity are trading signals.
        """
        changes = {}
        for key in ["tone", "positive_pct", "negative_pct", "uncertainty_pct", "fog_index"]:
            if key in current and key in previous:
                changes[f"{key}_change"] = current[key] - previous[key]
                if previous[key] != 0:
                    changes[f"{key}_pct_change"] = (
                        (current[key] - previous[key]) / abs(previous[key])
                    )

        # Signal: improving tone = bullish
        tone_change = changes.get("tone_change", 0)
        uncertainty_change = changes.get("uncertainty_pct_change", 0)

        changes["composite_signal"] = tone_change - 0.5 * uncertainty_change
        return changes
```

## Building a Text-Based Trading Signal

Combine all NLP components into a tradeable signal.

```python
class NLPTradingSignal:
    """
    Combine multiple NLP sources into a composite trading signal.
    """

    def __init__(
        self,
        news_weight: float = 0.4,
        filing_weight: float = 0.3,
        social_weight: float = 0.3,
    ):
        self.weights = {
            "news": news_weight,
            "filing": filing_weight,
            "social": social_weight,
        }

    def compute_signal(
        self,
        news_sentiment: float,
        filing_tone_change: float,
        social_sentiment: float,
        news_volume_z: float = 0,
    ) -> dict:
        """
        Compute composite NLP signal.

        Returns signal between -1 (bearish) and +1 (bullish)
        with confidence estimate.
        """
        # Normalize inputs to [-1, 1]
        news_norm = np.clip(news_sentiment * 2, -1, 1)
        filing_norm = np.clip(filing_tone_change * 100, -1, 1)
        social_norm = np.clip(social_sentiment * 2, -1, 1)

        # Weighted composite
        composite = (
            self.weights["news"] * news_norm
            + self.weights["filing"] * filing_norm
            + self.weights["social"] * social_norm
        )

        # Confidence: higher when sources agree
        source_signals = [news_norm, filing_norm, social_norm]
        agreement = 1 - np.std(source_signals)

        # Volume adjustment: unusual news volume increases signal strength
        volume_boost = 1 + np.clip(news_volume_z * 0.1, 0, 0.5)

        final_signal = np.clip(composite * volume_boost, -1, 1)

        return {
            "signal": final_signal,
            "confidence": agreement,
            "components": {
                "news": news_norm,
                "filing": filing_norm,
                "social": social_norm,
            },
        }
```

## FAQ

### How quickly does news sentiment decay as a trading signal?

News sentiment has a half-life of approximately 1-4 hours for breaking news and 1-2 days for earnings-related news. After 3-5 days, the informational content is almost entirely priced in. The decay is faster for large-cap stocks with high analyst coverage and slower for small-caps with limited institutional attention. Recency-weight your sentiment scores accordingly.

### Is FinBERT better than general BERT or GPT models for financial sentiment?

FinBERT significantly outperforms general-purpose models on financial text. In benchmarks on the Financial PhraseBank dataset, FinBERT achieves 85-88% accuracy compared to 75-80% for vanilla BERT. This is because financial language has domain-specific nuances: "liability" is negative in general text but neutral in finance, "volatile" is negative in general text but merely descriptive in finance. Always use domain-specific models when available.

### How do I handle conflicting signals from different text sources?

When news is bullish but social media is bearish (or vice versa), reduce position sizing rather than taking a directional bet. Conflicting signals indicate uncertainty, and the appropriate response is caution. Weight each source by its historical predictive accuracy for the specific ticker or sector, and require a minimum confidence threshold (e.g., 60% agreement) before acting.

### Can NLP signals be used for high-frequency trading?

NLP signals typically operate on a minutes-to-days timeframe, not microseconds. The latency of text processing (even with optimized models, inference takes 10-50 milliseconds per article) makes them unsuitable for latency-sensitive HFT. However, for medium-frequency strategies (holding periods of hours to days), NLP provides valuable alpha that is orthogonal to price-based signals.
