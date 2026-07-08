import unittest

from app.engine import run

DEMO = {
    "id": "wf_demo",
    "nodes": [
        {
            "id": "n1",
            "type": "text_input",
            "config": {"text": "Delivery was two days late and the box was damaged. Please refund."},
        },
        {"id": "n2", "type": "summarize", "config": {"max_sentences": 2}},
        {
            "id": "n3",
            "type": "classify",
            "config": {"labels": ["complaint", "request", "praise", "other"]},
        },
        {
            "id": "n4",
            "type": "message_prep",
            "config": {"template": "Subject: {label}\n\n{summary}", "channel": "email"},
        },
        {"id": "n5", "type": "output", "config": {}},
    ],
    "edges": [
        {"source": "n1", "target": "n2"},
        {"source": "n2", "target": "n3"},
        {"source": "n3", "target": "n4"},
        {"source": "n4", "target": "n5"},
    ],
}


class RunnerTests(unittest.TestCase):
    def test_full_run_succeeds(self):
        result = run(DEMO)
        self.assertEqual(result["status"], "success")
        statuses = {r["node_id"]: r["status"] for r in result["node_runs"]}
        self.assertTrue(all(status == "success" for status in statuses.values()))
        message = next(r for r in result["node_runs"] if r["node_id"] == "n4")["output"]["message"]
        self.assertIn("complaint", message)          # label reached message_prep
        self.assertIn("Delivery", message)           # summary accumulated through classify

    def test_error_skips_downstream(self):
        broken = {
            **DEMO,
            "nodes": [
                node if node["id"] != "n3" else {**node, "config": {"labels": []}}
                for node in DEMO["nodes"]
            ],
        }
        result = run(broken)
        statuses = {r["node_id"]: r["status"] for r in result["node_runs"]}
        self.assertEqual(result["status"], "error")
        self.assertEqual(statuses["n1"], "success")
        self.assertEqual(statuses["n3"], "error")
        self.assertEqual(statuses["n4"], "skipped")
        self.assertEqual(statuses["n5"], "skipped")


if __name__ == "__main__":
    unittest.main()
