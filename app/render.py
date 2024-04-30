from pathlib import Path
from typing import List

from dpn_pyutils.file import read_file_text
from jinja2 import BaseLoader, Environment


def render_template(template_file: Path, channels: List, threads: List) -> str:
    """
    Renders a list of channels and threads into a template string
    """

    environment = Environment(loader=BaseLoader(), autoescape=True)

    tpl = environment.from_string(
        read_file_text(template_file),
        globals={"channels": channels, "threads": threads},
    )

    return tpl.render()


