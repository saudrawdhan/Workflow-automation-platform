import os

from ..base import Node, NodeError, register

_TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".log", ".json", ""}


@register
class FileInput(Node):
    type = "file_input"
    display_name = "File Input"
    category = "source"
    inputs = []
    outputs = ["out"]
    params_schema = {
        "path": {
            "type": "string",
            "required": True,
            "help": "Server path of an uploaded file (.txt / .md / .csv / .pdf).",
        }
    }

    def execute(self, inputs, config, log):
        path = config.get("path")
        if not path or not os.path.isfile(path):
            raise NodeError(f"File Input: file not found ({path!r}).")

        extension = os.path.splitext(path)[1].lower()
        if extension == ".pdf":
            text = self._read_pdf(path)
        elif extension in _TEXT_EXTENSIONS:
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                text = handle.read()
        else:
            raise NodeError(f"File Input: unsupported file type {extension!r}.")

        text = text.strip()
        if not text:
            raise NodeError("File Input: file has no readable text.")
        log(f"file_input: {os.path.basename(path)} -> {len(text)} chars")
        return {"text": text, "filename": os.path.basename(path)}

    @staticmethod
    def _read_pdf(path):
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise NodeError("File Input: PDF support requires the 'pypdf' package.") from exc
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
