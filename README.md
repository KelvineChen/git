# 知遇LinkLab

知遇LinkLab 是一个面向高校科研协作的智能项目匹配原型。用户可以建立可编辑的能力画像，发布科研项目，并根据技能、时间投入和项目经历获得可解释的项目推荐。

当前版本已经具备从注册登录到画像保存、项目发布、批量推荐和意向记录的基本业务闭环，适合作为功能完整的毛胚版本继续迭代。

## 已实现功能

### 账号与数据持久化

- 用户注册：用户名、邮箱、学校、专业、年级
- 邮箱登录及 Streamlit 会话状态
- SQLite + SQLAlchemy 持久化
- 数据库文件：`backend/app.db`
- 后端启动时自动创建缺失的数据表

当前登录是原型简化方案，只使用邮箱，不包含密码或身份验证令牌。

### 我的画像

- 使用自然语言描述技能、经历、兴趣、协作偏好和每周时间
- 通过大模型解析为结构化画像
- 自动校验、补全和修正模型返回字段
- 解析结果可编辑并保存
- 再次登录时自动读取已有画像

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

### 双向意向后端能力

后端已经支持：

- 候选用户标记对项目感兴趣
- 查询项目下所有感兴趣用户
- 项目发起人标记对候选用户感兴趣
- 判断双方是否达成双向意向

前端“感兴趣”按钮目前仍是提示状态，尚未接入这些接口；发起人候选列表和双向确认页面也尚未实现。

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
- 数据库：SQLite、SQLAlchemy
- AI：OpenAI Python SDK 兼容接口
- 默认模型：`qwen-plus`
- HTTP：Requests

## 项目结构

```text
知遇LinkLab/
├── backend/
│   ├── main.py          # API、匹配算法和业务逻辑
│   ├── ai_service.py    # AI 解析、归一化与语义评分
│   ├── database.py      # 数据库连接、会话和初始化
│   ├── models.py        # SQLAlchemy 数据模型
│   ├── app.db           # SQLite 数据库
│   └── requirements.txt
├── frontend/
│   └── app.py           # Streamlit 页面
├── data/
│   └── zhilink.db       # 旧数据库迁移备份
└── README.md
```

## 数据表

- `users`：账号和学校信息
- `user_profiles`：用户结构化画像
- `projects`：项目基本信息和状态
- `project_profiles`：结构化项目需求
- `match_records`：匹配分数及候选用户意向
- `owner_interests`：项目发起人对候选用户的意向

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

访问地址：

- 前端：<http://localhost:8501>
- 健康检查：<http://localhost:8000/api/health>
- Swagger：<http://localhost:8000/docs>

## API 概览

| 方法 | 路径 | 功能 |
| --- | --- | --- |
| GET | `/api/health` | 健康检查 |
| POST | `/api/register` | 注册 |
| POST | `/api/login` | 邮箱登录 |
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

## 快速验收

1. 打开健康检查，确认返回 `{"status":"ok"}`。
2. 注册两个不同学校的账号，验证邮箱登录。
3. 为一个账号解析并保存画像，刷新后确认数据仍存在。
4. 用另一个账号发布项目，在“我的项目”中展开查看详情。
5. 回到候选账号，在“匹配推荐”切换同校和跨校范围。
6. 确认项目按总分排序，并显示三项进度条及解释。
7. 在 Swagger 中测试意向接口和双向确认接口。

## 当前不完整项

这是可以完整演示核心价值的毛胚版本，但距离正式产品仍有以下差距：

- 前端“感兴趣”按钮尚未调用 `POST /api/interest`
- 尚无发起人查看候选人、标记意向和双向成功的前端页面
- 登录没有密码、Token、权限校验和账号安全机制
- 后端目前无法验证调用 `owner_interest` 的请求者确实是项目发起人
- 缺少取消意向、关闭项目、编辑项目和删除项目
- 缺少数据库迁移工具、唯一约束补强和系统化自动测试
- AI 推荐存在非确定性，批量推荐的技能相关调用仍可能较慢
- 时间只处理带小时单位的单一周投入表达
- 匹配参数尚未用真实合作结果进行离线评估和校准
- 缺少隐私授权、敏感信息处理、审计和生产部署配置

## 当前定位

当前版本已经形成：

```text
注册登录
→ 用户画像解析与保存
→ 项目需求解析与发布
→ 数据库存储
→ 批量匹配与排序
→ 可解释结果
→ 双向意向后端基础
```

因此可以将它视为功能比较完整、能够持续微调的科研协作匹配原型，而不应描述为已经达到生产可用标准。

