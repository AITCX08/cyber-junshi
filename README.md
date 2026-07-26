# 赛博军师 / Cyber Junshi

[English](README.en.md)

> 你的个人 Agent 不缺工具，缺的是判断力。

赛博军师是一个 Agent 原生、本地优先的通用决策薄核。它通过 MCP 向个人 Agent 提供
安全路由、事实分层、方案代价和停止条件四套可解释机制；宿主 Agent 负责理解语言，
赛博军师负责校验结构，并把用户明确要求保存的结果写入本地 SQLite。

它不是心理诊断、紧急救援、法律意见，也不保证任何关系或决策结果。

## 四套机制

| 机制 | 回答的问题 |
| --- | --- |
| 安全路由 | 当前是普通、较高风险还是紧急场景？ |
| 事实分层 | 哪些是观察事实、合理推测和关键未知？ |
| 方案代价 | 短期收益、长期成本、可逆性、风险和信息增益分别如何？ |
| 停止条件 | 行动何时继续、降级或停止？ |

## 直接从 GitHub 运行

只需安装 [uv](https://docs.astral.sh/uv/)：

```bash
uvx --from git+https://github.com/AITCX08/cyber-junshi cyber-junshi demo
uvx --from git+https://github.com/AITCX08/cyber-junshi cyber-junshi doctor
uvx --from git+https://github.com/AITCX08/cyber-junshi cyber-junshi serve
```

未来发布到 PyPI 后可以使用短命令：

```bash
uvx cyber-junshi serve
```

v0.1 使用 MCP stdio，由宿主 Agent 启动并管理服务进程。

## 一键接入个人 Agent

安装命令默认只预览，不写文件。确认预览后加 `--apply`；程序只修改目标 Agent 的
配置，保留无关设置，并在覆盖现有文件前创建时间戳备份。

```bash
uvx --from git+https://github.com/AITCX08/cyber-junshi cyber-junshi install hermes
uvx --from git+https://github.com/AITCX08/cyber-junshi cyber-junshi install openclaw
uvx --from git+https://github.com/AITCX08/cyber-junshi cyber-junshi install codex
uvx --from git+https://github.com/AITCX08/cyber-junshi cyber-junshi install claude-desktop
```

确认后执行，例如：

```bash
uvx --from git+https://github.com/AITCX08/cyber-junshi cyber-junshi install hermes --apply
```

详细说明：[Hermes](adapters/hermes/README.md)、[OpenClaw](adapters/openclaw/README.md)、
[Codex](adapters/codex/README.md)、[Claude Desktop](adapters/claude-desktop/README.md)。

## 十一个 MCP 工具

| 工具 | 作用 |
| --- | --- |
| `assess_safety` | 只读安全筛查，返回等级、依据和下一步 |
| `structure_case` | 只读整理事实、推测和未知 |
| `compare_options` | 只读、可解释的方案排序 |
| `create_action_plan` | 只读校验观察窗口和退出规则 |
| `record_outcome` | 明确触发的本地 SQLite 写入 |
| `review_decision` | 只读复盘一条已保存结果 |
| `search_knowledge` | 只读检索本地知识，并返回证据等级和来源标识 |
| `remember_question` | 明确保存一个对象的问题、摘要和选定记忆 |
| `recall_subject` | 只读取指定对象的近期问题和有效记忆 |
| `list_subjects` | 只列对象别名和数量，不返回问题正文 |
| `forget_subject` | 确认后硬删除一个对象及其关联记忆 |

## 独立生成的知识包

[`knowledge/`](knowledge/) 下包含 19 篇核心知识和 15 篇实用表达。每条内容都在
[`knowledge/catalog.yaml`](knowledge/catalog.yaml) 中登记来源与证据等级。上游
`goutoujunshi` 仅作为选题发现线索；本仓库没有导入其正文、案例、话术模板、提示词或源码。

内容变更应先阅读[来源与净室政策](CONTENT_PROVENANCE.md)，发布前运行：

```bash
uv run cyber-junshi audit-knowledge --root .
```

## 效果演示

### 问：对象 A 连续两次临时取消见面，我还要继续约吗？

赛博军师  ❯ 先别急着把“两次取消”翻译成“不喜欢你”。现在能确认的只有两件事：
她两次临时取消了，也还没给出新的具体时间；原因、意愿和她最近的状态都还是未知。你不用替她
补完答案，也不用靠连发消息把未知变成更大的消耗。发一次就够：
“你连续两次临时取消，我们可以在你方便时重新约；如果你暂时不想继续，也请直接告诉我，我会尊重并不再追问。”
然后给这件事 48 小时。她如果给出具体时间，就按新的安排走；如果明确拒绝，或者 48 小时未回复，
就停止追问。你要的是一段自愿的沟通，不是一场靠反复确认换来的回应。

### 问：他最近回复越来越少，我忍不住想多发几条消息确认他是不是不在乎我。

赛博军师  ❯ “回复越来越少”是观察，不是判决书。它可能意味着忙、状态差、兴趣下降，
也可能只是沟通节奏变了；你目前不知道的是哪一种。连发消息看似能缓解焦虑，实际只会把你的判断
交给对方每一次是否回复。可以只说一次你的感受和需要：
“我注意到我们最近联系少了些。我还愿意继续沟通，但也想知道你现在是否有这个意愿；如果你想要空间，直接告诉我就好。”
说完就给对方选择。如果对方说明想要空间、明确拒绝，或继续沉默，就尊重这个信号并停止追问。
边界不是拿来测试对方会不会挽留你，而是让你不必在不确定里持续消耗。

### 问：前任说想要空间，但我只是想发个问候，真的不能联系吗？

赛博军师  ❯ 如果对方已经明确说想要空间，“只是问候”仍然是一种联系；别把自己的想念
包装成对方必须接住的善意。你可以想念，也可以难受，但这不等于你有继续进入对方生活的权限。
现在更稳妥的做法是先停止联系，把想说的话写下来、找朋友支持、把生活重新安排起来。只有对方主动
恢复沟通时，你再决定是否回应；若有必须处理的财物或安全事项，也只用清晰、必要、可留痕的渠道沟通。
尊重空间不是放弃尊严，而是不靠绕过边界来维持一段已经暂停的关系。

## Skills

- `skills/cyber-junshi`：通用决策工作流。
- `skills/relationship`：关系场景示例，明确拒绝操控、跟踪、冒充、人格诊断和绕过边界。

## 本地数据与隐私

- 默认数据库：`~/.cyber-junshi/cyber-junshi.db`
- 可用 `CYBER_JUNSHI_DB=/path/to/file.db` 修改路径。
- 不需要云账号；无遥测、模型网关、聊天抓取或自动导入。
- 决策输入不会自动记录；只有明确调用 `record_outcome` 才保存结果。
- `remember_question` 仅在明确调用时，把提交的问题、摘要和选定记忆保存到一个本地对象别名下。
- `recall_subject` 不跨对象检索；`forget_subject` 必须确认后才级联硬删除。
- 仓库案例全部为虚构数据，并明确标记为 synthetic。

## 本地开发

```bash
git clone https://github.com/AITCX08/cyber-junshi.git
cd cyber-junshi
uv sync --extra dev
uv run pytest
uv run ruff check .
```

## Docker

```bash
docker build -t cyber-junshi .
docker run --rm -i -v cyber-junshi-data:/data cyber-junshi
```

v0.1 是 stdio 服务，因此需要保留标准输入（`-i`），并让 MCP 客户端启动容器。

## 明确不做

v0.1 不解密或抓取聊天、不检查用户账号、不提供 Web 仪表盘、不内置模型、不做云同步、
不强制依赖 OpenViking，也不自动化抖音或社群运营。

许可证：[Apache-2.0](LICENSE)。
