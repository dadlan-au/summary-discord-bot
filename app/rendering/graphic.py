import secrets
from pathlib import Path
from typing import Dict, List

from config import get_config
from dpn_pyutils.file import save_file_text
from render import render_template
from rendering.browser import (
    generate_screenshot_animation,
    generate_screenshot_animation_key_frames,
    generate_screenshot_file,
)

config = get_config()

# Since secrets uses hex, the length will be double
RANDOM_NAME_LEN = 4
EVENTS_PER_PAGE = 7


def create_image_tix(summary_data: Dict, screenshot_file: Path | None = None) -> Path:
    """
    Renders the table of events to an image. Returns the path to the image file.
    """

    rendering_context = Path(config.RENDER_CONTEXT)
    if not rendering_context.exists():
        raise ValueError(f"Rendering context directory not found: {rendering_context}")

    rendered_html_path = Path(
        rendering_context, f"{secrets.token_hex(RANDOM_NAME_LEN)}.html"
    )

    if screenshot_file is None:
        screenshot_file = Path(
            rendering_context, f"{secrets.token_hex(RANDOM_NAME_LEN)}.png"
        )

    rendered_template = render_template(
        Path(config.RENDER_TIX_TEMPLATE_GRAPHIC_FILE), **summary_data
    )

    save_file_text(rendered_html_path, rendered_template, overwrite=True)

    generate_screenshot_file(rendered_html_path, screenshot_file)

    rendered_html_path.unlink()

    return screenshot_file


def create_image_tix_animated(
    summary_data: Dict, screenshot_animation_file: Path | None = None
) -> Path:
    """
    Renders a table of events into an animated image. Returns the path to the image file.
    """

    rendering_context = Path(config.RENDER_CONTEXT)
    if not rendering_context.exists():
        raise ValueError(f"Rendering context directory not found: {rendering_context}")

    rendered_html_path = Path(
        rendering_context, f"{secrets.token_hex(RANDOM_NAME_LEN)}.html"
    )

    if screenshot_animation_file is None:
        screenshot_animation_file = Path(
            rendering_context, f"{secrets.token_hex(RANDOM_NAME_LEN)}.gif"
        )

    rendered_template = render_template(
        Path(config.RENDER_TIX_TEMPLATE_GRAPHIC_FILE), **summary_data
    )

    save_file_text(rendered_html_path, rendered_template, overwrite=True)

    num_pages = (
        len(summary_data["events"]) + EVENTS_PER_PAGE - 1
    ) // EVENTS_PER_PAGE  # 7 Events per page, make sure to adjust CSS if this number changes

    generate_screenshot_animation(
        rendered_html_path, screenshot_animation_file, num_pages
    )

    rendered_html_path.unlink()

    return screenshot_animation_file


def create_image_tix_static_images(summary_data: Dict) -> List[bytes]:
    """
    Creates a set of image key frames that can be used as PNG images
    """

    rendering_context = Path(config.RENDER_CONTEXT)
    if not rendering_context.exists():
        raise ValueError(f"Rendering context directory not found: {rendering_context}")

    rendered_html_path = Path(
        rendering_context, f"{secrets.token_hex(RANDOM_NAME_LEN)}.html"
    )

    rendered_template = render_template(
        Path(config.RENDER_TIX_TEMPLATE_GRAPHIC_FILE), **summary_data
    )

    save_file_text(rendered_html_path, rendered_template, overwrite=True)

    num_pages = (
        len(summary_data["events"]) + EVENTS_PER_PAGE - 1
    ) // EVENTS_PER_PAGE  # 7 Events per page, make sure to adjust CSS if this number changes

    key_frame_images = generate_screenshot_animation_key_frames(
        rendered_html_path, num_pages
    )

    rendered_html_path.unlink()

    return key_frame_images


def create_text_tix(summary_data: Dict) -> str:
    """
    Renders the table of events to text. Returns the text.
    """

    rendered_template = render_template(
        Path(config.RENDER_TIX_TEMPLATE_TEXT_FILE), **summary_data
    )

    return rendered_template
