from django.template.loader import get_template
from typing import Any, Tuple


def render_email(template_name: str, context: Any = {}) -> Tuple[str, str]:
    """Render an email from two templates template.
    This function assumes that for template name both <template_name>.html and <template_name>.subject.txt
    exsists to generate both the body of the email and the subject.

    Args:
        template_name (str): the base of the template names
        contenxt (Any): the context provided to templates
    Returns:
        Tuple[str, str]: subject and html content of the email
    """
    subject_template = get_template(f"{template_name}.subject.txt")
    html_template = get_template(f"{template_name}.html")

    subject_rendered = subject_template.render(context).strip()
    html_rendered = html_template.render(context).strip()

    return subject_rendered, html_rendered
