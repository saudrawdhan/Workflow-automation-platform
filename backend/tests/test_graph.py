import unittest

from app.engine import topological_sort, validate
from app.engine.graph import CycleError, ValidationError


class GraphTests(unittest.TestCase):
    def test_linear_order(self):
        nodes = [
            {"id": "a", "type": "text_input", "config": {"text": "hi"}},
            {"id": "b", "type": "output"},
        ]
        edges = [{"source": "a", "target": "b"}]
        self.assertEqual(topological_sort(nodes, edges), ["a", "b"])

    def test_cycle_detected(self):
        nodes = [{"id": "a", "type": "summarize"}, {"id": "b", "type": "summarize"}]
        edges = [{"source": "a", "target": "b"}, {"source": "b", "target": "a"}]
        with self.assertRaises(CycleError):
            topological_sort(nodes, edges)

    def test_missing_start_or_end_is_invalid(self):
        nodes = [{"id": "a", "type": "summarize"}, {"id": "b", "type": "summarize"}]
        edges = [{"source": "a", "target": "b"}, {"source": "b", "target": "a"}]
        with self.assertRaises(ValidationError):
            validate(nodes, edges)

    def test_unknown_node_type_is_invalid(self):
        with self.assertRaises(ValidationError):
            validate([{"id": "a", "type": "does_not_exist"}], [])


if __name__ == "__main__":
    unittest.main()
