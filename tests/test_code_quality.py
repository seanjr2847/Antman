"""
Tests for code quality tools and automation.
"""
import os
import tempfile
import subprocess
from unittest.mock import patch, MagicMock, mock_open
from django.test import TestCase
import pytest

from core.code_quality.formatters import (
    BlackFormatter,
    IsortFormatter,
    CodeFormatter
)
from core.code_quality.linters import (
    RuffLinter,
    MyPyLinter,
    CodeLinter
)
from core.code_quality.hooks import (
    PreCommitManager,
    GitHookManager
)
from core.code_quality.analyzers import (
    CodeComplexityAnalyzer,
    CoverageAnalyzer,
    SecurityAnalyzer
)


class TestBlackFormatter(TestCase):
    """Test cases for Black code formatter."""
    
    def setUp(self):
        self.formatter = BlackFormatter()
    
    @patch('subprocess.run')
    def test_format_file_success(self, mock_run):
        """Test successful file formatting with Black."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        result = self.formatter.format_file('/path/to/file.py')
        
        self.assertTrue(result.success)
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        self.assertIn('black', call_args)
        self.assertIn('/path/to/file.py', call_args)
    
    @patch('subprocess.run')
    def test_format_file_with_options(self, mock_run):
        """Test formatting file with custom options."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        options = {'line_length': 120, 'skip_string_normalization': True}
        result = self.formatter.format_file('/path/to/file.py', options)
        
        call_args = mock_run.call_args[0][0]
        self.assertIn('--line-length=120', call_args)
        self.assertIn('--skip-string-normalization', call_args)
    
    @patch('subprocess.run')
    def test_format_directory(self, mock_run):
        """Test formatting entire directory."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        result = self.formatter.format_directory('/path/to/project/')
        
        self.assertTrue(result.success)
        call_args = mock_run.call_args[0][0]
        self.assertIn('/path/to/project/', call_args)
    
    @patch('subprocess.run')
    def test_check_mode(self, mock_run):
        """Test check mode without making changes."""
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="would reformat file.py")
        
        result = self.formatter.check_file('/path/to/file.py')
        
        self.assertFalse(result.success)
        self.assertIn("would reformat", result.output)
        call_args = mock_run.call_args[0][0]
        self.assertIn('--check', call_args)
    
    @patch('subprocess.run')
    def test_format_failure(self, mock_run):
        """Test handling formatting failures."""
        mock_run.return_value = MagicMock(
            returncode=1, 
            stdout="", 
            stderr="error: cannot format file.py: Cannot parse"
        )
        
        result = self.formatter.format_file('/path/to/file.py')
        
        self.assertFalse(result.success)
        self.assertIn("Cannot parse", result.error_message)


class TestIsortFormatter(TestCase):
    """Test cases for isort import formatter."""
    
    def setUp(self):
        self.formatter = IsortFormatter()
    
    @patch('subprocess.run')
    def test_format_imports(self, mock_run):
        """Test formatting imports with isort."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        result = self.formatter.format_file('/path/to/file.py')
        
        self.assertTrue(result.success)
        call_args = mock_run.call_args[0][0]
        self.assertIn('isort', call_args)
    
    @patch('subprocess.run')
    def test_format_with_profile(self, mock_run):
        """Test formatting with specific profile."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        options = {'profile': 'black'}
        result = self.formatter.format_file('/path/to/file.py', options)
        
        call_args = mock_run.call_args[0][0]
        self.assertIn('--profile=black', call_args)
    
    @patch('subprocess.run')
    def test_check_imports(self, mock_run):
        """Test checking import order without changes."""
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")
        
        result = self.formatter.check_file('/path/to/file.py')
        
        call_args = mock_run.call_args[0][0]
        self.assertIn('--check-only', call_args)


class TestCodeFormatter(TestCase):
    """Test cases for combined code formatter."""
    
    def setUp(self):
        self.formatter = CodeFormatter()
    
    @patch('core.code_quality.formatters.BlackFormatter.format_file')
    @patch('core.code_quality.formatters.IsortFormatter.format_file')
    def test_format_file_with_all_formatters(self, mock_isort, mock_black):
        """Test formatting file with all formatters."""
        mock_black.return_value = MagicMock(success=True)
        mock_isort.return_value = MagicMock(success=True)
        
        result = self.formatter.format_file('/path/to/file.py')
        
        self.assertTrue(result.success)
        mock_black.assert_called_once()
        mock_isort.assert_called_once()
    
    @patch('core.code_quality.formatters.BlackFormatter.format_file')
    @patch('core.code_quality.formatters.IsortFormatter.format_file')
    def test_format_failure_stops_chain(self, mock_isort, mock_black):
        """Test that formatter failure stops the chain."""
        mock_black.return_value = MagicMock(success=False, error_message="Black failed")
        
        result = self.formatter.format_file('/path/to/file.py')
        
        self.assertFalse(result.success)
        mock_black.assert_called_once()
        mock_isort.assert_not_called()
    
    def test_get_supported_extensions(self):
        """Test getting supported file extensions."""
        extensions = self.formatter.get_supported_extensions()
        
        self.assertIn('.py', extensions)
        self.assertIn('.pyi', extensions)


class TestRuffLinter(TestCase):
    """Test cases for Ruff linter."""
    
    def setUp(self):
        self.linter = RuffLinter()
    
    @patch('subprocess.run')
    def test_check_file_success(self, mock_run):
        """Test successful linting with Ruff."""
        mock_run.return_value = MagicMock(
            returncode=0, 
            stdout="All checks passed!", 
            stderr=""
        )
        
        result = self.linter.check_file('/path/to/file.py')
        
        self.assertTrue(result.success)
        self.assertEqual(len(result.issues), 0)
    
    @patch('subprocess.run')
    def test_check_file_with_issues(self, mock_run):
        """Test linting file with issues."""
        mock_output = """file.py:10:5: E501 line too long (88 > 79 characters)
file.py:15:1: F401 'os' imported but unused
file.py:20:10: E711 comparison to None should be 'if cond is None:'"""
        
        mock_run.return_value = MagicMock(
            returncode=1, 
            stdout=mock_output, 
            stderr=""
        )
        
        result = self.linter.check_file('/path/to/file.py')
        
        self.assertFalse(result.success)
        self.assertEqual(len(result.issues), 3)
        
        first_issue = result.issues[0]
        self.assertEqual(first_issue.line, 10)
        self.assertEqual(first_issue.column, 5)
        self.assertEqual(first_issue.code, 'E501')
        self.assertIn('line too long', first_issue.message)
    
    @patch('subprocess.run')
    def test_check_with_custom_config(self, mock_run):
        """Test linting with custom configuration."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        config_path = '/path/to/ruff.toml'
        result = self.linter.check_file('/path/to/file.py', config_path=config_path)
        
        call_args = mock_run.call_args[0][0]
        self.assertIn(f'--config={config_path}', call_args)
    
    @patch('subprocess.run')
    def test_fix_issues(self, mock_run):
        """Test fixing issues automatically."""
        mock_run.return_value = MagicMock(returncode=0, stdout="Fixed 3 issues", stderr="")
        
        result = self.linter.fix_file('/path/to/file.py')
        
        self.assertTrue(result.success)
        call_args = mock_run.call_args[0][0]
        self.assertIn('--fix', call_args)


class TestMyPyLinter(TestCase):
    """Test cases for MyPy type checker."""
    
    def setUp(self):
        self.linter = MyPyLinter()
    
    @patch('subprocess.run')
    def test_type_check_success(self, mock_run):
        """Test successful type checking."""
        mock_run.return_value = MagicMock(
            returncode=0, 
            stdout="Success: no issues found", 
            stderr=""
        )
        
        result = self.linter.check_file('/path/to/file.py')
        
        self.assertTrue(result.success)
        self.assertEqual(len(result.issues), 0)
    
    @patch('subprocess.run')
    def test_type_check_with_errors(self, mock_run):
        """Test type checking with errors."""
        mock_output = """file.py:10: error: Incompatible types in assignment (expression has type "str", variable has type "int")
file.py:15: error: Function is missing a return type annotation"""
        
        mock_run.return_value = MagicMock(
            returncode=1, 
            stdout=mock_output, 
            stderr=""
        )
        
        result = self.linter.check_file('/path/to/file.py')
        
        self.assertFalse(result.success)
        self.assertEqual(len(result.issues), 2)
        
        first_issue = result.issues[0]
        self.assertEqual(first_issue.line, 10)
        self.assertIn('Incompatible types', first_issue.message)
    
    @patch('subprocess.run')
    def test_check_with_mypy_config(self, mock_run):
        """Test type checking with mypy configuration."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        result = self.linter.check_file('/path/to/file.py', strict=True)
        
        call_args = mock_run.call_args[0][0]
        self.assertIn('--strict', call_args)


class TestCodeLinter(TestCase):
    """Test cases for combined code linter."""
    
    def setUp(self):
        self.linter = CodeLinter()
    
    @patch('core.code_quality.linters.RuffLinter.check_file')
    @patch('core.code_quality.linters.MyPyLinter.check_file')
    def test_check_with_all_linters(self, mock_mypy, mock_ruff):
        """Test checking file with all linters."""
        mock_ruff.return_value = MagicMock(success=True, issues=[])
        mock_mypy.return_value = MagicMock(success=True, issues=[])
        
        result = self.linter.check_file('/path/to/file.py')
        
        self.assertTrue(result.success)
        mock_ruff.assert_called_once()
        mock_mypy.assert_called_once()
    
    @patch('core.code_quality.linters.RuffLinter.check_file')
    @patch('core.code_quality.linters.MyPyLinter.check_file')
    def test_aggregates_issues_from_all_linters(self, mock_mypy, mock_ruff):
        """Test aggregating issues from all linters."""
        ruff_issue = MagicMock(code='E501', message='Line too long')
        mypy_issue = MagicMock(code='type', message='Type error')
        
        mock_ruff.return_value = MagicMock(success=False, issues=[ruff_issue])
        mock_mypy.return_value = MagicMock(success=False, issues=[mypy_issue])
        
        result = self.linter.check_file('/path/to/file.py')
        
        self.assertFalse(result.success)
        self.assertEqual(len(result.issues), 2)


class TestPreCommitManager(TestCase):
    """Test cases for pre-commit hook manager."""
    
    def setUp(self):
        self.manager = PreCommitManager()
    
    def test_generate_config(self):
        """Test generating pre-commit configuration."""
        config = self.manager.generate_config()
        
        self.assertIn('repos', config)
        self.assertIsInstance(config['repos'], list)
        
        # Check for expected hooks
        hook_ids = []
        for repo in config['repos']:
            for hook in repo.get('hooks', []):
                hook_ids.append(hook['id'])
        
        self.assertIn('black', hook_ids)
        self.assertIn('isort', hook_ids)
        self.assertIn('ruff', hook_ids)
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.dump')
    def test_save_config(self, mock_yaml_dump, mock_file):
        """Test saving pre-commit configuration to file."""
        config = {'repos': []}
        
        self.manager.save_config(config, '/path/to/.pre-commit-config.yaml')
        
        mock_file.assert_called_once_with('/path/to/.pre-commit-config.yaml', 'w')
        mock_yaml_dump.assert_called_once()
    
    @patch('subprocess.run')
    def test_install_hooks(self, mock_run):
        """Test installing pre-commit hooks."""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = self.manager.install_hooks('/path/to/project')
        
        self.assertTrue(result)
        call_args = mock_run.call_args[0][0]
        self.assertIn('pre-commit', call_args)
        self.assertIn('install', call_args)
    
    @patch('subprocess.run')
    def test_run_hooks(self, mock_run):
        """Test running pre-commit hooks."""
        mock_run.return_value = MagicMock(returncode=0, stdout="All hooks passed")
        
        result = self.manager.run_hooks('/path/to/project')
        
        self.assertTrue(result.success)
        call_args = mock_run.call_args[0][0]
        self.assertIn('pre-commit', call_args)
        self.assertIn('run', call_args)


class TestGitHookManager(TestCase):
    """Test cases for Git hook manager."""
    
    def setUp(self):
        self.manager = GitHookManager()
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_install_pre_commit_hook(self, mock_file, mock_exists):
        """Test installing pre-commit Git hook."""
        mock_exists.return_value = True
        
        self.manager.install_pre_commit_hook('/path/to/project')
        
        mock_file.assert_called()
        # Check that the hook script was written
        written_content = ''.join(call.args[0] for call in mock_file().write.call_args_list)
        self.assertIn('#!/bin/sh', written_content)
        self.assertIn('pre-commit', written_content)
    
    @patch('os.chmod')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_hook_is_executable(self, mock_file, mock_exists, mock_chmod):
        """Test that installed hook is executable."""
        mock_exists.return_value = True
        
        self.manager.install_pre_commit_hook('/path/to/project')
        
        mock_chmod.assert_called()
        # Check that executable permissions were set
        chmod_args = mock_chmod.call_args[0]
        self.assertTrue(chmod_args[1] & 0o755)


class TestCodeComplexityAnalyzer(TestCase):
    """Test cases for code complexity analyzer."""
    
    def setUp(self):
        self.analyzer = CodeComplexityAnalyzer()
    
    def test_analyze_simple_function(self):
        """Test analyzing simple function complexity."""
        code = """
def simple_function(x):
    return x + 1
"""
        
        result = self.analyzer.analyze_code(code)
        
        self.assertEqual(result.cyclomatic_complexity, 1)
        self.assertLess(result.cognitive_complexity, 5)
    
    def test_analyze_complex_function(self):
        """Test analyzing complex function."""
        code = """
def complex_function(x, y, z):
    if x > 0:
        if y > 0:
            for i in range(z):
                if i % 2 == 0:
                    try:
                        result = x / y
                    except ZeroDivisionError:
                        result = 0
                else:
                    result = x * y
            return result
        else:
            return x
    else:
        return 0
"""
        
        result = self.analyzer.analyze_code(code)
        
        self.assertGreater(result.cyclomatic_complexity, 5)
        self.assertGreater(result.cognitive_complexity, 10)
    
    @patch('subprocess.run')
    def test_analyze_file_with_radon(self, mock_run):
        """Test analyzing file complexity with radon."""
        mock_output = """file.py:
    F 1:0 simple_function - A (1)
    F 5:0 complex_function - C (8)"""
        
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=mock_output,
            stderr=""
        )
        
        result = self.analyzer.analyze_file('/path/to/file.py')
        
        self.assertEqual(len(result.functions), 2)
        self.assertEqual(result.functions[0].name, 'simple_function')
        self.assertEqual(result.functions[0].complexity, 1)


class TestCoverageAnalyzer(TestCase):
    """Test cases for test coverage analyzer."""
    
    def setUp(self):
        self.analyzer = CoverageAnalyzer()
    
    @patch('subprocess.run')
    def test_run_coverage_analysis(self, mock_run):
        """Test running coverage analysis."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        result = self.analyzer.run_tests_with_coverage('/path/to/project')
        
        self.assertTrue(result.success)
        call_args = mock_run.call_args[0][0]
        self.assertIn('coverage', call_args)
        self.assertIn('run', call_args)
    
    @patch('subprocess.run')
    def test_generate_coverage_report(self, mock_run):
        """Test generating coverage report."""
        mock_output = """Name                 Stmts   Miss  Cover
--------------------------------------------
core/models.py          50      5    90%
core/views.py           30      3    90%
core/utils.py           20      0   100%
--------------------------------------------
TOTAL                  100      8    92%"""
        
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=mock_output,
            stderr=""
        )
        
        result = self.analyzer.generate_report()
        
        self.assertEqual(result.total_coverage, 92.0)
        self.assertEqual(len(result.file_coverage), 3)
    
    @patch('subprocess.run')
    def test_coverage_threshold_check(self, mock_run):
        """Test checking coverage against threshold."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        # Mock coverage data
        with patch.object(self.analyzer, 'get_total_coverage', return_value=85.0):
            result = self.analyzer.check_threshold(90.0)
            
            self.assertFalse(result.meets_threshold)
            self.assertEqual(result.current_coverage, 85.0)
            self.assertEqual(result.required_coverage, 90.0)


class TestSecurityAnalyzer(TestCase):
    """Test cases for security analyzer."""
    
    def setUp(self):
        self.analyzer = SecurityAnalyzer()
    
    @patch('subprocess.run')
    def test_run_bandit_security_scan(self, mock_run):
        """Test running Bandit security scan."""
        mock_output = """{
    "results": [
        {
            "filename": "test.py",
            "line_number": 10,
            "issue_severity": "HIGH",
            "issue_confidence": "HIGH",
            "test_id": "B301",
            "test_name": "blacklist",
            "issue_text": "Use of insecure MD5 hash function."
        }
    ]
}"""
        
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout=mock_output,
            stderr=""
        )
        
        result = self.analyzer.scan_file('/path/to/file.py')
        
        self.assertFalse(result.success)
        self.assertEqual(len(result.issues), 1)
        
        issue = result.issues[0]
        self.assertEqual(issue.severity, 'HIGH')
        self.assertEqual(issue.test_id, 'B301')
        self.assertIn('MD5', issue.description)
    
    @patch('subprocess.run')
    def test_run_safety_dependency_check(self, mock_run):
        """Test running Safety dependency vulnerability check."""
        mock_output = """[
    {
        "advisory": "Vulnerability in package xyz",
        "cve": "CVE-2023-1234",
        "id": "12345",
        "specs": ["<1.2.3"],
        "v": "<1.2.3"
    }
]"""
        
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout=mock_output,
            stderr=""
        )
        
        result = self.analyzer.check_dependencies('/path/to/requirements.txt')
        
        self.assertFalse(result.success)
        self.assertEqual(len(result.vulnerabilities), 1)
        
        vuln = result.vulnerabilities[0]
        self.assertEqual(vuln.cve, 'CVE-2023-1234')
        self.assertIn('xyz', vuln.advisory)


@pytest.mark.integration
class TestCodeQualityIntegration(TestCase):
    """Integration tests for code quality tools."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test.py')
        
        # Create a test Python file
        with open(self.test_file, 'w') as f:
            f.write("""
import os
import sys

def test_function(x,y):
    if x>0:
        return x+y
    else:
        return 0

class TestClass:
    def __init__(self):
        pass
    
    def method(self):
        return "test"
""")
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_full_code_quality_pipeline(self):
        """Test running complete code quality pipeline."""
        formatter = CodeFormatter()
        linter = CodeLinter()
        
        # Format the code
        format_result = formatter.format_file(self.test_file)
        
        # Then lint it
        lint_result = linter.check_file(self.test_file)
        
        # Both should complete without errors
        self.assertIsNotNone(format_result)
        self.assertIsNotNone(lint_result)
    
    def test_pre_commit_workflow(self):
        """Test pre-commit workflow simulation."""
        manager = PreCommitManager()
        
        # Generate configuration
        config = manager.generate_config()
        self.assertIn('repos', config)
        
        # This would normally install and run hooks
        # but we'll just verify the configuration is valid
        self.assertIsInstance(config['repos'], list)
        self.assertGreater(len(config['repos']), 0)
