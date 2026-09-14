import json
import logging
import os

from openai import OpenAI


logger = logging.getLogger(__name__)


def parse_user_profile(raw_text: str) -> dict:
    """Parse a user's natural-language profile into structured JSON."""
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model = os.getenv("LLM_MODEL", "qwen-plus")  # 默认值给 qwen-plus

    if not api_key:
        raise RuntimeError("环境变量 LLM_API_KEY 未设置")
    if not base_url:
        raise RuntimeError("环境变量 LLM_BASE_URL 未设置")
    if not raw_text or not raw_text.strip():
        raise ValueError("raw_text 不能为空")

    client = OpenAI(api_key=api_key, base_url=base_url)

    prompt = f"""
请把下面的用户自然语言描述解析为结构化 JSON。

只返回 JSON，不要返回 Markdown、代码块或任何解释文字。JSON 必须包含以下字段：
- skills: list[str]，技能标签
- skill_levels: dict，技能等级，例如 {{"Python": "熟练"}}
- experience: list[str]，项目经历
- interests: list[str]，兴趣方向
- preference: str，协作偏好
- time_commitment: str，时间投入

用户描述：
{raw_text}
"""

    try:
        response = client.chat.completions.create(
            model=model,  # ✅ 用变量，不再写死 gpt-4o-mini
            messages=[
                {
                    "role": "system",
                    "content": "你是一个严谨的信息抽取助手。你只能输出合法 JSON。",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("模型返回为空")

        result = json.loads(content)
        if not isinstance(result, dict):
            raise ValueError("模型返回的 JSON 不是对象")
        return result
    except Exception:
        logger.exception("解析用户画像失败")
        raise


def parse_project_requirement(raw_text: str) -> dict:
    """Parse a natural-language project requirement into structured JSON."""
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model = os.getenv("LLM_MODEL", "qwen-plus")

    if not api_key:
        raise RuntimeError("环境变量 LLM_API_KEY 未设置")
    if not base_url:
        raise RuntimeError("环境变量 LLM_BASE_URL 未设置")
    if not raw_text or not raw_text.strip():
        raise ValueError("raw_text 不能为空")

    client = OpenAI(api_key=api_key, base_url=base_url)
    prompt = f"""
请把下面的项目需求自然语言描述解析为结构化 JSON。
只返回 JSON，不要返回 Markdown、代码块或任何解释文字。
JSON 必须包含以下字段：
- required_skills: list[str]，所需技能
- time_requirement: str，时间要求
- priority: list[str]，优先条件
- project_type: str，项目类型
- background: str，项目背景

项目需求：
{raw_text}
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个严谨的信息抽取助手。你只能输出合法 JSON。"},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("模型返回为空")
        result = json.loads(content)
        if not isinstance(result, dict):
            raise ValueError("模型返回的 JSON 不是对象")
        return result
    except Exception:
        logger.exception("解析项目需求失败")
        raise
