"""
Tests for comprehensive error handling system.
"""
import json
import logging
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory, override_settings
from django.http import Http404, HttpResponse
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.auth.models import User, AnonymousUser
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied as DRFPermissionDenied
import pytest

from core.error_handling.exceptions import (
    AntmanBaseException,
    ValidationError as AntmanValidationError,
    AuthenticationError,
    AuthorizationError,
    ResourceNotFoundError,
    ExternalServiceError,
    RateLimitExceededError
)
from core.error_handling.handlers import (
    ErrorHandler
)
from core.error_handling.middleware import (
    ErrorHandlingMiddleware,
    APIErrorHandlingMiddleware,
    RequestLoggingErrorMiddleware
)


class TestAntmanBaseException(TestCase):
    """Test cases for custom exception classes."""
    
    def test_basic_exception_creation(self):
        """Test base exception functionality."""
        error = AntmanBaseException(
            message="Test error",
            error_code="TEST_001",
            details={'field': 'value'}
        )
        
        self.assertEqual(str(error), "Test error")
        self.assertEqual(error.error_code, "TEST_001")
        self.assertEqual(error.details, {'field': 'value'})
    
    def test_validation_error(self):
        """Test validation error with field-specific errors."""
        error = AntmanValidationError(
            message="Validation failed",
            field_errors={
                'email': ['Invalid email format'],
                'password': ['Password too short', 'Password must contain numbers']
            }
        )
        
        self.assertEqual(error.error_code, "VALIDATION_ERROR")
        self.assertEqual(len(error.field_errors['password']), 2)
    
    def test_authentication_error(self):
        """Test authentication error."""
        error = AuthenticationError("Invalid credentials")
        
        self.assertEqual(error.error_code, "AUTHENTICATION_ERROR")
        self.assertEqual(error.http_status_code, 401)
    
    def test_authorization_error(self):
        """Test authorization error."""
        error = AuthorizationError("Access denied")
        
        self.assertEqual(error.error_code, "AUTHORIZATION_ERROR")
        self.assertEqual(error.http_status_code, 403)
    
    def test_resource_not_found_error(self):
        """Test resource not found error."""
        error = ResourceNotFoundError("User not found", resource_type="User", resource_id=123)
        
        self.assertEqual(error.error_code, "RESOURCE_NOT_FOUND")
        self.assertEqual(error.http_status_code, 404)
        self.assertEqual(error.resource_type, "User")
        self.assertEqual(error.resource_id, 123)
    
    def test_external_service_error(self):
        """Test external service error."""
        error = ExternalServiceError(
            "Payment service unavailable",
            service_name="stripe",
            service_response={'error': 'timeout'}
        )
        
        self.assertEqual(error.error_code, "EXTERNAL_SERVICE_ERROR")
        self.assertEqual(error.service_name, "stripe")
        self.assertEqual(error.service_response, {'error': 'timeout'})
    
    def test_rate_limit_exceeded_error(self):
        """Test rate limit exceeded error."""
        error = RateLimitExceededError(
            "Rate limit exceeded",
            limit=100,
            window=3600,
            retry_after=1800
        )
        
        self.assertEqual(error.error_code, "RATE_LIMIT_EXCEEDED")
        self.assertEqual(error.http_status_code, 429)
        self.assertEqual(error.limit, 100)
        self.assertEqual(error.retry_after, 1800)


class TestErrorHandlers(TestCase):
    """Test cases for error handler classes."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.error_handler = ErrorHandler()
    
    def test_error_handler_handle_validation_error(self):
        """Test handling Django validation errors."""
        request = self.factory.get('/')
        error = ValidationError("Invalid data")
        
        response = self.error_handler.handle_error(request, error)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid data", response.content.decode())
    
    def test_error_handler_handle_permission_denied(self):
        """Test handling permission denied errors."""
        request = self.factory.get('/')
        error = PermissionDenied("Access denied")
        
        response = self.error_handler.handle_error(request, error)
        
        self.assertEqual(response.status_code, 403)
    
    def test_error_handler_handle_404(self):
        """Test handling 404 errors."""
        request = self.factory.get('/')
        error = Http404("Page not found")
        
        response = self.error_handler.handle_error(request, error)
        
        self.assertEqual(response.status_code, 404)


class TestErrorHandlingMiddleware(TestCase):
    """Test cases for error handling middleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.get_response = MagicMock(return_value=HttpResponse())
        self.middleware = ErrorHandlingMiddleware(get_response=self.get_response)
    
    def test_middleware_catches_exceptions(self):
        """Test middleware catches and handles exceptions."""
        def view_that_raises(request):
            raise AntmanValidationError("Test validation error")
        
        middleware = ErrorHandlingMiddleware(view_that_raises)
        request = self.factory.get('/')
        
        response = middleware(request)
        
        self.assertEqual(response.status_code, 400)
    
    def test_middleware_passes_through_normal_responses(self):
        """Test middleware doesn't interfere with normal responses."""
        def normal_view(request):
            return HttpResponse("Success", status=200)
        
        middleware = ErrorHandlingMiddleware(normal_view)
        request = self.factory.get('/')
        
        response = middleware(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Success")


class TestRequestLoggingMiddleware(TestCase):
    """Test cases for request logging middleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.get_response = MagicMock(return_value=HttpResponse())
        self.middleware = RequestLoggingErrorMiddleware(get_response=self.get_response)
    
    @patch('core.error_handling.middleware.logger')
    def test_logs_request_details(self, mock_logger):
        """Test middleware logs request details."""
        request = self.factory.post('/api/test/', {'data': 'value'})
        request.user = AnonymousUser()
        
        response = self.middleware(request)
        
        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args[0][0]
        self.assertIn('POST', call_args)
        self.assertIn('/api/test/', call_args)


class TestAPIErrorHandlingMiddleware(TestCase):
    """Test cases for API error handling middleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.get_response = MagicMock(return_value=HttpResponse())
        self.middleware = APIErrorHandlingMiddleware(get_response=self.get_response)
    
    @patch('core.error_handling.middleware.logger')
    def test_logs_api_errors(self, mock_logger):
        """Test middleware logs API errors."""
        def view_that_raises(request):
            raise AntmanValidationError("Test validation error")
        
        middleware = APIErrorHandlingMiddleware(view_that_raises)
        request = self.factory.get('/')
        
        response = middleware(request)
        
        mock_logger.error.assert_called()
        call_args = mock_logger.error.call_args[0][0]
        self.assertIn('Test validation error', call_args)


@pytest.mark.integration
class TestErrorHandlingIntegration(APITestCase):
    """Integration tests for error handling system."""
    
    def test_api_validation_error_response(self):
        """Test API returns proper error response for validation errors."""
        # This would test an actual API endpoint that raises validation errors
        response = self.client.post('/api/test-validation/', {
            'invalid_field': 'invalid_value'
        })
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error_code', data)
        self.assertIn('message', data)
