# 知遇LinkLab

知遇LinkLab 是一个面向科研协作场景的智能画像与项目匹配原型。用户可以用自然语言描述个人能力或项目需求，系统通过兼容 OpenAI 接口格式的大模型将文本解析为结构化数据，再根据技能、时间和经历计算可解释的匹配分数。

## 当前功能

### 能力画像

- 输入技能、经历、兴趣方向、协作偏好和可投入时间等自然语言描述
- 调用 AI 生成结构化用户画像
- 返回技能标签、技能等级、项目经历、兴趣方向、协作偏好和时间投入

### 项目发布

- 输入项目名称和项目需求描述
- 调用 AI 解析项目背景、项目类型、所需技能、时间要求和优先条件
- 在页面中展示结构化项目需求

### 匹配测试

- 左侧输入用户自然语言，或直接粘贴已解析的用户画像 JSON
- 右侧输入项目需求自然语言
- 分别调用用户画像和项目需求解析接口
- 调用匹配接口计算综合匹配度
- 使用大号数字展示总分，并用进度条展示技能、时间和经历三个维度
- 展示可读的匹配结果说明

### 服务状态

- 前端启动时自动检查后端健康状态
- 后端正常时显示“后端连接正常”
- 后端不可用或接口异常时显示友好错误提示

## 技术栈

- 前端：Streamlit
- 后端：FastAPI、Uvicorn
- AI 调用：OpenAI Python SDK（兼容 OpenAI 接口格式）
- 当前默认模型：`qwen-plus`
- HTTP 请求：Requests

## 项目结构

```text
知遇LinkLab/
├── backend/
│   ├── main.py            # FastAPI 路由和匹配算法
│   ├── ai_service.py      # 用户画像及项目需求 AI 解析
│   └── requirements.txt   # 后端依赖
├── frontend/
│   └── app.py             # Streamlit 页面
└── README.md
```

## 环境准备

建议使用 Python 3.10 或更高版本。

在项目根目录创建并激活虚拟环境：

```powershell
cd C:\Users\zhang\Desktop\知遇LinkLab
python -m venv venv
.\venv\Scripts\Activate.ps1
```

安装依赖：

```powershell
python -m pip install -r backend\requirements.txt
python -m pip install streamlit
```

## 大模型配置

项目通过环境变量读取大模型配置。使用通义千问 OpenAI 兼容接口时，在启动后端的同一个 PowerShell 窗口中执行：

```powershell
$env:LLM_API_KEY = "你的 DashScope API Key"
$env:LLM_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
$env:LLM_MODEL = "qwen-plus"
```

请勿把真实 API Key 直接写入代码或提交到 Git 仓库。

## 启动项目

### 1. 启动后端

打开第一个 PowerShell 窗口：

```powershell
cd C:\Users\zhang\Desktop\知遇LinkLab\backend
uvicorn main:app --reload --port 8000
```

后端地址：

- 服务根地址：<http://localhost:8000>
- 健康检查：<http://localhost:8000/api/health>
- API 文档：<http://localhost:8000/docs>

### 2. 启动前端

打开第二个 PowerShell 窗口：

```powershell
cd C:\Users\zhang\Desktop\知遇LinkLab\frontend
streamlit run app.py
```

浏览器访问：<http://localhost:8501>

## API 说明

### 健康检查

```http
GET /api/health
```

响应：

```json
{"status": "ok"}
```

### 解析用户画像

```http
POST /api/parse_profile
Content-Type: application/json
```

请求：

```json
{
  "raw_text": "我熟练使用 Python 和 SQL，做过数据分析项目，每周可投入 8 小时。"
}
```

成功响应：

```json
{
  "success": true,
  "data": {
    "skills": ["Python", "SQL"],
    "skill_levels": {"Python": "熟练"},
    "experience": ["数据分析项目"],
    "interests": ["数据分析"],
    "preference": "未说明",
    "time_commitment": "8小时/周"
  }
}
```

### 解析项目需求

```http
POST /api/parse_project
Content-Type: application/json
```

请求：

```json
{
  "raw_text": "开发一个大模型科研助手，需要 Python、SQL 和前端能力，每周投入 10 小时。"
}
```

解析结果包含：

- `required_skills`：所需技能
- `time_requirement`：时间要求
- `priority`：优先条件
- `project_type`：项目类型
- `background`：项目背景

### 计算匹配度

```http
POST /api/match
Content-Type: application/json
```

请求示例：

```json
{
  "user_profile": {
    "skills": ["Python", "SQL"],
    "skill_levels": {"Python": "熟练"},
    "time_commitment": "12小时/周",
    "experience": ["大模型应用开发项目"]
  },
  "project_profile": {
    "required_skills": ["Python", "SQL", "前端"],
    "time_requirement": "10小时/周",
    "project_type": "大模型应用开发"
  }
}
```

响应示例：

```json
{
  "success": true,
  "total_score": 0.8,
  "skill_match": 0.667,
  "time_match": 1,
  "experience_match": 1,
  "explanation": "技能匹配良好，经验相关，时间投入充足"
}
```

## 匹配算法

综合匹配度由三个维度组成：

```text
技能匹配度 = 用户技能与项目技能的交集数量 / 项目所需技能数量
时间匹配度 = 用户时间 >= 项目要求时间时为 1，否则为 0
经历匹配度 = 用户经历关键词与项目类型关键词有重合时为 1，否则为 0

综合匹配度 = 技能匹配度 × 0.6
           + 时间匹配度 × 0.2
           + 经历匹配度 × 0.2
```

当前算法是透明、可复核的规则型基线，适合原型验证。它尚未结合技能熟练度权重、同义词识别、时间周期标准化或真实配对数据训练，因此匹配结果应作为协作参考，而不是对个人科研能力的绝对评价。

## 快速验收

1. 访问 `<http://localhost:8000/api/health>`，确认返回 `{"status":"ok"}`。
2. 打开 `<http://localhost:8501>`，确认存在“能力画像”“项目发布”“匹配测试”三个标签页。
3. 在能力画像页输入自然语言，确认可以得到结构化 JSON。
4. 在项目发布页填写项目名称和需求，确认可以得到项目结构化 JSON。
5. 在匹配测试页分别解析用户画像和项目需求，点击“计算匹配度”。
6. 确认页面显示综合分数、三个维度进度条和匹配说明。

## 已知限制

- AI 解析依赖外部模型服务和有效的环境变量配置。
- 大模型输出可能受输入表达和模型能力影响。
- 时间匹配目前只提取文本中的第一个小时数。
- 经历匹配目前采用简单关键词重合规则。
- 当前数据仅保存在页面会话中，尚未接入数据库和用户系统。
