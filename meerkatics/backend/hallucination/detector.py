# Meerkatics Advanced Hallucination Detection System
# Multi-modal hallucination detection using semantic analysis, fact-checking, and ML models

import re
import json
import asyncio
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from abc import ABC, abstractmethod
import logging
from concurrent.futures import ThreadPoolExecutor
import requests
from enum import Enum

# ========================================
# CORE DATA MODELS
# ========================================

class HallucinationType(Enum):
    FACTUAL_ERROR = "factual_error"
    SEMANTIC_INCONSISTENCY = "semantic_inconsistency"
    TEMPORAL_INCONSISTENCY = "temporal_inconsistency"
    SELF_CONTRADICTION = "self_contradiction"
    UNCERTAINTY_EXPRESSION = "uncertainty_expression"
    CONTEXT_MISALIGNMENT = "context_misalignment"
    KNOWLEDGE_CUTOFF_VIOLATION = "knowledge_cutoff_violation"
    IMPOSSIBLE_CLAIM = "impossible_claim"

class ConfidenceLevel(Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class HallucinationEvidence:
    """Evidence for a specific hallucination detection"""
    type: HallucinationType
    confidence: float  # 0.0 to 1.0
    text_segment: str
    explanation: str
    supporting_facts: List[str]
    contradiction_source: Optional[str] = None
    severity: str = "medium"  # low, medium, high, critical

@dataclass
class HallucinationResult:
    """Complete hallucination detection result"""
    request_id: str
    overall_score: float  # 0.0 (no hallucination) to 1.0 (definite hallucination)
    confidence_level: ConfidenceLevel
    detected_hallucinations: List[HallucinationEvidence]
    analysis_breakdown: Dict[str, float]
    recommendations: List[str]
    processing_time_ms: int
    timestamp: datetime
