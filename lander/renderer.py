"""HTML renderering functions."""

import os
import re

import jinja2


def create_jinja_env():
    """Create a Jinja2 `~jinja2.Environment`.

    Returns
    -------
    env : `jinja2.Environment`
        Jinja2 template rendering environment, configured to use templates in
        ``templates/``.
    """
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        autoescape=jinja2.select_autoescape(['html'])
    )
    env.filters['simple_date'] = filter_simple_date
    env.filters['paragraphify'] = filter_paragraphify
    return env


def render_homepage(config, env):
    """Render the homepage.jinja template."""
    template = env.get_template('homepage.jinja')
    rendered_page = template.render(
        config=config)
    return rendered_page


def filter_simple_date(value):
    """Filter a `datetime.datetime` into a 'YYYY-MM-DD' string."""
    return value.strftime('%Y-%m-%d')


def filter_paragraphify(value):
    """Convert text into one or more paragraphs, including <p> tags.

    Based on https://gist.github.com/cemk/1324543
    """
    value = re.sub(r'\r\n|\r|\n', '\n', value)  # Normalize newlines
    paras = re.split('\n{2,}', value)
    paras = ['<p>{0}</p>'.format(p) for p in paras if len(p) > 0]
    return jinja2.Markup('\n\n'.join(paras))
