"""Unit tests for logging setup."""

import logging

from docforge.logging.setup import TRACE, get_logger, setup_logging


def test_trace_level_registered():
    assert logging.getLevelName(TRACE) == "TRACE"
    assert TRACE == 5


def test_get_logger_returns_bound_logger():
    logger = get_logger("test.module")
    assert logger is not None


def test_setup_logging_human_format():
    setup_logging(level="WARNING", fmt="human")
    root = logging.getLogger()
    assert root.level == logging.WARNING


def test_setup_logging_json_format():
    setup_logging(level="ERROR", fmt="json")
    root = logging.getLogger()
    assert root.level == logging.ERROR


def test_setup_logging_trace_level():
    setup_logging(level="TRACE", fmt="human")
    root = logging.getLogger()
    assert root.level == TRACE
