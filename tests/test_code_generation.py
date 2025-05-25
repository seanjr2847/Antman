"""
Tests for code generation functionality.
"""
import os
import tempfile
import shutil
from unittest.mock import patch, mock_open, MagicMock
from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from io import StringIO
import pytest

from core.code_generation.generators import (
    ModelGenerator,
    ViewGenerator,
    SerializerGenerator,
    CodeGenerationError
)
from core.code_generation.templates import TemplateManager


class TestModelGenerator(TestCase):
    """Test cases for Django model code generation."""
    
    def setUp(self):
        self.generator = ModelGenerator()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_generate_basic_model(self):
        """Test generating a basic Django model."""
        model_config = {
            'name': 'Product',
            'app_name': 'inventory',
            'fields': [
                {'name': 'title', 'type': 'CharField', 'max_length': 200},
                {'name': 'price', 'type': 'DecimalField', 'max_digits': 10, 'decimal_places': 2},
                {'name': 'created_at', 'type': 'DateTimeField', 'auto_now_add': True}
            ]
        }
        
        result = self.generator.generate(model_config)
        
        self.assertIn('class Product(models.Model):', result)
        self.assertIn('title = models.CharField(max_length=200)', result)
        self.assertIn('price = models.DecimalField(max_digits=10, decimal_places=2)', result)
        self.assertIn('created_at = models.DateTimeField(auto_now_add=True)', result)
        self.assertIn('def __str__(self):', result)
        self.assertIn('class Meta:', result)
    
    def test_generate_model_with_relationships(self):
        """Test generating a model with foreign key relationships."""
        model_config = {
            'name': 'Order',
            'app_name': 'orders',
            'fields': [
                {'name': 'customer', 'type': 'ForeignKey', 'to': 'auth.User', 'on_delete': 'CASCADE'},
                {'name': 'product', 'type': 'ForeignKey', 'to': 'inventory.Product', 'on_delete': 'CASCADE'},
                {'name': 'quantity', 'type': 'PositiveIntegerField', 'default': 1}
            ]
        }
        
        result = self.generator.generate(model_config)
        
        self.assertIn('customer = models.ForeignKey', result)
        self.assertIn('on_delete=models.CASCADE', result)
        self.assertIn("to='auth.User'", result)
    
    def test_generate_model_invalid_config(self):
        """Test error handling for invalid model configuration."""
        invalid_config = {
            'name': '',  # Empty name should raise error
            'fields': []
        }
        
        with self.assertRaises(CodeGenerationError):
            self.generator.generate(invalid_config)
    
    def test_save_generated_model(self):
        """Test saving generated model to file."""
        model_config = {
            'name': 'TestModel',
            'app_name': 'test_app',
            'fields': [
                {'name': 'name', 'type': 'CharField', 'max_length': 100}
            ]
        }
        
        file_path = os.path.join(self.temp_dir, 'models.py')
        
        with patch('builtins.open', mock_open()) as mock_file:
            self.generator.save_to_file(model_config, file_path)
            mock_file.assert_called_once_with(file_path, 'w', encoding='utf-8')


class TestViewGenerator(TestCase):
    """Test cases for Django view code generation."""
    
    def setUp(self):
        self.generator = ViewGenerator()
    
    def test_generate_list_view(self):
        """Test generating a ListView."""
        view_config = {
            'name': 'ProductListView',
            'type': 'ListView',
            'model': 'Product',
            'app_name': 'inventory'
        }
        
        result = self.generator.generate(view_config)
        
        self.assertIn('class ProductListView(ListView):', result)
        self.assertIn('model = Product', result)
        self.assertIn('from django.views.generic import ListView', result)
    
    def test_generate_detail_view(self):
        """Test generating a DetailView."""
        view_config = {
            'name': 'ProductDetailView',
            'type': 'DetailView',
            'model': 'Product',
            'app_name': 'inventory'
        }
        
        result = self.generator.generate(view_config)
        
        self.assertIn('class ProductDetailView(DetailView):', result)
        self.assertIn('model = Product', result)
    
    def test_generate_api_view(self):
        """Test generating a DRF APIView."""
        view_config = {
            'name': 'ProductAPIView',
            'type': 'APIView',
            'model': 'Product',
            'app_name': 'inventory',
            'methods': ['GET', 'POST']
        }
        
        result = self.generator.generate(view_config)
        
        self.assertIn('class ProductAPIView(APIView):', result)
        self.assertIn('def get(self, request, pk=None):', result)
        self.assertIn('def post(self, request):', result)
        self.assertIn('from rest_framework.views import APIView', result)
    
    def test_generate_view_invalid_type(self):
        """Test error handling for invalid view type."""
        invalid_config = {
            'name': 'TestView',
            'type': 'InvalidViewType',
            'model': 'TestModel'
        }
        
        with self.assertRaises(CodeGenerationError):
            self.generator.generate(invalid_config)


class TestSerializerGenerator(TestCase):
    """Test cases for DRF serializer code generation."""
    
    def setUp(self):
        self.generator = SerializerGenerator()
    
    def test_generate_model_serializer(self):
        """Test generating a ModelSerializer."""
        serializer_config = {
            'name': 'ProductSerializer',
            'model': 'Product',
            'app_name': 'inventory',
            'fields': ['id', 'title', 'price', 'created_at']
        }
        
        result = self.generator.generate(serializer_config)
        
        self.assertIn('class ProductSerializer(serializers.ModelSerializer):', result)
        self.assertIn('model = Product', result)
        self.assertIn("fields = ['id', 'title', 'price', 'created_at']", result)
        self.assertIn('from rest_framework import serializers', result)
    
    def test_generate_serializer_with_validation(self):
        """Test generating a serializer with custom validation."""
        serializer_config = {
            'name': 'ProductSerializer',
            'model': 'Product',
            'app_name': 'inventory',
            'fields': ['title', 'price'],
            'validations': [
                {'field': 'price', 'method': 'validate_price'}
            ]
        }
        
        result = self.generator.generate(serializer_config)
        
        self.assertIn('def validate_price(self, value):', result)
        self.assertIn('if value <= 0:', result)
        self.assertIn('raise serializers.ValidationError', result)
    
    def test_generate_nested_serializer(self):
        """Test generating a serializer with nested relationships."""
        serializer_config = {
            'name': 'OrderSerializer',
            'model': 'Order',
            'app_name': 'orders',
            'fields': ['id', 'customer', 'product', 'quantity'],
            'nested_fields': [
                {'field': 'customer', 'serializer': 'UserSerializer'},
                {'field': 'product', 'serializer': 'ProductSerializer'}
            ]
        }
        
        result = self.generator.generate(serializer_config)
        
        self.assertIn('customer = UserSerializer(read_only=True)', result)
        self.assertIn('product = ProductSerializer(read_only=True)', result)


class TestTemplateManager(TestCase):
    """Test cases for template management system."""
    
    def setUp(self):
        self.template_manager = TemplateManager()
    
    def test_load_template(self):
        """Test loading a template file."""
        with patch('builtins.open', mock_open(read_data='Hello {{ name }}!')):
            template = self.template_manager.load_template('test_template.txt')
            self.assertEqual(template, 'Hello {{ name }}!')
    
    def test_render_template(self):
        """Test rendering a template with context."""
        template_content = 'Hello {{ name }}! You are {{ age }} years old.'
        context = {'name': 'John', 'age': 30}
        
        result = self.template_manager.render_template(template_content, context)
        
        self.assertEqual(result, 'Hello John! You are 30 years old.')
    
    def test_load_nonexistent_template(self):
        """Test error handling for nonexistent template."""
        with patch('builtins.open', side_effect=FileNotFoundError):
            with self.assertRaises(CodeGenerationError):
                self.template_manager.load_template('nonexistent.txt')


class TestCodeGenerationManagementCommand(TestCase):
    """Test cases for Django management command."""
    
    def test_generate_model_command(self):
        """Test the generate_code management command for models."""
        with patch('core.code_generation.generators.ModelGenerator.generate') as mock_generate:
            mock_generate.return_value = 'Generated model code'
            
            out = StringIO()
            call_command(
                'generate_code',
                'model',
                '--name=TestModel',
                '--app=test_app',
                '--fields=name:CharField:max_length=100',
                stdout=out
            )
            
            self.assertIn('Model generated successfully', out.getvalue())
            mock_generate.assert_called_once()
    
    def test_generate_view_command(self):
        """Test the generate_code management command for views."""
        with patch('core.code_generation.generators.ViewGenerator.generate') as mock_generate:
            mock_generate.return_value = 'Generated view code'
            
            out = StringIO()
            call_command(
                'generate_code',
                'view',
                '--name=TestView',
                '--type=ListView',
                '--model=TestModel',
                stdout=out
            )
            
            self.assertIn('View generated successfully', out.getvalue())
            mock_generate.assert_called_once()
    
    def test_invalid_generator_type(self):
        """Test error handling for invalid generator type."""
        with self.assertRaises(CommandError):
            call_command('generate_code', 'invalid_type')


@pytest.mark.integration
class TestCodeGenerationIntegration(TestCase):
    """Integration tests for code generation system."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_full_model_generation_workflow(self):
        """Test complete model generation workflow."""
        model_config = {
            'name': 'Product',
            'app_name': 'inventory',
            'fields': [
                {'name': 'title', 'type': 'CharField', 'max_length': 200},
                {'name': 'price', 'type': 'DecimalField', 'max_digits': 10, 'decimal_places': 2}
            ]
        }
        
        generator = ModelGenerator()
        code = generator.generate(model_config)
        
        # Verify the generated code is syntactically valid Python
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError:
            self.fail("Generated code is not valid Python syntax")
        
        # Verify required components are present
        self.assertIn('class Product(models.Model):', code)
        self.assertIn('def __str__(self):', code)
        self.assertIn('class Meta:', code)
    
    def test_view_and_serializer_generation_consistency(self):
        """Test that view and serializer generation are consistent."""
        model_name = 'Product'
        app_name = 'inventory'
        
        view_config = {
            'name': f'{model_name}APIView',
            'type': 'APIView',
            'model': model_name,
            'app_name': app_name
        }
        
        serializer_config = {
            'name': f'{model_name}Serializer',
            'model': model_name,
            'app_name': app_name,
            'fields': ['id', 'title', 'price']
        }
        
        view_generator = ViewGenerator()
        serializer_generator = SerializerGenerator()
        
        view_code = view_generator.generate(view_config)
        serializer_code = serializer_generator.generate(serializer_config)
        
        # Both should reference the same model
        self.assertIn(f'from {app_name}.models import {model_name}', view_code)
        self.assertIn(f'from {app_name}.models import {model_name}', serializer_code)
