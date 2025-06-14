# meerkatics/sdk/meerkatics/caching.py

import time
import hashlib
import json
import os
import logging
from typing import Dict, Any, Optional, Union, Tuple
from threading import Lock

logger = logging.getLogger(__name__)

class ResponseCache:
    """
    Simple cache for LLM responses to avoid duplicate API calls.
    """
    
    def __init__(
        self, 
        max_size: int = 1000,
        ttl: int = 3600,  # 1 hour default TTL
        disk_cache: bool = False,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize the response cache.
        
        Args:
            max_size: Maximum number of items in the cache
            ttl: Time-to-live in seconds
            disk_cache: Whether to persist cache to disk
            cache_dir: Directory for disk cache
        """
        self.max_size = max_size
        self.ttl = ttl
        self.disk_cache = disk_cache
        self.cache_dir = cache_dir
        
        if disk_cache and not cache_dir:
            self.cache_dir = os.path.join(os.path.expanduser("~"), ".meerkatics", "cache")
            os.makedirs(self.cache_dir, exist_ok=True)
        
        self.cache = {}  # In-memory cache
        self.access_times = {}  # Last access time for each key
        self.lock = Lock()  # Thread safety
        
        # Load cache from disk if enabled
        if self.disk_cache:
            self._load_cache()
    
    def _generate_key(self, provider: str, model: str, prompt: str, params: Dict[str, Any]) -> str:
        """Generate a unique cache key based on request parameters."""
        # Sort params for consistent key generation
        sorted_params = {k: params[k] for k in sorted(params.keys())}
        
        # Create string representation and hash it
        key_data = f"{provider}:{model}:{prompt}:{json.dumps(sorted_params)}"
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()
    
    def get(
        self, 
        provider: str, 
        model: str, 
        prompt: str, 
        params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Get a cached response if available and valid.
        
        Args:
            provider: LLM provider
            model: Model name
            prompt: Input prompt
            params: Additional parameters
            
        Returns:
            Cached response or None if not found/expired
        """
        key = self._generate_key(provider, model, prompt, params)
        
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                timestamp = entry.get("timestamp", 0)
                
                # Check if entry is still valid
                if time.time() - timestamp <= self.ttl:
                    # Update access time
                    self.access_times[key] = time.time()
                    return entry.get("response")
                else:
                    # Remove expired entry
                    del self.cache[key]
                    if key in self.access_times:
                        del self.access_times[key]
        
        return None
    
    def put(
        self, 
        provider: str, 
        model: str, 
        prompt: str, 
        params: Dict[str, Any],
        response: Dict[str, Any]
    ) -> None:
        """
        Store a response in the cache.
        
        Args:
            provider: LLM provider
            model: Model name
            prompt: Input prompt
            params: Additional parameters
            response: Response to cache
        """
        key = self._generate_key(provider, model, prompt, params)
        
        with self.lock:
            # Check if we need to evict entries
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_entry()
            
            # Store the entry
            self.cache[key] = {
                "timestamp": time.time(),
                "response": response,
                "provider": provider,
                "model": model
            }
            
            self.access_times[key] = time.time()
            
            # Persist to disk if enabled
            if self.disk_cache:
                self._save_cache()
    
    def clear(self) -> None:
        """Clear the entire cache."""
        with self.lock:
            self.cache = {}
            self.access_times = {}
            
            if self.disk_cache:
                self._save_cache()
    
    def _evict_entry(self) -> None:
        """Evict the least recently used entry."""
        if not self.access_times:
            return
            
        # Find least recently used key
        lru_key = min(self.access_times.items(), key=lambda x: x[1])[0]
        
        # Remove it
        if lru_key in self.cache:
            del self.cache[lru_key]
        if lru_key in self.access_times:
            del self.access_times[lru_key]
    
    def _save_cache(self) -> None:
        """Save cache to disk if disk caching is enabled."""
        if not self.disk_cache or not self.cache_dir:
            return
            
        try:
            cache_file = os.path.join(self.cache_dir, "response_cache.json")
            
            with open(cache_file, 'w') as f:
                json.dump({
                    "cache": self.cache,
                    "access_times": self.access_times
                }, f)
        except Exception as e:
            logger.error(f"Failed to save cache to disk: {str(e)}")
    
    def _load_cache(self) -> None:
        """Load cache from disk if available."""
        if not self.disk_cache or not self.cache_dir:
            return
            
        try:
            cache_file = os.path.join(self.cache_dir, "response_cache.json")
            
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    
                    # Load and validate entries
                    valid_entries = {}
                    valid_access_times = {}
                    
                    for key, entry in data.get("cache", {}).items():
                        timestamp = entry.get("timestamp", 0)
                        
                        # Skip expired entries
                        if time.time() - timestamp <= self.ttl:
                            valid_entries[key] = entry
                            valid_access_times[key] = data.get("access_times", {}).get(key, timestamp)
                    
                    # Update cache with valid entries
                    self.cache = valid_entries
                    self.access_times = valid_access_times
        except Exception as e:
            logger.error(f"Failed to load cache from disk: {str(e)}")