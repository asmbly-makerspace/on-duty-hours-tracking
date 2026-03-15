# pylint: disable=missing-docstring
import datetime
import sys
from unittest.mock import MagicMock

import pytest

# config.py is gitignored (holds real credentials); stub it so google_services can import
sys.modules["config"] = MagicMock()

from helpers.google_services import SheetsOperations


def build_sheets_op(values, sheet="Sheet1"):
    sheet_ops = SheetsOperations(MagicMock(), "Test", "123")
    mock_sheet = MagicMock()
    mock_sheet.get().execute.return_value = {
        "sheets": [{"properties": {"title": sheet}}]
    }
    mock_sheet.values().get().execute.return_value = (
        {"values": values} if values else {}
    )
    sheet_ops.sheet = mock_sheet
    return sheet_ops, mock_sheet


@pytest.mark.parametrize(
    "time_in, clock_in, expected",
    [
        ("3:00 PM", True, datetime.datetime(2026, 3, 13, 15, 0)),
        ("12:00 AM", True, datetime.datetime(2026, 3, 13, 0, 0)),
        ("5:00 PM", False, datetime.datetime(2026, 3, 13, 17, 0)),
        ("15:00:00", True, datetime.datetime(2026, 3, 13, 15, 0)),
        ("3:00:00 PM", True, datetime.datetime(2026, 3, 13, 15, 0)),
    ],
)
def test_time_formats(time_in, clock_in, expected):
    sheet_ops, _ = build_sheets_op([["03/13/2026", time_in, "5:00 PM"]])
    assert sheet_ops.get_last_entry_datetime(clock_in=clock_in) == expected


def test_unparseable_time_raises():
    sheet_ops, _ = build_sheets_op([["03/13/2026", "invalid", "5:00 PM"]])
    with pytest.raises(ValueError, match="Unable to parse time '03/13/2026' 'invalid'"):
        sheet_ops.get_last_entry_datetime(clock_in=True)


def test_renamed_sheet():
    sheet_ops, mock_sheet = build_sheets_op(
        [["03/13/2026", "3:00 PM", "5:00 PM"]], sheet="ODV Log"
    )
    sheet_ops.get_last_entry_datetime()
    assert mock_sheet.values().get.call_args.kwargs["range"] == "'ODV Log'!A3:C"
