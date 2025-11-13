import pytest
from unittest.mock import patch, MagicMock

import types

def dummy_coro():
    async def _coro():
        return "done"
    return _coro()

def test_run_daily_crawl_calls_crawl_book_urls():
    with patch("scheduler.tasks.crawl_book_urls", return_value=dummy_coro()) as mock_crawl:
        with patch("scheduler.tasks.asyncio.run") as mock_run:
            from scheduler.tasks import run_daily_crawl
            run_daily_crawl()
            mock_run.assert_called_once()
            # Optionally check that the argument is a coroutine
            assert isinstance(mock_run.call_args[0][0], types.CoroutineType)

def test_run_daily_change_report_calls_generate_daily_change_report_and_prints():
    with patch("scheduler.tasks.generate_daily_change_report") as mock_report:
        mock_report.return_value = ("report.json", "report.csv")
        with patch("builtins.print") as mock_print:
            from scheduler.tasks import run_daily_change_report
            run_daily_change_report()
            mock_report.assert_called_once()
            mock_print.assert_any_call("Daily report generated: report.json, report.csv")

def test_run_daily_change_report_handles_none_files():
    with patch("scheduler.tasks.generate_daily_change_report") as mock_report:
        mock_report.return_value = (None, None)
        with patch("builtins.print") as mock_print:
            from scheduler.tasks import run_daily_change_report
            run_daily_change_report()
            mock_report.assert_called_once()
            mock_print.assert_not_called()