"""
Capacity Forecasting Module
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from typing import Union, Optional
import logging


class CapacityForecaster:
    def __init__(self, n_lags: int = 5, n_estimators: int = 100, random_state: int = 42):
        """
        Initialize the capacity forecaster.
        
        Args:
            n_lags: Number of lag features to use.
            n_estimators: Number of trees in the random forest.
            random_state: Random seed for reproducibility.
        """
        self.n_lags = n_lags
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1
        )
        self.is_fitted = False
        self.logger = logging.getLogger(__name__)

    def _create_lag_features(self, data: np.ndarray) -> np.ndarray:
        """
        Create lag features for time series data.
        
        Args:
            data: 1D array of time series values.
            
        Returns:
            2D array of shape (n_samples, n_lags) where each row contains
            the previous n_lags values.
        """
        if len(data) < self.n_lags + 1:
            raise ValueError(f"Data length must be at least {self.n_lags + 1}")
        
        X = []
        for i in range(self.n_lags, len(data)):
            X.append(data[i - self.n_lags:i])
        return np.array(X)

    def fit(self, data: Union[np.ndarray, pd.Series]) -> 'CapacityForecaster':
        """
        Fit the capacity forecaster to the time series data.
        
        Args:
            data: 1D array of time series values (e.g., CPU utilization).
            
        Returns:
            Self instance.
        """
        if isinstance(data, pd.Series):
            data = data.values
        
        # Create lag features and target (next value)
        X = self._create_lag_features(data)
        y = data[self.n_lags:]  # Target is the next value after the lags
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_fitted = True
        return self

    def predict(self, data: Union[np.ndarray, pd.Series], steps: int = 1) -> np.ndarray:
        """
        Predict future capacity utilization.
        
        Args:
            data: Recent time series data (must be at least n_lags long).
            steps: Number of future steps to predict.
            
        Returns:
            Array of predicted values.
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before making predictions.")
        
        if isinstance(data, pd.Series):
            data = data.values
        
        if len(data) < self.n_lags:
            raise ValueError(f"Input data must have at least {self.n_lags} points")
        
        predictions = []
        current_data = data.tolist()
        
        for _ in range(steps):
            # Prepare the last n_lags points
            X_new = np.array(current_data[-self.n_lags:]).reshape(1, -1)
            X_new_scaled = self.scaler.transform(X_new)
            pred = self.model.predict(X_new_scaled)[0]
            predictions.append(pred)
            current_data.append(pred)
        
        return np.array(predictions)