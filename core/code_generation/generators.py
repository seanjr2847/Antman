"""
Code generators for Django models, views, and serializers.
"""
import os
from typing import Dict, Any, List
from jinja2 import Template
from .exceptions import CodeGenerationError, InvalidConfigurationError
from .templates import TemplateManager, MODEL_TEMPLATE, VIEW_TEMPLATE, SERIALIZER_TEMPLATE


class BaseGenerator:
    """Base class for code generators."""
    
    def __init__(self):
        self.template_manager = TemplateManager()
    
    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration dictionary."""
        raise NotImplementedError("Subclasses must implement validate_config")
    
    def generate(self, config: Dict[str, Any]) -> str:
        """Generate code based on configuration."""
        raise NotImplementedError("Subclasses must implement generate")
    
    def save_to_file(self, config: Dict[str, Any], file_path: str) -> None:
        """Save generated code to file."""
        code = self.generate(config)
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
        except Exception as e:
            raise CodeGenerationError(f"Error saving to file '{file_path}': {str(e)}")


class ModelGenerator(BaseGenerator):
    """Generator for Django models."""
    
    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate model configuration."""
        if not config.get('name'):
            raise InvalidConfigurationError("Model name is required")
        
        if not config.get('fields'):
            raise InvalidConfigurationError("At least one field is required")
        
        # Validate field configurations
        for field in config['fields']:
            if not field.get('name'):
                raise InvalidConfigurationError("Field name is required")
            if not field.get('type'):
                raise InvalidConfigurationError("Field type is required")
            
            # Validate specific field types
            if field['type'] == 'CharField' and not field.get('max_length'):
                field['max_length'] = 200  # Set default
            elif field['type'] == 'DecimalField':
                if not field.get('max_digits'):
                    field['max_digits'] = 10
                if not field.get('decimal_places'):
                    field['decimal_places'] = 2
            elif field['type'] == 'ForeignKey':
                if not field.get('to'):
                    raise InvalidConfigurationError("ForeignKey field requires 'to' parameter")
                if not field.get('on_delete'):
                    field['on_delete'] = 'CASCADE'
    
    def generate(self, config: Dict[str, Any]) -> str:
        """Generate Django model code."""
        self.validate_config(config)
        
        context = {
            'model_name': config['name'],
            'model_description': config.get('description', f"{config['name']} model."),
            'fields': config['fields'],
            'str_field': config.get('str_field'),
            'verbose_name': config.get('verbose_name'),
            'verbose_name_plural': config.get('verbose_name_plural'),
            'ordering': config.get('ordering'),
            'db_table': config.get('db_table'),
            'imports': config.get('imports', [])
        }
        
        try:
            template = Template(MODEL_TEMPLATE)
            return template.render(**context)
        except Exception as e:
            raise CodeGenerationError(f"Error generating model: {str(e)}")


class ViewGenerator(BaseGenerator):
    """Generator for Django views."""
    
    SUPPORTED_VIEW_TYPES = ['ListView', 'DetailView', 'CreateView', 'UpdateView', 'DeleteView', 'APIView']
    
    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate view configuration."""
        if not config.get('name'):
            raise InvalidConfigurationError("View name is required")
        
        if not config.get('type'):
            raise InvalidConfigurationError("View type is required")
        
        if config['type'] not in self.SUPPORTED_VIEW_TYPES:
            raise InvalidConfigurationError(f"Unsupported view type: {config['type']}")
        
        if not config.get('model'):
            raise InvalidConfigurationError("Model name is required")
        
        if not config.get('app_name'):
            raise InvalidConfigurationError("App name is required")
        
        # Set defaults for API views
        if config['type'] == 'APIView' and not config.get('methods'):
            config['methods'] = ['GET', 'POST']
    
    def generate(self, config: Dict[str, Any]) -> str:
        """Generate Django view code."""
        self.validate_config(config)
        
        context = {
            'view_name': config['name'],
            'view_type': config['type'],
            'model_name': config['model'],
            'app_name': config['app_name'],
            'methods': config.get('methods', []),
            'paginate_by': config.get('paginate_by', 20),
            'queryset_filters': config.get('queryset_filters', []),
            'form_class': config.get('form_class'),
            'fields': config.get('fields', "'__all__'")
        }
        
        try:
            template = Template(VIEW_TEMPLATE)
            return template.render(**context)
        except Exception as e:
            raise CodeGenerationError(f"Error generating view: {str(e)}")


class SerializerGenerator(BaseGenerator):
    """Generator for DRF serializers."""
    
    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate serializer configuration."""
        if not config.get('name'):
            raise InvalidConfigurationError("Serializer name is required")
        
        if not config.get('model'):
            raise InvalidConfigurationError("Model name is required")
        
        if not config.get('app_name'):
            raise InvalidConfigurationError("App name is required")
        
        if not config.get('fields'):
            config['fields'] = "'__all__'"
    
    def generate(self, config: Dict[str, Any]) -> str:
        """Generate DRF serializer code."""
        self.validate_config(config)
        
        context = {
            'serializer_name': config['name'],
            'model_name': config['model'],
            'app_name': config['app_name'],
            'fields': config['fields'],
            'read_only_fields': config.get('read_only_fields'),
            'extra_kwargs': config.get('extra_kwargs'),
            'validations': config.get('validations', []),
            'nested_fields': config.get('nested_fields', []),
            'nested_serializers': config.get('nested_serializers', []),
            'custom_methods': config.get('custom_methods', [])
        }
        
        try:
            template = Template(SERIALIZER_TEMPLATE)
            return template.render(**context)
        except Exception as e:
            raise CodeGenerationError(f"Error generating serializer: {str(e)}")


class CodeGeneratorManager:
    """Manager for all code generators."""
    
    def __init__(self):
        self.generators = {
            'model': ModelGenerator(),
            'view': ViewGenerator(),
            'serializer': SerializerGenerator()
        }
    
    def get_generator(self, generator_type: str) -> BaseGenerator:
        """Get generator by type."""
        if generator_type not in self.generators:
            raise CodeGenerationError(f"Unknown generator type: {generator_type}")
        return self.generators[generator_type]
    
    def generate_code(self, generator_type: str, config: Dict[str, Any]) -> str:
        """Generate code using specified generator."""
        generator = self.get_generator(generator_type)
        return generator.generate(config)
    
    def save_code(self, generator_type: str, config: Dict[str, Any], file_path: str) -> None:
        """Generate and save code to file."""
        generator = self.get_generator(generator_type)
        generator.save_to_file(config, file_path)
    
    def get_supported_types(self) -> List[str]:
        """Get list of supported generator types."""
        return list(self.generators.keys())


# Convenience functions
def generate_model(config: Dict[str, Any]) -> str:
    """Generate Django model code."""
    generator = ModelGenerator()
    return generator.generate(config)


def generate_view(config: Dict[str, Any]) -> str:
    """Generate Django view code."""
    generator = ViewGenerator()
    return generator.generate(config)


def generate_serializer(config: Dict[str, Any]) -> str:
    """Generate DRF serializer code."""
    generator = SerializerGenerator()
    return generator.generate(config)


def generate_crud_set(model_config: Dict[str, Any], app_name: str) -> Dict[str, str]:
    """Generate complete CRUD set (model, views, serializer)."""
    model_name = model_config['name']
    
    # Generate model
    model_code = generate_model(model_config)
    
    # Generate API view
    view_config = {
        'name': f'{model_name}APIView',
        'type': 'APIView',
        'model': model_name,
        'app_name': app_name,
        'methods': ['GET', 'POST', 'PUT', 'DELETE']
    }
    view_code = generate_view(view_config)
    
    # Generate serializer
    serializer_config = {
        'name': f'{model_name}Serializer',
        'model': model_name,
        'app_name': app_name,
        'fields': "'__all__'"
    }
    serializer_code = generate_serializer(serializer_config)
    
    return {
        'model': model_code,
        'view': view_code,
        'serializer': serializer_code
    }
