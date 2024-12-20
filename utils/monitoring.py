import logging
from datetime import datetime
from typing import Dict, List, Any
import json

logger = logging.getLogger(__name__)

class ActivityMonitor:
    def __init__(self):
        self.activities: List[Dict[str, Any]] = []

    async def log_activity(self, activity_type: str, details: dict):
        activity = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': activity_type,
            'details': details
        }
        self.activities.append(activity)
        logger.info(f"Activity logged: {json.dumps(activity)}")
        
        if await self._check_suspicious(activity):
            logger.warning(f"Suspicious activity detected: {json.dumps(activity)}")
    
    async def _check_suspicious(self, activity: dict) -> bool:
        if activity['type'] == 'blockchain':
            if 'value' in activity['details']:
                value = float(activity['details']['value'])
                if value > 1.0:
                    return True
                    
        elif activity['type'] == 'twitter':
            recent_tweets = [
                a for a in self.activities[-10:]
                if a['type'] == 'twitter' 
                and (datetime.utcnow() - datetime.fromisoformat(a['timestamp'])).seconds < 3600
            ]
            if len(recent_tweets) > 5:
                return True
                
        return False

    def get_recent_activities(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self.activities[-limit:]

    async def generate_report(self) -> Dict[str, Any]:
        return {
            'total_activities': len(self.activities),
            'types_breakdown': self._get_type_breakdown(),
            'recent_suspicious': self._get_suspicious_activities(),
            'hourly_volume': self._get_hourly_volume()
        }
    
    def _get_type_breakdown(self) -> Dict[str, int]:
        breakdown = {}
        for activity in self.activities:
            activity_type = activity['type']
            breakdown[activity_type] = breakdown.get(activity_type, 0) + 1
        return breakdown
    
    def _get_suspicious_activities(self) -> List[Dict[str, Any]]:
        return [
            activity for activity in self.activities[-100:]
            if activity.get('suspicious', False)
        ]
    
    def _get_hourly_volume(self) -> Dict[str, int]:
        hourly = {}
        for activity in self.activities:
            hour = datetime.fromisoformat(activity['timestamp']).strftime('%Y-%m-%d %H:00')
            hourly[hour] = hourly.get(hour, 0) + 1
        return hourly