from ..base import Node, NodeError, register


@register
class Output(Node):
    type = "output"
    display_name = "Final Output"
    category = "sink"
    inputs = ["in"]
    outputs = []
    params_schema = {}

    def execute(self, inputs, config, log):
        if not inputs:
            raise NodeError("Final Output: no input received.")
        result = (
            inputs.get("message")
            or inputs.get("summary")
            or inputs.get("text")
            or inputs
        )
        log("output: captured final result")
        return {"result": result}
