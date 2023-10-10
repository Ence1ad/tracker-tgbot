from typing import Optional, Any, Dict

from jinja2 import Environment, PackageLoader, select_autoescape, Template

env = Environment(
    loader=PackageLoader('template_engine', 'templates'),
    autoescape=select_autoescape(['html'])
)


def render_template(name: str, values: Optional[Dict[str, Any]] = None, **kwargs: dict) -> str:
    """
    Renders template & returns text

    :param name: Name of template
    :param values: Values for template (optional)
    :param kwargs: Keyword-arguments for template (high-priority)
    """
    template: Template = env.get_template(name)
    if values:
        rendered_template: str = template.render(values, **kwargs)
    else:
        rendered_template: str = template.render(**kwargs)
    return rendered_template
