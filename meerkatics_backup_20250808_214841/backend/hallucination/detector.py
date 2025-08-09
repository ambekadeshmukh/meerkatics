
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

# ========================================
# BASE DETECTOR INTERFACE
# ========================================

class BaseHallucinationDetector(ABC):
    """Base class for hallucination detection methods"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    @abstractmethod
    def detect(self, prompt: str, response: str, context: Dict[str, Any] = None) -> Tuple[float, List[HallucinationEvidence]]:
        """
        Detect hallucinations in the response
        
        Returns:
            Tuple of (confidence_score, evidence_list)
        """
        pass
    
    @abstractmethod
    def get_detector_name(self) -> str:
        """Get the name of this detector"""
        pass

# ========================================
# SEMANTIC CONSISTENCY DETECTOR
# ========================================

class SemanticConsistencyDetector(BaseHallucinationDetector):
    """Detects semantic inconsistencies within the response"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.similarity_threshold = config.get('similarity_threshold', 0.3) if config else 0.3
        
        # Try to import sentence transformers for embeddings
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embeddings_available = True
        except ImportError:
            self.logger.warning("sentence-transformers not available, using simpler semantic analysis")
            self.embeddings_available = False
    
    def detect(self, prompt: str, response: str, context: Dict[str, Any] = None) -> Tuple[float, List[HallucinationEvidence]]:
        """Detect semantic inconsistencies"""
        evidence = []
        
        # Split response into sentences
        sentences = self._split_into_sentences(response)
        
        if len(sentences) < 2:
            return 0.0, evidence
        
        # Check for contradictions between sentences
        contradictions = self._find_contradictions(sentences)
        
        # Check for semantic drift
        semantic_drift = self._detect_semantic_drift(sentences)
        
        # Check prompt-response alignment
        alignment_score = self._check_prompt_alignment(prompt, response)
        
        # Calculate overall score
        contradiction_score = min(len(contradictions) * 0.2, 1.0)
        drift_score = semantic_drift
        alignment_penalty = max(0, 0.5 - alignment_score)
        
        overall_score = min(contradiction_score + drift_score + alignment_penalty, 1.0)
        
        # Create evidence for contradictions
        for contradiction in contradictions:
            evidence.append(HallucinationEvidence(
                type=HallucinationType.SELF_CONTRADICTION,
                confidence=contradiction['confidence'],
                text_segment=f"{contradiction['sentence1']} | {contradiction['sentence2']}",
                explanation=f"These sentences appear to contradict each other",
                supporting_facts=[],
                severity="high" if contradiction['confidence'] > 0.7 else "medium"
            ))
        
        # Create evidence for semantic drift
        if semantic_drift > 0.6:
            evidence.append(HallucinationEvidence(
                type=HallucinationType.SEMANTIC_INCONSISTENCY,
                confidence=semantic_drift,
                text_segment=response[:200] + "..." if len(response) > 200 else response,
                explanation="Response shows semantic drift or inconsistent topic flow",
                supporting_facts=[],
                severity="medium"
            ))
        
        # Create evidence for poor prompt alignment
        if alignment_score < 0.3:
            evidence.append(HallucinationEvidence(
                type=HallucinationType.CONTEXT_MISALIGNMENT,
                confidence=1.0 - alignment_score,
                text_segment=response[:100] + "..." if len(response) > 100 else response,
                explanation="Response does not align well with the prompt",
                supporting_facts=[],
                severity="medium"
            ))
        
        return overall_score, evidence
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _find_contradictions(self, sentences: List[str]) -> List[Dict[str, Any]]:
        """Find contradictory statements"""
        contradictions = []
        
        # Simple contradiction patterns
        contradiction_patterns = [
            (r'\b(is|are|was|were)\b', r'\b(is not|are not|was not|were not|isn\'t|aren\'t|wasn\'t|weren\'t)\b'),
            (r'\byes\b', r'\bno\b'),
            (r'\btrue\b', r'\bfalse\b'),
            (r'\balways\b', r'\bnever\b'),
            (r'\ball\b', r'\bnone\b'),
            (r'\bpossible\b', r'\bimpossible\b'),
        ]
        
        for i, sent1 in enumerate(sentences):
            for j, sent2 in enumerate(sentences[i+1:], i+1):
                # Check for direct negation patterns
                for pos_pattern, neg_pattern in contradiction_patterns:
                    if re.search(pos_pattern, sent1, re.IGNORECASE) and re.search(neg_pattern, sent2, re.IGNORECASE):
                        # Check if they're talking about similar subjects
                        similarity = self._calculate_sentence_similarity(sent1, sent2)
                        if similarity > 0.4:  # Similar enough to be a contradiction
                            contradictions.append({
                                'sentence1': sent1,
                                'sentence2': sent2,
                                'confidence': similarity * 0.8,
                                'pattern': f"{pos_pattern} vs {neg_pattern}"
                            })
        
        return contradictions
    
    def _calculate_sentence_similarity(self, sent1: str, sent2: str) -> float:
        """Calculate semantic similarity between sentences"""
        if self.embeddings_available:
            try:
                embeddings = self.model.encode([sent1, sent2])
                similarity = np.dot(embeddings[0], embeddings[1]) / (
                    np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
                )
                return float(similarity)
            except Exception:
                pass
        
        # Fallback to simple word overlap
        words1 = set(sent1.lower().split())
        words2 = set(sent2.lower().split())
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def _detect_semantic_drift(self, sentences: List[str]) -> float:
        """Detect semantic drift across sentences"""
        if len(sentences) < 3:
            return 0.0
        
        similarities = []
        for i in range(len(sentences) - 1):
            sim = self._calculate_sentence_similarity(sentences[i], sentences[i + 1])
            similarities.append(sim)
        
        # If similarity drops significantly, it might indicate drift
        avg_similarity = np.mean(similarities)
        min_similarity = np.min(similarities)
        
        # Drift score increases as similarities decrease
        drift_score = max(0, 0.8 - avg_similarity) + max(0, 0.5 - min_similarity)
        
        return min(drift_score, 1.0)
    
    def _check_prompt_alignment(self, prompt: str, response: str) -> float:
        """Check how well response aligns with prompt"""
        if not prompt or not response:
            return 0.5
        
        return self._calculate_sentence_similarity(prompt, response)
    
    def get_detector_name(self) -> str:
        return "semantic_consistency"

# ========================================
# FACTUAL VERIFICATION DETECTOR
# ========================================

class FactualVerificationDetector(BaseHallucinationDetector):
    """Detects factual errors using knowledge bases and web search"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.knowledge_sources = config.get('knowledge_sources', []) if config else []
        self.enable_web_search = config.get('enable_web_search', True) if config else True
        self.wikipedia_api_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
        
        # Common factual patterns to check
        self.factual_patterns = {
            'dates': r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}\b',
            'years': r'\b(19|20)\d{2}\b',
            'numbers': r'\b\d+(?:,\d{3})*(?:\.\d+)?\s*(?:million|billion|trillion|thousand)?\b',
            'percentages': r'\b\d+(?:\.\d+)?%\b',
            'currencies': r'\$\d+(?:,\d{3})*(?:\.\d{2})?\b',
            'measurements': r'\b\d+(?:\.\d+)?\s*(?:kg|km|m|cm|mm|lb|ft|in|miles|meters)\b',
            'people': r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # Simple name pattern
        }
    
    def detect(self, prompt: str, response: str, context: Dict[str, Any] = None) -> Tuple[float, List[HallucinationEvidence]]:
        """Detect factual errors"""
        evidence = []
        
        # Extract factual claims from response
        claims = self._extract_factual_claims(response)
        
        # Verify each claim
        verification_results = []
        for claim in claims:
            result = self._verify_claim(claim)
            verification_results.append(result)
            
            if result['status'] == 'false':
                evidence.append(HallucinationEvidence(
                    type=HallucinationType.FACTUAL_ERROR,
                    confidence=result['confidence'],
                    text_segment=claim['text'],
                    explanation=result['explanation'],
                    supporting_facts=result.get('sources', []),
                    severity="high"
                ))
            elif result['status'] == 'unverifiable':
                evidence.append(HallucinationEvidence(
                    type=HallucinationType.KNOWLEDGE_CUTOFF_VIOLATION,
                    confidence=result['confidence'],
                    text_segment=claim['text'],
                    explanation="Claim cannot be verified with available knowledge sources",
                    supporting_facts=[],
                    severity="medium"
                ))
        
        # Calculate overall factual error score
        if not verification_results:
            overall_score = 0.0
        else:
            error_count = sum(1 for r in verification_results if r['status'] in ['false', 'unverifiable'])
            overall_score = min(error_count / len(verification_results), 1.0)
        
        return overall_score, evidence
    
    def _extract_factual_claims(self, text: str) -> List[Dict[str, Any]]:
        """Extract factual claims from text"""
        claims = []
        
        # Extract sentences that contain factual patterns
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if sentence contains factual information
            claim_types = []
            for pattern_name, pattern in self.factual_patterns.items():
                if re.search(pattern, sentence, re.IGNORECASE):
                    claim_types.append(pattern_name)
            
            if claim_types:
                claims.append({
                    'text': sentence,
                    'types': claim_types,
                    'confidence': self._estimate_claim_confidence(sentence)
                })
        
        return claims
    
    def _estimate_claim_confidence(self, claim: str) -> float:
        """Estimate how confident the claim appears to be"""
        # Look for uncertainty markers
        uncertainty_markers = [
            'might', 'maybe', 'perhaps', 'possibly', 'likely', 'probably',
            'i think', 'i believe', 'it seems', 'appears to be', 'could be'
        ]
        
        confidence = 1.0
        claim_lower = claim.lower()
        
        for marker in uncertainty_markers:
            if marker in claim_lower:
                confidence -= 0.2
        
        return max(0.1, confidence)
    
    def _verify_claim(self, claim: Dict[str, Any]) -> Dict[str, Any]:
        """Verify a factual claim"""
        # This is a simplified implementation
        # In production, you would integrate with proper fact-checking APIs
        
        try:
            # Simple Wikipedia verification for demonstration
            if 'people' in claim['types']:
                return self._verify_person_claim(claim)
            elif 'dates' in claim['types'] or 'years' in claim['types']:
                return self._verify_date_claim(claim)
            else:
                return self._verify_general_claim(claim)
        
        except Exception as e:
            self.logger.error(f"Error verifying claim: {e}")
            return {
                'status': 'unverifiable',
                'confidence': 0.5,
                'explanation': 'Unable to verify due to technical error',
                'sources': []
            }
    
    def _verify_person_claim(self, claim: Dict[str, Any]) -> Dict[str, Any]:
        """Verify claims about people"""
        # Extract person names
        names = re.findall(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', claim['text'])
        
        if not names:
            return {'status': 'unverifiable', 'confidence': 0.3, 'explanation': 'No clear person name found'}
        
        # Try to verify the first name found
        name = names[0]
        try:
            # Simple Wikipedia check
            wiki_url = self.wikipedia_api_url + name.replace(' ', '_')
            response = requests.get(wiki_url, timeout=5)
            
            if response.status_code == 200:
                wiki_data = response.json()
                return {
                    'status': 'verified',
                    'confidence': 0.8,
                    'explanation': f'Person found in Wikipedia: {wiki_data.get("title", name)}',
                    'sources': [f'Wikipedia: {wiki_data.get("title", name)}']
                }
            else:
                return {
                    'status': 'unverifiable',
                    'confidence': 0.6,
                    'explanation': f'Person "{name}" not found in Wikipedia',
                    'sources': []
                }
        
        except Exception:
            return {
                'status': 'unverifiable',
                'confidence': 0.4,
                'explanation': 'Unable to verify person information',
                'sources': []
            }
    
    def _verify_date_claim(self, claim: Dict[str, Any]) -> Dict[str, Any]:
        """Verify date-related claims"""
        # Simple date validation
        text = claim['text']
        
        # Check for impossible dates
        if re.search(r'february\s+3[01]', text, re.IGNORECASE):
            return {
                'status': 'false',
                'confidence': 0.95,
                'explanation': 'February cannot have 30 or 31 days',
                'sources': ['Calendar facts']
            }
        
        # Check for future dates presented as historical facts
        current_year = datetime.now().year
        future_years = re.findall(r'\b(20[3-9]\d|2[1-9]\d\d)\b', text)
        
        if future_years and any('happened' in text.lower() or 'occurred' in text.lower() for _ in [1]):
            return {
                'status': 'false',
                'confidence': 0.9,
                'explanation': f'Future year {future_years[0]} presented as historical fact',
                'sources': ['Temporal logic']
            }
        
        return {
            'status': 'plausible',
            'confidence': 0.7,
            'explanation': 'Date appears plausible',
            'sources': []
        }
    
    def _verify_general_claim(self, claim: Dict[str, Any]) -> Dict[str, Any]:
        """Verify general factual claims"""
        # This would integrate with fact-checking APIs in production
        return {
            'status': 'unverifiable',
            'confidence': 0.5,
            'explanation': 'General fact checking not implemented in demo',
            'sources': []
        }
    
    def get_detector_name(self) -> str:
        return "factual_verification"

# ========================================
# UNCERTAINTY EXPRESSION DETECTOR
# ========================================

class UncertaintyExpressionDetector(BaseHallucinationDetector):
    """Detects uncertainty expressions that might indicate hallucination"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        
        # Uncertainty indicators with confidence scores
        self.uncertainty_patterns = {
            'hedging': {
                'patterns': [
                    r'\bmight\b', r'\bmay\b', r'\bcould\b', r'\bwould\b',
                    r'\bperhaps\b', r'\bmaybe\b', r'\bpossibly\b', r'\blikely\b',
                    r'\bprobably\b', r'\bapparently\b', r'\bseemingly\b'
                ],
                'weight': 0.3
            },
            'epistemic_uncertainty': {
                'patterns': [
                    r'\bi think\b', r'\bi believe\b', r'\bi assume\b', r'\bi guess\b',
                    r'\bin my opinion\b', r'\bit seems\b', r'\bit appears\b',
                    r'\bto my knowledge\b', r'\bas far as i know\b'
                ],
                'weight': 0.5
            },
            'contradictory_signals': {
                'patterns': [
                    r'\bbut\b', r'\bhowever\b', r'\balthough\b', r'\bthough\b',
                    r'\bon the other hand\b', r'\bnevertheless\b', r'\bnonetheless\b'
                ],
                'weight': 0.2
            },
            'vague_quantifiers': {
                'patterns': [
                    r'\bsome\b', r'\bmany\b', r'\bfew\b', r'\bseveral\b',
                    r'\ba lot of\b', r'\bplenty of\b', r'\bnumerous\b'
                ],
                'weight': 0.1
            }
        }
    
    def detect(self, prompt: str, response: str, context: Dict[str, Any] = None) -> Tuple[float, List[HallucinationEvidence]]:
        """Detect uncertainty expressions"""
        evidence = []
        uncertainty_scores = {}
        
        # Check each category of uncertainty
        for category, config in self.uncertainty_patterns.items():
            matches = []
            for pattern in config['patterns']:
                found_matches = list(re.finditer(pattern, response, re.IGNORECASE))
                matches.extend(found_matches)
            
            if matches:
                # Calculate density of uncertainty markers
                density = len(matches) / max(len(response.split()), 1)
                category_score = min(density * config['weight'] * 10, 1.0)
                uncertainty_scores[category] = category_score
                
                if category_score > 0.3:
                    # Extract text segments with uncertainty
                    segments = []
                    for match in matches[:3]:  # Limit to first 3 matches
                        start = max(0, match.start() - 20)
                        end = min(len(response), match.end() + 20)
                        segments.append(response[start:end])
                    
                    evidence.append(HallucinationEvidence(
                        type=HallucinationType.UNCERTAINTY_EXPRESSION,
                        confidence=category_score,
                        text_segment="; ".join(segments),
                        explanation=f"High density of {category.replace('_', ' ')} expressions",
                        supporting_facts=[f"Found {len(matches)} instances"],
                        severity="low" if category_score < 0.5 else "medium"
                    ))
        
        # Calculate overall uncertainty score
        overall_score = min(sum(uncertainty_scores.values()), 1.0)
        
        return overall_score, evidence
    
    def get_detector_name(self) -> str:
        return "uncertainty_expression"

# ========================================
# TEMPORAL CONSISTENCY DETECTOR
# ========================================

class TemporalConsistencyDetector(BaseHallucinationDetector):
    """Detects temporal inconsistencies and anachronisms"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.current_year = datetime.now().year
        
        # Historical periods and their year ranges
        self.historical_periods = {
            'ancient': (0, 500),
            'medieval': (500, 1500),
            'renaissance': (1400, 1700),
            'industrial revolution': (1760, 1840),
            'world war i': (1914, 1918),
            'world war ii': (1939, 1945),
            'cold war': (1947, 1991),
            'modern era': (1900, 2000),
            'contemporary': (2000, self.current_year)
        }
    
    def detect(self, prompt: str, response: str, context: Dict[str, Any] = None) -> Tuple[float, List[HallucinationEvidence]]:
        """Detect temporal inconsistencies"""
        evidence = []
        
        # Extract dates and temporal references
        temporal_refs = self._extract_temporal_references(response)
        
        # Check for anachronisms
        anachronisms = self._detect_anachronisms(temporal_refs, response)
        
        # Check for temporal impossibilities
        impossibilities = self._detect_temporal_impossibilities(temporal_refs)
        
        # Calculate score
        error_count = len(anachronisms) + len(impossibilities)
        overall_score = min(error_count * 0.3, 1.0)
        
        # Create evidence for anachronisms
        for anachronism in anachronisms:
            evidence.append(HallucinationEvidence(
                type=HallucinationType.TEMPORAL_INCONSISTENCY,
                confidence=anachronism['confidence'],
                text_segment=anachronism['text'],
                explanation=anachronism['explanation'],
                supporting_facts=anachronism['facts'],
                severity="high"
            ))
        
        # Create evidence for impossibilities
        for impossibility in impossibilities:
            evidence.append(HallucinationEvidence(
                type=HallucinationType.IMPOSSIBLE_CLAIM,
                confidence=impossibility['confidence'],
                text_segment=impossibility['text'],
                explanation=impossibility['explanation'],
                supporting_facts=impossibility['facts'],
                severity="critical"
            ))
        
        return overall_score, evidence
    
    def _extract_temporal_references(self, text: str) -> List[Dict[str, Any]]:
        """Extract temporal references from text"""
        refs = []
        
        # Extract years
        years = re.finditer(r'\b(19|20)\d{2}\b', text)
        for match in years:
            refs.append({
                'type': 'year',
                'value': int(match.group()),
                'text': match.group(),
                'position': match.span()
            })
        
        # Extract dates
        dates = re.finditer(r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+(19|20)\d{2}\b', text, re.IGNORECASE)
        for match in dates:
            year_match = re.search(r'(19|20)\d{2}', match.group())
            refs.append({
                'type': 'date',
                'value': int(year_match.group()) if year_match else None,
                'text': match.group(),
                'position': match.span()
            })
        
        # Extract historical periods
        for period, _ in self.historical_periods.items():
            pattern = r'\b' + re.escape(period) + r'\b'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                refs.append({
                    'type': 'period',
                    'value': period,
                    'text': match.group(),
                    'position': match.span()
                })
        
        return refs
    
    def _detect_anachronisms(self, temporal_refs: List[Dict[str, Any]], full_text: str) -> List[Dict[str, Any]]:
        """Detect anachronistic statements"""
        anachronisms = []
        
        # Technologies and their invention years
        technology_timeline = {
            'internet': 1969,
            'world wide web': 1989,
            'smartphone': 2007,
            'iphone': 2007,
            'facebook': 2004,
            'twitter': 2006,
            'youtube': 2005,
            'google': 1998,
            'email': 1971,
            'television': 1927,
            'radio': 1895,
            'telephone': 1876,
            'computer': 1940,
            'automobile': 1885,
            'airplane': 1903
        }
        
        # Check for technologies mentioned in wrong time periods
        for tech, invention_year in technology_timeline.items():
            tech_pattern = r'\b' + re.escape(tech) + r'\b'
            tech_matches = list(re.finditer(tech_pattern, full_text, re.IGNORECASE))
            
            for tech_match in tech_matches:
                # Look for nearby year references
                for temp_ref in temporal_refs:
                    if temp_ref['type'] in ['year', 'date'] and abs(tech_match.start() - temp_ref['position'][0]) < 100:
                        mentioned_year = temp_ref['value']
                        if mentioned_year < invention_year:
                            # Get context around the anachronism
                            start = max(0, tech_match.start() - 50)
                            end = min(len(full_text), tech_match.end() + 50)
                            context = full_text[start:end]
                            
                            anachronisms.append({
                                'text': context,
                                'explanation': f"{tech.title()} was not invented until {invention_year}, but mentioned in context of {mentioned_year}",
                                'confidence': 0.9,
                                'facts': [f"{tech.title()} invented in {invention_year}"]
                            })
        
        return anachronisms
    
    def _detect_temporal_impossibilities(self, temporal_refs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect temporal impossibilities"""
        impossibilities = []
        
        # Check for future dates presented as past events
        for ref in temporal_refs:
            if ref['type'] in ['year', 'date'] and ref['value']:
                if ref['value'] > self.current_year:
                    # Look for past tense indicators nearby
                    # This is a simplified check
                    impossibilities.append({
                        'text': ref['text'],
                        'explanation': f"Future year {ref['value']} cannot be referenced as a past event",
                        'confidence': 0.95,
                        'facts': [f"Current year is {self.current_year}"]
                    })
        
        return impossibilities
    
    def get_detector_name(self) -> str:
        return "temporal_consistency"



# ========================================
# MAIN HALLUCINATION DETECTION ORCHESTRATOR
# ========================================

class AdvancedHallucinationDetector:
    """Main orchestrator for all hallucination detection methods"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger("HallucinationDetector")
        
        # Initialize detectors
        self.detectors = {}
        self._initialize_detectors()
        
        # Weights for combining detector scores
        self.detector_weights = {
            'semantic_consistency': 0.25,
            'factual_verification': 0.35,
            'uncertainty_expression': 0.15,
            'temporal_consistency': 0.25
        }
        
        # Threading for parallel detection
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
    
    def _initialize_detectors(self):
        """Initialize all detector instances"""
        try:
            self.detectors['semantic_consistency'] = SemanticConsistencyDetector(
                self.config.get('semantic_consistency', {})
            )
            self.detectors['factual_verification'] = FactualVerificationDetector(
                self.config.get('factual_verification', {})
            )
            self.detectors['uncertainty_expression'] = UncertaintyExpressionDetector(
                self.config.get('uncertainty_expression', {})
            )
            self.detectors['temporal_consistency'] = TemporalConsistencyDetector(
                self.config.get('temporal_consistency', {})
            )
            
            self.logger.info(f"Initialized {len(self.detectors)} hallucination detectors")
            
        except Exception as e:
            self.logger.error(f"Error initializing detectors: {e}")
            raise
    
    def detect_hallucinations(
        self,
        request_id: str,
        prompt: str,
        response: str,
        context: Dict[str, Any] = None
    ) -> HallucinationResult:
        """
        Perform comprehensive hallucination detection
        
        Args:
            request_id: Unique identifier for this request
            prompt: Original prompt/input
            response: LLM response to analyze
            context: Additional context (model info, etc.)
            
        Returns:
            HallucinationResult with comprehensive analysis
        """
        start_time = time.time()
        
        try:
            # Run all detectors in parallel
            futures = {}
            for detector_name, detector in self.detectors.items():
                future = self.thread_pool.submit(
                    self._run_detector_safely,
                    detector,
                    prompt,
                    response,
                    context
                )
                futures[detector_name] = future
            
            # Collect results
            detector_results = {}
            all_evidence = []
            
            for detector_name, future in futures.items():
                try:
                    score, evidence = future.result(timeout=30)  # 30 second timeout
                    detector_results[detector_name] = score
                    all_evidence.extend(evidence)
                    
                except Exception as e:
                    self.logger.error(f"Error in {detector_name}: {e}")
                    detector_results[detector_name] = 0.0
            
            # Calculate weighted overall score
            overall_score = self._calculate_overall_score(detector_results)
            
            # Determine confidence level
            confidence_level = self._determine_confidence_level(overall_score, all_evidence)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(detector_results, all_evidence)
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            result = HallucinationResult(
                request_id=request_id,
                overall_score=overall_score,
                confidence_level=confidence_level,
                detected_hallucinations=all_evidence,
                analysis_breakdown=detector_results,
                recommendations=recommendations,
                processing_time_ms=processing_time_ms,
                timestamp=datetime.now(timezone.utc)
            )
            
            self.logger.info(
                f"Hallucination detection completed for {request_id}: "
                f"score={overall_score:.3f}, evidence_count={len(all_evidence)}, "
                f"time={processing_time_ms}ms"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in hallucination detection: {e}")
            # Return default result in case of error
            return HallucinationResult(
                request_id=request_id,
                overall_score=0.0,
                confidence_level=ConfidenceLevel.VERY_LOW,
                detected_hallucinations=[],
                analysis_breakdown={},
                recommendations=["Unable to complete hallucination analysis due to technical error"],
                processing_time_ms=int((time.time() - start_time) * 1000),
                timestamp=datetime.now(timezone.utc)
            )
    
    def _run_detector_safely(
        self,
        detector: BaseHallucinationDetector,
        prompt: str,
        response: str,
        context: Dict[str, Any]
    ) -> Tuple[float, List[HallucinationEvidence]]:
        """Safely run a detector with error handling"""
        try:
            return detector.detect(prompt, response, context)
        except Exception as e:
            self.logger.error(f"Error in {detector.get_detector_name()}: {e}")
            return 0.0, []
    
    def _calculate_overall_score(self, detector_results: Dict[str, float]) -> float:
        """Calculate weighted overall hallucination score"""
        total_score = 0.0
        total_weight = 0.0
        
        for detector_name, score in detector_results.items():
            weight = self.detector_weights.get(detector_name, 0.0)
            total_score += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return min(total_score / total_weight, 1.0)
    
    def _determine_confidence_level(
        self,
        overall_score: float,
        evidence: List[HallucinationEvidence]
    ) -> ConfidenceLevel:
        """Determine confidence level based on score and evidence"""
        
        # Count high-confidence evidence
        high_confidence_count = sum(1 for e in evidence if e.confidence > 0.8)
        critical_severity_count = sum(1 for e in evidence if e.severity == "critical")
        
        # Determine confidence level
        if overall_score >= 0.8 and high_confidence_count >= 2:
            return ConfidenceLevel.VERY_HIGH
        elif overall_score >= 0.6 and (high_confidence_count >= 1 or critical_severity_count >= 1):
            return ConfidenceLevel.HIGH
        elif overall_score >= 0.4:
            return ConfidenceLevel.MEDIUM
        elif overall_score >= 0.2:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    def _generate_recommendations(
        self,
        detector_results: Dict[str, float],
        evidence: List[HallucinationEvidence]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Overall recommendations based on score
        max_score = max(detector_results.values()) if detector_results else 0.0
        
        if max_score > 0.7:
            recommendations.append("⚠️ High hallucination risk detected. Consider regenerating the response.")
        elif max_score > 0.4:
            recommendations.append("⚡ Moderate hallucination risk. Review response carefully before use.")
        
        # Specific recommendations based on detector results
        if detector_results.get('factual_verification', 0) > 0.5:
            recommendations.append("🔍 Verify factual claims independently before trusting this response.")
        
        if detector_results.get('semantic_consistency', 0) > 0.5:
            recommendations.append("📝 Response contains contradictions. Check for logical consistency.")
        
        if detector_results.get('temporal_consistency', 0) > 0.5:
            recommendations.append("📅 Temporal inconsistencies detected. Verify dates and historical claims.")
        
        if detector_results.get('uncertainty_expression', 0) > 0.6:
            recommendations.append("❓ High uncertainty in response. Model may be unsure about the answer.")
        
        # Evidence-specific recommendations
        critical_evidence = [e for e in evidence if e.severity == "critical"]
        if critical_evidence:
            recommendations.append("🚨 Critical issues found. Do not use this response without significant verification.")
        
        # If no specific issues found
        if not recommendations and max_score < 0.2:
            recommendations.append("✅ Response appears to have low hallucination risk.")
        
        return recommendations
