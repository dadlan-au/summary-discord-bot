from pathlib import Path
from typing import List

from dpn_pyutils.file import read_file_text
from jinja2 import BaseLoader, Environment


def render_template(template_file: Path, **kwargs) -> str:
    """
    Renders a list of channels and threads into a template string
    """

    environment = Environment(loader=BaseLoader(), autoescape=True)

    tpl = environment.from_string(
        read_file_text(template_file),
        globals=kwargs,
    )

    return tpl.render()


def split_rendered_text_max_length(rendered_text: str, max_length: int) -> List[str]:
    """
    Splits a rendered text based on maximum length, being careful to preserve URLs
    """

    lines = rendered_text.split("\n")
    result = []
    current_text = ""

    for line in lines:
        if line.strip():
            # +1 is to account for a newline character
            if len(current_text) + len(line) + 1 > max_length:
                if current_text:
                    result.append(current_text)
                current_text = line
            else:
                current_text += ("\n" if current_text else "") + line

    if current_text:
        result.append(current_text)

    return result
