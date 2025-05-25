"""
Code quality tools integration for automated code formatting and linting.
향후 유지보수가 쉽도록 코드 퀄리티 및 자동생성 및 리팅기능 추가
"""
import os
import subprocess
import tempfile
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json


class CodeQualityError(Exception):
    """Exception for code quality tool errors."""
    pass


class CodeFormatter:
    """Code formatting using Black."""
    
    def __init__(self, line_length: int = 88, target_version: str = "py39"):
        self.line_length = line_length
        self.target_version = target_version
    
    def format_code(self, code: str) -> str:
        """Format Python code using Black."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            # Run Black on the temporary file
            cmd = [
                'black',
                '--line-length', str(self.line_length),
                '--target-version', self.target_version,
                '--quiet',
                temp_file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise CodeQualityError(f"Black formatting failed: {result.stderr}")
            
            # Read the formatted code
            with open(temp_file_path, 'r', encoding='utf-8') as f:
                formatted_code = f.read()
            
            # Clean up
            os.unlink(temp_file_path)
            
            return formatted_code
            
        except Exception as e:
            # Clean up on error
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            raise CodeQualityError(f"Error formatting code: {str(e)}")
    
    def format_file(self, file_path: str) -> bool:
        """Format a Python file using Black."""
        try:
            cmd = [
                'black',
                '--line-length', str(self.line_length),
                '--target-version', self.target_version,
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            raise CodeQualityError(f"Error formatting file {file_path}: {str(e)}")
    
    def check_formatting(self, code: str) -> bool:
        """Check if code is properly formatted."""
        try:
            formatted_code = self.format_code(code)
            return code.strip() == formatted_code.strip()
        except Exception:
            return False


class ImportSorter:
    """Import sorting using isort."""
    
    def __init__(self, profile: str = "black", line_length: int = 88):
        self.profile = profile
        self.line_length = line_length
    
    def sort_imports(self, code: str) -> str:
        """Sort imports in Python code using isort."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            # Run isort on the temporary file
            cmd = [
                'isort',
                '--profile', self.profile,
                '--line-length', str(self.line_length),
                '--quiet',
                temp_file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise CodeQualityError(f"isort failed: {result.stderr}")
            
            # Read the sorted code
            with open(temp_file_path, 'r', encoding='utf-8') as f:
                sorted_code = f.read()
            
            # Clean up
            os.unlink(temp_file_path)
            
            return sorted_code
            
        except Exception as e:
            # Clean up on error
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            raise CodeQualityError(f"Error sorting imports: {str(e)}")
    
    def sort_file_imports(self, file_path: str) -> bool:
        """Sort imports in a Python file using isort."""
        try:
            cmd = [
                'isort',
                '--profile', self.profile,
                '--line-length', str(self.line_length),
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            raise CodeQualityError(f"Error sorting imports in file {file_path}: {str(e)}")
    
    def check_import_sorting(self, code: str) -> bool:
        """Check if imports are properly sorted."""
        try:
            sorted_code = self.sort_imports(code)
            return code.strip() == sorted_code.strip()
        except Exception:
            return False


class CodeLinter:
    """Code linting using Ruff."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
    
    def lint_code(self, code: str) -> List[Dict[str, Any]]:
        """Lint Python code using Ruff."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            # Run Ruff on the temporary file
            cmd = ['ruff', 'check', '--output-format=json', temp_file_path]
            
            if self.config_file:
                cmd.extend(['--config', self.config_file])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Clean up
            os.unlink(temp_file_path)
            
            # Parse JSON output
            if result.stdout:
                try:
                    issues = json.loads(result.stdout)
                    return issues
                except json.JSONDecodeError:
                    return []
            
            return []
            
        except Exception as e:
            # Clean up on error
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            raise CodeQualityError(f"Error linting code: {str(e)}")
    
    def lint_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Lint a Python file using Ruff."""
        try:
            cmd = ['ruff', 'check', '--output-format=json', file_path]
            
            if self.config_file:
                cmd.extend(['--config', self.config_file])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Parse JSON output
            if result.stdout:
                try:
                    issues = json.loads(result.stdout)
                    return issues
                except json.JSONDecodeError:
                    return []
            
            return []
            
        except Exception as e:
            raise CodeQualityError(f"Error linting file {file_path}: {str(e)}")
    
    def fix_code(self, code: str) -> str:
        """Fix linting issues in Python code using Ruff."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            # Run Ruff fix on the temporary file
            cmd = ['ruff', 'check', '--fix', temp_file_path]
            
            if self.config_file:
                cmd.extend(['--config', self.config_file])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Read the fixed code
            with open(temp_file_path, 'r', encoding='utf-8') as f:
                fixed_code = f.read()
            
            # Clean up
            os.unlink(temp_file_path)
            
            return fixed_code
            
        except Exception as e:
            # Clean up on error
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            raise CodeQualityError(f"Error fixing code: {str(e)}")


class CodeQualityManager:
    """Manager for all code quality tools."""
    
    def __init__(
        self,
        line_length: int = 88,
        target_version: str = "py39",
        isort_profile: str = "black",
        ruff_config: Optional[str] = None
    ):
        self.formatter = CodeFormatter(line_length, target_version)
        self.import_sorter = ImportSorter(isort_profile, line_length)
        self.linter = CodeLinter(ruff_config)
    
    def process_code(self, code: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Process code through all quality tools."""
        # Step 1: Sort imports
        processed_code = self.import_sorter.sort_imports(code)
        
        # Step 2: Format code
        processed_code = self.formatter.format_code(processed_code)
        
        # Step 3: Fix linting issues
        processed_code = self.linter.fix_code(processed_code)
        
        # Step 4: Get remaining lint issues
        lint_issues = self.linter.lint_code(processed_code)
        
        return processed_code, lint_issues
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a file through all quality tools."""
        try:
            # Read original file
            with open(file_path, 'r', encoding='utf-8') as f:
                original_code = f.read()
            
            # Process code
            processed_code, lint_issues = self.process_code(original_code)
            
            # Write back if changed
            if original_code != processed_code:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(processed_code)
            
            return {
                'file_path': file_path,
                'changed': original_code != processed_code,
                'lint_issues': lint_issues,
                'success': True
            }
            
        except Exception as e:
            return {
                'file_path': file_path,
                'changed': False,
                'lint_issues': [],
                'success': False,
                'error': str(e)
            }
    
    def process_directory(self, directory_path: str, extensions: List[str] = None) -> List[Dict[str, Any]]:
        """Process all Python files in a directory."""
        if extensions is None:
            extensions = ['.py']
        
        results = []
        directory = Path(directory_path)
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix in extensions:
                result = self.process_file(str(file_path))
                results.append(result)
        
        return results
    
    def check_code_quality(self, code: str) -> Dict[str, Any]:
        """Check code quality without modifying the code."""
        # Check formatting
        is_formatted = self.formatter.check_formatting(code)
        
        # Check import sorting
        imports_sorted = self.import_sorter.check_import_sorting(code)
        
        # Get lint issues
        lint_issues = self.linter.lint_code(code)
        
        return {
            'is_formatted': is_formatted,
            'imports_sorted': imports_sorted,
            'lint_issues': lint_issues,
            'quality_score': self._calculate_quality_score(is_formatted, imports_sorted, lint_issues)
        }
    
    def _calculate_quality_score(
        self, 
        is_formatted: bool, 
        imports_sorted: bool, 
        lint_issues: List[Dict[str, Any]]
    ) -> float:
        """Calculate a quality score from 0 to 100."""
        score = 100.0
        
        # Deduct points for formatting issues
        if not is_formatted:
            score -= 20
        
        # Deduct points for import sorting issues
        if not imports_sorted:
            score -= 10
        
        # Deduct points for lint issues
        for issue in lint_issues:
            # Deduct more points for errors than warnings
            if issue.get('type') == 'error':
                score -= 5
            else:
                score -= 2
        
        return max(0.0, score)


# Convenience functions
def format_code(code: str, line_length: int = 88) -> str:
    """Format Python code using Black."""
    formatter = CodeFormatter(line_length)
    return formatter.format_code(code)


def sort_imports(code: str, profile: str = "black") -> str:
    """Sort imports in Python code using isort."""
    sorter = ImportSorter(profile)
    return sorter.sort_imports(code)


def lint_code(code: str) -> List[Dict[str, Any]]:
    """Lint Python code using Ruff."""
    linter = CodeLinter()
    return linter.lint_code(code)


def process_code_quality(code: str) -> Tuple[str, List[Dict[str, Any]]]:
    """Process code through all quality tools."""
    manager = CodeQualityManager()
    return manager.process_code(code)
