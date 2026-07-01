"""Markdown reports for owner/operator experience."""

from __future__ import annotations

from trading_core.equity_owner_operator_experience.io import write_text


def write_reports(output_dir, payloads: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = {
        "A_SHARE_OWNER_DAILY_OPERATOR_STATUS.md": render_status(payloads),
        "A_SHARE_KNOWN_BLOCKED_STATE_GUIDE.md": render_blocked_guide(payloads),
        "A_SHARE_OPERATOR_ACTION_MENU.md": render_action_menu(payloads),
        "A_SHARE_ARTIFACT_NAVIGATION_INDEX.md": render_navigation(payloads),
        "A_SHARE_OPERATOR_QUICKSTART.md": render_quickstart(payloads),
        "A_SHARE_OPERATOR_SOURCE_TRACE.md": render_source_trace(payloads),
    }
    for name, text in reports.items():
        write_text(output_dir / name, text)


def render_status(payloads: dict) -> str:
    card = payloads["owner_daily_status_card"]
    return "\n".join(
        [
            "# A 股 Owner Daily Operator Status",
            "",
            "## 1. 今日系统状态",
            "- 当前系统是 research-system RC passed。",
            "## 2. v0.9.0 RC 状态",
            f"- full pytest: {card['full_pytest_result']}",
            "## 3. Owner-readiness 状态",
            f"- owner-readiness 仍然 blocked，分数 {card['readiness_score']} / 阈值 {card['minimum_owner_readiness_score']}，gap {card['score_gap']}。",
            "## 4. 为什么当前仍然 Blocked",
            "- blocked 状态是已知且审计过的，不是 owner operational acceptability 通过。",
            "## 5. 可以安全查看的内容",
            "- operator status、known blocked state、RC report、full regression result、audit sweep result、artifact navigation。",
            "## 6. 禁止执行的动作",
            "- 不连接 broker，不读取真实账户，不下真实订单，不生成订单预览，不生成交易信号，不调用旧 run-daily，不执行 official day2。",
            "## 7. 测试与审计状态",
            "- v0.9.0 full pytest passed；v0.9.1 小版本只要求 targeted pytest。",
            "## 8. 下一步建议",
            "- 先 review known blocked state and unresolved blockers。",
            "## 9. 免责声明",
            "- 本报告仅用于 research-only / virtual-only operator experience，不是投资建议，也不是订单指令。",
            "",
        ]
    )


def render_blocked_guide(payloads: dict) -> str:
    banner = payloads["known_blocked_state_banner"]
    explanation = payloads["known_blocked_state_explanation"]
    return "\n".join(
        [
            "# A Share Known Blocked State Guide",
            "",
            f"- {banner['headline']}",
            *[f"- {line}" for line in banner["messages"]],
            "",
            "## What blocked means",
            explanation["what_blocked_means"],
            "## Safe to view",
            ", ".join(explanation["what_is_safe_to_view"]),
            "## Not allowed",
            ", ".join(explanation["what_is_not_allowed"]),
            "",
        ]
    )


def render_action_menu(payloads: dict) -> str:
    menu = payloads["operator_action_menu"]
    lines = ["# A Share Operator Action Menu", ""]
    lines.extend(f"- {row['action_type']}: {row['label']} (allowed={row['allowed']})" for row in menu["actions"])
    lines.append("")
    return "\n".join(lines)


def render_navigation(payloads: dict) -> str:
    index = payloads["artifact_navigation_index"]
    lines = ["# A Share Artifact Navigation Index", ""]
    lines.extend(f"- {row['group']}: {row['title']} -> `{row['path']}`" for row in index["items"])
    lines.append("")
    return "\n".join(lines)


def render_quickstart(payloads: dict) -> str:
    return "\n".join(
        [
            "# A Share Operator Quickstart",
            "",
            "## 1. 先看什么",
            "- 先看 owner daily status，再看 known blocked state。",
            "## 2. 怎么理解 blocked",
            "- blocked 是已知、审计过的 owner-readiness 状态，不等于系统故障。",
            "## 3. 怎么找关键报告",
            "- 使用 artifact navigation 找 RC、audit、full regression、closeout 和 blocker 资料。",
            "## 4. 下一步可以做什么",
            "- 做非交易动作：review blockers、准备 future evidence collection、改善 report usability。",
            "## 5. 哪些动作不能做",
            "- 不连接 broker、不读取真实账户、不下单、不生成订单预览、不调用旧 run-daily、不执行 official day2。",
            "",
        ]
    )


def render_source_trace(payloads: dict) -> str:
    trace = payloads["operator_source_trace"]
    return "\n".join(
        [
            "# A Share Operator Source Trace",
            "",
            f"- source_trace_complete: {trace['source_trace_complete']}",
            f"- source_artifacts: {len(trace['source_artifacts'])}",
            f"- output_artifacts: {len(trace['output_artifacts'])}",
            "",
        ]
    )


def render_audit(audit: dict) -> str:
    return "\n".join(
        [
            "# A Share Owner Operator Experience Audit",
            "",
            f"- overall_passed: {audit['overall_passed']}",
            f"- blocking_reasons: {audit['blocking_reasons']}",
            f"- source_release_candidate: {audit['input_checks']['source_release_candidate']}",
            f"- known_owner_readiness_state: {audit['operator_experience_checks']['known_owner_readiness_state']}",
            f"- owner_operationally_acceptable: {audit['operator_experience_checks']['owner_operationally_acceptable']}",
            f"- full_pytest_run: {audit['test_policy']['full_pytest_run']}",
            f"- recommended_next_version: {audit['recommended_next_version']}",
            "",
        ]
    )
