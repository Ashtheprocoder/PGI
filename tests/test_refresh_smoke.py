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

<<<<<<< ours
<<<<<<< ours
=======
=======
>>>>>>> theirs
    def test_build_mvp_overview_empty_inputs(self):
        mvp = rd.build_mvp_overview([], [], {"projects": [], "open_tasks": [], "connected": False}, 0)
        self.assertEqual(mvp["unified_model_version"], 1)
        self.assertEqual(mvp["tasks_overview"]["open_total"], 0)
        self.assertEqual(mvp["weekly_review"]["win_rate"], 0.0)

<<<<<<< ours
>>>>>>> theirs
=======
    def test_generate_execution_insights_adds_execution_block(self):
        daily = [
            {
                "date": "2026-04-01",
                "agg": 5,
                "habits": {h: 1 for h in rd.HABIT_NAMES},
                "streaks": {h: 1 for h in rd.HABIT_NAMES},
            },
            {
                "date": "2026-04-02",
                "agg": 0,
                "habits": {h: 0 for h in rd.HABIT_NAMES},
                "streaks": {h: 0 for h in rd.HABIT_NAMES},
            },
        ]
        out = rd.generate_execution_insights(daily)
        self.assertIn("execution", out[0])
        self.assertIn("missed_high_value", out[1]["execution"])
        self.assertIsInstance(out[1]["execution"]["efficiency"], float)

>>>>>>> theirs

if __name__ == "__main__":
    unittest.main()
