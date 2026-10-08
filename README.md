# 知遇LinkLab

知遇LinkLab 是一个面向高校科研协作的智能项目匹配原型。用户可以建立可编辑的能力画像，发布科研项目，并根据技能、时间投入和项目经历获得可解释的项目推荐。

当前版本已经具备从注册登录、邮箱验证、画像保存、项目发布、项目发现、批量推荐、双向意向、通知、收藏、反馈到管理员治理的完整演示闭环，适合作为功能较完整的科研协作匹配原型继续迭代。

## 已实现功能

### 账号与数据持久化

- 用户注册：用户名、邮箱、密码、学校、专业、年级
- 使用用户名和密码登录，Streamlit 保存当前会话
- 普通用户密码使用 PBKDF2-HMAC-SHA256、随机盐和 600000 次迭代后存储
- 密码至少 8 位，注册时校验两次输入
- SQLAlchemy 持久化：本地默认使用 SQLite，云端通过 `DATABASE_URL` 使用 PostgreSQL
- 本地数据库文件：`backend/app.db`（运行时生成，不提交 Git）
- 后端启动时自动创建缺失的数据表
- 登录令牌仅以 SHA-256 摘要存入 `user_sessions`，有效期默认 30 天，退出登录后撤销
- 支持 6 位邮箱验证码；验证通过前，账户邮箱不会在双方匹配详情中展示
- 注册成功后自动登录并进入邮箱验证引导，可当场发送和填写验证码，也可暂时跳过后在“我的画像”中继续验证

旧版无密码注册和登录接口已经移除，避免绕过密码验证。普通用户 token 已用于邮箱验证接口鉴权；其他部分业务接口仍在逐步迁移，因此当前认证体系仍属于原型阶段。

### 管理员后台

- 独立的管理员注册、登录和多页面管理端
- 管理员申请默认处于 `pending`，需已批准管理员审核
- 支持用户列表、搜索、详情以及项目列表和项目详情
- 管理员密码与二级密码分别使用 bcrypt 哈希
- 管理接口使用 Bearer token 验证
- 初始管理员由 `backend/init_admin.py` 创建；当前脚本仍使用脚本内置的初始化参数，文档不展示具体密码。正式部署前应改为从部署平台的密钥环境变量读取，并重新初始化或重置初始管理员密码

### 第二轮视觉与交互系统

- 新增 `shared_ui` 共享设计系统，用户端和管理端复用主题、品牌与数据组件
- 登录注册页使用全屏科研协作网络主视觉、深色遮罩和玻璃表单
- 用户工作台采用浅色内容区、深色侧栏以及蓝、青、紫、绿多色信息层级
- 管理端使用紫色身份强调，危险操作统一使用红色，成功操作使用绿色
- 综合匹配度使用圆环展示，技能、时间、经验使用独立进度条，避免饼图造成占比误解
- 首页指标卡、项目卡片、通知、空状态、状态徽章和页面标题已统一
- 页面入场、卡片悬停、按钮反馈、分数圆环和进度条具备轻量动效
- 支持减少动态效果的系统偏好，不依赖额外 JavaScript 动画库
- 已适配桌面、平板和手机：平板指标两列，手机表单和操作区单列
- 动态 HTML 数据统一转义，避免用户名、项目名等内容造成 HTML 注入

### 第三轮动效与体验精修

- 页面入场调整为约 240ms 的淡入上移，降低页面重跑后的突兀感
- 原生展开器增加标题悬停、键盘焦点、箭头旋转和内容淡入，不强制模拟动态高度
- 按钮、提示框、卡片和侧栏导航保留低幅度过渡，避免影响信息阅读
- 管理端复用同一动效规则，但保持更克制的信息密度
- 成功操作在原有 `st.success` 基础上增加 Toast 反馈
- 保留 `prefers-reduced-motion`，系统减少动态效果时自动关闭非必要动画
- 未修改后端、数据库、匹配算法、接口格式或第三方依赖

### 我的画像

- 使用自然语言描述技能、经历、兴趣、协作偏好和每周时间
- 通过大模型解析为结构化画像
- 自动校验、补全和修正模型返回字段
- 解析结果可编辑并保存
- 再次登录时自动读取已有画像
- 可向注册邮箱发送验证码并完成真实性验证
- 验证码只保存 HMAC-SHA256 摘要，10 分钟过期，具备重发间隔、每日额度和错误次数限制

### 邮箱验证与隐私

- 邮件通过 Resend HTTPS API 发送，不在项目中保存邮件服务密钥
- 验证码默认 10 分钟有效，同一账号或邮箱 24 小时内最多发送 10 次
- 连续发送默认需要间隔 60 秒，单个验证码最多允许 5 次错误尝试
- 新验证码生成后，旧的未使用验证码立即失效
- 验证码只保存带独立 Pepper 的 HMAC-SHA256 摘要
- 邮箱验证接口要求有效的 Bearer token，服务端数据库只保存 token 的 SHA-256 摘要
- 邮箱验证未启用或邮件服务配置不完整时，页面会保留原有业务能力并给出明确提示
- 双方达成互选后，只有已验证的账户邮箱才会作为联系方式展示

注册流程如下：

```text
填写账号与邮箱
→ 创建账号并自动登录
→ 发送 6 位验证码
→ 输入验证码完成验证
→ 进入平台
```

用户也可以选择“稍后验证，进入平台”。未验证状态不会阻止画像、项目和匹配功能，
但账号邮箱不会作为双方互选后的可信联系方式展示。

### 发布与管理项目

- 填写项目名称、需求描述和开放范围
- AI 提取所需技能、时间要求、优先条件、项目类型和背景
- 解析结果可编辑后发布
- “我的项目”按时间倒序展示已发布项目
- 使用展开面板查看完整需求

### 匹配推荐

- 支持“同校优先”和“跨校开放”筛选
- 从所有招募中的项目生成推荐列表
- 按综合匹配度降序排列
- 展示技能、时间、经历三项得分和解释文案
- 匹配结果写入 `match_records`
- 同一用户与项目已有经验分时复用缓存，减少重复 AI 调用

匹配卡片支持展开“匹配分析”，使用柱状图直观展示技能、时间和经验三个维度，辅助用户理解总分来源。

### 通知中心

- 候选人表达兴趣、双方互选、项目方拒绝、项目状态变化时发送站内通知
- 项目删除、平台下架或恢复时通知相关用户
- 支持未读数量、单条已读、全部已读和关联项目跳转

### 收藏与意见反馈

- 用户可以收藏、取消收藏并查看收藏项目
- 重复收藏采用幂等处理，不会产生重复数据
- 用户可以提交功能建议、匹配不准确、使用问题、内容举报、账号问题等反馈
- 用户可以查看反馈处理状态和管理员回复

### 管理员运营与内容治理

- 管理员可以查看、筛选、回复和关闭用户反馈
- 管理端提供用户、项目、反馈和匹配相关基础统计及图表
- 管理员可以填写原因下架项目，也可以恢复项目
- 被下架项目不会出现在项目发现和匹配推荐中
- 治理操作记录原因、处理时间和原状态，并通知相关用户

### 双向意向后端能力

后端和用户端已经支持：

- 候选用户标记对项目感兴趣
- 查询项目下所有感兴趣用户
- 项目发起人标记对候选用户感兴趣
- 判断双方是否达成双向意向

前端“感兴趣”按钮已经接入接口，成功后持久化状态并禁用重复点击；“我的项目”中可以查看候选人并处理感兴趣/暂不考虑，双方匹配后可以按隐私规则查看联系方式。

## 匹配算法

### 技能匹配

系统先归一化用户技能、兴趣和项目所需技能，再由大模型判断语义相似度。相似度不低于 `0.7` 记为命中；AI 调用失败时降级为不区分大小写的字面匹配。

兴趣命中只按半个技能命中计算：

```text
skill_match = min(
    (技能命中数 + 0.5 × 兴趣命中数) / 项目所需技能数,
    1.0
)
```

以项目需求数量为分母，表示用户对项目能力要求的覆盖程度。

### 时间匹配

系统支持从“每周12小时”“10小时/周”“6 hours/week”“6 h/week”等格式提取时间。

```text
用户时间 >= 项目要求          1.0
用户时间 >= 项目要求 × 0.8    0.7
用户时间 >= 项目要求 × 0.5    0.4
用户时间 <  项目要求 × 0.5    0.1
任一方无法解析                0.5
```

### 经历匹配

系统使用大模型结合用户经历、项目类型和项目背景生成 `0～1` 的语义相关性分数。调用失败或结果无法解析时使用中性分 `0.5`。

### 综合得分

```text
total_score = skill_match × 0.6
            + time_match × 0.2
            + experience_match × 0.2
```

技能权重最高，因为它反映项目核心任务覆盖度；时间反映合作可执行性；经历反映迁移成本。当前权重和阈值是原型阶段的可解释规则，尚未基于大规模真实合作数据完成统计校准。

## 技术栈

- 前端：Streamlit
- 后端：FastAPI、Uvicorn
- 数据库：SQLite（本地）、PostgreSQL（云端）、SQLAlchemy、Alembic
- AI：OpenAI Python SDK 兼容接口
- 默认模型：`qwen-plus`
- HTTP：Requests
- 密码哈希：PBKDF2-HMAC-SHA256、bcrypt
- 邮件服务：Resend HTTPS API

## 项目结构

```text
知遇LinkLab/
├── backend/
│   ├── main.py          # API、匹配算法和业务逻辑
│   ├── ai_service.py    # AI 解析、归一化与语义评分
│   ├── email_service.py # 邮箱验证码邮件发送适配器
│   ├── database.py      # 数据库连接、会话和初始化
│   ├── models.py        # SQLAlchemy 数据模型
│   ├── alembic/         # 正式数据库迁移脚本
│   ├── alembic.ini      # Alembic 配置
│   ├── app.db           # 本地运行时生成的 SQLite 数据库
│   ├── init_admin.py    # 初始化管理员（当前脚本参数需后续安全加固）
│   └── requirements.txt
├── frontend/
│   ├── app.py           # Streamlit 用户端
│   └── requirements.txt
├── frontend_admin/      # Streamlit 管理员端
│   ├── admin_app.py
│   ├── ui.py            # 管理端共享界面入口
│   └── requirements.txt
├── shared_ui/
│   ├── theme.py         # 用户端、认证页和管理端主题
│   ├── components.py    # 品牌、指标、状态、分数与空状态组件
│   └── assets/          # 桌面和移动端科研协作主视觉
├── data/
│   └── zhilink.db       # 旧数据库迁移备份
├── tests/               # 后端安全逻辑和 Streamlit 回归测试
├── render.yaml          # Render 后端部署配置
├── .env.example         # 环境变量示例，不包含真实密钥
└── README.md
```

## 数据表

- `users`：账号和学校信息
- `user_sessions`：普通用户登录会话，只保存 token 摘要、有效期和撤销状态
- `email_verifications`：验证码摘要、有效期、尝试次数和使用状态
- `user_profiles`：用户结构化画像
- `projects`：项目基本信息和状态
- `project_profiles`：结构化项目需求
- `match_records`：匹配分数及候选用户意向
- `owner_interests`：项目发起人对候选用户的意向
- `notifications`：站内通知
- `favorite_projects`：项目收藏
- `feedback`：用户反馈和管理员处理结果

## 环境配置

建议使用 Python 3.10 或更高版本。

```powershell
cd C:\Users\zhang\Desktop\知遇LinkLab
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
python -m pip install streamlit
```

配置通义千问 OpenAI 兼容接口：

```powershell
$env:LLM_API_KEY = "你的 DashScope API Key"
$env:LLM_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
$env:LLM_MODEL = "qwen-plus"
```

不要将真实 API Key 写入代码或提交到 Git。

需要在本地测试邮箱验证时，再配置以下变量：

```powershell
$env:EMAIL_VERIFICATION_ENABLED = "true"
$env:EMAIL_PROVIDER = "resend"
$env:EMAIL_API_KEY = "你的 Resend API Key"
$env:EMAIL_FROM = "知遇 LinkLab <verify@你的已验证域名>"
$env:EMAIL_CODE_PEPPER = "至少 32 位、与 API Key 不同的随机密钥"
```

尚未完成 Resend 发件域名验证时，应保持
`EMAIL_VERIFICATION_ENABLED=false`。验证码有效期、发送间隔、每日限额和最大尝试次数
可通过 `.env.example` 中对应变量调整。

创建初始管理员（当前脚本）：

```powershell
cd C:\Users\zhang\Desktop\知遇LinkLab\backend
python init_admin.py
```

注意：当前 `init_admin.py` 尚未读取 `INITIAL_ADMIN_PASSWORD` 和
`INITIAL_ADMIN_USER_PASSWORD`。这两个环境变量目前不会改变初始化密码；公网正式使用前必须先完成该安全加固，不能直接把脚本内置密码用于生产环境。

## 启动方式

后端：

```powershell
cd C:\Users\zhang\Desktop\知遇LinkLab\backend
uvicorn main:app --reload --port 8000
```

前端：

```powershell
cd C:\Users\zhang\Desktop\知遇LinkLab\frontend
streamlit run app.py
```

管理员端：

```powershell
cd C:\Users\zhang\Desktop\知遇LinkLab\frontend_admin
streamlit run admin_app.py --server.port 8502
```

## 云平台启动配置

### FastAPI 后端（Render）

仓库根目录提供了 `render.yaml`。手动创建 Render Web Service 时使用：

```text
Root Directory: backend
Build Command: pip install -r requirements.txt && alembic upgrade head
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
Health Check Path: /api/health
```

免费 Render 服务不提供 Pre-Deploy Command，因此迁移在 Build Command 中执行。
迁移返回非零状态时构建失败，应用不会带着不完整的数据库结构启动。不要把
`alembic upgrade head` 拼接进 Start Command，否则每次服务重启都会重复执行迁移。

后端必须配置以下环境变量：

```text
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/database
LLM_API_KEY=你的 DashScope API Key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus
EMAIL_VERIFICATION_ENABLED=true
EMAIL_PROVIDER=resend
EMAIL_API_KEY=你的 Resend API Key
EMAIL_FROM=知遇 LinkLab <verify@你的已验证域名>
EMAIL_CODE_PEPPER=至少32位的独立随机密钥
EMAIL_CODE_EXPIRE_MINUTES=10
EMAIL_SEND_INTERVAL_SECONDS=60
EMAIL_DAILY_LIMIT=10
EMAIL_MAX_ATTEMPTS=5
```

Render 提供的 PostgreSQL 地址如果以 `postgresql://` 开头，可以改为
`postgresql+psycopg2://`。`EMAIL_API_KEY`、`EMAIL_CODE_PEPPER`、数据库密码和
LLM Key 都属于敏感信息，不得提交到 GitHub。正式开启邮箱验证前，应先在
Resend 验证发件域名，并确认 `EMAIL_FROM` 使用该域名；未完成时保持
`EMAIL_VERIFICATION_ENABLED=false`。建议最后再将开关改为 `true`，避免服务在配置不完整时对外开放发送入口。

### Streamlit 用户端（Streamlit Community Cloud）

```text
Repository: 当前 GitHub 仓库
Branch: main
Main file path: frontend/app.py
Root Directory: 仓库根目录（Streamlit Cloud 通过 Main file path 定位）
Build Command: 平台自动执行 pip install -r frontend/requirements.txt
Start Command: 平台自动执行 streamlit run frontend/app.py
```

在 Streamlit Secrets 或应用环境配置中设置：

```text
BACKEND_URL=https://你的-Render-后端地址
```

### Streamlit 管理端（Streamlit Community Cloud）

创建第二个 Streamlit 应用：

```text
Repository: 当前 GitHub 仓库
Branch: main
Main file path: frontend_admin/admin_app.py
Root Directory: 仓库根目录
Build Command: 平台自动执行 pip install -r frontend_admin/requirements.txt
Start Command: 平台自动执行 streamlit run frontend_admin/admin_app.py
```

同样设置：

```text
BACKEND_URL=https://你的-Render-后端地址
```

### 数据库迁移

Alembic 配置位于 `backend/alembic.ini`，迁移文件位于
`backend/alembic/versions/`。命令必须在 `backend` 目录执行：

```powershell
cd C:\Users\zhang\Desktop\知遇LinkLab\backend
alembic upgrade head
```

新建迁移的开发流程：

```powershell
alembic revision --autogenerate -m "describe schema change"
alembic upgrade head
```

新建的 SQLite 或 PostgreSQL 空库应直接执行 `alembic upgrade head`。已有旧版
`app.db` 必须先备份并检查结构，不能直接标记到最新版本。若数据库已完整包含
`0007_user_ban_fields` 及以前的结构，可执行：

```powershell
alembic stamp 0007_user_ban_fields
alembic upgrade head
```

这样会实际执行 `0008_email_verification`，创建登录会话和邮箱验证结构。若旧库结构
不确定，应先复制数据库进行迁移演练，不要直接对唯一数据副本执行 `stamp`。

### 本地模拟生产启动

PowerShell 中分别启动三个服务：

```powershell
cd C:\Users\zhang\Desktop\知遇LinkLab\backend
$env:PORT = "8000"
alembic upgrade head
uvicorn main:app --host 0.0.0.0 --port $env:PORT
```

```powershell
cd C:\Users\zhang\Desktop\知遇LinkLab\frontend
$env:BACKEND_URL = "http://localhost:8000"
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

```powershell
cd C:\Users\zhang\Desktop\知遇LinkLab\frontend_admin
$env:BACKEND_URL = "http://localhost:8000"
streamlit run admin_app.py --server.address 0.0.0.0 --server.port 8502
```

本地继续使用已有 `backend/app.db` 时，应按上一节先备份、确认结构，再从对应版本
执行迁移；不要为了消除报错直接运行 `alembic stamp head`。

访问地址：

- 前端：<http://localhost:8501>
- 管理员端：<http://localhost:8502>
- 健康检查：<http://localhost:8000/api/health>
- Swagger：<http://localhost:8000/docs>

## API 概览

| 方法 | 路径 | 功能 |
| --- | --- | --- |
| GET | `/api/health` | 健康检查 |
| POST | `/api/auth/register` | 用户密码注册 |
| POST | `/api/auth/login` | 用户名密码登录 |
| POST | `/api/auth/logout` | 撤销当前用户会话 |
| GET | `/api/email/status` | 查询当前邮箱验证状态（Bearer token） |
| POST | `/api/email/send_code` | 向当前账户邮箱发送验证码（Bearer token） |
| POST | `/api/email/verify` | 校验验证码并标记邮箱已验证（Bearer token） |
| POST | `/api/admin/register` | 管理员注册申请 |
| POST | `/api/admin/login` | 管理员登录 |
| GET/POST | `/api/admin/*` | 管理员查询与审核接口 |
| POST | `/api/parse_profile` | AI 解析用户画像 |
| POST | `/api/save_profile` | 保存或更新画像 |
| GET | `/api/profile/{user_id}` | 获取画像 |
| POST | `/api/parse_project` | AI 解析项目需求 |
| POST | `/api/create_project` | 发布项目 |
| GET | `/api/project/{project_id}` | 获取项目详情 |
| GET | `/api/my_projects/{user_id}` | 获取用户发布的项目 |
| POST | `/api/match` | 单次匹配 |
| GET | `/api/match_list/{user_id}` | 批量项目推荐 |
| POST | `/api/interest` | 用户标记感兴趣 |
| GET | `/api/interested_users/{project_id}` | 查询感兴趣用户 |
| POST | `/api/owner_interest` | 发起人标记候选人 |
| POST | `/api/check_mutual` | 检查双向意向 |
| POST | `/api/project_status` | 更新项目状态 |
| DELETE | `/api/project/{project_id}` | 删除项目及关联数据 |
| GET/POST | `/api/notifications/*` | 查询通知和标记已读 |
| GET/POST/DELETE | `/api/favorites/*` | 收藏、取消收藏和查看收藏 |
| POST | `/api/feedback` | 提交用户反馈 |
| GET | `/api/my_feedback/{user_id}` | 查看我的反馈 |
| GET | `/api/admin/statistics` | 管理员运营统计 |
| POST | `/api/admin/project/{project_id}/moderation` | 下架或恢复项目 |
| GET/POST | `/api/admin/feedback*` | 管理员查看和处理反馈 |

## 快速验收

1. 打开健康检查，确认返回 `{"status":"ok"}`。
2. 注册两个不同学校的账号，验证正确密码可登录、错误密码被拒绝。
3. 配置邮件服务后发送邮箱验证码，确认错误验证码被拒绝、正确验证码验证成功。
4. 在邮箱未验证时完成双方互选，确认邮箱不展示；验证后确认邮箱正常展示。
5. 为一个账号解析并保存画像，刷新后确认数据仍存在。
6. 用另一个账号发布项目，在“我的项目”中展开查看详情。
7. 回到候选账号，在“匹配推荐”切换同校和跨校范围。
8. 确认项目按总分排序，并显示三项进度条及解释。
9. 在 Swagger 中测试意向接口和双向确认接口。
10. 创建初始管理员，在管理员端验证登录、用户和项目查询。
11. 收藏项目，确认“我的收藏”可以查看详情和取消收藏。
12. 提交意见反馈，在管理端回复并确认用户收到通知。
13. 在管理端下架项目，确认项目从发现和推荐中消失，再恢复项目。
14. 分别以 `1440×900`、`1024×768` 和 `390×844` 检查登录页、首页、匹配推荐和管理控制台，确认没有文字重叠或横向滚动。
15. 检查页面入场、匹配分析展开收起、按钮反馈、加载状态和系统减少动态效果模式。

## 当前边界与下一步

当前版本已经可以完整演示核心价值，但距离正式生产产品仍有以下差距：

- 普通用户 token 尚未应用到全部业务接口，部分接口仍依赖请求中的 `user_id/owner_id`
- 旧版无密码用户没有自动迁移密码，需要补充设置或重置密码流程
- 缺少找回密码、修改密码和“退出所有设备”等完整账号安全能力
- 管理员 token 保存在进程内存中，服务重启后失效且多实例不能共享
- 缺少取消意向和项目编辑；状态更新及删除已有后端接口但未接入前端
- 为兼容历史 SQLite 数据，`init_db()` 仍保留轻量补列逻辑；长期应统一由 Alembic 管理结构变更
- 已具备邮箱验证安全测试和 Streamlit 核心流程回归测试，但覆盖范围尚未达到完整生产级别
- AI 推荐存在非确定性，批量推荐的技能相关调用仍可能较慢
- 时间只处理带小时单位的单一周投入表达
- 匹配参数尚未用真实合作结果进行离线评估和校准
- 缺少完整的隐私授权、敏感信息处理和操作审计
- `init_admin.py` 仍包含内置初始化凭据，尚未读取示例环境变量；正式部署前必须完成安全改造并轮换现有初始密码
- 反馈、收藏和治理已完成基础版本，还可以继续增加分页、批量操作和更细的运营报表
- Streamlit 页面切换仍以脚本重跑为基础，当前采用新页面淡入上移，不是 React 式连续转场

## 当前定位

当前版本已经形成：

```text
注册登录
→ 用户画像解析与保存
→ 项目需求解析与发布
→ 项目发现、筛选和收藏
→ 数据库存储
→ 批量匹配与排序
→ 可解释结果
→ 双向意向与联系方式解锁
→ 通知和用户反馈
→ 管理员统计与项目治理
```

因此可以将它视为功能比较完整、页面可用、具备基础运营能力的科研协作匹配原型，而不应描述为已经达到生产可用标准。

