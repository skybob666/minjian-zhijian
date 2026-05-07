import requests
import json

def llm_analyze(text):
    prompt = f"""
你是专业的民事裁判文书解析助手，只能从给定的文本中提取信息，不能编造。
严格按照下面的JSON格式输出，没有的字段写“未提取”，不要多余解释。

提取字段：
1. 案号：必须带括号和年份，如(2025)京0105民初69761号，只写案号本身。
2. 审理法院：只写法院全称，如北京市朝阳区人民法院。
3. 案由：只写纠纷类型，如买卖合同纠纷，不要多余文字。
4. 原告：只写姓名/名称，不要“原告：”前缀，多个原告用顿号分隔。
5. 被告：只写姓名/名称，不要“被告：”前缀，多个被告用顿号分隔。
6. 审判程序：如一审普通程序、二审程序，写清楚。
7. 公告送达：是/否，文书中提到公告送达写“是”，否则写“否”。
8. 立案日期：格式为YYYY年MM月DD日，从文书中找法院受理案件的日期，没写就写“未提取”。
9. 开庭日期：格式为YYYY年MM月DD日，从文书中找公开开庭审理的日期，没写就写“未提取”。
10. 判决日期：格式为YYYY年MM月DD日，从文书末尾找判决日期，没写就写“未提取”。
11. 审判员：只写姓名，优先提取末尾署名的法官姓名，多个用顿号分隔，找不到写“未提取”。
12. 书记员：只写姓名，优先提取末尾署名的书记员姓名，多个用顿号分隔，找不到写“未提取”。
13. 裁判主文：一句话概括法院的最终判决结果，只写判决的核心内容，如“被告支付货款29624元及利息”，不超过100字。

文书内容：
{text[:9000]}
"""
    try:
        resp = requests.post(
            url="https://open.bigmodel.cn/api/paas/v4/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer b81aa49fd83549d6830c2175b226f2d0.ZOngwZ89PUMvILYf"
            },
            json={
                "model": "glm-4-flash",  # 免费的Flash模型，速度快、额度足
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0
            }
        )
        resp.raise_for_status()
        data = resp.json()
        # 智谱的正确返回路径！
        choices = data.get("choices", [])
        if not choices:
            return {"错误": "大模型返回异常，未找到choices字段"}

        message = choices[0].get("message", {})
        content = message.get("content", "")

        if not content:
            return {"错误": "大模型返回内容为空"}

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"错误": "大模型返回的不是标准JSON", "原始内容": content}

    except requests.exceptions.RequestException as e:
        return {"错误": f"网络请求失败：{str(e)}"}
    except Exception as e:
        return {"错误": f"未知错误：{str(e)}"}