# Cyclical Pattern Detection Module

Advanced pattern detection for quantitative trading analytics using signal processing, machine learning, and time series analysis.

## Overview

This module provides three complementary approaches to detecting and analyzing cyclical patterns in political trading data:

1. **Fourier Analysis** - Frequency domain analysis to detect periodic patterns
2. **Hidden Markov Models** - Regime detection and state transitions
3. **Dynamic Time Warping** - Pattern matching across different time scales

## Models

### 1. Fourier Cyclical Detector

Detects periodic patterns using Fast Fourier Transform (FFT) and seasonal decomposition.

**Key Features:**
- Identifies dominant cycles (weekly, monthly, quarterly, annual, election cycles)
- Seasonal decomposition (trend, seasonal, residual)
- Cycle-based forecasting
- Confidence scoring for detected patterns

**Example Usage:**

```python
from app.ml.cyclical import FourierCyclicalDetector
import pandas as pd

# Load trading data
trades_df = pd.DataFrame(...)  # Your trade frequency data
trade_frequency = trades_df.groupby('date').size()

# Detect cycles
detector = FourierCyclicalDetector(min_strength=0.1, min_confidence=0.6)
result = detector.detect_cycles(trade_frequency, sampling_rate='daily')

# View results
print(f"Found {result['total_cycles_found']} cycles")
for cycle in result['dominant_cycles']:
    print(f"- {cycle['category']}: {cycle['period_days']:.1f} days (confidence: {cycle['confidence']:.1%})")

# Get human-readable summary
print(detector.get_cycle_summary())

# Access forecast
forecast = result['cycle_forecast']
print(f"30-day forecast: {forecast['forecast']}")
```

**Detected Cycle Categories:**
- `weekly`: 5-7 days
- `monthly`: 20-31 days
- `quarterly`: 60-95 days
- `annual`: 240-270 trading days
- `election_cycle`: 480-1500 days (2-4 years)

### 2. HMM Regime Detector

Identifies market regimes using Hidden Markov Models with Gaussian emissions.

**Key Features:**
- Multi-state regime detection (bull, bear, high volatility, low volatility)
- Transition probability matrix
- Expected duration in each regime
- Real-time regime classification

**Example Usage:**

```python
from app.ml.cyclical import RegimeDetector
import pandas as pd

# Load data
returns = ...  # Daily returns
volumes = ...  # Trading volumes (optional)

# Fit model and detect regimes
detector = RegimeDetector(n_states=4)
result = detector.fit_and_predict(returns, volumes)

# Current regime
print(f"Current regime: {result['current_regime_name']}")
print(f"Confidence: {result['regime_probabilities'][result['current_regime']]:.1%}")
print(f"Expected duration: {result['expected_duration'][result['current_regime']]:.1f} periods")

# Regime characteristics
for state, chars in result['regime_characteristics'].items():
    print(f"\nRegime {state}: {chars['name']}")
    print(f"  Avg return: {chars['avg_return']:.2%}")
    print(f"  Volatility: {chars['volatility']:.2%}")
    print(f"  Frequency: {chars['frequency']:.1%}")

# Transition probabilities from current regime
transitions = detector.get_regime_transition_probabilities(result['current_regime'])
print(f"\nTransition probabilities: {transitions}")

# Get summary
print(detector.get_regime_summary(result))
```

**Typical Regimes:**
- **Bull Market**: Positive returns, low volatility
- **Bear Market**: Negative returns, high volatility
- **High Volatility**: Choppy, uncertain conditions
- **Low Volatility**: Stable, predictable period

### 3. Dynamic Time Warping Matcher

Finds historical patterns similar to current trading patterns using DTW distance.

**Key Features:**
- Finds similar historical periods
- Predicts outcomes based on historical matches
- Works across different time scales
- Confidence-weighted predictions

**Example Usage:**

```python
from app.ml.cyclical import DynamicTimeWarpingMatcher
import pandas as pd

# Load data
trade_frequency = ...  # Full historical data
current_pattern = trade_frequency[-30:]  # Last 30 days

# Find similar patterns
matcher = DynamicTimeWarpingMatcher(similarity_threshold=0.7)
matches = matcher.find_similar_patterns(
    current_pattern,
    trade_frequency,
    window_size=30,
    top_k=10
)

# View matches
for i, match in enumerate(matches[:3]):
    print(f"\nMatch {i+1}:")
    print(f"  Date: {match['match_date']}")
    print(f"  Similarity: {match['similarity_score']:.1%}")
    print(f"  30d outcome: {match['outcome_30d']['total_return']:+.2%}")
    print(f"  90d outcome: {match['outcome_90d']['total_return']:+.2%}")

# Get prediction based on matches
prediction = matcher.predict_from_matches(matches, horizon=30)
print(f"\nPredicted 30-day return: {prediction['predicted_return']:+.2%}")
print(f"Confidence: {prediction['confidence']:.1%}")
print(f"Historical range: {prediction['return_distribution']['min']:+.2%} to {prediction['return_distribution']['max']:+.2%}")

# Get summary
print(matcher.get_pattern_summary())
```

## MLFlow Experiment Tracking

All models support comprehensive experiment tracking with MLFlow.

**Example Usage:**

```python
from app.ml.cyclical import CyclicalExperimentTracker, track_complete_cyclical_analysis
import pandas as pd

# Option 1: Track individual model
tracker = CyclicalExperimentTracker(experiment_name="my_experiment")

fourier = FourierCyclicalDetector()
result = fourier.detect_cycles(data)
run_id = tracker.track_fourier_detection(
    fourier,
    data,
    result,
    tags={'politician': 'Nancy Pelosi', 'ticker': 'NVDA'}
)

# Option 2: Track complete analysis (all three models)
data = pd.DataFrame({
    'returns': ...,
    'volumes': ...
})

run_ids = track_complete_cyclical_analysis(
    data,
    experiment_name="pelosi_nvda_analysis",
    tags={'politician': 'Nancy Pelosi', 'ticker': 'NVDA'}
)

print(f"Tracked runs: {run_ids}")
# View in MLFlow UI: http://localhost:5000
```

**What Gets Tracked:**
- **Parameters**: Model configuration, data characteristics
- **Metrics**: Cycle strengths, regime probabilities, pattern similarities
- **Artifacts**:
  - JSON files with detailed results
  - Human-readable summaries
  - Visualizations (plots)
- **Tags**: Metadata for organizing experiments

## Combined Analysis

Use all three models together for comprehensive insights:

```python
from app.ml.cyclical import (
    FourierCyclicalDetector,
    RegimeDetector,
    DynamicTimeWarpingMatcher
)
import pandas as pd

# Load data
trades_df = pd.DataFrame(...)
returns = trades_df['returns']
volumes = trades_df['volumes']

# 1. Detect cyclical patterns
fourier = FourierCyclicalDetector()
cycles = fourier.detect_cycles(returns)

# 2. Identify current regime
hmm = RegimeDetector(n_states=4)
regimes = hmm.fit_and_predict(returns, volumes)

# 3. Find similar historical periods
dtw = DynamicTimeWarpingMatcher()
matches = dtw.find_similar_patterns(returns, returns, window_size=30, top_k=5)
prediction = dtw.predict_from_matches(matches)

# Combined insights
insights = {
    'dominant_cycles': cycles['dominant_cycles'][:3],
    'current_regime': regimes['current_regime_name'],
    'regime_confidence': regimes['regime_probabilities'][regimes['current_regime']],
    'similar_periods_found': len(matches),
    'predicted_30d_return': prediction['predicted_return'],
    'prediction_confidence': prediction['confidence']
}

print(insights)
```

## Testing

Run the test suite:

```bash
# From backend directory
pytest tests/ml/test_cyclical.py -v

# Run specific test class
pytest tests/ml/test_cyclical.py::TestFourierCyclicalDetector -v

# Run with coverage
pytest tests/ml/test_cyclical.py --cov=app.ml.cyclical
```

## Dependencies

All dependencies are included in `requirements-ml.txt`:

```
scipy>=1.10.0           # FFT, signal processing
hmmlearn>=0.3.0         # Hidden Markov Models
dtaidistance>=2.3.10    # Dynamic Time Warping
statsmodels>=0.14.0     # Seasonal decomposition
mlflow>=2.9.0           # Experiment tracking
matplotlib>=3.7.0       # Visualization
seaborn>=0.12.0         # Enhanced plotting
```

## Performance Considerations

**Fourier Analysis:**
- Time complexity: O(n log n) due to FFT
- Fast for sequences up to 10,000+ points
- Memory efficient

**HMM:**
- Time complexity: O(T × N² × K) where T=length, N=states, K=iterations
- Moderate for typical trading data (T=500-1000, N=3-5)
- May be slow for very long sequences or many states

**DTW:**
- Time complexity: O(n × m × w) where n,m=sequence lengths, w=window size
- Can be slow for large datasets
- Use `max_distance` parameter to speed up matching
- Consider down-sampling very long sequences

## Next Steps

1. **Week 2**: Implement portfolio optimization using regime information
2. **Week 3**: Add automated cycle-based trading signals
3. **Week 4**: Integrate with backtesting framework
4. **Week 5**: Build ensemble predictor combining all three models

## References

- Fourier Analysis: [Cooley-Tukey FFT Algorithm](https://en.wikipedia.org/wiki/Cooley%E2%80%93Tukey_FFT_algorithm)
- HMM: [A Tutorial on Hidden Markov Models](https://www.cs.ubc.ca/~murphyk/Bayes/rabiner.pdf)
- DTW: [Dynamic Time Warping](https://en.wikipedia.org/wiki/Dynamic_time_warping)

## Support

For questions or issues:
1. Check test suite for usage examples: `tests/ml/test_cyclical.py`
2. Review MLFlow UI for logged experiments: http://localhost:5000
3. See parent ML module README: `../README.md`
