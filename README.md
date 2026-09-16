# 知遇LinkLab

知遇LinkLab 是一个面向科研协作场景的智能画像与项目匹配原型。用户可以用自然语言描述个人能力和项目需求，系统使用兼容 OpenAI 接口的大模型将文本转换为结构化数据，并从技能、时间和经历三个维度计算可解释的匹配结果。

## 当前功能

### 能力画像

- 用自然语言输入技能、技能水平、项目经历、兴趣、协作偏好和每周可投入时间
- 通过 AI 生成结构化用户画像
- 自动补全缺失字段，并修正列表、字典和字符串等常见类型问题
- 清理模型可能返回的 Markdown 代码块标记

### 项目发布

- 填写项目名称和自然语言需求描述
- 通过 AI 提取所需技能、时间要求、优先条件、项目类型和项目背景
- 自动校验并补全结构化项目数据

### 匹配测试

- 用户画像支持自然语言输入，也支持直接粘贴 JSON
- 项目需求支持自然语言解析
- 分别展示用户技能标签和项目需求标签
- 计算技能、时间、经历三个维度的匹配度
- 展示综合分数、三项进度条和根据实际输入生成的解释文案

### 服务状态

- 页面加载时自动访问后端健康检查接口
- 后端正常时显示“后端连接正常”
- 后端或接口不可用时显示友好错误提示

## 技术栈

- 前端：Streamlit
- 后端：FastAPI、Uvicorn
- AI 调用：OpenAI Python SDK（兼容 OpenAI 接口格式）
- 默认模型：`qwen-plus`
- HTTP 请求：Requests
- 数据库依赖预留：SQLAlchemy（当前版本尚未持久化数据）

## 项目结构

```text
知遇LinkLab/
├── backend/
│   ├── main.py            # FastAPI 路由、匹配算法和解释生成
│   ├── ai_service.py      # AI 解析、技能归一化及语义相关性判断
│   └── requirements.txt   # Python 依赖
├── frontend/
│   └── app.py             # Streamlit 页面
└── README.md
```

## 环境准备

建议使用 Python 3.10 或更高版本。

```powershell
cd C:\Users\zhang\Desktop\知遇LinkLab
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
python -m pip install streamlit
```

## 大模型配置

项目从环境变量读取大模型配置。使用通义千问 OpenAI 兼容接口时，在启动后端的同一个 PowerShell 窗口中执行：

```powershell
$env:LLM_API_KEY = "你的 DashScope API Key"
$env:LLM_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
$env:LLM_MODEL = "qwen-plus"
```

不要将真实 API Key 写入代码或提交到 Git 仓库。

## 启动项目

### 1. 启动后端

```powershell
cd C:\Users\zhang\Desktop\知遇LinkLab\backend
uvicorn main:app --reload --port 8000
```

- 根接口：<http://localhost:8000>
- 健康检查：<http://localhost:8000/api/health>
- Swagger 文档：<http://localhost:8000/docs>

### 2. 启动前端

在另一个 PowerShell 窗口中执行：

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

```json
{"status": "ok"}
```

### 解析用户画像

```http
POST /api/parse_profile
Content-Type: application/json
```

```json
{
  "raw_text": "我熟练使用Python和SQL，做过大模型API项目，对NLP感兴趣，每周可投入8小时。"
}
```

结构化结果包含：

- `skills`：技能列表
- `skill_levels`：技能水平
- `experience`：项目经历
- `interests`：兴趣方向
- `preference`：协作偏好
- `time_commitment`：每周时间投入

### 解析项目需求

```http
POST /api/parse_project
Content-Type: application/json
```

```json
{
  "raw_text": "开发一个大模型科研助手，需要Python、NLP和前端能力，每周投入10小时，有API开发经验者优先。"
}
```

结构化结果包含：

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

```json
{
  "user_profile": {
    "skills": ["Python", "SQL"],
    "skill_levels": {"Python": "熟练", "SQL": "掌握"},
    "experience": ["调用大模型API完成问答系统"],
    "interests": ["NLP"],
    "preference": "线上协作",
    "time_commitment": "每周8小时"
  },
  "project_profile": {
    "required_skills": ["Python", "NLP", "前端开发"],
    "time_requirement": "10小时/周",
    "priority": ["有大模型项目经验"],
    "project_type": "大模型应用开发",
    "background": "构建面向科研人员的智能问答工具"
  }
}
```

成功响应包含：

```json
{
  "success": true,
  "total_score": 0.72,
  "skill_match": 0.5,
  "time_match": 0.7,
  "experience_match": 0.9,
  "explanation": "根据实际分数和输入内容生成的匹配说明"
}
```

以上分数仅为响应格式示例，实际结果取决于模型判断和输入内容。

## 匹配算法

### 技能匹配

系统先使用 AI 归一化用户技能、兴趣和项目技能，例如将 `ML` 归一化为“机器学习”。随后由 AI 判断用户技能与项目技能的语义相似度，相似度达到 `0.7` 记为一次命中。AI 调用失败时自动降级为不区分大小写的字面匹配。

兴趣也会参与匹配，但一次兴趣命中只按半个技能命中计算：

```text
skill_match = min(
    (技能命中数 + 0.5 × 兴趣命中数) / 项目所需技能数,
    1.0
)
```

以项目需求为分母，表示用户对项目必要能力的覆盖程度。

### 时间匹配

系统可从“每周12小时”“10小时/周”“6 hours/week”“6 h/week”等文本中提取小时数，然后分档评分：

```text
用户时间 >= 项目要求                         1.0
用户时间 >= 项目要求 × 0.8                   0.7
用户时间 >= 项目要求 × 0.5                   0.4
用户时间 <  项目要求 × 0.5                   0.1
任一时间无法解析或项目要求不大于0             0.5
```

相比简单的 0/1 判断，分档评分能够区分“接近满足”和“严重不足”。无法解析时使用中性分 `0.5`，避免因信息缺失直接判为不匹配。

### 经历匹配

系统将用户经历、项目类型和项目背景交给 AI，得到 `0～1` 的语义相关性评分。这可以识别“大模型API小项目”和“大模型应用开发”这类文字不同但语义相关的内容。

模型返回值会被限制在 `0～1`。调用失败或结果无法解析时使用中性分 `0.5`，保证匹配接口仍能返回结果。

### 综合得分

```text
total_score = skill_match × 0.6
            + time_match × 0.2
            + experience_match × 0.2
```

技能权重最高，因为它直接反映用户能否覆盖项目核心任务；时间和经历各占 `20%`，分别反映合作可执行性和经验迁移成本。当前权重和 `0.7` 语义阈值属于原型阶段的规则参数，尚未通过大规模真实配对数据进行统计校准。

## 稳定性设计

- AI 解析结果会进行字段补全、类型转换和空值清理
- 用户画像和项目需求缺失字段时使用预设默认值
- 技能归一化失败时返回原技能列表
- 技能语义匹配失败时降级为字面匹配
- 经历判断失败时返回中性分 `0.5`
- 后端保留匹配调试输出，便于检查技能、时间和经历的中间结果

## 快速验收

1. 访问 <http://localhost:8000/api/health>，确认返回 `{"status":"ok"}`。
2. 打开 <http://localhost:8501>，确认存在“能力画像”“项目发布”“匹配测试”三个标签页。
3. 在能力画像页输入自然语言，确认返回六个用户画像字段。
4. 在项目发布页输入项目需求，确认返回五个项目字段。
5. 在匹配测试页分别解析用户与项目数据，然后点击“计算匹配度”。
6. 确认页面显示总分、技能/时间/经历进度条及包含优势和差距的解释。
7. 查看后端终端，确认能看到技能标准化结果、命中数、时间提取值和经历评分等调试信息。

## 已知限制

- AI 功能依赖有效的模型配置、网络连接和服务额度。
- AI 评分可能随模型版本、提示词和输入表达发生变化，当前结果不应作为对个人能力的绝对评价。
- 时间解析使用文本中第一个带小时单位的数字，暂不支持“每天2小时”等周期自动换算。
- 当前技能命中按 AI 返回的用户技能项统计；多个用户技能指向同一项目技能时可能重复计数，最终分数虽限制为 `1.0`，仍存在高估覆盖率的可能。
- 当前数据仅保存在 Streamlit 会话中，尚未接入数据库、账号系统和历史记录。
- SQLAlchemy 已列入依赖，但当前版本尚未使用。
