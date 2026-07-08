from ..base import Node, NodeError, register
from ..llm.provider import summarize as provider_summarize


@register
class Summarize(Node):
    type = "summarize"
    display_name = "Summarize"
    category = "action"
    inputs = ["in"]
    outputs = ["out"]
    params_schema = {"max_sentences": {"type": "integer", "default": 3}}

    def execute(self, inputs, config, log):
        text = inputs.get("text")
        if not text:
            raise NodeError("Summarize: no input text on port 'in'.")
        max_sentences = int(config.get("max_sentences") or 3)
        summary, backend = provider_summarize(text, max_sentences)
        log(f"summarize: provider={backend}, {len(text)} -> {len(summary)} chars")
        return {"text": text, "summary": summary}
