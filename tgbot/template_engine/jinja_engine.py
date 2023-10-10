from pathlib import Path
from typing import Optional, Any, Dict

from jinja2 import Environment, select_autoescape, Template, FileSystemLoader


# path = Path(__file__).parent.parent / 'templates'
path = 'tgbot/template_engine/templates'
env = Environment(
    loader=FileSystemLoader(Path(path)),
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
