from docx import Document
from io import BytesIO

def read_docx(file):
    doc = Document(BytesIO(file.read()))
    return "\n".join([p.text for p in doc.paragraphs if p.text])