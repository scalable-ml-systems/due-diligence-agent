from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape


def render_report(template_path: Path, out_path: Path, context: dict[str, Any]) -> None:
    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        autoescape=select_autoescape(enabled_extensions=()),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    tmpl = env.get_template(template_path.name)
    out_path.write_text(tmpl.render(**context), encoding="utf-8")
