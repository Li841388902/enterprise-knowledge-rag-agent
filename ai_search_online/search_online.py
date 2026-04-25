
import os
import requests

ALY_AI_SEARCH_API_KEY = os.getenv("ALY_AI_SEARCH_API_KEY")
ALY_AI_SEARCH_ENDPOINT = "default-8kgh.platform-cn-beijing.opensearch.aliyuncs.com"

def web_search_online(query: str) -> str:
    if not ALY_AI_SEARCH_API_KEY:
        return "错误：未配置 ALY_AI_SEARCH_API_KEY 环境变量"

    url = f"https://{ALY_AI_SEARCH_ENDPOINT}/v3/openapi/workspaces/default/web-search/ops-web-search-001"
    headers = {
        "Authorization": f"Bearer {ALY_AI_SEARCH_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "query": query,
        "need_summary": True,
        "query_rewrite": True
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        search_list = data.get("result", {}).get("search_result", [])

        results = []
        for idx, item in enumerate(search_list, 1):
            title = item.get("title", "").strip()
            snippet = item.get("snippet", "").strip()
            link = item.get("link", "").strip()

            # 🔥 关键：过滤掉【只有标题、无摘要、无链接】的无效结果
            if not snippet and not link:
                continue  # 直接跳过

            results.append(f"【搜索{idx}】{title}\n{snippet}\n{link}")

        if not results:
            return "未找到有效信息（部分结果无摘要/链接，已过滤）"

        return "\n\n".join(results)

    except Exception as e:
        return f"搜索失败：{str(e)}"

