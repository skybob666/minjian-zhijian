import streamlit as st
from core.parser import extract_elements
from core.rule_check import run_rule_check
from core.llm_adapter import llm_analyze
from utils.file_reader import read_document
import time

st.set_page_config(page_title="民检智鉴", layout="wide")
st.title("⚖️ 民检智鉴 — 民事检察智能识别模型")
st.markdown("### 北京市人民检察院|人工智能与检察监督深度融合")

# =======================
# 【模式选择：单篇 / 批量】
# =======================
mode = st.radio("选择模式", ["单篇文书解析", "批量文书筛查"], horizontal=True)

# 初始化耗时变量（防止报错）
cost_rule_elem = 0.0
cost_rule_check = 0.0
cost_llm = 0.0

# ==============================================
# 模式 1：单篇解析（完美修复版）
# ==============================================
if mode == "单篇文书解析":
    uploaded = st.file_uploader("上传文书（.doc / .docx）", type=["doc", "docx"])

    if uploaded:
        try:
            text = read_document(uploaded)

            # 1. 计时：要素解析（只调用一次）
            t1_start = time.time()
            info = extract_elements(text)
            t1_end = time.time()
            cost_rule_elem = round(t1_end - t1_start, 2)

            # 2. 计时：规则违法筛查（只调用一次）
            t2_start = time.time()
            with st.spinner("🤖 规则模型正在解析文书..."):
                rule_clues = run_rule_check(text)
            t2_end = time.time()
            cost_rule_check = round(t2_end - t2_start, 2)

            # 3. 计时：大模型解析（只调用一次）
            t3_start = time.time()
            with st.spinner("🤖 大模型正在深度解析文书..."):
                llm_result = llm_analyze(text)
            t3_end = time.time()
            cost_llm = round(t3_end - t3_start, 2)

            # --- 双列对比：左侧规则解析，右侧大模型解析 ---
            col1, col2 = st.columns(2)

            # 左侧：文书要素解析（规则版）
            with col1:
                st.subheader("📌 文书要素解析（规则引擎）")
                st.json(info)

            # 右侧：大模型增强解析
            with col2:
                st.subheader("🤖 案件结构化解析（大模型增强）")
                if "错误" in llm_result:
                    st.error(f"大模型解析失败：{llm_result['错误']}")
                else:
                    llm_info = llm_result
                    colA, colB = st.columns(2)
                    with colA:
                        st.markdown(f"**案号**：{llm_info.get('案号', '未提取')}")
                        st.markdown(f"**法院**：{llm_info.get('审理法院', '未提取')}")
                        st.markdown(f"**案由**：{llm_info.get('案由', '未提取')}")
                        st.markdown(f"**程序**：{llm_info.get('审判程序', '未提取')} | 公告送达：{llm_info.get('公告送达', '未提取')}")

                    with colB:
                        st.markdown(f"**原告**：{llm_info.get('原告', '未提取')}")
                        st.markdown(f"**被告**：{llm_info.get('被告', '未提取')}")
                        st.markdown(f"**审判员**：{llm_info.get('审判员', '未提取')}")
                        st.markdown(f"**书记员**：{llm_info.get('书记员', '未提取')}")

                    st.markdown("---")
                    st.markdown("⏱ **程序时间轴（大模型识别）**")
                    st.markdown(f"立案：{llm_info.get('立案日期', '未提取')} → 开庭：{llm_info.get('开庭日期', '未提取')} → 判决：{llm_info.get('判决日期', '未提取')}")

                    st.markdown("---")
                    st.markdown("📄 **裁判主文（大模型提取）**")
                    st.success(llm_info.get('裁判主文', '未提取'))

            # --- 违法情形初步评估（按老师要求：风险等级） ---
            st.markdown("---")
            st.subheader("📝 疑似违法情形初步评估报告")
            
            # 老师要求：风险等级判定
            clue_count = len(rule_clues) if isinstance(rule_clues, list) else 0
            if clue_count == 0:
                st.success("✅ 未发现疑似违法情形")
            elif clue_count == 1:
                st.warning("🟡 中风险（发现 1 项违法事项）")
            else:
                st.error(f"🔴 高风险（发现 {clue_count} 项违法事项）")

            # 展示所有违法事项
            if rule_clues:
                for idx, item in enumerate(rule_clues, 1):
                    with st.container(border=True):
                        st.markdown(f"**问题{idx}：{item.get('问题', '未识别')}**")
                        st.markdown(f"⚖️ 风险等级：{item.get('风险等级', '未评估')}")
                        st.markdown(f"📜 法律依据：{item.get('法律依据', '未提供')}")
                        st.markdown(f"🧠 初步评估：{item.get('初步评估', '未评估')}")
                        st.markdown(f"✅ 检察建议：{item.get('检察建议', '未提供')}")

        except Exception as e:
            st.error(f"解析出错：{str(e)}")

        # 在页面最底部加一行小字耗时
        st.markdown("---")
        st.caption(f"⏱ 要素解析耗时：{cost_rule_elem}s | 规则筛查耗时：{cost_rule_check}s | 大模型解析耗时：{cost_llm}s")

# ==============================================
# 批量筛查（美化版 + 双栏详情 + 跨案分析）
# ==============================================
elif mode == "批量文书筛查":
    uploaded_files = st.file_uploader("批量上传裁判文书", type="docx", accept_multiple_files=True)

    if "task_list" not in st.session_state:
        st.session_state.task_list = []
    if "selected_task_idx" not in st.session_state:
        st.session_state.selected_idx = None

    if uploaded_files and st.button("▶ 开始批量解析"):
        st.session_state.task_list = []
        bar = st.progress(0)
        for i, file in enumerate(uploaded_files):
            bar.progress((i+1)/len(uploaded_files), text=f"解析：{file.name}")
            try:
                text = read_document(file)
                pages = max(1, len(text)//600)
                t0 = time.time()
                info_rule = extract_elements(text)
                clues = run_rule_check(text)
                info_llm = llm_analyze(text)
                cost = round(time.time()-t0, 2)
                cnt = len(clues)
                if cnt == 0:
                    lv = "✅ 低风险"
                elif cnt == 1:
                    lv = f"🟡 中风险({cnt}项)"
                else:
                    lv = f"🔴 高风险({cnt}项)"
                st.session_state.task_list.append({
                    "name": file.name, "pages": pages, "time": cost,
                    "risk_level": lv, "risk_count": cnt,
                    "info_rule": info_rule, "info_llm": info_llm, "clues": clues
                })
            except:
                st.session_state.task_list.append({
                    "name": file.name, "pages":0,"time":0,"risk_level":"❌ 解析失败","risk_count":0,
                    "info_rule":{},"info_llm":{},"clues":[]
                })
        bar.empty()
        st.success("✅ 批量解析完成")

        # 跨案分析
        try:
            from core.rule_check import run_cross_case_analysis
            cross = run_cross_case_analysis(st.session_state.task_list)
            if cross:
                st.divider()
                st.subheader("🔍 跨案大数据监督线索")
                for c in cross:
                    with st.container(border=True):
                        st.markdown(f"**{c['问题']}**")
                        st.markdown(f"等级：{c['风险等级']}｜依据：{c['法律依据']}")
        except:
            pass

    # 任务列表
    if st.session_state.task_list:
        st.subheader("📋 批量筛查清单")
        for i, task in enumerate(st.session_state.task_list):
            with st.container(border=True):
                a,b,c,d = st.columns([3,1,1,2])
                with a: st.write(f"📄 {task['name']}")
                with b: st.write(f"页数：{task['pages']}")
                with c: st.write(f"{task['time']}s")
                with d:
                    if "高风险" in task['risk_level']:
                        st.error(task['risk_level'])
                    elif "中风险" in task['risk_level']:
                        st.warning(task['risk_level'])
                    else:
                        st.success(task['risk_level'])
                if st.button("查看完整解析", key=f"btn_{i}"):
                    st.session_state.selected_idx = i

    # 详情页（美化双栏）
    if st.session_state.get("selected_idx", None) is not None:
        try:
            t = st.session_state.task_list[st.session_state.selected_idx]
            st.divider()
            st.subheader(f"🔍 详情：{t['name']}")
            cnt = t['risk_count']
            if cnt == 0:
                st.success("✅ 低风险")
            elif cnt == 1:
                st.warning("🟡 中风险")
            else:
                st.error(f"🔴 高风险({cnt}项)")

            # 双栏展示
            colA, colB = st.columns(2)
            with colA:
                with st.container(border=True):
                    st.markdown("#### 📌 规则引擎结果")
                    st.json(t['info_rule'], expanded=False)
            with colB:
                with st.container(border=True):
                    st.markdown("#### 🤖 大模型增强结果")
                    st.json(t['info_llm'], expanded=False)

            # 违法事项
            if t['clues']:
                st.divider()
                st.markdown("#### 触发监督事项")
                for idx, item in enumerate(t['clues'],1):
                    with st.container(border=True):
                        st.markdown(f"**问题{idx}：{item['问题']}**")
                        st.markdown(f"依据：{item['法律依据']}｜建议：{item['检察建议']}")

            if st.button("关闭详情"):
                st.session_state.selected_idx = None
                st.rerun()
        except:
            st.error("详情加载失败")
