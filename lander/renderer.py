"""HTML renderering functions."""

import os

import jinja2


def create_jinja_env():
    """Create a Jinja2 `~jinja2.Environment`.

    Returns
    -------
    env : `jinja2.Environment`
        Jinja2 template rendering environment, configured to use templates in
        ``templates/``.
    """
    template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        autoescape=jinja2.select_autoescape(['html'])
    )
    return env


def render_homepage(config, env):
    """Render the homepage.jinja template."""
    template = env.get_template('homepage.jinja')
    rendered_page = template.render(
        config=config)
    return rendered_page
