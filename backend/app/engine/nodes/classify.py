from ..base import Node, NodeError, register
from ..llm.provider import classify as provider_classify


@register
class Classify(Node):
    type = "classify"
    display_name = "Classify"
    category = "action"
    inputs = ["in"]
    outputs = ["out"]
    params_schema = {
        "labels": {
            "type": "list[string]",
            "default": ["complaint", "request", "praise", "other"],
        }
    }

    def execute(self, inputs, config, log):
        text = inputs.get("summary") or inputs.get("text")
        if not text:
            raise NodeError("Classify: no input text.")
        labels = config.get("labels") or []
        if not labels:
            raise NodeError("Classify: labels list is empty.")
        label, confidence, backend = provider_classify(text, labels)
        log(f"classify: provider={backend}, label={label} ({confidence:.2f})")
        return {"label": label, "confidence": confidence, "text": text}
