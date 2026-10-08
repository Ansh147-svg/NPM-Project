"""
Alert Explanation Service
"""

from .openai_service import OpenAIService
import logging
from typing import Dict, Any


class AlertExplanationService:
    def __init__(self):
        """
        Initialize the alert explanation service.
        """
        self.openai_service = OpenAIService()
        self.logger = logging.getLogger(__name__)

    def explain_alert(self, alert_data: Dict[str, Any]) -> str:
        """
        Generate an explanation for an alert.
        
        Args:
            alert_data: Dictionary containing alert information.
                Expected keys: alert_id, alert_name, severity, description, 
                metrics (optional), logs (optional).
                
        Returns:
            A human-readable explanation of the alert.
        """
        # Construct a prompt for the OpenAI API
        prompt = f"""
        Explain the following IT alert in a clear, concise manner suitable for an IT operator:
        
        Alert ID: {alert_data.get('alert_id', 'N/A')}
        Alert Name: {alert_data.get('alert_name', 'N/A')}
        Severity: {alert_data.get('severity', 'N/A')}
        Description: {alert_data.get('description', 'N/A')}
        """
        
        # Add metrics if available
        if 'metrics' in alert_data and alert_data['metrics']:
            prompt += f"\nMetrics: {alert_data['metrics']}"
        
        # Add logs if available
        if 'logs' in alert_data and alert_data['logs']:
            prompt += f"\nLogs: {alert_data['logs']}"
        
        prompt += "\n\nExplanation:"
        
        system_message = """
        You are an expert IT operations analyst. Your task is to explain alerts in a clear, 
        concise, and actionable manner. Focus on what the alert means, potential impact, 
        and suggest immediate steps if applicable. Avoid technical jargon where possible, 
        but be precise.
        """
        
        try:
            explanation = self.openai_service._create_chat_completion(
                prompt=prompt,
                system_message=system_message,
                temperature=0.3,  # Lower temperature for more focused explanations
                max_tokens=300
            )
            return explanation
        except Exception as e:
            self.logger.error(f"Failed to generate alert explanation: {e}")
            return f"Unable to generate explanation due to an error: {str(e)}"