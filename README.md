# 知遇LinkLab

## 项目简介

知遇LinkLab 是一个面向科研合作的智能匹配平台。用户可以用自然语言描述自己的技能、兴趣和项目需求，系统调用大模型（千问）将其解析为结构化数据，帮助找到合适的科研搭档。

## 环境要求

- Python ≥ 3.9（推荐 3.10+）
- 依赖包：见 `backend/requirements.txt`
- 环境变量：
  - `LLM_API_KEY`：大模型 API Key
  - `LLM_BASE_URL`：大模型接口地址
  - `LLM_MODEL`：模型名称（默认 `qwen-plus`）

## 启动步骤

### 后端

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000