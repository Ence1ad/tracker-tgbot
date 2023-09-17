from typing import Optional, Any, Dict

from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader('tgbot', 'templates'),
    autoescape=select_autoescape(['html'])
)


def render_template(name: str, values: Optional[Dict[str, Any]] = None, **kwargs) -> str:
    """
    Renders template & returns text
    :param name: Name of template
    :param values: Values for template (optional)
    :param kwargs: Keyword-arguments for template (high-priority)
    """

    template = env.get_template(name)

    if values:
        rendered_template = template.render(values, **kwargs)
    else:
        rendered_template = template.render(**kwargs)

    return rendered_template
