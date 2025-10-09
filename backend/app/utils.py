from django.template.loader import get_template


def render_email(template_name, context={}):
    """Render an email from a template."""
    subject_template = get_template(f"{template_name}.subject.txt")
    html_template = get_template(f"{template_name}.html")

    subject_rendered = subject_template.render(context).strip()
    html_rendered = html_template.render(context).strip()

    return subject_rendered, html_rendered
