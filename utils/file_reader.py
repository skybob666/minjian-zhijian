import os
import tempfile
import docx
import mammoth

def read_document(uploaded_file):
    """
    支持 .doc / .docx，兼容 Streamlit 上传文件
    云端可运行，无需 antiword，无需 Word
    """
    # 获取文件后缀
    ext = os.path.splitext(uploaded_file.name)[1].lower()

    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        if ext == ".docx":
            doc = docx.Document(tmp_path)
            text = "\n".join([p.text for p in doc.paragraphs])

        elif ext == ".doc":
            with open(tmp_path, "rb") as f:
                result = mammoth.extract_raw_text(f)
            text = result.value

        else:
            raise ValueError("仅支持 .doc / .docx 格式")

    finally:
        # 清理临时文件
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    return text
