# ========================================
# API ENDPOINTS FOR HALLUCINATION DETECTION
# ========================================

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List

hallucination_router = APIRouter(prefix="/hallucination", tags=["Hallucination Detection"])

class HallucinationAnalysisRequest(BaseModel):
    prompt: str
    response: str
    model_info: Optional[Dict[str, Any]] = None
    async_analysis: bool = True

class HallucinationAnalysisResponse(BaseModel):
    request_id: str
    overall_score: float
    confidence_level: str
    detected_hallucinations: List[Dict[str, Any]]
    analysis_breakdown: Dict[str, float]
    recommendations: List[str]
    processing_time_ms: int

# Global service instance
hallucination_service = HallucinationMonitoringService()

@hallucination_router.post("/analyze", response_model=HallucinationAnalysisResponse)
async def analyze_hallucination(
    request: HallucinationAnalysisRequest,
    background_tasks: BackgroundTasks,
    request_id: str = None
):
    """Analyze text for potential hallucinations"""
    
    if not request_id:
        import uuid
        request_id = str(uuid.uuid4())
    
    try:
        result = await hallucination_service.analyze_response(
            request_id=request_id,
            prompt=request.prompt,
            response=request.response,
            model_info=request.model_info
        )
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail="Hallucination analysis failed"
            )
        
        return HallucinationAnalysisResponse(
            request_id=result.request_id,
            overall_score=result.overall_score,
            confidence_level=result.confidence_level.value,
            detected_hallucinations=[asdict(evidence) for evidence in result.detected_hallucinations],
            analysis_breakdown=result.analysis_breakdown,
            recommendations=result.recommendations,
            processing_time_ms=result.processing_time_ms
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing hallucination: {str(e)}"
        )

@hallucination_router.get("/result/{request_id}")
async def get_hallucination_result(request_id: str):
    """Get stored hallucination analysis result"""
    
    result = hallucination_service.get_result(request_id)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Hallucination analysis result not found"
        )
    
    return HallucinationAnalysisResponse(
        request_id=result.request_id,
        overall_score=result.overall_score,
        confidence_level=result.confidence_level.value,
        detected_hallucinations=[asdict(evidence) for evidence in result.detected_hallucinations],
        analysis_breakdown=result.analysis_breakdown,
        recommendations=result.recommendations,
        processing_time_ms=result.processing_time_ms
    )

@hallucination_router.get("/statistics")
async def get_hallucination_statistics(time_window_hours: int = 24):
    """Get hallucination detection statistics"""
    
    try:
        stats = hallucination_service.get_statistics(time_window_hours)
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting statistics: {str(e)}"
        )

# ========================================
# USAGE EXAMPLES AND INTEGRATION
# ========================================

"""
# Example 1: Standalone usage
detector = AdvancedHallucinationDetector()

result = detector.detect_hallucinations(
    request_id="test_001",
    prompt="What is the capital of France?",
    response="The capital of France is Paris, which was founded in 1985 by Napoleon Bonaparte.",
    context={"model": "gpt-3.5-turbo"}
)

print(f"Hallucination Score: {result.overall_score:.3f}")
print(f"Confidence: {result.confidence_level.value}")
print(f"Issues Found: {len(result.detected_hallucinations)}")

for evidence in result.detected_hallucinations:
    print(f"- {evidence.type.value}: {evidence.explanation}")

# Example 2: Integration with Meerkatics SDK
class EnhancedMeerkaticsMonitor(MeerkaticsMonitor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hallucination_service = HallucinationMonitoringService({
            'enabled': True,
            'async_mode': True,
            'store_results': True
        })
    
    async def _enhanced_track_request(self, request_data, response_data):
        # Normal tracking
        self._track_request(request_data, response_data)
        
        # Hallucination detection
        if response_data.response:
            prompt = request_data.prompt or " ".join([
                msg.get('content', '') for msg in (request_data.messages or [])
            ])
            
            hallucination_result = await self.hallucination_service.analyze_response(
                request_id=request_data.request_id,
                prompt=prompt,
                response=response_data.response,
                model_info={
                    'provider': request_data.provider,
                    'model': request_data.model
                }
            )
            
            # Add hallucination data to tracking
            if hallucination_result and hallucination_result.overall_score > 0.3:
                self.add_metadata('hallucination_score', hallucination_result.overall_score)
                self.add_metadata('hallucination_confidence', hallucination_result.confidence_level.value)

# Example 3: Real-time monitoring integration
async def monitor_llm_call_with_hallucination_detection(prompt, response, model_info):
    # Create detector
    detector = AdvancedHallucinationDetector()
    
    # Analyze for hallucinations
    result = await asyncio.create_task(
        asyncio.get_event_loop().run_in_executor(
            None,
            detector.detect_hallucinations,
            f"req_{int(time.time())}",
            prompt,
            response,
            model_info
        )
    )
    
    # Take action based on results
    if result.overall_score > 0.7:
        # High hallucination risk - log alert
        logging.warning(f"High hallucination risk detected: {result.overall_score:.3f}")
        
        # Could trigger alerts, regeneration, human review, etc.
        return {
            'response': response,
            'hallucination_warning': True,
            'hallucination_score': result.overall_score,
            'recommendations': result.recommendations
        }
    
    return {
        'response': response,
        'hallucination_warning': False,
        'hallucination_score': result.overall_score
    }

# Example 4: Batch processing for model evaluation
def evaluate_model_hallucination_rate(test_cases):
    detector = AdvancedHallucinationDetector()
    results = []
    
    for i, (prompt, response) in enumerate(test_cases):
        result = detector.detect_hallucinations(
            request_id=f"eval_{i}",
            prompt=prompt,
            response=response
        )
        results.append(result)
    
    # Calculate statistics
    avg_score = sum(r.overall_score for r in results) / len(results)
    high_risk_rate = sum(1 for r in results if r.overall_score > 0.6) / len(results)
    
    print(f"Model Hallucination Evaluation:")
    print(f"Average Score: {avg_score:.3f}")
    print(f"High Risk Rate: {high_risk_rate:.1%}")
    
    return results
"""