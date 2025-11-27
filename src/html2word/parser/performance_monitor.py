"""
Performance monitoring utilities for CSS optimization.

Provides timing decorators and performance metrics collection.
"""

import time
import logging
import functools
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from contextlib import contextmanager
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""

    total_time: float = 0.0
    node_count: int = 0
    rule_count: int = 0
    match_count: int = 0
    avg_time_per_node: float = 0.0
    avg_rules_per_node: float = 0.0

    # Detailed timing breakdowns
    css_apply_time: float = 0.0
    selector_match_time: float = 0.0
    style_merge_time: float = 0.0
    tree_traversal_time: float = 0.0

    # Additional stats
    max_node_time: float = 0.0
    min_node_time: float = float('inf')
    node_timings: List[float] = field(default_factory=list)

    def calculate_averages(self):
        """Calculate average metrics."""
        if self.node_count > 0:
            self.avg_time_per_node = self.total_time / self.node_count
            self.avg_rules_per_node = self.match_count / self.node_count

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'total_time': self.total_time,
            'node_count': self.node_count,
            'rule_count': self.rule_count,
            'match_count': self.match_count,
            'avg_time_per_node': self.avg_time_per_node,
            'avg_rules_per_node': self.avg_rules_per_node,
            'css_apply_time': self.css_apply_time,
            'selector_match_time': self.selector_match_time,
            'style_merge_time': self.style_merge_time,
            'tree_traversal_time': self.tree_traversal_time,
            'max_node_time': self.max_node_time,
            'min_node_time': self.min_node_time if self.min_node_time != float('inf') else 0.0
        }

    def save_to_file(self, filepath: str):
        """Save metrics to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info(f"Performance metrics saved to {filepath}")

    def print_summary(self):
        """Print a formatted summary of metrics."""
        print("\n" + "="*60)
        print("PERFORMANCE METRICS SUMMARY")
        print("="*60)
        print(f"Total Time: {self.total_time:.2f}s")
        print(f"Node Count: {self.node_count:,}")
        print(f"Rule Count: {self.rule_count:,}")
        print(f"Match Count: {self.match_count:,}")
        print(f"Avg Time per Node: {self.avg_time_per_node*1000:.2f}ms")
        print(f"Avg Rules per Node: {self.avg_rules_per_node:.1f}")
        print("-"*60)
        print("Timing Breakdown:")
        print(f"  CSS Apply: {self.css_apply_time:.2f}s ({self.css_apply_time/self.total_time*100:.1f}%)")
        print(f"  Selector Match: {self.selector_match_time:.2f}s ({self.selector_match_time/self.total_time*100:.1f}%)")
        print(f"  Style Merge: {self.style_merge_time:.2f}s ({self.style_merge_time/self.total_time*100:.1f}%)")
        print(f"  Tree Traversal: {self.tree_traversal_time:.2f}s ({self.tree_traversal_time/self.total_time*100:.1f}%)")
        print("="*60 + "\n")


class PerformanceMonitor:
    """Global performance monitor instance."""

    def __init__(self):
        self.metrics = PerformanceMetrics()
        self.enabled = True
        self.timers = {}

    def reset(self):
        """Reset all metrics."""
        self.metrics = PerformanceMetrics()
        self.timers = {}

    @contextmanager
    def timer(self, name: str):
        """Context manager for timing code blocks."""
        if not self.enabled:
            yield
            return

        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            if name not in self.timers:
                self.timers[name] = []
            self.timers[name].append(elapsed)

            # Update specific metrics
            if name == 'apply_styles_to_tree':
                self.metrics.css_apply_time += elapsed
            elif name == 'selector_match':
                self.metrics.selector_match_time += elapsed
            elif name == 'style_merge':
                self.metrics.style_merge_time += elapsed
            elif name == 'tree_traversal':
                self.metrics.tree_traversal_time += elapsed

    def record_node_time(self, elapsed: float):
        """Record time for processing a single node."""
        self.metrics.node_timings.append(elapsed)
        self.metrics.max_node_time = max(self.metrics.max_node_time, elapsed)
        self.metrics.min_node_time = min(self.metrics.min_node_time, elapsed)

    def finalize(self):
        """Finalize metrics calculation."""
        self.metrics.calculate_averages()
        self.metrics.total_time = sum(self.metrics.node_timings) if self.metrics.node_timings else 0.0

    def get_metrics(self) -> PerformanceMetrics:
        """Get current metrics."""
        return self.metrics


# Global monitor instance
_monitor = PerformanceMonitor()


def get_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance."""
    return _monitor


def performance_monitor(func: Callable) -> Callable:
    """Decorator to monitor function performance."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        monitor = get_monitor()
        if not monitor.enabled:
            return func(*args, **kwargs)

        with monitor.timer(func.__name__):
            result = func(*args, **kwargs)

        return result

    return wrapper


def timed_operation(name: str) -> Callable:
    """Decorator factory for timing specific operations."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            monitor = get_monitor()
            if not monitor.enabled:
                return func(*args, **kwargs)

            with monitor.timer(name):
                result = func(*args, **kwargs)

            return result

        return wrapper
    return decorator


class Timer:
    """Simple timer class for manual timing."""

    def __init__(self, name: Optional[str] = None):
        self.name = name
        self.start_time = None
        self.elapsed = 0.0

    def start(self):
        """Start the timer."""
        self.start_time = time.perf_counter()

    def stop(self) -> float:
        """Stop the timer and return elapsed time."""
        if self.start_time is None:
            return 0.0
        self.elapsed = time.perf_counter() - self.start_time
        self.start_time = None
        return self.elapsed

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
        if self.name:
            logger.debug(f"{self.name} took {self.elapsed:.4f}s")