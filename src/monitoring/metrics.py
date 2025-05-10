"""Metrics service for application monitoring."""
from prometheus_client import Counter, Histogram, Gauge, Info
from typing import Dict, Any

# Define metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

active_users_gauge = Gauge(
    'active_users',
    'Number of currently active users'
)

validation_requests_total = Counter(
    'validation_requests_total',
    'Total number of problem validation requests'
)

validation_score_histogram = Histogram(
    'validation_score',
    'Distribution of validation scores',
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

system_info = Info('system', 'System information')

class MetricsService:
    """Service for collecting and exposing application metrics."""
    
    @staticmethod
    def record_request(method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request metrics."""
        http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
        http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
    
    @staticmethod
    def set_active_users(count: int):
        """Set the number of active users."""
        active_users_gauge.set(count)
    
    @staticmethod
    def record_validation_request():
        """Record a problem validation request."""
        validation_requests_total.inc()
    
    @staticmethod
    def record_validation_score(score: float):
        """Record a validation score."""
        validation_score_histogram.observe(score)
    
    @staticmethod
    def set_system_info(info: Dict[str, Any]):
        """Set system information metrics."""
        system_info.info(info)
