"""
ML Pipeline for AI Operations
"""

from typing import Dict, Any, Optional
import logging
import numpy as np
import pandas as pd
from .anomaly_detection import AnomalyDetector
from .predictive_monitoring import PredictiveMonitor
from .capacity_forecasting import CapacityForecaster


class MLPipeline:
    def __init__(self):
        """
        Initialize the ML Pipeline.
        """
        self.anomaly_detector = AnomalyDetector()
        self.predictive_monitor = PredictiveMonitor()
        self.capacity_forecaster = CapacityForecaster()
        self.logger = logging.getLogger(__name__)
        self.is_fitted = False

    def fit_anomaly_detector(self, X: np.ndarray) -> 'MLPipeline':
        """
        Fit the anomaly detection model.
        
        Args:
            X: Training data.
            
        Returns:
            Self instance.
        """
        self.anomaly_detector.fit(X)
        return self

    def fit_predictive_monitor(self, data: np.ndarray) -> 'MLPipeline':
        """
        Fit the predictive monitoring model.
        
        Args:
            data: Time series data.
            
        Returns:
            Self instance.
        """
        self.predictive_monitor.fit(data)
        return self

    def fit_capacity_forecaster(self, data: np.ndarray) -> 'MLPipeline':
        """
        Fit the capacity forecasting model.
        
        Args:
            data: Time series data.
            
        Returns:
            Self instance.
        """
        self.capacity_forecaster.fit(data)
        return self

    def detect_anomalies(self, X: np.ndarray) -> Dict[str, Any]:
        """
        Detect anomalies in the data.
        
        Args:
            X: Data to analyze.
            
        Returns:
            Dictionary with anomaly predictions and scores.
        """
        predictions = self.anomaly_detector.predict(X)
        scores = self.anomaly_detector.predict_proba(X)
        return {
            "predictions": predictions.tolist(),
            "scores": scores.tolist(),
            "anomaly_count": int((predictions == -1).sum())
        }

    def predict_next_values(self, data: np.ndarray, steps: int = 1) -> Dict[str, Any]:
        """
        Predict future values for monitoring.
        
        Args:
            data: Recent time series data.
            steps: Number of steps to predict.
            
        Returns:
            Dictionary with predictions.
        """
        predictions = self.predictive_monitor.predict(data, steps=steps)
        return {
            "predictions": predictions.tolist(),
            "steps": steps
        }

    def forecast_capacity(self, data: np.ndarray, steps: int = 1) -> Dict[str, Any]:
        """
        Forecast future capacity utilization.
        
        Args:
            data: Recent capacity data.
            steps: Number of steps to forecast.
            
        Returns:
            Dictionary with forecasts.
        """
        predictions = self.capacity_forecaster.predict(data, steps=steps)
        return {
            "predictions": predictions.tolist(),
            "steps": steps
        }