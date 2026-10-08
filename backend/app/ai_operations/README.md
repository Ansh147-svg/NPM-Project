# AI Operations Module

This module provides AI-driven capabilities for IT operations including:
- Alert Explanation
- Root Cause Analysis
- Anomaly Detection
- Predictive Monitoring
- Capacity Forecasting

## Components

- `ml/`: Machine learning models and pipeline
- `services/`: AI services (OpenAI integration)
- `api/`: API route definitions
- `schemas/`: Pydantic models for request/validation
- `utils/`: Helper functions

## Installation

Ensure the following dependencies are installed:
- scikit-learn
- openai
- fastapi
- pydantic
- numpy
- pandas

Add the module to your Python path and import as needed.

## Usage

### ML Pipeline
```python
from app.ai_operations.ml.pipeline import MLPipeline
import numpy as np

# Initialize pipeline
pipeline = MLPipeline()

# Fit anomaly detector
data = np.array([[1, 2, 3], [4, 5, 6], ...])
pipeline.fit_anomaly_detector(data)

# Detect anomalies
result = pipeline.detect_anomalies(data)
```

### API Endpoints
The module provides the following REST endpoints under `/ai-operations`:
- POST `/explain-alert` - Generate alert explanation
- POST `/root-cause-analysis` - Perform root cause analysis
- POST `/detect-anomalies` - Detect anomalies in metrics
- POST `/predictive-monitoring` - Forecast future values
- POST `/capacity-forecasting` - Forecast capacity utilization

See the API documentation (Swagger UI) for detailed request/response formats.

## Configuration

Set the following environment variables for OpenAI integration:
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_API_BASE`: (Optional) Base URL for OpenAI compatible API (defaults to https://api.openai.com/v1)

## Dashboard
See `DASHBOARD.md` for an outline of the recommended dashboard components.