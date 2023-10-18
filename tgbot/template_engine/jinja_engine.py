from pathlib import Path

from typing import Any

from jinja2 import Environment, select_autoescape, Template, FileSystemLoader


path = 'tgbot/template_engine/templates'
env = Environment(
    loader=FileSystemLoader(Path(path)),
    autoescape=select_autoescape(['html'])
)


def render_template(name: str, values: dict[str, Any] | None = None,
                    **kwargs: dict[str, str]) -> str:
    """Render a Jinja2 template with optional context values.

    This function renders a Jinja2 template with the specified template name, using the
    provided context values and keyword arguments.

    :param name: str: The name of the Jinja2 template to render.
    :param values: dict[str, Any] | None: A dictionary of context values to pass to the
    template (default is None).
    :param kwargs: dict[str, str]: Additional keyword arguments to pass to the template.
    :return: str: The rendered template as a string.
    """
    template: Template = env.get_template(name)
    if values:
        return template.render(values, **kwargs)
    else:
        return template.render(**kwargs)

