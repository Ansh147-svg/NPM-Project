"""
API Routes for AI Operations Module
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging
import numpy as np

from ..services.alert_explanation_service import AlertExplanationService
from ..services.root_cause_analysis_service import RootCauseAnalysisService
from ..ml.pipeline import MLPipeline
from ..schemas.alert import (
    AlertExplanationRequest,
    AlertExplanationResponse,
    RootCauseAnalysisRequest,
    RootCauseAnalysisResponse
)
from ..schemas.metrics import (
    AnomalyDetectionRequest,
    AnomalyDetectionResponse,
    PredictiveMonitoringRequest,
    PredictiveMonitoringResponse,
    CapacityForecastingRequest,
    CapacityForecastingResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services (in a real app, these might be dependency injected)
alert_explanation_service = AlertExplanationService()
root_cause_analysis_service = RootCauseAnalysisService()
ml_pipeline = MLPipeline()


@router.post("/explain-alert", response_model=AlertExplanationResponse)
async def explain_alert(request: AlertExplanationRequest):
    """
    Generate an explanation for the given alert.
    """
    try:
        explanation = alert_explanation_service.explain_alert(request.alert.dict())
        return AlertExplanationResponse(
            explanation=explanation,
            alert_id=request.alert.alert_id
        )
    except Exception as e:
        logger.error(f"Error in explain_alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/root-cause-analysis", response_model=RootCauseAnalysisResponse)
async def root_cause_analysis(request: RootCauseAnalysisRequest):
    """
    Perform root cause analysis for the given alert.
    """
    try:
        analysis = root_cause_analysis_service.analyze_root_cause(
            alert_data=request.alert.dict(),
            related_metrics=request.related_metrics,
            recent_logs=request.recent_logs,
            topology_info=request.topology_info
        )
        return RootCauseAnalysisResponse(
            analysis=analysis,
            alert_id=request.alert.alert_id
        )
    except Exception as e:
        logger.error(f"Error in root_cause_analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-anomalies", response_model=AnomalyDetectionResponse)
async def detect_anomalies(request: AnomalyDetectionRequest):
    """
    Detect anomalies in the provided metrics data.
    """
    try:
        # Convert list of lists to numpy array
        data = np.array(request.data)
        # In a real scenario, we would need to fit the model first.
        # For now, we assume the model is pre-trained or we fit on the fly (not ideal for production).
        # We'll fit the anomaly detector on the provided data (for demo purposes).
        ml_pipeline.fit_anomaly_detector(data)
        result = ml_pipeline.detect_anomalies(data)
        return AnomalyDetectionResponse(**result)
    except Exception as e:
        logger.error(f"Error in detect_anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predictive-monitoring", response_model=PredictiveMonitoringResponse)
async def predictive_monitoring(request: PredictiveMonitoringRequest):
    """
    Predict future values for monitoring metrics.
    """
    try:
        data = np.array(request.data)
        # Fit the predictive monitor on the provided data (for demo)
        ml_pipeline.fit_predictive_monitor(data)
        result = ml_pipeline.predict_next_values(data, steps=request.steps)
        return PredictiveMonitoringResponse(**result)
    except Exception as e:
        logger.error(f"Error in predictive_monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/capacity-forecasting", response_model=CapacityForecastingResponse)
async def capacity_forecasting(request: CapacityForecastingRequest):
    """
    Forecast future capacity utilization.
    """
    try:
        data = np.array(request.data)
        # Fit the capacity forecaster on the provided data (for demo)
        ml_pipeline.fit_capacity_forecaster(data)
        result = ml_pipeline.forecast_capacity(data, steps=request.steps)
        return CapacityForecastingResponse(**result)
    except Exception as e:
        logger.error(f"Error in capacity_forecasting: {e}")
        raise HTTPException(status_code=500, detail=str(e))