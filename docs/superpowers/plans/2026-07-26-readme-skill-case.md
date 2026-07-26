# README Skill 工作流案例实施计划

> **供执行型 Agent 使用：** 必须使用 `superpowers:executing-plans` 逐项实施；步骤使用复选框追踪。

**目标：** 在中英文 README 加入可核验的虚构关系 Skill 完整工作流案例，并以测试防止安全声明和工具流程退化。

**架构：** 仅修改文档和文档契约测试，不增加运行时代码。案例按安全路由、知识检索、事实分层、方案比较、行动计划、显式对象记忆的顺序呈现；工具结果均为说明性节选。

**技术栈：** Markdown、Pytest、Ruff、现有 `cyber-junshi audit-knowledge` CLI。

## 全局约束

- Markdown 默认使用中文；`README.en.md` 是明确的英文国际化例外。
- 案例必须是虚构合成，不包含真实个人信息、原始聊天、密钥、数据库路径或生产记录。
- 不诊断动机；只能发送一条自愿、非指控式澄清消息，未回复即停止。
- `remember_question` 只能在用户明确同意后调用；`recall_subject` 只能展示同一对象别名的记录。
- 不新增依赖，不改变 MCP、SQLite 或知识检索运行时代码。

---

## 文件结构

- 修改：`README.md` — 添加中文默认的虚构工作流案例。
- 修改：`README.en.md` — 添加语义等价的英文案例。
- 修改：`tests/test_public_artifacts.py` — 断言案例必须出现的工具和安全边界。

### 任务 1：先建立 README 案例的文档契约测试

**文件：**

- 修改：`tests/test_public_artifacts.py`
- 测试：`tests/test_public_artifacts.py::test_readmes_include_a_safe_skill_workflow_case`

**接口：**

- 消费：仓库根目录 UTF-8 编码的 `README.md` 和 `README.en.md`。
- 产出：`test_readmes_include_a_safe_skill_workflow_case`，要求案例包含七个关键工具和安全文本。

- [x] **步骤 1：编写失败测试**

在 `tests/test_public_artifacts.py` 追加以下测试：

```python
def test_readmes_include_a_safe_skill_workflow_case() -> None:
    required_tools = {
        "assess_safety", "search_knowledge", "structure_case", "compare_options",
        "create_action_plan", "remember_question", "recall_subject",
    }
    required_phrases = {
        "README.md": ("虚构", "明确同意", "48 小时", "未回复"),
        "README.en.md": ("fictional", "explicitly agrees", "48-hour", "no reply"),
    }
    for readme_name, phrases in required_phrases.items():
        content = (ROOT / readme_name).read_text(encoding="utf-8")
        for tool in required_tools:
            assert tool in content
        for phrase in phrases:
            assert phrase in content
```

- [x] **步骤 2：运行测试并确认失败**

运行：

```powershell
$env:UV_CACHE_DIR='C:\\tmp\\uv-cache'; $env:TEMP='C:\\tmp'; $env:TMP='C:\\tmp'; uv run pytest tests/test_public_artifacts.py::test_readmes_include_a_safe_skill_workflow_case -q --basetemp='C:\\tmp\\pytest-readme-case-red'
```

预期：失败，现有 README 缺少 `48 小时` / `48-hour` 案例文字。

### 任务 2：在两个 README 加入语义等价的完整案例

**文件：**

- 修改：`README.md`
- 修改：`README.en.md`
- 测试：`tests/test_public_artifacts.py::test_readmes_include_a_safe_skill_workflow_case`

**接口：**

- 消费：现有七个 MCP 工具的名称和显式写入语义。
- 产出：中文 `## 真实 Skill 工作流案例（虚构）` 与英文 `## Real Skill workflow case (fictional)`。

- [x] **步骤 1：写入中文案例**

在 `README.md` 的 `## Skills` 之前新增章节。首句必须为“以下是合成案例，不是真实聊天或咨询记录。”；六个编号步骤须依次展示：选择 `relationship` Skill；`assess_safety` 返回 `normal`；`search_knowledge` 包含 `evidence_level` 与 `source_ids`；`structure_case` 分开事实、推断、未知；`compare_options` / `create_action_plan` 比较等待、一次澄清、不再联系并设 48 小时窗口；用户明确同意后调用 `remember_question`，再以 `recall_subject` 回忆“对象 A”。

- [x] **步骤 2：写入中文唯一消息与停止条件**

消息必须是：“你连续两次临时取消，我们可以在你方便时重新约；如果你暂时不想继续，也请直接告诉我，我会尊重并不再追问。” 案例必须写明未回复即停止，且取消见面不等于动机、人格或诊断。

- [x] **步骤 3：写入英文等价案例**

在 `README.en.md` 的 `## Skills` 之前新增章节，首句必须为“This is a synthetic example, not a real chat or consultation record.”。保持中文案例相同的六步、工具顺序、一次澄清、48-hour observation window、no reply stop condition、explicitly agrees 后记忆、按对象隔离回忆。

- [x] **步骤 4：运行定向测试并确认通过**

运行任务 1 步骤 2 的命令；预期：`1 passed`。

### 任务 3：执行完整验证并提交

**文件：**

- 修改：`README.md`
- 修改：`README.en.md`
- 修改：`tests/test_public_artifacts.py`
- 创建：`docs/superpowers/plans/2026-07-26-readme-skill-case.md`

**接口：**

- 消费：通过的定向案例测试。
- 产出：通过项目质量门禁的文档提交。

- [x] **步骤 1：执行完整测试**

运行：

```powershell
$env:UV_CACHE_DIR='C:\\tmp\\uv-cache'; $env:TEMP='C:\\tmp'; $env:TMP='C:\\tmp'; uv run pytest -q --basetemp='C:\\tmp\\pytest-readme-case-all'
```

预期：所有测试通过。

- [x] **步骤 2：执行静态检查、知识审计与差异检查**

运行：

```powershell
$env:UV_CACHE_DIR='C:\\tmp\\uv-cache'; $env:TEMP='C:\\tmp'; $env:TMP='C:\\tmp'; uv run ruff check .
$env:UV_CACHE_DIR='C:\\tmp\\uv-cache'; $env:TEMP='C:\\tmp'; $env:TMP='C:\\tmp'; uv run cyber-junshi audit-knowledge --root .
git diff --check
```

预期：Ruff 无违规，审计 JSON 的 `errors` 为空，差异检查无输出。

- [x] **步骤 3：提交明确范围的文件**

运行：

```powershell
git add -- README.md README.en.md tests/test_public_artifacts.py docs/superpowers/plans/2026-07-26-readme-skill-case.md
git diff --cached --check
git commit -m "docs: add safe skill workflow case"
```

预期：仅上述四个文件进入提交。
