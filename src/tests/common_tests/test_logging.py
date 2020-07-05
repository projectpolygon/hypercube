import pytest
import sys
from common.logging import Logger, LogLevel


def log_each(logger: Logger):
    logger.log_error('error msg')
    logger.log_warn('warn msg')
    logger.log_info('info blue msg')
    logger.log_success('success msg')
    logger.log_debug('debug msg')
    logger.log_trace('trace msg')


def test_log_level_trace(capsys):
    # Arrange
    expected_included = ["trace", "debug", "success", "info", "warn", "error"]
    logger = Logger(LogLevel.TRACE)
    # Act
    log_each(logger)
    captured = capsys.readouterr()
    # Assert
    for msg in expected_included:
        assert msg in captured.out


def test_log_level_debug(capsys):
    # Arrange
    expected_included = ["debug", "success", "info", "warn", "error"]
    expected_excluded = ["trace"]
    logger = Logger(LogLevel.DEBUG)
    # Act
    log_each(logger)
    captured = capsys.readouterr()
    # Assert
    for msg in expected_included:
        assert msg in captured.out
    for msg in expected_excluded:
        assert msg not in captured.out


def test_log_level_info(capsys):
    # Arrange
    expected_included = ["success", "info", "warn", "error"]
    expected_excluded = ["debug", "trace"]
    logger = Logger(LogLevel.INFO)
    # Act
    log_each(logger)
    captured = capsys.readouterr()
    # Assert
    for msg in expected_included:
        assert msg in captured.out
    for msg in expected_excluded:
        assert msg not in captured.out


def test_log_level_warn(capsys):
    # Arrange
    expected_included = ["warn", "error"]
    expected_excluded = ["success", "info", "debug", "trace"]
    logger = Logger(LogLevel.WARN)
    # Act
    log_each(logger)
    captured = capsys.readouterr()
    # Assert
    for msg in expected_included:
        assert msg in captured.out
    for msg in expected_excluded:
        assert msg not in captured.out


def test_log_level_error(capsys):
    # Arrange
    expected_included = ["error"]
    expected_excluded = ["warn", "success", "info", "debug", "trace"]
    logger = Logger(LogLevel.ERROR)
    # Act
    log_each(logger)
    captured = capsys.readouterr()
    # Assert
    for msg in expected_included:
        assert msg in captured.out
    for msg in expected_excluded:
        assert msg not in captured.out


def test_print_sameline(capsys):
    # Arrange
    logger = Logger()
    # Act
    logger.print_sameline("hello")
    logger.print_sameline("world")
    captured = capsys.readouterr()
    # Assert
    assert captured.out == "\rhello\rworld"
