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

## 真实 Skill 工作流案例（虚构）

以下是合成案例，不是真实聊天或咨询记录；它不诊断任何人，也不保证关系结果。用户问：
“对象 A 连续两次临时取消见面，我该不该继续约？”宿主 Agent 负责理解问题和组织回复，
赛博军师负责用工具校验结构。工具结果是为说明流程而写的节选，不是对对象 A 动机的判断。

1. **选择 Skill 与安全路由。** 宿主 Agent 选择 `relationship` Skill，并先调用
   `assess_safety`。本例没有自伤、暴力、威胁、强迫、跟踪或隐私暴露信号，返回
   `level: "normal"`；因此可以继续分析。若出现这些信号，则先处理安全，不优化消息。
2. **检索而不冒充结论。** `search_knowledge("沟通 边界 一次澄清")` 返回本地资料的
   节选，例如 `{"id":"core-07","evidence_level":"E1","source_ids":["cdc-healthy-communication","project-four-mechanisms"]}`。
   证据等级和来源标识帮助审阅依据，但取消见面本身不能证明回避、冷淡或任何人格标签。
3. **分开事实、推断与未知。** `structure_case` 的输入与结果保持三层：
   - 事实：对象 A 两次临时取消；尚未提出新的具体时间。
   - 推断：对象 A 可能暂时不方便继续安排；这不是已证实的动机。
   - 未知：取消原因、是否仍愿意见面、何时方便。
4. **比较方案代价。** `compare_options` 比较“等待对方提出时间”“发送一次澄清”“不再联系”。
   此例选择可逆、信息增益较高的“一次澄清”，而不是反复追问；“不再联系”始终是有效选项。
5. **先写停止条件再行动。** `create_action_plan` 设定 48 小时观察窗口：若对方主动给出
   具体时间则继续；若明确说不想继续则停止；48 小时未回复也停止，不再追加消息、换号或请他人代为联系。
   唯一消息是：“你连续两次临时取消，我们可以在你方便时重新约；如果你暂时不想继续，也请直接告诉我，我会尊重并不再追问。”
6. **记忆必须显式同意且按对象隔离。** 宿主 Agent 先问“你是否明确同意把这次问题和
   ‘只发送一次澄清、未回复即停止’保存到本地的对象 A 记录中？”只有用户回答明确同意后，
   才调用 `remember_question`。之后调用 `recall_subject("对象 A")` 只返回对象 A 的问题与
   有效记忆；它不会跨对象检索，也不会在后台自动保存。

宿主 Agent 负责措辞、上下文和最终呈现；赛博军师负责安全路由、证据分层、方案比较、
停止条件以及用户明确授权后的本地记忆。

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
