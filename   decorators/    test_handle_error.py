def test_handle_error_oarc_error_verbose(runner):
    mode = 'config_error'
    error_cls, expected_msg = OARC_ERRORS_TO_TEST[mode]
    expected_code = getattr(error_cls, 'exit_code', 1)

    result = runner.invoke(command_under_test, [f'--mode={mode}', '--verbose'])
    assert result.exit_code == expected_code
    assert "Executing mode:" in result.output
    assert "ERROR" in result.output
    assert f"➤ {expected_msg}" in result.output
    assert "Traceback (most recent call last):" in result.output
    assert f"oarc_utils.errors.oarc_crawlers_errors.{error_cls.__name__}: {expected_msg}" in result.output

def test_handle_error_transport_error_verbose(runner):
    result = runner.invoke(command_under_test, ['--mode=transport_error', '--verbose'])
    assert result.exit_code == 1
    assert "Executing mode:" in result.output
    assert "UNEXPECTED ERROR" in result.output
    assert "➤ TransportError: MCP transport failed." in result.output
    assert "Traceback (most recent call last):" in result.output
    assert "oarc_utils.errors.oarc_crawlers_errors.TransportError: MCP transport failed." in result.output

def test_get_error_verbose_includes_traceback():
    try:
        raise BuildError("Compilation failed")
    except BuildError as e:
        result = get_error(e, verbose=True)
        assert result["exit_code"] == 7
        assert "traceback" in result
        assert "Traceback (most recent call last):" in result["traceback"]
        assert "oarc_utils.errors.oarc_crawlers_errors.BuildError: Compilation failed" in result["traceback"]