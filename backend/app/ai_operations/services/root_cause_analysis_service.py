"""
Root Cause Analysis Service
"""

from .openai_service import OpenAIService
import logging
from typing import Dict, Any, List, Optional


class RootCauseAnalysisService:
    def __init__(self):
        """
        Initialize the root cause analysis service.
        """
        self.openai_service = OpenAIService()
        self.logger = logging.getLogger(__name__)

    def analyze_root_cause(
        self,
        alert_data: Dict[str, Any],
        related_metrics: Optional[Dict[str, Any]] = None,
        recent_logs: Optional[List[str]] = None,
        topology_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Perform root cause analysis for an alert.
        
        Args:
            alert_data: Dictionary containing alert information.
            related_metrics: Optional dictionary of related metrics.
            recent_logs: Optional list of recent log entries.
            topology_info: Optional information about system topology.
            
        Returns:
            A string describing the likely root cause and contributing factors.
        """
        # Construct a prompt for the OpenAI API
        prompt = f"""
        Perform a root cause analysis for the following IT alert:
        
        Alert ID: {alert_data.get('alert_id', 'N/A')}
        Alert Name: {alert_data.get('alert_name', 'N/A')}
        Severity: {alert_data.get('severity', 'N/A')}
        Description: {alert_data.get('description', 'N/A')}
        """
        
        if related_metrics:
            prompt += f"\n\nRelated Metrics:\n{related_metrics}"
        
        if recent_logs:
            prompt += f"\n\nRecent Logs:\n" + "\n".join(recent_logs)
        
        if topology_info:
            prompt += f"\n\nTopology Information:\n{topology_info}"
        
        prompt += "\n\nBased on the above information, provide a concise root cause analysis. "
        prompt += "Include: "
        prompt += "1. Most likely root cause "
        prompt += "2. Contributing factors "
        prompt += "3. Suggested investigative steps "
        prompt += "4. Potential impact if not addressed"
        
        system_message = """
        You are an expert IT systems engineer with deep knowledge of infrastructure, 
        networks, applications, and databases. Your task is to analyze alerts and 
        determine the most likely root cause. Be concise, technical, and actionable.
        """
        
        try:
            analysis = self.openai_service._create_chat_completion(
                prompt=prompt,
                system_message=system_message,
                temperature=0.4,  # Slightly higher for analysis but still focused
                max_tokens=500
            )
            return analysis
        except Exception as e:
            self.logger.error(f"Failed to perform root cause analysis: {e}")
            return f"Unable to perform root cause analysis due to an error: {str(e)}"