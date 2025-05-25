"""
Django management command for code generation.
"""
from django.core.management.base import BaseCommand, CommandError
from django.core.management import CommandParser
from core.code_generation.generators import (
    ModelGenerator, 
    ViewGenerator, 
    SerializerGenerator,
    CodeGenerationError
)


class Command(BaseCommand):
    """Django management command for generating code."""
    
    help = 'Generate Django code (models, views, serializers)'
    
    def add_arguments(self, parser: CommandParser):
        """Add command arguments."""
        parser.add_argument(
            'generator_type',
            choices=['model', 'view', 'serializer'],
            help='Type of code to generate'
        )
        
        # Common arguments
        parser.add_argument('--name', required=True, help='Name of the component')
        parser.add_argument('--app', '--app-name', dest='app_name', help='Django app name')
        
        # Model-specific arguments
        parser.add_argument('--fields', help='Model fields (format: name:type:options)')
        parser.add_argument('--str-field', help='Field to use in __str__ method')
        
        # View-specific arguments
        parser.add_argument('--type', '--view-type', dest='view_type', help='Type of view')
        parser.add_argument('--model', help='Model name for the view')
        parser.add_argument('--template', help='Template name')
        
        # Serializer-specific arguments
        parser.add_argument('--serializer-fields', help='Serializer fields')
        
        # Output options
        parser.add_argument('--output', '-o', help='Output file path')
        parser.add_argument('--dry-run', action='store_true', help='Show generated code without saving')
    
    def handle(self, *args, **options):
        """Handle the command execution."""
        generator_type = options['generator_type']
        
        try:
            if generator_type == 'model':
                code = self._generate_model(options)
            elif generator_type == 'view':
                code = self._generate_view(options)
            elif generator_type == 'serializer':
                code = self._generate_serializer(options)
            else:
                raise CommandError(f"Unknown generator type: {generator_type}")
            
            if options['dry_run']:
                self.stdout.write(self.style.SUCCESS("Generated code:"))
                self.stdout.write(code)
            else:
                if options['output']:
                    with open(options['output'], 'w', encoding='utf-8') as f:
                        f.write(code)
                    self.stdout.write(
                        self.style.SUCCESS(f"{generator_type.title()} code saved to {options['output']}")
                    )
                else:
                    self.stdout.write(self.style.SUCCESS(f"{generator_type.title()} generated successfully:"))
                    self.stdout.write(code)
                    
        except CodeGenerationError as e:
            raise CommandError(f"Code generation failed: {str(e)}")
        except Exception as e:
            raise CommandError(f"Unexpected error: {str(e)}")
    
    def _generate_model(self, options):
        """Generate model code."""
        config = {
            'name': options['name'],
            'fields': self._parse_fields(options.get('fields', '')),
            'str_field': options.get('str_field')
        }
        
        if options.get('app_name'):
            config['app_name'] = options['app_name']
        
        generator = ModelGenerator()
        return generator.generate(config)
    
    def _generate_view(self, options):
        """Generate view code."""
        if not options.get('view_type'):
            raise CommandError("View type is required (--type)")
        
        config = {
            'name': options['name'],
            'type': options['view_type'],
            'model': options.get('model'),
            'app_name': options.get('app_name'),
            'template_name': options.get('template')
        }
        
        generator = ViewGenerator()
        return generator.generate(config)
    
    def _generate_serializer(self, options):
        """Generate serializer code."""
        config = {
            'name': options['name'],
            'model': options.get('model', options['name'].replace('Serializer', '')),
            'app_name': options.get('app_name'),
            'fields': self._parse_serializer_fields(options.get('serializer_fields', ''))
        }
        
        generator = SerializerGenerator()
        return generator.generate(config)
    
    def _parse_fields(self, fields_str):
        """Parse field string into field configuration."""
        if not fields_str:
            return []
        
        fields = []
        for field_def in fields_str.split(','):
            parts = field_def.strip().split(':')
            if len(parts) < 2:
                continue
            
            field = {
                'name': parts[0].strip(),
                'type': parts[1].strip()
            }
            
            # Parse additional options
            for option in parts[2:]:
                if '=' in option:
                    key, value = option.split('=', 1)
                    field[key.strip()] = value.strip()
                else:
                    field[option.strip()] = True
            
            fields.append(field)
        
        return fields
    
    def _parse_serializer_fields(self, fields_str):
        """Parse serializer fields string."""
        if not fields_str:
            return ['id']
        
        return [field.strip() for field in fields_str.split(',') if field.strip()]
