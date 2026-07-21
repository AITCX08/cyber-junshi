import asyncio
import os
import sys
from pathlib import Path
from uuid import UUID

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from cyber_junshi.mcp.server import create_server


def _call(server, name: str, arguments: dict[str, object]) -> dict[str, object]:
    result = asyncio.run(server.call_tool(name, arguments))
    if isinstance(result, tuple):
        _, structured = result
        assert isinstance(structured, dict)
        return structured
    assert isinstance(result, dict)
    return result


def test_server_exposes_exact_public_tool_surface(tmp_path: Path) -> None:
    server = create_server(tmp_path / "mcp.db")

    tools = asyncio.run(server.list_tools())

    assert {tool.name for tool in tools} == {
        "assess_safety",
        "structure_case",
        "compare_options",
        "create_action_plan",
        "record_outcome",
        "review_decision",
        "search_knowledge",
        "remember_question",
        "recall_subject",
        "list_subjects",
        "forget_subject",
    }


def test_decision_tools_complete_a_synthetic_decision_cycle(tmp_path: Path) -> None:
    server = create_server(tmp_path / "mcp.db")

    safety = _call(server, "assess_safety", {"text": "我们下周再约时间聊"})
    assert safety["level"] == "normal"

    layers = _call(
        server,
        "structure_case",
        {
            "facts": ["对方取消了一次见面"],
            "inferences": ["对方可能在回避"],
            "unknowns": ["取消的具体原因"],
        },
    )
    assert layers["facts"] == ["对方取消了一次见面"]

    ranked = _call(
        server,
        "compare_options",
        {
            "options": [
                {
                    "name": "连续追问",
                    "short_term_gain": 8,
                    "long_term_cost": 8,
                    "reversibility": 2,
                    "risk": 8,
                    "information_gain": 2,
                },
                {
                    "name": "澄清一次并观察",
                    "short_term_gain": 6,
                    "long_term_cost": 2,
                    "reversibility": 9,
                    "risk": 3,
                    "information_gain": 8,
                },
            ]
        },
    )
    assert ranked["options"][0]["name"] == "澄清一次并观察"

    plan_arguments = {
        "action": "澄清一次并观察",
        "observation_hours": 48,
        "success_signals": ["收到明确回复"],
        "downgrade_signals": ["只有含糊回复"],
        "stop_signals": ["明确要求不要联系"],
    }
    plan = _call(server, "create_action_plan", plan_arguments)
    assert plan["observation_hours"] == 48

    recorded = _call(
        server,
        "record_outcome",
        {
            "case_id": "case-demo-001",
            **plan_arguments,
            "observed_signals": ["收到明确回复"],
            "note": "synthetic",
        },
    )
    UUID(str(recorded["record_id"]))

    review = _call(server, "review_decision", {"record_id": recorded["record_id"]})
    assert review["status"] == "continue"


def test_memory_tools_keep_questions_isolated_and_deletable(tmp_path: Path) -> None:
    server = create_server(tmp_path / "mcp.db")

    saved = _call(
        server,
        "remember_question",
        {
            "subject_alias": "对象甲",
            "question_text": "对方取消了见面，我应该再问一次吗？",
            "summary": "一次约见被取消",
            "memories": [
                {"kind": "fact", "content": "约见被取消", "confidence": 1.0},
                {"kind": "unknown", "content": "取消原因", "confidence": 0.2},
            ],
        },
    )
    UUID(str(saved["question_id"]))

    recalled = _call(server, "recall_subject", {"subject_alias": "对象甲", "limit": 10})
    assert recalled["alias"] == "对象甲"
    assert recalled["questions"][0]["summary"] == "一次约见被取消"
    assert {item["content"] for item in recalled["memory_items"]} == {
        "约见被取消",
        "取消原因",
    }

    subjects = _call(server, "list_subjects", {"include_archived": False})
    assert subjects["subjects"][0]["question_count"] == 1

    forgotten = _call(
        server, "forget_subject", {"subject_alias": "对象甲", "confirm": True}
    )
    assert forgotten == {"subjects": 1, "questions": 1, "memory_items": 2}
    assert _call(server, "list_subjects", {"include_archived": False}) == {"subjects": []}


def test_search_knowledge_tool_returns_provenance(tmp_path: Path) -> None:
    server = create_server(tmp_path / "mcp.db")

    result = _call(server, "search_knowledge", {"query": "同意与亲密", "limit": 3})

    assert result["items"][0]["id"] == "core-08"
    assert result["items"][0]["source_ids"] == ["cdc-consent", "project-four-mechanisms"]


def test_stdio_protocol_initializes_and_calls_a_tool(tmp_path: Path) -> None:
    async def exercise_protocol() -> None:
        parameters = StdioServerParameters(
            command=sys.executable,
            args=["-m", "cyber_junshi.mcp.server"],
            env={**os.environ, "CYBER_JUNSHI_DB": str(tmp_path / "stdio.db")},
        )
        async with (
            stdio_client(parameters) as (reader, writer),
            ClientSession(reader, writer) as session,
        ):
            await session.initialize()
            tools = await session.list_tools()
            assert len(tools.tools) == 11
            result = await session.call_tool(
                "assess_safety", {"text": "我们下周再约时间聊"}
            )
            assert not result.isError

    asyncio.run(exercise_protocol())
