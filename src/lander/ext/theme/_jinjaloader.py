"""Jinja template loader for theme plugins."""

from __future__ import annotations

import logging
import re
from os.path import getmtime
from typing import TYPE_CHECKING, Callable, Optional, Tuple

from jinja2 import BaseLoader, TemplateNotFound

if TYPE_CHECKING:
    from pathlib import Path

    from jinja2 import Environment

    from lander.ext.theme._base import ThemePlugin


__all__ = ["ThemeTemplateLoader"]


SITE_FILE_PATTERN = re.compile(r"^\$(?P<theme>[a-zA-Z0-9]+)\/(?P<path>.+)$")


class ThemeTemplateLoader(BaseLoader):
    """Jinja2 Template loader for theme templates.

    Parameters
    ----------
    theme : `lander.ext.theme.ThemePlugin`
        The theme plugin associated with this template loader.

    Notes
    -----
    The template loader deals with two types of templates:

    - Site file templates. These templates are located with the "site"
      directory (`lander.ext.theme.ThemePlugin.site_dir`) of a theme and
      correspond to pages in the landing page. When referencing these
      templates using the `get_source` method, prefix the path of the template
      with this pattern: ``$<theme name>/<template path>``. For example:
      ``$base/index.html.jinja``.

    - Templates indended to be included by site file templates (using the
      Jinja2 ``include`` syntax). These templates are simply referenced by
      their relative path within a theme's templates directory
      (`lander.ext.theme.ThemePlugin.templates_dir`)

    In addition to these theme template types, this template loader also
    implements template inheritance. If a template isn't found in a theme,
    the loader calls the loader of the base theme (set via the theme's
    `lander.ext.theme.ThemePlugin.base_theme_name` property).
    """

    def __init__(self, theme: ThemePlugin) -> None:
        self._logger = logging.getLogger(__name__)
        self._theme = theme

    @property
    def theme(self) -> ThemePlugin:
        """The theme plugin."""
        return self._theme

    @property
    def inherited_loader(self) -> Optional[ThemeTemplateLoader]:
        """The template loader from the theme's base theme (if the theme
        inherits from a base theme).
        """
        if self._theme.base_theme is not None:
            return self._theme.base_theme.template_loader
        else:
            return None

    def get_source(
        self, environment: Environment, template: str
    ) -> Tuple[str, str, Callable]:
        """Get the template source given its name

        Implements the Jinja `jinja.BaseLoader` interface.
        """
        if template.startswith("$"):
            match = SITE_FILE_PATTERN.match(template)
            if match:
                theme_name = match["theme"]
                file_path = match["path"]
                return self.get_site_file_template(
                    environment, theme_name, file_path
                )
            else:
                raise TemplateNotFound(template)
        else:
            return self.get_theme_template(environment, template)

    def get_site_file_template(
        self, environment: Environment, theme_name: str, file_path: str
    ) -> Tuple[str, str, Callable]:
        """Get the source for a templated site file."""
        if theme_name == self.theme.name:
            path = self.theme.site_dir.joinpath(file_path)
            self._logger.debug(
                "%s loader: looking for site file at path %s",
                self.theme.name,
                path,
            )
            if not path.is_file():
                raise TemplateNotFound(file_path)
            return self._return_source(path)
        elif self.inherited_loader is not None:
            return self.inherited_loader.get_site_file_template(
                environment, theme_name, file_path
            )
        else:
            self._logger.debug(
                "%s loader: no inherited loaders available for theme name %s",
                self.theme.name,
                theme_name,
            )
            raise TemplateNotFound(file_path)

    def get_theme_template(
        self, environment: Environment, template: str
    ) -> Tuple[str, str, Callable]:
        """Get the source for a theme template, or a template in an inherited
        theme.
        """
        path = self.theme.templates_dir.joinpath(template)
        if path.is_file():
            return self._return_source(path)
        elif self.inherited_loader is not None:
            return self.inherited_loader.get_theme_template(
                environment, template
            )
        else:
            raise TemplateNotFound(template)

    def _return_source(self, path: Path) -> Tuple[str, str, Callable]:
        """Return template source following the `Loader.get_source`
        return-type specification.
        """
        source = path.read_text()
        modified_time = getmtime(path)
        return (
            source,
            str(path.resolve()),
            lambda: modified_time == getmtime(path),
        )
