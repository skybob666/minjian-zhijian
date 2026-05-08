# utils/file_reader.py
import io
from docx import Document

def read_docx(file):
    """读取streamlit上传的docx文件"""
    doc = Document(io.BytesIO(file.read()))
    return "\n".join([p.text for p in doc.paragraphs])
