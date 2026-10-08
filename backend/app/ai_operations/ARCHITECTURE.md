# AI Operations Module Architecture

## Overview
The AI Operations Module for NetVision provides intelligent operations capabilities including alert explanation, root cause analysis, anomaly detection, predictive monitoring, and capacity forecasting.

## Components

### 1. ML Pipeline (ml/)
Handles machine learning models for:
- Anomaly Detection
- Predictive Monitoring
- Capacity Forecasting

### 2. AI Services (services/)
Interfaces with OpenAI Compatible APIs for:
- Alert Explanation
- Root Cause Analysis

### 3. API Layer (api/)
RESTful endpoints exposing the module's functionality.

### 4. Data Schemas (schemas/)
Pydantic models for request/response validation.

### 5. Utilities (utils/)
Helper functions and shared components.

## Data Flow
1. Incoming metrics and alerts are processed by the ML pipeline for anomaly detection and forecasting.
2. Detected anomalies trigger alert explanation and root cause analysis via AI services.
3. Results are exposed through the API for consumption by the dashboard and other services.

## Dependencies
- scikit-learn
- OpenAI API client
- pandas
- numpy
- FastAPI (if used in backend)