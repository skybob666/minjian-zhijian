import os
import tempfile
import docx
import olefile

def read_document(uploaded_file):
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    uploaded_file.seek(0)

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    text = ""
    try:
        # 1. 处理 .docx
        if ext == ".docx":
            doc = docx.Document(tmp_path)
            text = "\n".join([p.text for p in doc.paragraphs])

        # 2. 处理 .doc（用 olefile 解析二进制内容）
        elif ext == ".doc":
            if olefile.isOleFile(tmp_path):
                ole = olefile.OleFileIO(tmp_path)
                if ole.exists('WordDocument'):
                    # 提取文本流（兼容大多数旧版 .doc）
                    word_stream = ole.openstream('WordDocument')
                    raw = word_stream.read()
                    # 尝试常见编码解码
                    for enc in ["utf-8", "gbk", "gb2312", "cp1252"]:
                        try:
                            text = raw.decode(enc)
                            break
                        except:
                            continue
                ole.close()
            else:
                # 兜底：直接读取文件内容
                with open(tmp_path, "rb") as f:
                    raw = f.read()
                    for enc in ["utf-8", "gbk", "gb2312", "cp1252"]:
                        try:
                            text = raw.decode(enc)
                            break
                        except:
                            continue

        else:
            raise ValueError("仅支持 .doc / .docx 格式文件")

        # 清洗文本：去除非打印字符，只保留有效内容
        text = ''.join([c for c in text if c.isprintable() or c in ['\n', '\t', '\r']])
        if len(text.strip()) < 20:
            raise ValueError("文档内容为空或解析失败，请检查文件格式")

        return text

    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
