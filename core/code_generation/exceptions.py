"""
Custom exceptions for code generation module.
"""


class CodeGenerationError(Exception):
    """Base exception for code generation errors."""
    
    def __init__(self, message, details=None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self):
        return self.message


class InvalidConfigurationError(CodeGenerationError):
    """Raised when configuration is invalid."""
    pass


class TemplateNotFoundError(CodeGenerationError):
    """Raised when template file is not found."""
    pass


class GenerationFailedError(CodeGenerationError):
    """Raised when code generation fails."""
    pass
