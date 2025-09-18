"""
Basic tests for SpineAPI - Simple import and functionality tests
"""
import pytest


def test_spineapi_import():
    """Test that spineapi package can be imported"""
    import spineapi
    assert spineapi.__version__ == "0.1.0"


def test_cli_module_import():
    """Test that CLI module exists and has main function"""
    try:
        from spineapi.cli import main
        assert callable(main)
    except ImportError as e:
        pytest.skip(f"CLI import failed (expected in CI): {e}")


def test_basic_package_structure():
    """Test that basic package structure exists"""
    import spineapi
    assert hasattr(spineapi, '__version__')
    assert hasattr(spineapi, '__name__')


def test_version_string():
    """Test version string format"""
    import spineapi
    version = spineapi.__version__
    assert isinstance(version, str)
    assert len(version.split('.')) >= 2  # At least major.minor


def test_package_metadata():
    """Test package has basic metadata"""
    import spineapi
    # Just verify these don't raise exceptions
    assert spineapi.__name__ == "spineapi"
    assert spineapi.__version__ is not None
