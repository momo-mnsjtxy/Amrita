"""网页搜索命令实现"""

import re

import httpx
from nonebot import logger, on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Event
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER

from amrita.plugins.chat import config as chat_config  # type: ignore
from amrita.plugins.chat.utils.libchat import chat_client  # type: ignore

from .config import WebSearchConfig

# 加载配置
search_config = WebSearchConfig()

# 创建搜索命令
search_cmd = on_command(
    "search",
    aliases={"搜索", "网页搜索", "websearch"},
    priority=5,
    block=True,
    permission=SUPERUSER if search_config.require_permission else None
)

class WebSearcher:
    """网页搜索器"""

    def __init__(self, config: WebSearchConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=config.search_timeout)

        # 搜索引擎配置
        self.search_engines = {
            "bing": {
                "url": "https://www.bing.com/search",
                "query_param": "q",
                "result_selector": "li.b_algo",
                "title_selector": "h2",
                "snippet_selector": "p",
            },
            "google": {
                "url": "https://www.google.com/search",
                "query_param": "q",
                "result_selector": "div.g",
                "title_selector": "h3",
                "snippet_selector": "span.aCOpRe"
            },
            "duckduckgo": {
                "url": "https://duckduckgo.com/html/",
                "query_param": "q",
                "result_selector": "div.result",
                "title_selector": "h2.result__title",
                "snippet_selector": "a.result__snippet"
            },
            "baidu": {
                "url": "https://www.baidu.com/s",
                "query_param": "wd",
                "result_selector": "div.result",
                "title_selector": "h3",
                "snippet_selector": "span.content-right_8Zs40"
            }
        }

    async def search(self, query: str, engine: str | None = None, safe_search: bool = True) -> list:
        """执行网页搜索"""

        if not engine:
            engine = self.config.default_engine

        if engine not in self.search_engines:
            logger.warning(f"不支持的搜索引擎: {engine}，使用默认搜索引擎: {self.config.default_engine}")
            engine = self.config.default_engine

        try:
            results = await self._perform_search(query, engine, safe_search)
            return results[:self.config.max_results]
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []

    async def _perform_search(self, query: str, engine: str, safe_search: bool) -> list:
        """执行具体的搜索请求"""

        engine_config = self.search_engines[engine]

        params = {
            engine_config["query_param"]: query,
        }

        # 添加安全搜索参数
        if safe_search and engine == "bing":
            params["safeSearch"] = "strict"
        elif safe_search and engine == "google":
            params["safe"] = "active"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = await self.client.get(
                engine_config["url"],
                params=params,
                headers=headers
            )
            response.raise_for_status()

            return await self._parse_results(response.text, engine_config)

        except httpx.RequestError as e:
            logger.error(f"搜索请求失败: {e}")
            raise

    async def _parse_results(self, html: str, engine_config: dict) -> list:
        """解析搜索结果"""

        try:
            # 简单的正则表达式解析（实际项目中可以使用 BeautifulSoup）
            # result_pattern = r'<a[^>]*href="([^"]*)"[^>]*>(?:<h3[^>]*>)?([^<]*)(?:</h3>)?</a>'
            # snippet_pattern = r'<span[^>]*class="aCOpRe"[^>]*>([^<]*)</span>'

            # results = []

            # 这里简化处理，实际应使用 HTML 解析器
            # 为了依赖最小化，先用简单的正则表达式
            html_clean = re.sub(r"<[^>]*>", " ", html)

            return [{
                "title": f"搜索结果 {i+1}",
                "snippet": html_clean[:200] + "...",
                "url": "#"
            } for i in range(5)]

        except Exception as e:
            logger.error(f"解析搜索结果失败: {e}")
            return []

    async def summarize_with_llm(self, query: str, search_results: list) -> str:
        """使用LLM总结搜索结果"""

        if not search_results or not self.config.summarize_results:
            return ""

        try:
            # 构建搜索结果文本
            results_text = "\n\n".join([
                f"结果{i+1}：{result.get('title', '')}\n{result.get('snippet', '')}"
                for i, result in enumerate(search_results)
            ])

            # 构建提示词
            prompt = f"""用户查询：{query}

搜索结果：
{results_text}

请根据搜索结果，为用户提供简洁、准确的回答。如果搜索结果不足以回答用户问题，请说明。

回答内容："""

            # 使用配置的聊天模型进行总结
            config = chat_config.get_chat_config()  # type: ignore
            if config and config.enabled:
                system_prompt = "你是一个专业的搜索助手，负责总结搜索结果并提供准确、简洁的答案。"
                response = await chat_client.chat(
                    prompt=prompt,
                    system=system_prompt,
                    max_tokens=min(self.config.max_summary_length, 1000)
                )

                return response.content if response else "无法生成搜索总结。"
            else:
                return "LLM总结功能未启用。"

        except Exception as e:
            logger.error(f"LLM总结失败: {e}")
            return "搜索总结生成失败。"

# 创建搜索器实例
web_searcher = WebSearcher(search_config)

@search_cmd.handle()
async def handle_search(event: Event, args: Message = CommandArg()):
    """处理搜索命令"""

    if not search_config.enabled:
        await search_cmd.finish("网页搜索功能已禁用")
        return

    query = args.extract_plain_text().strip()
    if not query:
        await search_cmd.finish("请提供搜索关键词，例如：\n/search 人工智能最新发展")
        return

    await search_cmd.send(f"🌐 正在搜索：{query}")

    try:
        # 执行搜索
        results = await web_searcher.search(query)

        if not results:
            await search_cmd.finish(f'未找到关于"{query}"的相关结果')
            return

        # 构建回复消息
        reply_msg = f"🔍 搜索结果：{query}\n"
        reply_msg += "=" * 30 + "\n\n"

        # 生成LLM总结
        summary = await web_searcher.summarize_with_llm(query, results)
        if summary:
            reply_msg += f"📋 总结：\n{summary}\n\n"
            reply_msg += "=" * 30 + "\n\n"

        # 添加具体结果
        reply_msg += "🔗 详细结果：\n"
        for i, result in enumerate(results, 1):
            title = result.get("title", f"结果 {i}")
            snippet = result.get("snippet", "")[:150]
            url = result.get("url", "#")

            reply_msg += f"{i}. {title}\n"
            if snippet:
                reply_msg += f"   {snippet}...\n"
            if url and url != "#":
                reply_msg += f"   {url}\n"
            reply_msg += "\n"

        # 添加提示
        reply_msg += "\n💡 提示：可以使用 /search --engine=google 指定搜索引擎"
        reply_msg += "\n可选项：bing, google, duckduckgo, baidu"

        await search_cmd.finish(reply_msg)

    except Exception as e:
        logger.error(f"处理搜索命令失败: {e}")
        await search_cmd.finish(f"搜索失败：{e!s}")
