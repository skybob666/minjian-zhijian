import os
import docx
import mammoth

def read_document(file_path):
    """
    云端安全版：支持 .doc 和 .docx
    不依赖 antiword、不依赖 pywin32
    """
    ext = os.path.splitext(file_path)[1].lower()

    # 处理 docx
    if ext == ".docx":
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    # 处理 doc（云端安全！）
    elif ext == ".doc":
        with open(file_path, "rb") as f:
            result = mammoth.extract_raw_text(f)
        return result.value

    else:
        raise Exception("仅支持 .doc 和 .docx 格式文件")
