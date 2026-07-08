from ..base import Node, NodeError, register


@register
class TextInput(Node):
    type = "text_input"
    display_name = "Text Input"
    category = "source"
    inputs = []
    outputs = ["out"]
    params_schema = {"text": {"type": "string", "widget": "textarea", "required": True}}

    def execute(self, inputs, config, log):
        text = (config.get("text") or "").strip()
        if not text:
            raise NodeError("Text Input: text is empty.")
        log(f"text_input: {len(text)} chars")
        return {"text": text}
