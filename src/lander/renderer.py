"""HTML renderering functions."""

__all__ = [
    "create_jinja_env",
    "render_homepage",
    "filter_simple_date",
    "filter_paragraphify",
]

import datetime
import re
from pathlib import Path
from typing import TYPE_CHECKING

import jinja2
from markupsafe import Markup

if TYPE_CHECKING:
    from lander.config import Configuration


def create_jinja_env() -> jinja2.Environment:
    """Create a Jinja2 `~jinja2.Environment`.

    Returns
    -------
    env : `jinja2.Environment`
        Jinja2 template rendering environment, configured to use templates in
        ``templates/``.
    """
    template_dir = Path(__file__).parent / "templates"
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        autoescape=jinja2.select_autoescape(["html"]),
    )
    env.filters["simple_date"] = filter_simple_date
    env.filters["paragraphify"] = filter_paragraphify
    return env


def render_homepage(config: "Configuration", env: jinja2.Environment) -> str:
    """Render the homepage.jinja template."""
    template = env.get_template("homepage.jinja")
    return template.render(config=config)


def filter_simple_date(value: datetime.datetime) -> str:
    """Filter a `datetime.datetime` into a 'YYYY-MM-DD' string."""
    return value.strftime("%Y-%m-%d")


def filter_paragraphify(value: str) -> str:
    """Convert text into one or more paragraphs, including <p> tags.

    Based on https://gist.github.com/cemk/1324543
    """
    value = re.sub(r"\r\n|\r|\n", "\n", value)  # Normalize newlines
    paras = re.split("\n{2,}", value)
    paras = [f"<p>{p}</p>" for p in paras if len(p) > 0]
    return Markup("\n\n".join(paras))
