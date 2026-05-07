import os
import tempfile
import docx
import mammoth

def read_document(uploaded_file):
    """
    兼容 Streamlit 上传文件的 doc/docx 读取函数
    """
    # 1. 获取文件扩展名
    ext = os.path.splitext(uploaded_file.name)[1].lower()

    # 2. 创建临时文件，把上传的文件写入磁盘
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        # 3. 根据格式读取
        if ext == ".docx":
            doc = docx.Document(tmp_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        elif ext == ".doc":
            with open(tmp_path, "rb") as f:
                result = mammoth.extract_raw_text(f)
            text = result.value
        else:
            raise ValueError("仅支持 .doc 和 .docx 格式文件")
    finally:
        # 4. 读取完成后，删除临时文件，避免占用空间
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    return text
