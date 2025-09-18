"""
Basic tests for SpineAPI CLI
"""
import pytest
from spineapi.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_version_command():
    """Test version command works"""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "SpineAPI" in result.stdout


def test_help_command():
    """Test help command works"""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "SpineAPI" in result.stdout


def test_cli_import():
    """Test that CLI module can be imported"""
    from spineapi.cli import main
    assert callable(main)


def test_parser_import():
    """Test that parser module can be imported"""
    from spineapi.parsers.openapi import OpenAPIParser
    assert OpenAPIParser is not None


def test_generator_import():
    """Test that generator module can be imported"""
    from spineapi.generators.main import CodeGenerator
    assert CodeGenerator is not None
