# ML Module Documentation

## Overview

This module contains the advanced AI/ML capabilities for the Quant Analytics Platform, including:

- **Cyclical Pattern Detection** (Fourier, HMM, DTW)
- **Deep Learning Models** (LSTM, Transformers)
- **Factor Analysis** (Fama-French)
- **Options Analytics** (Gamma Exposure)
- **Network Analysis** (Trading clusters)
- **Ensemble Predictions**

## Quick Start

### 1. Setup Infrastructure

```bash
# From project root
./setup-ml.sh
```

This will:
- Install ML dependencies
- Start MLFlow, MinIO, Redis, Celery workers
- Create MLFlow experiment
- Verify setup

### 2. Train Your First Model

```python
from app.ml.cyclical.fourier import FourierCyclicalDetector
from app.ml.utils.mlflow_tracker import MLFlowTracker

# Initialize
detector = FourierCyclicalDetector()
tracker = MLFlowTracker()

# Train
with tracker.start_run("my_first_model"):
    results = detector.detect_cycles(trading_data)
    tracker.log_metrics(results)
```

### 3. Make Predictions

```python
from app.ml.ensemble import MultiModelEnsemble

ensemble = MultiModelEnsemble()
prediction = ensemble.predict(recent_data, market_context)

print(f"Predicted return: {prediction['prediction']['return']:.2%}")
print(f"Confidence: {prediction['confidence']:.2f}")
```

## Module Structure

```
app/ml/
├── __init__.py                  # Main exports
├── ensemble.py                  # Multi-model ensemble
├── features/                    # Feature engineering
│   ├── engineering.py          # 200+ features
│   └── selection.py            # Feature selection
├── cyclical/                    # Pattern detection
│   ├── fourier.py              # Fourier analysis
│   ├── hmm.py                  # Hidden Markov Models
│   ├── dtw.py                  # Dynamic Time Warping
│   └── seasonal.py             # Seasonal decomposition
├── deep_learning/               # Neural networks
│   ├── lstm.py                 # LSTM models
│   ├── transformer.py          # Transformer models
│   └── attention.py            # Attention mechanisms
├── factors/                     # Factor analysis
│   ├── fama_french.py          # Fama-French models
│   └── custom_factors.py       # Custom factors
├── options/                     # Options analytics
│   ├── gamma_exposure.py       # Gamma analysis
│   ├── volatility.py           # Volatility models
│   └── greeks.py               # Options Greeks
├── network/                     # Network analysis
│   ├── graph_analysis.py       # Graph algorithms
│   └── clustering.py           # Community detection
├── pipeline/                    # ML pipeline
│   ├── training.py             # Training pipeline
│   ├── inference.py            # Inference pipeline
│   └── backtesting.py          # Backtest engine
└── utils/                       # Utilities
    ├── metrics.py              # Evaluation metrics
    ├── mlflow_tracker.py       # MLFlow integration
    └── model_registry.py       # Model management
```

## Configuration

All ML settings are in `app/core/ml_config.py`:

```python
from app.core.ml_config import ml_settings

# Access settings
print(ml_settings.MLFLOW_TRACKING_URI)
print(ml_settings.LSTM_HIDDEN_DIM)
print(ml_settings.ENSEMBLE_MODELS)
```

Environment variables (`.env`):
```bash
ML_MLFLOW_TRACKING_URI=http://localhost:5000
ML_MODEL_CACHE_DIR=./models
ML_RANDOM_SEED=42
ML_USE_GPU=false
ML_LSTM_HIDDEN_DIM=128
ML_N_FEATURES=200
```

## Training Models

### Via CLI

```bash
# Train all models
python -m app.cli ml train

# Train specific model
python -m app.cli ml train --model cyclical

# Backtest
python -m app.cli ml backtest --strategy follow_politicians --start 2020-01-01 --end 2024-12-31
```

### Via Celery (Production)

```python
from app.tasks.ml_tasks import train_ensemble_model

# Trigger training job
result = train_ensemble_model.delay(
    start_date="2020-01-01",
    end_date="2024-12-31"
)

# Check status
print(result.status)
```

### Programmatically

```python
from app.ml.pipeline.training import MLTrainingPipeline

pipeline = MLTrainingPipeline(config)
results = await pipeline.train_all_models()
```

## Making Predictions

### REST API

```bash
curl http://localhost:8000/api/v1/ml/predictions/NVDA?horizon=30d
```

Response:
```json
{
  "prediction": {
    "return": 0.052,
    "volatility": 0.023,
    "probability": {"up": 0.65, "down": 0.25, "flat": 0.10}
  },
  "confidence": 0.78,
  "similar_patterns": [...],
  "current_regime": "Bull Market",
  "factors": {...}
}
```

### Python

```python
from app.ml.ensemble import get_ml_ensemble

ensemble = get_ml_ensemble()
prediction = ensemble.predict(ticker_data, market_context)
```

## Monitoring

### MLFlow UI

Access at `http://localhost:5000`

- View experiments
- Compare runs
- Visualize metrics
- Download models

### Celery Monitoring (Flower)

Access at `http://localhost:5555`

- Monitor workers
- View task queues
- Check task history
- Revoke tasks

### Metrics

All predictions are logged with:
- Model performance metrics
- Feature importance
- Prediction confidence
- Actual vs predicted

## Common Tasks

### Add a New Feature

```python
# In app/ml/features/engineering.py

def extract_my_feature(self, trades):
    """Extract my custom feature."""
    return trades.apply(lambda x: ...)
```

### Add a New Model

```python
# Create app/ml/my_model/my_detector.py

class MyDetector:
    def predict(self, data, context):
        # Your logic here
        return prediction
```

Register in ensemble:
```python
# In ml_config.py
ENSEMBLE_MODELS = [
    "cyclical",
    "regime",
    "my_model"  # Add here
]
```

### Retrain Models

```bash
# Manual retrain
python -m app.cli ml train --force

# Scheduled (via Celery Beat)
# Runs automatically every 7 days
```

## Troubleshooting

### MLFlow Not Starting

```bash
# Check logs
docker logs quant-mlflow

# Recreate database
docker-compose -f docker-compose-ml.yml down -v
docker-compose -f docker-compose-ml.yml up -d
```

### Celery Workers Not Processing

```bash
# Check worker logs
docker logs quant-celery-ml

# Restart workers
docker restart quant-celery-ml
```

### Out of Memory

Reduce batch sizes in `ml_config.py`:
```python
ML_LSTM_BATCH_SIZE=16  # Default: 32
ML_N_JOBS=2  # Default: -1 (all CPUs)
```

### GPU Not Detected

```bash
# Enable GPU
ML_USE_GPU=true

# Check CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

## Performance Tuning

### Feature Engineering

```python
# Parallel processing
ML_N_JOBS=-1  # Use all CPUs

# Feature caching
ML_FEATURE_CACHE_TTL=3600  # 1 hour
```

### Model Inference

```python
# Use ONNX for faster inference
# Models are automatically converted

# Prediction caching
ML_PREDICTION_CACHE_TTL=300  # 5 minutes
```

### Training

```python
# Hyperparameter tuning
ML_OPTUNA_N_TRIALS=100
ML_OPTUNA_TIMEOUT=3600

# Early stopping
ML_LSTM_EPOCHS=100  # Max epochs
# Early stopping built into training loop
```

## API Reference

See full API documentation at `/api/v1/docs` when server is running.

Key endpoints:
- `GET /api/v1/ml/predictions/{ticker}` - Get predictions
- `POST /api/v1/ml/anomaly-detection` - Detect anomalies
- `GET /api/v1/ml/models` - List models
- `POST /api/v1/ml/train` - Trigger training

## Best Practices

1. **Always use MLFlow** for experiment tracking
2. **Version your models** in the registry
3. **Backtest** before deploying to production
4. **Monitor** prediction accuracy over time
5. **Retrain regularly** (default: weekly)
6. **Cache predictions** to reduce latency
7. **Use walk-forward validation** for time series
8. **Document** model changes and performance

## Support

- See `ADVANCED_AI_SYSTEM.md` for architecture details
- Check Issues: https://github.com/your-repo/issues
- Email: support@yourplatform.com

## Contributing

1. Add tests for new features
2. Document all functions
3. Follow code style (black, ruff)
4. Update this README
5. Submit PR with backtest results

---

**Happy Training! 🚀📊🤖**
