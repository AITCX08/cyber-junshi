# README 效果演示实施计划

> **供执行型 Agent 使用：** 必须使用 `superpowers:executing-plans` 逐项实施；步骤使用复选框追踪。

**目标：** 将 README 的工具流程案例改成三条“问题 + 赛博军师完整回答”的效果演示，并以文档测试锁定展示主题和安全边界。

**架构：** 仅编辑 `README.md`、`README.en.md` 和公开文档测试。两个 README 都以效果演示为主，不出现工具调用、JSON、内部推理过程或额外案例来源说明；现有全局隐私文本保持不变。

**技术栈：** Markdown、Pytest、Ruff、现有 `cyber-junshi audit-knowledge` CLI。

## 全局约束

- Markdown 默认使用中文；`README.en.md` 是明确的英文国际化例外。
- 章节标题只能是“效果演示”及其英文等价标题，不在案例附近增加数据来源或生成方式说明。
- 三条案例依次覆盖连续取消见面、关系冷淡后的边界沟通、分开后是否联系。
- 每条回答必须区分观察与猜测，包含一个可执行下一步及停止条件。
- 不诊断动机或人格；不建议操控、跟踪、绕过拉黑、冒充、第三方施压或反复联系。
- 不新增依赖，不改变 MCP、SQLite、知识库或 Skill 接口。

---

## 文件结构

- 修改：`README.md` — 将六步工具流程替换成三条中文效果演示。
- 修改：`README.en.md` — 将六步工具流程替换成三条语义等价的英文效果演示。
- 修改：`tests/test_public_artifacts.py` — 将旧工作流断言改成效果演示断言。

### 任务 1：先建立效果演示的文档契约测试

**文件：**

- 修改：`tests/test_public_artifacts.py`
- 测试：`tests/test_public_artifacts.py::test_readmes_include_safe_effect_examples`

**接口：**

- 消费：根目录的 UTF-8 `README.md` 和 `README.en.md`。
- 产出：`test_readmes_include_safe_effect_examples`，验证标题、三条主题、一次消息、48 小时、未回复停止和对象隔离记忆说明。

- [x] **步骤 1：替换旧测试为失败测试**

将 `test_readmes_include_a_safe_skill_workflow_case` 整体替换为：

```python
def test_readmes_include_safe_effect_examples() -> None:
    required_phrases = {
        "README.md": (
            "## 效果演示", "连续两次临时取消", "回复越来越少", "前任", "48 小时",
            "未回复", "赛博军师  ❯",
        ),
        "README.en.md": (
            "## Effect examples", "cancelled two meetings", "replies have become sparse",
            "former partner", "48 hours", "no reply", "Cyber Junshi  ❯",
        ),
    }
    for readme_name, phrases in required_phrases.items():
        content = (ROOT / readme_name).read_text(encoding="utf-8")
        for phrase in phrases:
            assert phrase in content
```

- [x] **步骤 2：运行测试并确认失败**

运行：

```powershell
$env:UV_CACHE_DIR='C:\\tmp\\uv-cache'; $env:TEMP='C:\\tmp'; $env:TMP='C:\\tmp'; uv run pytest tests/test_public_artifacts.py::test_readmes_include_safe_effect_examples -q --basetemp='C:\\tmp\\pytest-effect-examples-red'
```

预期：失败，因为现有 README 没有“效果演示”标题和三条主题。

### 任务 2：加入中英文效果演示

**文件：**

- 修改：`README.md`
- 修改：`README.en.md`
- 测试：`tests/test_public_artifacts.py::test_readmes_include_safe_effect_examples`

**接口：**

- 消费：任务 1 的文档契约。
- 产出：中文 `## 效果演示` 与英文 `## Effect examples`，每个章节包含三条“问题 + 赛博军师回答”。

- [x] **步骤 1：替换中文旧案例章节**

删除从 `## 真实 Skill 工作流案例（虚构）` 到 `## Skills` 之前的全部旧案例内容，新增 `## 效果演示`。三条标题分别包含“连续两次临时取消”“回复越来越少”“前任”。每条回答以 `赛博军师  ❯` 开头；第一条包含一条非指控式消息、48 小时和未回复即停止；第二条把回复变少与不在乎区分开；第三条尊重对方提出的空间需求并拒绝借问候绕过边界。

- [x] **步骤 2：替换英文旧案例章节**

删除从 `## Real Skill workflow case (fictional)` 到 `## Skills` 之前的全部旧案例内容，新增 `## Effect examples`。三条主题和安全边界与中文等价，回答以 `Cyber Junshi  ❯` 开头，并包含 `cancelled two meetings`、`replies have become sparse`、`former partner`、`48 hours` 和 `no reply`。

- [x] **步骤 3：运行定向测试并确认通过**

运行任务 1 步骤 2 的命令；预期：`1 passed`。

### 任务 3：完整验证并提交

**文件：**

- 修改：`README.md`
- 修改：`README.en.md`
- 修改：`tests/test_public_artifacts.py`
- 创建：`docs/superpowers/plans/2026-07-26-readme-effect-examples.md`

**接口：**

- 消费：通过的定向效果演示测试。
- 产出：通过质量门禁的文档变更提交。

- [x] **步骤 1：执行完整测试**

运行：

```powershell
$env:UV_CACHE_DIR='C:\\tmp\\uv-cache'; $env:TEMP='C:\\tmp'; $env:TMP='C:\\tmp'; uv run pytest -q --basetemp='C:\\tmp\\pytest-effect-examples-all'
```

预期：所有测试通过。

- [x] **步骤 2：执行静态检查、知识审计与差异检查**

运行：

```powershell
$env:UV_CACHE_DIR='C:\\tmp\\uv-cache'; $env:TEMP='C:\\tmp'; $env:TMP='C:\\tmp'; uv run ruff check .
$env:UV_CACHE_DIR='C:\\tmp\\uv-cache'; $env:TEMP='C:\\tmp'; $env:TMP='C:\\tmp'; uv run cyber-junshi audit-knowledge --root .
git diff --check
```

预期：Ruff 无违规，知识审计 JSON 的 `errors` 为空，差异检查无输出。

- [x] **步骤 3：提交明确范围的文件**

运行：

```powershell
git add -- README.md README.en.md tests/test_public_artifacts.py docs/superpowers/plans/2026-07-26-readme-effect-examples.md
git diff --cached --check
git commit -m "docs: add README effect examples"
```

预期：仅上述四个文件进入提交。
