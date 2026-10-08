"""
Anomaly Detection Module
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import List, Union, Optional
import pandas as pd


class AnomalyDetector:
    def __init__(self, contamination: float = 0.1, random_state: int = 42):
        """
        Initialize the anomaly detector.
        
        Args:
            contamination: Expected proportion of anomalies in the data.
            random_state: Random seed for reproducibility.
        """
        self.contamination = contamination
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100
        )
        self.is_fitted = False

    def fit(self, X: Union[np.ndarray, pd.DataFrame]) -> 'AnomalyDetector':
        """
        Fit the anomaly detector to the training data.
        
        Args:
            X: Training data of shape (n_samples, n_features).
            
        Returns:
            Self instance.
        """
        if isinstance(X, pd.DataFrame):
            X = X.values
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_fitted = True
        return self

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """
        Predict whether each sample is an anomaly.
        
        Args:
            X: Data of shape (n_samples, n_features).
            
        Returns:
            Array of predictions (-1 for anomalies, 1 for normal).
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before making predictions.")
        
        if isinstance(X, pd.DataFrame):
            X = X.values
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def predict_proba(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """
        Predict the anomaly score for each sample.
        
        Args:
            X: Data of shape (n_samples, n_features).
            
        Returns:
            Array of anomaly scores (lower means more anomalous).
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before making predictions.")
        
        if isinstance(X, pd.DataFrame):
            X = X.values
        
        X_scaled = self.scaler.transform(X)
        return self.model.decision_function(X_scaled)