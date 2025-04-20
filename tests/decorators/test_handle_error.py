import pytest
import click
from click.testing import CliRunner

from oarc_utils.decorators import handle_error, get_error
from oarc_utils.errors import (
    OARCError,
    AuthenticationError,
    BuildError,
    ConfigurationError,
    CrawlerOpError,
    DataExtractionError,
    NetworkError,
    PublishError,
    ResourceNotFoundError,
    TransportError, # Note: Not an OARCError subclass
    MCPError,       # Note: Not an OARCError subclass
)


# --- Test Click Commands ---

# Define all OarcError subclasses to test
OARC_ERRORS_TO_TEST = {
    'oarc_error': (OARCError, "Generic OARC error."),
    'auth_error': (AuthenticationError, "Authentication failed."),
    'build_error': (BuildError, "Build process failed."),
    'config_error': (ConfigurationError, "Invalid configuration."),
    'crawler_op_error': (CrawlerOpError, "Crawler operation failed."),
    'data_extraction_error': (DataExtractionError, "Data extraction failed."),
    'network_error': (NetworkError, "Network connection failed."),
    'publish_error': (PublishError, "Publishing failed."),
    'resource_not_found_error': (ResourceNotFoundError, "Resource not found."),
    # MCPError and TransportError are not OarcError subclasses, test separately if needed
}

# Add new modes to the Choice list
# Add 'transport_error'
command_modes = ['success', 'unexpected', 'usage_error', 'transport_error'] + list(OARC_ERRORS_TO_TEST.keys())

@click.command()
@click.option('--mode', required=True, type=click.Choice(command_modes))
@click.option('--verbose', is_flag=True)
@handle_error
def command_under_test(mode, verbose):
    """A command function wrapped by handle_error for testing."""
    click.echo(f"Executing mode: {mode}, Verbose: {verbose}")

    if mode == 'success':
        click.echo("Success message")
        return 0 # Explicit success code
    elif mode == 'unexpected':
        raise ValueError("An unexpected standard error.")
    elif mode == 'usage_error':
        raise click.exceptions.UsageError("Simulated usage error.")
    elif mode == 'transport_error': # Add case for TransportError
        raise TransportError("MCP transport failed.")
    elif mode in OARC_ERRORS_TO_TEST:
        error_cls, error_msg = OARC_ERRORS_TO_TEST[mode]
        raise error_cls(error_msg)

    # Should not be reached in error modes
    return 99

# --- Pytest Fixtures ---

@pytest.fixture
def runner():
    """Click CliRunner fixture."""
    return CliRunner()

# --- Tests for @handle_error decorator ---

def test_handle_error_success(runner):
    """Test successful command execution."""
    result = runner.invoke(command_under_test, ['--mode=success'])
    assert result.exit_code == 0
    assert "Executing mode: success" in result.output
    assert "Success message" in result.output
    assert "ERROR" not in result.output

@pytest.mark.parametrize("mode", OARC_ERRORS_TO_TEST.keys())
def test_handle_error_all_oarc_subclasses(runner, mode):
    """Test handling of all defined OarcError subclasses."""
    error_cls, expected_msg = OARC_ERRORS_TO_TEST[mode]
    expected_code = getattr(error_cls, 'exit_code', 1) # Get code from class or default

    result = runner.invoke(command_under_test, [f'--mode={mode}'])

    assert result.exit_code == expected_code
    assert "Executing mode:" in result.output # Check it started execution
    assert "ERROR" in result.output # Check the error box title
    assert f"➤ {expected_msg}" in result.output
    assert "Traceback" not in result.output # Default, verbose=False

def test_handle_error_unexpected_exception(runner):
    """Test handling of non-OarcError exceptions."""
    result = runner.invoke(command_under_test, ['--mode=unexpected'])
    assert result.exit_code == 1 # Default exit code for unexpected
    assert "Executing mode:" in result.output
    assert "UNEXPECTED ERROR" in result.output
    assert "➤ ValueError: An unexpected standard error." in result.output
    assert "Traceback" not in result.output

def test_handle_error_unexpected_exception_verbose(runner):
    """Test handling of non-OarcError exceptions with verbose=True."""
    result = runner.invoke(command_under_test, ['--mode=unexpected', '--verbose'])
    assert result.exit_code == 1
    assert "Executing mode:" in result.output
    assert "UNEXPECTED ERROR" in result.output
    assert "➤ ValueError: An unexpected standard error." in result.output
    assert "Traceback (most recent call last):" in result.output # Check for traceback

def test_handle_error_oarc_error_verbose(runner):
    """Test handling of OarcError with verbose=True."""
    # Use one specific error for the verbose test
    mode = 'config_error'
    error_cls, expected_msg = OARC_ERRORS_TO_TEST[mode]
    expected_code = getattr(error_cls, 'exit_code', 1)

    result = runner.invoke(command_under_test, [f'--mode={mode}', '--verbose'])
    assert result.exit_code == expected_code
    assert "Executing mode:" in result.output
    assert "ERROR" in result.output
    assert f"➤ {expected_msg}" in result.output
    # Traceback should be printed by get_error via click.secho in verbose mode
    assert "Traceback (most recent call last):" in result.output
    assert f"oarc_utils.errors.oarc_crawlers_errors.{error_cls.__name__}: {expected_msg}" in result.output

def test_handle_error_transport_error(runner):
    """Test handling of TransportError (which is not an OarcError)."""
    result = runner.invoke(command_under_test, ['--mode=transport_error'])
    assert result.exit_code == 1 # Should use default exit code 1
    assert "Executing mode:" in result.output
    assert "UNEXPECTED ERROR" in result.output # Should be treated as unexpected
    assert "➤ TransportError: MCP transport failed." in result.output
    assert "Traceback" not in result.output

def test_handle_error_transport_error_verbose(runner):
    """Test handling of TransportError with verbose=True."""
    result = runner.invoke(command_under_test, ['--mode=transport_error', '--verbose'])
    assert result.exit_code == 1
    assert "Executing mode:" in result.output
    assert "UNEXPECTED ERROR" in result.output
    assert "➤ TransportError: MCP transport failed." in result.output
    assert "Traceback (most recent call last):" in result.output # Check for traceback
    assert "oarc_utils.errors.oarc_crawlers_errors.TransportError: MCP transport failed." in result.output

def test_handle_error_click_usage_error(runner):
    """Test handling of Click UsageError (simulated)."""
    # Note: Click itself usually catches bad args before the function runs.
    # Here we test the decorator's explicit catch block.
    result = runner.invoke(command_under_test, ['--mode=usage_error'])
    assert result.exit_code == 2
    assert "Error: Simulated usage error." in result.output

def test_handle_error_click_no_such_command(runner):
    """Test the specific 'No such command' UsageError handling."""
    @click.group()
    def cli_group():
        pass

    @cli_group.command()
    @handle_error
    def existing_command():
        click.echo("Should not run")

    try:
        ctx = cli_group.make_context(info_name='cli', args=['nonexistent'])
        with ctx:
            pass
    except click.exceptions.UsageError as e:
        @handle_error
        def dummy_func():
            raise e

        exit_code = dummy_func()
        assert exit_code == 2
        assert "No such command 'nonexistent'" in str(e)

def test_handle_error_click_bad_parameter(runner):
    """Test UsageError from Click itself due to bad parameters."""
    result = runner.invoke(command_under_test, ['--mode=invalid_choice'])
    assert result.exit_code == 2 # Click's default for usage errors
    # When CliRunner catches UsageError, result.exception becomes SystemExit(2)
    assert "Invalid value for '--mode'" in result.output # Click's error message

# --- Tests for internal helper functions (Optional, as decorator tests cover them) ---

def test_get_error_structure():
    """Test the structure returned by get_error."""
    err = ValueError("Test message")
    result = get_error(err, verbose=False)
    assert result == {
        "success": False,
        "error": "Test message",
        "error_type": "ValueError",
        "exit_code": 1 # Default for non-OarcError
    }

    oarc_err = NetworkError("Connection timeout")
    result_oarc = get_error(oarc_err, verbose=False)
    assert result_oarc == {
        "success": False,
        "error": "Connection timeout",
        "error_type": "NetworkError",
        "exit_code": 2 # Specific code for NetworkError
    }

    # Test MCPError (not an OarcError)
    mcp_err = MCPError("MCP communication failed")
    result_mcp = get_error(mcp_err, verbose=False)
    assert result_mcp == {
        "success": False,
        "error": "MCP communication failed",
        "error_type": "MCPError",
        "exit_code": 1 # Default exit code
    }


def test_get_error_verbose_includes_traceback():
    """Test get_error includes traceback when verbose=True."""
    try:
        raise BuildError("Compilation failed")
    except BuildError as e:
        result = get_error(e, verbose=True)
        assert result["exit_code"] == 7
        assert "traceback" in result
        assert "Traceback (most recent call last):" in result["traceback"]
        assert "oarc_utils.errors.oarc_crawlers_errors.BuildError: Compilation failed" in result[
            "traceback"]
