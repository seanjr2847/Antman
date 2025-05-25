"""
Tests for middleware components.
"""
import time
import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory, override_settings
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User, AnonymousUser
from django.core.cache import cache
import pytest

from core.middleware.logging import RequestLoggingMiddleware
from core.middleware.performance import PerformanceMonitoringMiddleware
from core.middleware.security import SecurityHeadersMiddleware
from core.middleware.rate_limiting import RateLimitingMiddleware
from core.middleware.cors import CORSMiddleware


class TestRequestLoggingMiddleware(TestCase):
    """Test cases for request logging middleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.get_response = MagicMock(return_value=HttpResponse())
        self.middleware = RequestLoggingMiddleware(self.get_response)
    
    @patch('core.middleware.logging.logger')
    def test_logs_basic_request_info(self, mock_logger):
        """Test logging basic request information."""
        request = self.factory.get('/api/test/')
        request.user = AnonymousUser()
        
        response = self.middleware(request)
        
        mock_logger.info.assert_called()
        log_message = mock_logger.info.call_args[0][0]
        self.assertIn('GET', log_message)
        self.assertIn('/api/test/', log_message)
    
    @patch('core.middleware.logging.logger')
    def test_logs_authenticated_user(self, mock_logger):
        """Test logging authenticated user information."""
        user = User(id=1, username='testuser')
        request = self.factory.get('/api/test/')
        request.user = user
        
        response = self.middleware(request)
        
        mock_logger.info.assert_called()
        log_message = mock_logger.info.call_args[0][0]
        self.assertIn('testuser', log_message)
    
    @patch('core.middleware.logging.logger')
    def test_logs_request_headers(self, mock_logger):
        """Test logging request headers."""
        request = self.factory.get('/api/test/', HTTP_USER_AGENT='TestAgent/1.0')
        request.user = AnonymousUser()
        
        response = self.middleware(request)
        
        mock_logger.debug.assert_called()
        debug_message = mock_logger.debug.call_args[0][0]
        self.assertIn('User-Agent', debug_message)
        self.assertIn('TestAgent/1.0', debug_message)
    
    @override_settings(DEBUG=True)
    @patch('core.middleware.logging.logger')
    def test_logs_request_body_in_debug(self, mock_logger):
        """Test logging request body in debug mode."""
        request = self.factory.post('/api/test/', 
                                  json.dumps({'key': 'value'}),
                                  content_type='application/json')
        request.user = AnonymousUser()
        
        response = self.middleware(request)
        
        mock_logger.debug.assert_called()
    
    @patch('core.middleware.logging.logger')
    def test_logs_response_status(self, mock_logger):
        """Test logging response status."""
        self.get_response.return_value = HttpResponse(status=201)
        request = self.factory.post('/api/test/')
        request.user = AnonymousUser()
        
        response = self.middleware(request)
        
        # Should log both request and response
        self.assertEqual(mock_logger.info.call_count, 2)
        response_log = mock_logger.info.call_args_list[1][0][0]
        self.assertIn('201', response_log)
    
    @patch('core.middleware.logging.logger')
    def test_excludes_sensitive_headers(self, mock_logger):
        """Test that sensitive headers are excluded from logs."""
        request = self.factory.get('/api/test/', 
                                 HTTP_AUTHORIZATION='Bearer secret-token',
                                 HTTP_X_API_KEY='secret-key')
        request.user = AnonymousUser()
        
        response = self.middleware(request)
        
        mock_logger.debug.assert_called()
        debug_message = mock_logger.debug.call_args[0][0]
        self.assertNotIn('secret-token', debug_message)
        self.assertNotIn('secret-key', debug_message)
        self.assertIn('[REDACTED]', debug_message)


class TestPerformanceMonitoringMiddleware(TestCase):
    """Test cases for performance monitoring middleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
    
    @patch('core.middleware.performance.logger')
    def test_logs_request_duration(self, mock_logger):
        """Test logging request duration."""
        def slow_response(request):
            time.sleep(0.01)
            return HttpResponse()
        
        middleware = PerformanceMonitoringMiddleware(slow_response)
        request = self.factory.get('/api/test/')
        
        response = middleware(request)
        
        mock_logger.info.assert_called()
        log_message = mock_logger.info.call_args[0][0]
        self.assertIn('duration', log_message.lower())
    
    @patch('core.middleware.performance.logger')
    def test_warns_on_slow_requests(self, mock_logger):
        """Test warning on slow requests."""
        def very_slow_response(request):
            time.sleep(0.1)
            return HttpResponse()
        
        with override_settings(SLOW_REQUEST_THRESHOLD=0.05):
            middleware = PerformanceMonitoringMiddleware(very_slow_response)
            request = self.factory.get('/api/slow/')
            
            response = middleware(request)
            
            mock_logger.warning.assert_called()
            warning_message = mock_logger.warning.call_args[0][0]
            self.assertIn('slow request', warning_message.lower())
    
    @patch('core.middleware.performance.logger')
    def test_tracks_memory_usage(self, mock_logger):
        """Test tracking memory usage."""
        def memory_intensive_response(request):
            # Simulate memory usage
            data = [i for i in range(1000)]
            return HttpResponse()
        
        middleware = PerformanceMonitoringMiddleware(memory_intensive_response)
        request = self.factory.get('/api/test/')
        
        response = middleware(request)
        
        mock_logger.info.assert_called()
        log_message = mock_logger.info.call_args[0][0]
        self.assertIn('memory', log_message.lower())
    
    @patch('core.middleware.performance.statsd')
    def test_sends_metrics_to_statsd(self, mock_statsd):
        """Test sending performance metrics to StatsD."""
        def test_response(request):
            return HttpResponse()
        
        middleware = PerformanceMonitoringMiddleware(test_response)
        request = self.factory.get('/api/test/')
        
        response = middleware(request)
        
        mock_statsd.timing.assert_called()
        mock_statsd.increment.assert_called()


class TestSecurityHeadersMiddleware(TestCase):
    """Test cases for security headers middleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.get_response = MagicMock(return_value=HttpResponse())
        self.middleware = SecurityHeadersMiddleware(self.get_response)
    
    def test_adds_security_headers(self):
        """Test adding security headers to response."""
        request = self.factory.get('/api/test/')
        
        response = self.middleware(request)
        
        self.assertIn('X-Content-Type-Options', response)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        
        self.assertIn('X-Frame-Options', response)
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        
        self.assertIn('X-XSS-Protection', response)
        self.assertEqual(response['X-XSS-Protection'], '1; mode=block')
        
        self.assertIn('Strict-Transport-Security', response)
        self.assertIn('Referrer-Policy', response)
    
    def test_csp_header(self):
        """Test Content Security Policy header."""
        request = self.factory.get('/api/test/')
        
        response = self.middleware(request)
        
        self.assertIn('Content-Security-Policy', response)
        csp = response['Content-Security-Policy']
        self.assertIn("default-src 'self'", csp)
        self.assertIn("script-src 'self'", csp)
    
    @override_settings(DEBUG=True)
    def test_relaxed_csp_in_debug(self):
        """Test relaxed CSP in debug mode."""
        request = self.factory.get('/api/test/')
        
        response = self.middleware(request)
        
        csp = response['Content-Security-Policy']
        self.assertIn("'unsafe-eval'", csp)
    
    def test_api_endpoints_get_json_csp(self):
        """Test API endpoints get appropriate CSP for JSON responses."""
        self.get_response.return_value = JsonResponse({'data': 'test'})
        request = self.factory.get('/api/test/')
        
        response = self.middleware(request)
        
        csp = response['Content-Security-Policy']
        self.assertIn("default-src 'none'", csp)


class TestRateLimitingMiddleware(TestCase):
    """Test cases for rate limiting middleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.get_response = MagicMock(return_value=HttpResponse())
        self.middleware = RateLimitingMiddleware(self.get_response)
        cache.clear()
    
    def tearDown(self):
        cache.clear()
    
    def test_allows_requests_within_limit(self):
        """Test allowing requests within rate limit."""
        request = self.factory.get('/api/test/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        response = self.middleware(request)
        
        self.assertEqual(response.status_code, 200)
        self.get_response.assert_called_once()
    
    @override_settings(RATE_LIMIT_REQUESTS=2, RATE_LIMIT_WINDOW=60)
    def test_blocks_requests_over_limit(self):
        """Test blocking requests over rate limit."""
        request = self.factory.get('/api/test/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        # Make requests up to limit
        for i in range(2):
            response = self.middleware(request)
            self.assertEqual(response.status_code, 200)
        
        # Next request should be blocked
        response = self.middleware(request)
        self.assertEqual(response.status_code, 429)
        
        data = json.loads(response.content.decode())
        self.assertEqual(data['error_code'], 'RATE_LIMIT_EXCEEDED')
    
    def test_different_ips_have_separate_limits(self):
        """Test that different IPs have separate rate limits."""
        request1 = self.factory.get('/api/test/')
        request1.META['REMOTE_ADDR'] = '127.0.0.1'
        
        request2 = self.factory.get('/api/test/')
        request2.META['REMOTE_ADDR'] = '192.168.1.1'
        
        with override_settings(RATE_LIMIT_REQUESTS=1, RATE_LIMIT_WINDOW=60):
            # First IP makes request
            response1 = self.middleware(request1)
            self.assertEqual(response1.status_code, 200)
            
            # Second IP should still be allowed
            response2 = self.middleware(request2)
            self.assertEqual(response2.status_code, 200)
    
    def test_authenticated_users_get_higher_limits(self):
        """Test that authenticated users get higher rate limits."""
        user = User(id=1, username='testuser')
        request = self.factory.get('/api/test/')
        request.user = user
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        with override_settings(
            RATE_LIMIT_REQUESTS=1, 
            RATE_LIMIT_AUTHENTICATED_REQUESTS=5,
            RATE_LIMIT_WINDOW=60
        ):
            # Should allow more requests for authenticated users
            for i in range(3):
                response = self.middleware(request)
                self.assertEqual(response.status_code, 200)
    
    def test_rate_limit_headers(self):
        """Test rate limit headers in response."""
        request = self.factory.get('/api/test/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        response = self.middleware(request)
        
        self.assertIn('X-RateLimit-Limit', response)
        self.assertIn('X-RateLimit-Remaining', response)
        self.assertIn('X-RateLimit-Reset', response)
    
    def test_whitelist_bypasses_rate_limit(self):
        """Test that whitelisted IPs bypass rate limiting."""
        request = self.factory.get('/api/test/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        with override_settings(
            RATE_LIMIT_REQUESTS=1,
            RATE_LIMIT_WHITELIST=['127.0.0.1'],
            RATE_LIMIT_WINDOW=60
        ):
            # Should allow unlimited requests from whitelisted IP
            for i in range(5):
                response = self.middleware(request)
                self.assertEqual(response.status_code, 200)


class TestCORSMiddleware(TestCase):
    """Test cases for CORS middleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.get_response = MagicMock(return_value=HttpResponse())
        self.middleware = CORSMiddleware(self.get_response)
    
    def test_adds_cors_headers(self):
        """Test adding CORS headers to response."""
        request = self.factory.get('/api/test/')
        
        response = self.middleware(request)
        
        self.assertIn('Access-Control-Allow-Origin', response)
        self.assertIn('Access-Control-Allow-Methods', response)
        self.assertIn('Access-Control-Allow-Headers', response)
    
    def test_handles_preflight_request(self):
        """Test handling preflight OPTIONS request."""
        request = self.factory.options('/api/test/')
        request.META['HTTP_ACCESS_CONTROL_REQUEST_METHOD'] = 'POST'
        request.META['HTTP_ACCESS_CONTROL_REQUEST_HEADERS'] = 'Content-Type'
        
        response = self.middleware(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Access-Control-Allow-Methods', response)
        self.assertIn('POST', response['Access-Control-Allow-Methods'])
    
    @override_settings(CORS_ALLOWED_ORIGINS=['https://example.com'])
    def test_respects_allowed_origins(self):
        """Test respecting allowed origins setting."""
        request = self.factory.get('/api/test/')
        request.META['HTTP_ORIGIN'] = 'https://example.com'
        
        response = self.middleware(request)
        
        self.assertEqual(response['Access-Control-Allow-Origin'], 'https://example.com')
    
    @override_settings(CORS_ALLOWED_ORIGINS=['https://example.com'])
    def test_blocks_disallowed_origins(self):
        """Test blocking disallowed origins."""
        request = self.factory.get('/api/test/')
        request.META['HTTP_ORIGIN'] = 'https://malicious.com'
        
        response = self.middleware(request)
        
        self.assertNotEqual(response['Access-Control-Allow-Origin'], 'https://malicious.com')
    
    def test_credentials_support(self):
        """Test credentials support in CORS."""
        request = self.factory.get('/api/test/')
        
        with override_settings(CORS_ALLOW_CREDENTIALS=True):
            response = self.middleware(request)
            
            self.assertEqual(response['Access-Control-Allow-Credentials'], 'true')


@pytest.mark.integration
class TestMiddlewareIntegration(TestCase):
    """Integration tests for middleware stack."""
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_middleware_order_matters(self):
        """Test that middleware order affects behavior."""
        def test_view(request):
            return HttpResponse("Success")
        
        # Stack middleware in specific order
        middleware_stack = SecurityHeadersMiddleware(
            PerformanceMonitoringMiddleware(
                RequestLoggingMiddleware(test_view)
            )
        )
        
        request = self.factory.get('/api/test/')
        request.user = AnonymousUser()
        
        response = middleware_stack(request)
        
        # Should have security headers
        self.assertIn('X-Content-Type-Options', response)
        # Should have processed through all middleware
        self.assertEqual(response.status_code, 200)
    
    @patch('core.middleware.logging.logger')
    @patch('core.middleware.performance.logger')
    def test_error_handling_in_middleware_stack(self, mock_perf_logger, mock_req_logger):
        """Test error handling across middleware stack."""
        def failing_view(request):
            raise Exception("Test error")
        
        middleware_stack = RequestLoggingMiddleware(
            PerformanceMonitoringMiddleware(failing_view)
        )
        
        request = self.factory.get('/api/test/')
        request.user = AnonymousUser()
        
        with self.assertRaises(Exception):
            response = middleware_stack(request)
        
        # Should still log the request
        mock_req_logger.info.assert_called()
    
    def test_middleware_with_different_content_types(self):
        """Test middleware behavior with different content types."""
        def json_view(request):
            return JsonResponse({'status': 'success'})
        
        middleware = SecurityHeadersMiddleware(json_view)
        request = self.factory.get('/api/test/')
        
        response = middleware(request)
        
        # Should have appropriate headers for JSON response
        self.assertIn('Content-Security-Policy', response)
        self.assertEqual(response['Content-Type'], 'application/json')
    
    @override_settings(DEBUG=False)
    def test_production_middleware_behavior(self):
        """Test middleware behavior in production settings."""
        def test_view(request):
            return HttpResponse("Success")
        
        middleware = SecurityHeadersMiddleware(test_view)
        request = self.factory.get('/api/test/')
        
        response = middleware(request)
        
        # Should have strict security headers in production
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        csp = response['Content-Security-Policy']
        self.assertNotIn("'unsafe-eval'", csp)
