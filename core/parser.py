# core/parser.py 【最终强化版】
# 司法裁判文书 · 高精度结构化解析
import re

def clean_text(text):
    """预处理：去空格、换行、乱码，解决案号提取失败问题"""
    text = re.sub(r'\s+', ' ', text)
    text = text.replace("　", "")
    return text.strip()

def extract_elements(text):
    text = clean_text(text)

    # 1. 案号：通用模式，不硬编码省份
    case_no = re.search(r'[(（]\d{4}[)）][^号]*?[民刑行赔执][终初申再监决]?\d+号', text)
    case_no = case_no.group().replace(" ", "") if case_no else "未提取"

    # 2. 法院：优先用"审理法院"标签，否则在前800字里匹配"xx人民法院"
    court_match = re.search(r'审理法院[：:]\s*([\u4e00-\u9fa5]+人民法院)', text)
    if court_match:
        court = court_match.group(1)
    else:
        court_match = re.search(r'([\u4e00-\u9fa5]{2,}(?:省|市|区|县)人民法院)', text[:800])
        court = court_match.group(1) if court_match else "未提取"

    # 3. 案由：优先用"案由"标签，否则取最后一个"xx纠纷"
    case_type_match = re.search(r'案由[：:]\s*.*?([\u4e00-\u9fa5]+纠纷)', text)
    if case_type_match:
        case_type = case_type_match.group(1)
    else:
        all_types = re.findall(r'([\u4e00-\u9fa5]+纠纷)', text)
        case_type = all_types[-1] if all_types else "未提取"

    # --------------------------
    # 3. 当事人（原告、被告）
    # --------------------------
    plaintiff = re.search(r'原告[:：](.*?)(被告|法定代理人|诉讼代理人|$)', text)
    plaintiff = plaintiff.group(1).strip() if plaintiff else "未提取"

    defendant = re.search(r'被告[:：](.*?)(法定代理人|诉讼代理人|$)', text)
    defendant = defendant.group(1).strip() if defendant else "未提取"

    # --------------------------
    # 4. 程序信息
    # --------------------------
    procedure = "简易程序" if "简易程序" in text else "普通程序"
    notice_service = "是" if "公告送达" in text else "否"

    # --------------------------
    # 5. 时间轴（立案 | 开庭 | 判决）
    # --------------------------
    file_date = re.search(r'(?:立案|受理).*?(\d{4}年\d{1,2}月\d{1,2}日)', text)
    file_date = file_date.group(1) if file_date else "未提取"

    trial_date = re.search(r'(?:开庭|庭审).*?(\d{4}年\d{1,2}月\d{1,2}日)', text)
    trial_date = trial_date.group(1) if trial_date else "未提取"

    judge_date = re.search(r'(?:判决|裁定).*?(\d{4}年\d{1,2}月\d{1,2}日)', text)
    judge_date = judge_date.group(1) if judge_date else "未提取"

    # --------------------------
    # 6. 审判组织（审判员 / 书记员）
    # --------------------------
    judge = re.search(r'审判员[:：](.*?) ', text)
    judge = judge.group(1).strip() if judge else "未提取"

    clerk = re.search(r'书记员[:：](.*)', text)
    clerk = clerk.group(1).strip() if clerk else "未提取"

    # --------------------------
    # 7. 裁判主文（精准提取）
    # --------------------------
    main_text = re.search(r'判决如下(.*?)。', text, re.S)
    main_text = main_text.group(1).strip() if main_text else "未提取"

    # --------------------------
    # 最终结构化输出（规则引擎直接调用）
    # --------------------------
    return {
        "案号": case_no,
        "审理法院": court,
        "案由": case_type,
        "原告": plaintiff,
        "被告": defendant,
        "审判程序": procedure,
        "公告送达": notice_service,
        "立案日期": file_date,
        "开庭日期": trial_date,
        "判决日期": judge_date,
        "审判员": judge,
        "书记员": clerk,
        "裁判主文": main_text[:150] + "..." if len(main_text) > 150 else main_text
    }
