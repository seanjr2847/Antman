"""
Custom exception classes for comprehensive error handling.
"""
import datetime
from typing import Dict, Any, Optional, List


class AntmanBaseException(Exception):
    """Base exception class for all Antman-specific errors."""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = None, 
        details: Dict[str, Any] = None,
        http_status_code: int = 500
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.details = details or {}
        self.http_status_code = http_status_code
        self.timestamp = datetime.datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON serialization."""
        return {
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat(),
            'http_status_code': self.http_status_code
        }
    
    def __str__(self):
        return self.message


class ValidationError(AntmanBaseException):
    """Exception for validation errors."""
    
    def __init__(
        self, 
        message: str, 
        field_errors: Dict[str, List[str]] = None,
        details: Dict[str, Any] = None
    ):
        super().__init__(
            message, 
            error_code="VALIDATION_ERROR", 
            details=details,
            http_status_code=400
        )
        self.field_errors = field_errors or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary including field errors."""
        data = super().to_dict()
        if self.field_errors:
            data['field_errors'] = self.field_errors
        return data


class AuthenticationError(AntmanBaseException):
    """Exception for authentication failures."""
    
    def __init__(self, message: str = "Authentication failed", details: Dict[str, Any] = None):
        super().__init__(
            message, 
            error_code="AUTHENTICATION_ERROR", 
            details=details,
            http_status_code=401
        )


class AuthorizationError(AntmanBaseException):
    """Exception for authorization failures."""
    
    def __init__(self, message: str = "Access denied", details: Dict[str, Any] = None):
        super().__init__(
            message, 
            error_code="AUTHORIZATION_ERROR", 
            details=details,
            http_status_code=403
        )


class ResourceNotFoundError(AntmanBaseException):
    """Exception for resource not found errors."""
    
    def __init__(
        self, 
        message: str, 
        resource_type: str = None, 
        resource_id: Any = None,
        details: Dict[str, Any] = None
    ):
        super().__init__(
            message, 
            error_code="RESOURCE_NOT_FOUND", 
            details=details,
            http_status_code=404
        )
        self.resource_type = resource_type
        self.resource_id = resource_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary including resource info."""
        data = super().to_dict()
        if self.resource_type:
            data['resource_type'] = self.resource_type
        if self.resource_id is not None:
            data['resource_id'] = self.resource_id
        return data


class ExternalServiceError(AntmanBaseException):
    """Exception for external service failures."""
    
    def __init__(
        self, 
        message: str, 
        service_name: str = None,
        service_response: Dict[str, Any] = None,
        details: Dict[str, Any] = None
    ):
        super().__init__(
            message, 
            error_code="EXTERNAL_SERVICE_ERROR", 
            details=details,
            http_status_code=502
        )
        self.service_name = service_name
        self.service_response = service_response or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary including service info."""
        data = super().to_dict()
        if self.service_name:
            data['service_name'] = self.service_name
        if self.service_response:
            data['service_response'] = self.service_response
        return data


class RateLimitExceededError(AntmanBaseException):
    """Exception for rate limit exceeded errors."""
    
    def __init__(
        self, 
        message: str = "Rate limit exceeded", 
        limit: int = None,
        window: int = None,
        retry_after: int = None,
        details: Dict[str, Any] = None
    ):
        super().__init__(
            message, 
            error_code="RATE_LIMIT_EXCEEDED", 
            details=details,
            http_status_code=429
        )
        self.limit = limit
        self.window = window
        self.retry_after = retry_after
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary including rate limit info."""
        data = super().to_dict()
        if self.limit is not None:
            data['limit'] = self.limit
        if self.window is not None:
            data['window'] = self.window
        if self.retry_after is not None:
            data['retry_after'] = self.retry_after
        return data


class BusinessLogicError(AntmanBaseException):
    """Exception for business logic violations."""
    
    def __init__(self, message: str, rule_name: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message, 
            error_code="BUSINESS_LOGIC_ERROR", 
            details=details,
            http_status_code=422
        )
        self.rule_name = rule_name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary including rule info."""
        data = super().to_dict()
        if self.rule_name:
            data['rule_name'] = self.rule_name
        return data


class ConfigurationError(AntmanBaseException):
    """Exception for configuration errors."""
    
    def __init__(self, message: str, config_key: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message, 
            error_code="CONFIGURATION_ERROR", 
            details=details,
            http_status_code=500
        )
        self.config_key = config_key
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary including config info."""
        data = super().to_dict()
        if self.config_key:
            data['config_key'] = self.config_key
        return data


class DatabaseError(AntmanBaseException):
    """Exception for database-related errors."""
    
    def __init__(
        self, 
        message: str, 
        operation: str = None,
        table: str = None,
        details: Dict[str, Any] = None
    ):
        super().__init__(
            message, 
            error_code="DATABASE_ERROR", 
            details=details,
            http_status_code=500
        )
        self.operation = operation
        self.table = table
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary including database info."""
        data = super().to_dict()
        if self.operation:
            data['operation'] = self.operation
        if self.table:
            data['table'] = self.table
        return data


class CacheError(AntmanBaseException):
    """Exception for cache-related errors."""
    
    def __init__(
        self, 
        message: str, 
        cache_key: str = None,
        cache_backend: str = None,
        details: Dict[str, Any] = None
    ):
        super().__init__(
            message, 
            error_code="CACHE_ERROR", 
            details=details,
            http_status_code=500
        )
        self.cache_key = cache_key
        self.cache_backend = cache_backend
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary including cache info."""
        data = super().to_dict()
        if self.cache_key:
            data['cache_key'] = self.cache_key
        if self.cache_backend:
            data['cache_backend'] = self.cache_backend
        return data


class FileSystemError(AntmanBaseException):
    """Exception for file system errors."""
    
    def __init__(
        self, 
        message: str, 
        file_path: str = None,
        operation: str = None,
        details: Dict[str, Any] = None
    ):
        super().__init__(
            message, 
            error_code="FILESYSTEM_ERROR", 
            details=details,
            http_status_code=500
        )
        self.file_path = file_path
        self.operation = operation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary including file system info."""
        data = super().to_dict()
        if self.file_path:
            data['file_path'] = self.file_path
        if self.operation:
            data['operation'] = self.operation
        return data
