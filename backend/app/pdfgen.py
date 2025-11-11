# backend/app/pdfgen.py
import os
from jinja2 import Template as JinjaTemplate
from weasyprint import HTML, CSS

def render_html_from_template(tpl_html: str, css: str, data: dict) -> str:
    """
    Combine template HTML (Jinja2) + CSS + data into a full HTML document string.
    """
    # ensure we remove any unwanted default subtitle:
    # tpl_html should not contain "Data Science Student" fixed text.
    jtpl = JinjaTemplate(tpl_html)
    body = jtpl.render(**data)

    full = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
{css}
@page {{ size: A4; margin: 1cm; }}
</style>
</head>
<body>
{body}
</body>
</html>"""
    return full

def generate_pdf_from_html(html_str: str, outpath: str):
    """Generate a PDF file from rendered HTML string using WeasyPrint."""
    # WeasyPrint will take the HTML string and write the PDF.
    HTML(string=html_str).write_pdf(outpath)
    return outpath
