from ..base import Node, NodeError, register


@register
class MessagePrepare(Node):
    type = "message_prep"
    display_name = "Message Prepare"
    category = "action"
    inputs = ["in"]
    outputs = ["out"]
    params_schema = {
        "channel": {
            "type": "enum",
            "options": ["email", "telegram", "plain"],
            "default": "email",
        },
        "template": {
            "type": "string",
            "widget": "textarea",
            "default": "Subject: {label}\n\n{summary}\n\n— Auto-generated",
        },
    }

    def execute(self, inputs, config, log):
        template = config.get("template") or "{summary}"
        channel = config.get("channel") or "plain"
        fields = {
            "label": inputs.get("label", ""),
            "summary": inputs.get("summary", ""),
            "text": inputs.get("text", ""),
            "confidence": inputs.get("confidence", ""),
        }
        try:
            message = template.format(**fields)
        except KeyError as exc:
            raise NodeError(f"Message Prepare: template references unknown field {exc}.") from exc
        log(f"message_prep: channel={channel}, {len(message)} chars")
        return {"message": message, "channel": channel}
