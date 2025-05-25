"""
Template management system for code generation.
"""
import os
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader, Template
from .exceptions import CodeGenerationError, TemplateNotFoundError


class TemplateManager:
    """Manages code generation templates."""
    
    def __init__(self, template_dir=None):
        self.template_dir = template_dir or self._get_default_template_dir()
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def _get_default_template_dir(self):
        """Get default template directory."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, 'templates')
    
    def load_template(self, template_name: str) -> str:
        """Load template content from file."""
        try:
            template_path = os.path.join(self.template_dir, template_name)
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise TemplateNotFoundError(f"Template '{template_name}' not found")
        except Exception as e:
            raise CodeGenerationError(f"Error loading template '{template_name}': {str(e)}")
    
    def render_template(self, template_content: str, context: Dict[str, Any]) -> str:
        """Render template with given context."""
        try:
            template = Template(template_content)
            return template.render(**context)
        except Exception as e:
            raise CodeGenerationError(f"Error rendering template: {str(e)}")
    
    def render_template_file(self, template_name: str, context: Dict[str, Any]) -> str:
        """Load and render template file."""
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            raise CodeGenerationError(f"Error rendering template '{template_name}': {str(e)}")
    
    def list_templates(self) -> list:
        """List available templates."""
        try:
            templates = []
            for root, dirs, files in os.walk(self.template_dir):
                for file in files:
                    if file.endswith(('.j2', '.jinja', '.template')):
                        rel_path = os.path.relpath(os.path.join(root, file), self.template_dir)
                        templates.append(rel_path)
            return templates
        except Exception as e:
            raise CodeGenerationError(f"Error listing templates: {str(e)}")


# Template content constants
MODEL_TEMPLATE = """from django.db import models
{% if imports %}
{% for import in imports %}
{{ import }}
{% endfor %}
{% endif %}


class {{ model_name }}(models.Model):
    \"\"\"{{ model_description|default('Model description.') }}\"\"\"
    
    {% for field in fields %}
    {% if field.type == 'CharField' %}
    {{ field.name }} = models.CharField(max_length={{ field.max_length|default(200) }}{% if field.blank %}, blank=True{% endif %}{% if field.null %}, null=True{% endif %}{% if field.default %}, default='{{ field.default }}'{% endif %})
    {% elif field.type == 'TextField' %}
    {{ field.name }} = models.TextField({% if field.blank %}blank=True{% endif %}{% if field.null %}{% if field.blank %}, {% endif %}null=True{% endif %}{% if field.default %}{% if field.blank or field.null %}, {% endif %}default='{{ field.default }}'{% endif %})
    {% elif field.type == 'IntegerField' %}
    {{ field.name }} = models.IntegerField({% if field.default %}default={{ field.default }}{% endif %}{% if field.null %}{% if field.default %}, {% endif %}null=True{% endif %})
    {% elif field.type == 'PositiveIntegerField' %}
    {{ field.name }} = models.PositiveIntegerField({% if field.default %}default={{ field.default }}{% endif %}{% if field.null %}{% if field.default %}, {% endif %}null=True{% endif %})
    {% elif field.type == 'DecimalField' %}
    {{ field.name }} = models.DecimalField(max_digits={{ field.max_digits|default(10) }}, decimal_places={{ field.decimal_places|default(2) }}{% if field.default %}, default={{ field.default }}{% endif %}{% if field.null %}, null=True{% endif %})
    {% elif field.type == 'BooleanField' %}
    {{ field.name }} = models.BooleanField(default={{ field.default|default('False') }})
    {% elif field.type == 'DateTimeField' %}
    {{ field.name }} = models.DateTimeField({% if field.auto_now_add %}auto_now_add=True{% elif field.auto_now %}auto_now=True{% endif %}{% if field.default and not field.auto_now_add and not field.auto_now %}, default='{{ field.default }}'{% endif %}{% if field.null %}, null=True{% endif %})
    {% elif field.type == 'DateField' %}
    {{ field.name }} = models.DateField({% if field.auto_now_add %}auto_now_add=True{% elif field.auto_now %}auto_now=True{% endif %}{% if field.default and not field.auto_now_add and not field.auto_now %}, default='{{ field.default }}'{% endif %}{% if field.null %}, null=True{% endif %})
    {% elif field.type == 'ForeignKey' %}
    {{ field.name }} = models.ForeignKey(to='{{ field.to }}', on_delete=models.{{ field.on_delete|default('CASCADE') }}{% if field.related_name %}, related_name='{{ field.related_name }}'{% endif %}{% if field.null %}, null=True{% endif %}{% if field.blank %}, blank=True{% endif %})
    {% elif field.type == 'ManyToManyField' %}
    {{ field.name }} = models.ManyToManyField('{{ field.to }}'{% if field.related_name %}, related_name='{{ field.related_name }}'{% endif %}{% if field.blank %}, blank=True{% endif %})
    {% elif field.type == 'OneToOneField' %}
    {{ field.name }} = models.OneToOneField('{{ field.to }}', on_delete=models.{{ field.on_delete|default('CASCADE') }}{% if field.related_name %}, related_name='{{ field.related_name }}'{% endif %}{% if field.null %}, null=True{% endif %})
    {% else %}
    {{ field.name }} = models.{{ field.type }}({% if field.options %}{{ field.options }}{% endif %})
    {% endif %}
    {% endfor %}
    
    def __str__(self):
        {% if str_field %}
        return str(self.{{ str_field }})
        {% else %}
        return f"{{ model_name }} #{self.pk}"
        {% endif %}
    
    class Meta:
        {% if verbose_name %}
        verbose_name = "{{ verbose_name }}"
        {% endif %}
        {% if verbose_name_plural %}
        verbose_name_plural = "{{ verbose_name_plural }}"
        {% endif %}
        {% if ordering %}
        ordering = {{ ordering }}
        {% endif %}
        {% if db_table %}
        db_table = "{{ db_table }}"
        {% endif %}
        {% if not verbose_name and not verbose_name_plural and not ordering and not db_table %}
        pass
        {% endif %}
"""

VIEW_TEMPLATE = """{% if view_type == 'ListView' %}
from django.views.generic import ListView
from {{ app_name }}.models import {{ model_name }}


class {{ view_name }}(ListView):
    \"\"\"List view for {{ model_name }} objects.\"\"\"
    model = {{ model_name }}
    template_name = '{{ app_name }}/{{ model_name|lower }}_list.html'
    context_object_name = '{{ model_name|lower }}_list'
    paginate_by = {{ paginate_by|default(20) }}
    
    {% if queryset_filters %}
    def get_queryset(self):
        queryset = super().get_queryset()
        {% for filter in queryset_filters %}
        queryset = queryset.filter({{ filter }})
        {% endfor %}
        return queryset
    {% endif %}

{% elif view_type == 'DetailView' %}
from django.views.generic import DetailView
from {{ app_name }}.models import {{ model_name }}


class {{ view_name }}(DetailView):
    \"\"\"Detail view for {{ model_name }} objects.\"\"\"
    model = {{ model_name }}
    template_name = '{{ app_name }}/{{ model_name|lower }}_detail.html'
    context_object_name = '{{ model_name|lower }}'

{% elif view_type == 'CreateView' %}
from django.views.generic import CreateView
from django.urls import reverse_lazy
from {{ app_name }}.models import {{ model_name }}
{% if form_class %}
from {{ app_name }}.forms import {{ form_class }}
{% endif %}


class {{ view_name }}(CreateView):
    \"\"\"Create view for {{ model_name }} objects.\"\"\"
    model = {{ model_name }}
    {% if form_class %}
    form_class = {{ form_class }}
    {% else %}
    fields = {{ fields|default("'__all__'") }}
    {% endif %}
    template_name = '{{ app_name }}/{{ model_name|lower }}_form.html'
    success_url = reverse_lazy('{{ app_name }}:{{ model_name|lower }}-list')

{% elif view_type == 'APIView' %}
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from {{ app_name }}.models import {{ model_name }}
from {{ app_name }}.serializers import {{ model_name }}Serializer


class {{ view_name }}(APIView):
    \"\"\"API view for {{ model_name }} objects.\"\"\"
    
    {% if 'GET' in methods %}
    def get(self, request, pk=None):
        \"\"\"Retrieve {{ model_name }} object(s).\"\"\"
        if pk:
            try:
                obj = {{ model_name }}.objects.get(pk=pk)
                serializer = {{ model_name }}Serializer(obj)
                return Response(serializer.data)
            except {{ model_name }}.DoesNotExist:
                return Response(
                    {'error': '{{ model_name }} not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            objects = {{ model_name }}.objects.all()
            serializer = {{ model_name }}Serializer(objects, many=True)
            return Response(serializer.data)
    {% endif %}
    
    {% if 'POST' in methods %}
    def post(self, request):
        \"\"\"Create new {{ model_name }} object.\"\"\"
        serializer = {{ model_name }}Serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    {% endif %}
    
    {% if 'PUT' in methods %}
    def put(self, request, pk):
        \"\"\"Update {{ model_name }} object.\"\"\"
        try:
            obj = {{ model_name }}.objects.get(pk=pk)
        except {{ model_name }}.DoesNotExist:
            return Response(
                {'error': '{{ model_name }} not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = {{ model_name }}Serializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    {% endif %}
    
    {% if 'DELETE' in methods %}
    def delete(self, request, pk):
        \"\"\"Delete {{ model_name }} object.\"\"\"
        try:
            obj = {{ model_name }}.objects.get(pk=pk)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except {{ model_name }}.DoesNotExist:
            return Response(
                {'error': '{{ model_name }} not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    {% endif %}
{% endif %}
"""

SERIALIZER_TEMPLATE = """from rest_framework import serializers
from {{ app_name }}.models import {{ model_name }}
{% if nested_serializers %}
{% for serializer in nested_serializers %}
from {{ serializer.app }}.serializers import {{ serializer.name }}
{% endfor %}
{% endif %}


class {{ serializer_name }}(serializers.ModelSerializer):
    \"\"\"Serializer for {{ model_name }} model.\"\"\"
    
    {% if nested_fields %}
    {% for field in nested_fields %}
    {{ field.field }} = {{ field.serializer }}(read_only=True)
    {% endfor %}
    {% endif %}
    
    class Meta:
        model = {{ model_name }}
        fields = {{ fields }}
        {% if read_only_fields %}
        read_only_fields = {{ read_only_fields }}
        {% endif %}
        {% if extra_kwargs %}
        extra_kwargs = {{ extra_kwargs }}
        {% endif %}
    
    {% if validations %}
    {% for validation in validations %}
    def validate_{{ validation.field }}(self, value):
        \"\"\"Validate {{ validation.field }} field.\"\"\"
        {% if validation.field == 'price' %}
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        {% elif validation.field == 'email' %}
        if not value or '@' not in value:
            raise serializers.ValidationError("Invalid email format")
        {% else %}
        # Custom validation for {{ validation.field }}
        if not value:
            raise serializers.ValidationError("{{ validation.field }} is required")
        {% endif %}
        return value
    {% endfor %}
    {% endif %}
    
    {% if custom_methods %}
    {% for method in custom_methods %}
    def {{ method.name }}(self, obj):
        \"\"\"{{ method.description|default('Custom method.') }}\"\"\"
        {{ method.body|default('return None') }}
    {% endfor %}
    {% endif %}
"""
