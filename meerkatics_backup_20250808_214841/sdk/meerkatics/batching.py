# meerkatics/sdk/meerkatics/batching.py

import time
import threading
import queue
import logging
from typing import Dict, Any, List, Callable, Optional

logger = logging.getLogger(__name__)

class BatchProcessor:
    """
    Provides batching capabilities for high-volume applications.
    Collects metrics and sends them in batches to reduce overhead.
    """
    
    def __init__(
        self,
        process_func: Callable,
        batch_size: int = 10,
        flush_interval: float = 5.0,
        max_queue_size: int = 1000,
        auto_flush: bool = True
    ):
        """
        Initialize a batch processor.
        
        Args:
            process_func: Function to process a batch of items
            batch_size: Number of items to collect before processing
            flush_interval: Maximum time (seconds) between flushes
            max_queue_size: Maximum size of the queue
            auto_flush: Whether to automatically flush in background
        """
        self.process_func = process_func
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.max_queue_size = max_queue_size
        
        self.queue = queue.Queue(maxsize=max_queue_size)
        self.last_flush = time.time()
        self.flush_lock = threading.Lock()
        self.stopping = threading.Event()
        
        # Start auto-flush thread if enabled
        if auto_flush:
            self.flush_thread = threading.Thread(target=self._auto_flush_loop, daemon=True)
            self.flush_thread.start()
        else:
            self.flush_thread = None
    
    def add(self, item: Any) -> bool:
        """
        Add an item to the batch.
        Returns True if successful, False if queue is full.
        """
        try:
            self.queue.put_nowait(item)
            
            # Flush if batch size reached
            if self.queue.qsize() >= self.batch_size:
                self.flush()
                
            return True
        except queue.Full:
            logger.warning("BatchProcessor queue is full, item dropped")
            return False
    
    def flush(self) -> int:
        """
        Process all items currently in the queue.
        Returns the number of items processed.
        """
        # Use lock to prevent multiple simultaneous flushes
        if not self.flush_lock.acquire(blocking=False):
            return 0
        
        try:
            items = []
            while not self.queue.empty() and len(items) < self.max_queue_size:
                try:
                    items.append(self.queue.get_nowait())
                    self.queue.task_done()
                except queue.Empty:
                    break
            
            if items:
                try:
                    self.process_func(items)
                except Exception as e:
                    logger.error(f"Error processing batch: {str(e)}")
            
            self.last_flush = time.time()
            return len(items)
        finally:
            self.flush_lock.release()
    
    def _auto_flush_loop(self):
        """Background thread that periodically flushes the queue."""
        while not self.stopping.is_set():
            time_since_flush = time.time() - self.last_flush
            
            if time_since_flush >= self.flush_interval:
                self.flush()
            
            # Sleep for a short time to avoid CPU spinning
            time.sleep(min(1.0, self.flush_interval / 5))
    
    def stop(self):
        """Stop the batch processor and flush remaining items."""
        if self.flush_thread and self.flush_thread.is_alive():
            self.stopping.set()
            self.flush_thread.join(timeout=self.flush_interval)
        
        # Final flush
        self.flush()