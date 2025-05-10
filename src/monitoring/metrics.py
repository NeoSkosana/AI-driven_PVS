"""Metrics service for application monitoring."""
from prometheus_client import Counter, Histogram, Gauge, Info
from typing import Dict, Any
import time

# API Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

# Business Logic Metrics
validation_requests_total = Counter(
    'validation_requests_total',
    'Total number of problem validation requests',
    ['status']  # pending, completed, failed
)

validation_processing_time = Histogram(
    'validation_processing_time_seconds',
    'Time taken to process a validation request',
    ['status'],
    buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0)
)

# System Metrics
active_users_gauge = Gauge(
    'active_users',
    'Number of currently active users'
)

system_memory_usage = Gauge(
    'system_memory_usage_bytes',
    'Current system memory usage in bytes'
)

# Cache Metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total number of cache hits',
    ['cache_type']  # redis, local, etc.
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total number of cache misses',
    ['cache_type']
)

# External Service Metrics
external_service_requests = Counter(
    'external_service_requests_total',
    'Total number of requests to external services',
    ['service', 'endpoint', 'status']
)

external_service_latency = Histogram(
    'external_service_latency_seconds',
    'External service request latency in seconds',
    ['service', 'endpoint'],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0)
)

# Error Metrics
error_counts = Counter(
    'error_total',
    'Total number of errors',
    ['type', 'location']
)

class MetricsManager:
    """Manager class for handling metrics collection and updates."""
    
    @staticmethod
    def record_request_duration(method: str, endpoint: str, start_time: float):
        """Record the duration of an HTTP request."""
        duration = time.time() - start_time
        http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
    
    @staticmethod
    def record_validation_request(status: str):
        """Record a validation request."""
        validation_requests_total.labels(status=status).inc()
    
    @staticmethod
    def record_validation_time(duration: float, status: str):
        """Record the time taken to process a validation request."""
        validation_processing_time.labels(status=status).observe(duration)
    
    @staticmethod
    def record_error(error_type: str, location: str):
        """Record an error occurrence."""
        error_counts.labels(type=error_type, location=location).inc()
    
    @staticmethod
    def record_cache_operation(operation_type: str, cache_type: str):
        """Record cache hits and misses."""
        if operation_type == 'hit':
            cache_hits_total.labels(cache_type=cache_type).inc()
        elif operation_type == 'miss':
            cache_misses_total.labels(cache_type=cache_type).inc()
    
    @staticmethod
    def record_external_request(service: str, endpoint: str, status: str, duration: float):
        """Record external service request metrics."""
        external_service_requests.labels(
            service=service,
            endpoint=endpoint,
            status=status
        ).inc()
        external_service_latency.labels(
            service=service,
            endpoint=endpoint
        ).observe(duration)
