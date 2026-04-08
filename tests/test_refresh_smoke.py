import json
import tempfile
import unittest
from pathlib import Path

import refresh_dashboard as rd


class RefreshSmokeTests(unittest.TestCase):
    def test_parse_thefor_supports_dict_payload(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "habits-test.json"
            p.write_text(json.dumps({
                "habits": [
                    {
                        "title": "Trading Study",
                        "checkedDays": [{"day": "2026-04-06T00:00:00Z"}],
                    }
                ]
            }), encoding="utf-8")

            report = {}
            day_map = rd.parse_thefor(p, run_report=report)
            self.assertIn("2026-04-06", day_map)
            self.assertEqual(day_map["2026-04-06"]["Trading Study"], 1)

    def test_load_latest_payload_rejects_invalid_shape(self):
        with tempfile.TemporaryDirectory() as td:
            latest = Path(td) / "latest.json"
            latest.write_text(json.dumps({"daily": []}), encoding="utf-8")
            old = rd.LATEST_JSON
            try:
                rd.LATEST_JSON = latest
                self.assertIsNone(rd.load_latest_payload())
            finally:
                rd.LATEST_JSON = old


if __name__ == "__main__":
    unittest.main()
