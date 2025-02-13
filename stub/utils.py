from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from io import BytesIO
from datetime import datetime

class PDFGenerator:
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(str(self.template_dir)))

    def generate_order_report(self, table_data):
        # Load and render template
        template = self.jinja_env.get_template("pdf/order_report.html")
        html_content = template.render(
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            table_data=table_data
        )

        # Load CSS
        css_file = self.template_dir / "pdf" / "styles.css"
        css = CSS(filename=str(css_file))

        # Generate PDF
        buffer = BytesIO()
        HTML(string=html_content).write_pdf(
            buffer,
            stylesheets=[css],
            presentational_hints=True
        )
        buffer.seek(0)

        return buffer
