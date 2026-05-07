import os
import tempfile
import docx
from zipfile import BadZipFile

def read_document(uploaded_file):
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    uploaded_file.seek(0)  # 重置文件指针

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        # ------------------------
        # 优先：docx 正常读取
        # ------------------------
        if ext == ".docx":
            try:
                doc = docx.Document(tmp_path)
                text = "\n".join([p.text for p in doc.paragraphs])
            except BadZipFile:
                # 如果不是真正的 docx，尝试当作文本读
                with open(tmp_path, "rb") as f:
                    text = f.read().decode("utf-8", errors="ignore")

        # ------------------------
        # .doc 旧二进制格式
        # 云端安全：不使用 mammoth / antiword
        # ------------------------
        elif ext == ".doc":
            try:
                # 尝试以二进制读取（兼容绝大多数 .doc）
                with open(tmp_path, "rb") as f:
                    raw = f.read().decode("utf-8", errors="ignore")
                text = raw
            except:
                # 兜底：GBK 兼容旧中文文档
                with open(tmp_path, "rb") as f:
                    raw = f.read().decode("gbk", errors="ignore")
                text = raw

        else:
            raise Exception("仅支持 .doc / .docx 文件")

        # 简单清洗空白
        text = text.strip()
        if len(text) < 20:
            raise Exception("文档内容过短，可能是图片版PDF或损坏文件")

        return text

    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
