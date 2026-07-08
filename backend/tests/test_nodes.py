import unittest

from app.engine import NODE_REGISTRY, NodeError


def _run(node_type, inputs, config):
    logs = []
    output = NODE_REGISTRY[node_type].execute(inputs, config, logs.append)
    return output, logs


class NodeTests(unittest.TestCase):
    def test_text_input(self):
        output, _ = _run("text_input", {}, {"text": "hello world"})
        self.assertEqual(output["text"], "hello world")

    def test_text_input_empty_raises(self):
        with self.assertRaises(NodeError):
            _run("text_input", {}, {"text": "   "})

    def test_summarize_mock(self):
        output, _ = _run("summarize", {"text": "One. Two. Three. Four."}, {"max_sentences": 2})
        self.assertEqual(output["summary"], "One. Two.")

    def test_classify_mock_keyword(self):
        output, _ = _run(
            "classify",
            {"text": "I want a refund, it arrived damaged"},
            {"labels": ["complaint", "praise", "other"]},
        )
        self.assertEqual(output["label"], "complaint")

    def test_classify_empty_labels_raises(self):
        with self.assertRaises(NodeError):
            _run("classify", {"text": "hi"}, {"labels": []})

    def test_message_prep_fills_template(self):
        output, _ = _run(
            "message_prep",
            {"label": "complaint", "summary": "late and damaged"},
            {"template": "Subject: {label}\n\n{summary}", "channel": "email"},
        )
        self.assertIn("complaint", output["message"])
        self.assertIn("late and damaged", output["message"])

    def test_message_prep_unknown_field_raises(self):
        with self.assertRaises(NodeError):
            _run("message_prep", {}, {"template": "{does_not_exist}"})


if __name__ == "__main__":
    unittest.main()
