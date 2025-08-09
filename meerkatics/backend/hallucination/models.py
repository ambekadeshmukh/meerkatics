# ========================================
# INTEGRATION WITH MEERKATICS MONITOR
# ========================================

class HallucinationMonitoringService:
    """Service for integrating hallucination detection with main monitoring"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.detector = AdvancedHallucinationDetector(config)
        self.enabled = config.get('enabled', True)
        self.async_mode = config.get('async_mode', True)
        self.store_results = config.get('store_results', True)
        
        # Storage for results (in production, this would be a database)
        self.results_storage = {}
        
        self.logger = logging.getLogger("HallucinationMonitoring")
    
    async def analyze_response(
        self,
        request_id: str,
        prompt: str,
        response: str,
        model_info: Dict[str, Any] = None
    ) -> Optional[HallucinationResult]:
        """Analyze response for hallucinations"""
        
        if not self.enabled:
            return None
        
        try:
            if self.async_mode:
                # Run detection in background
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    self.detector.detect_hallucinations,
                    request_id,
                    prompt,
                    response,
                    model_info
                )
            else:
                # Run detection synchronously
                result = self.detector.detect_hallucinations(
                    request_id, prompt, response, model_info
                )
            
            # Store result if configured
            if self.store_results:
                self.results_storage[request_id] = result
            
            # Log significant findings
            if result.overall_score > 0.5:
                self.logger.warning(
                    f"High hallucination score ({result.overall_score:.3f}) for request {request_id}"
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in hallucination analysis: {e}")
            return None
    
    def get_result(self, request_id: str) -> Optional[HallucinationResult]:
        """Get stored hallucination analysis result"""
        return self.results_storage.get(request_id)
    
    def get_statistics(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Get hallucination detection statistics"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
        
        recent_results = [
            result for result in self.results_storage.values()
            if result.timestamp > cutoff_time
        ]
        
        if not recent_results:
            return {
                'total_analyzed': 0,
                'average_score': 0.0,
                'high_risk_count': 0,
                'detection_rate': 0.0
            }
        
        total_analyzed = len(recent_results)
        average_score = sum(r.overall_score for r in recent_results) / total_analyzed
        high_risk_count = sum(1 for r in recent_results if r.overall_score > 0.6)
        detection_rate = high_risk_count / total_analyzed
        
        # Breakdown by type
        type_counts = {}
        for result in recent_results:
            for evidence in result.detected_hallucinations:
                type_name = evidence.type.value
                type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        return {
            'total_analyzed': total_analyzed,
            'average_score': average_score,
            'high_risk_count': high_risk_count,
            'detection_rate': detection_rate,
            'hallucination_types': type_counts,
            'time_window_hours': time_window_hours
        }
