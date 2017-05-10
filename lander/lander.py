"""Coordination infrastructure for making a landing page."""

from .renderer import create_jinja_env, render_homepage


class Lander(object):
    """Lander coordinates the creation and upload of a landing page for
    a PDF document.
    """

    def __init__(self, config):
        super().__init__()
        self._config = config

    def render(self):
        jinja_env = create_jinja_env()
        print(render_homepage(self._config, jinja_env))
