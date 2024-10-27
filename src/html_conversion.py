import subprocess
from xhtml2pdf import pisa

# Markdown conversion
def convert_to_markdown(html_file, md_file):
    subprocess.run(['pandoc', '-f', 'html', '-t', 'markdown', '-o', md_file, html_file], check=True)

# PDF conversion
def convert_to_pdf(html_file, pdf_file):
    with open(html_file, 'r') as html, open(pdf_file, 'wb') as pdf:
        pisa.CreatePDF(html.read(), dest=pdf)

# Text conversion
def convert_to_text(html_file, txt_file):
    with open(html_file, 'r') as f:
        soup = BeautifulSoup(f, 'html.parser')
        with open(txt_file, 'w') as out:
            out.write(soup.get_text())

# JSON conversion
def convert_to_json(html_file, json_file):
    # Implementation similar to provided code
    pass