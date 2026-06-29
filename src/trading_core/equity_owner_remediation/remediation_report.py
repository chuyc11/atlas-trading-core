"""Markdown reports for owner remediation."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def write_remediation_reports(output_dir: Path, payload: dict[str, Any]) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = {
        "owner_remediation_runbook_report": output_dir / "A_SHARE_OWNER_REMEDIATION_RUNBOOK.md",
        "safe_action_checklist_report": output_dir / "A_SHARE_SAFE_ACTION_CHECKLIST.md",
        "data_remediation_guide_report": output_dir / "A_SHARE_DATA_REMEDIATION_GUIDE.md",
        "workflow_remediation_guide_report": output_dir / "A_SHARE_WORKFLOW_REMEDIATION_GUIDE.md",
        "remediation_source_trace_report": output_dir / "A_SHARE_REMEDIATION_SOURCE_TRACE.md",
    }
    reports["owner_remediation_runbook_report"].write_text(render_runbook(payload), encoding="utf-8")
    reports["safe_action_checklist_report"].write_text(render_safe_action_checklist(payload), encoding="utf-8")
    reports["data_remediation_guide_report"].write_text(render_data_guide(payload), encoding="utf-8")
    reports["workflow_remediation_guide_report"].write_text(render_workflow_guide(payload), encoding="utf-8")
    reports["remediation_source_trace_report"].write_text(render_source_trace(payload), encoding="utf-8")
    return reports


def render_runbook(payload: dict[str, Any]) -> str:
    summary = payload["remediation_summary"]
    priority = payload["remediation_priority_summary"]["priority_buckets"]
    issues = payload["issue_catalog"].get("issues", [])
    lines = [
        "# A股 Owner Remediation Runbook",
        "",
        "## 1. 今日修复总览",
        f"- as_of_date: {summary['as_of_date']}",
        f"- issue_count: {summary['issue_count']}",
        f"- automatic_action_count: {summary['automatic_action_count']}",
        "- 本阶段只生成修复手册和安全检查清单，不执行 remediation action。",
        "",
        "## 2. 当前 issue 摘要",
    ]
    lines.extend([f"- {issue['severity']} / {issue['category']}: {issue['issue_code']}" for issue in issues] or ["- None"])
    lines.extend(["", "## 3. P0 blocking 修复手册"])
    lines.extend(_bucket_lines(priority, "P0_blocking"))
    lines.extend(["", "## 4. P1 warning 排查手册"])
    lines.extend(_bucket_lines(priority, "P1_high_warning"))
    lines.extend(["", "## 5. P2 known non-blocking 说明"])
    lines.extend(_bucket_lines(priority, "P2_known_non_blocking"))
    lines.extend(["", "## 6. P4 等待更多历史数据事项"])
    lines.extend(_bucket_lines(priority, "P4_wait_for_history"))
    lines.extend(
        [
            "",
            "## 7. 数据刷新问题排查",
            "- 查看 freshness、schema、coverage 和 provider artifacts；只做验证，不自动刷新。",
            "",
            "## 8. Provider 问题排查",
            "- 查看 provider health 与 fallback report，确认是否为已知降级。",
            "",
            "## 9. Workflow 问题排查",
            "- 查看 current-day manifest、audit 和 source trace。",
            "",
            "## 10. Dashboard / Monitoring 问题排查",
            "- 查看 dashboard audit、monitoring audit、alert event log 与 boundary check。",
            "",
            "## 11. 安全边界",
            "- 本手册是研究系统健康排查材料，不是交易指令。",
            "- 本阶段不连接券商，不读取真实账户，不下真实订单，不生成订单预览，不生成买卖信号。",
            "",
            "## 12. 下一步建议",
            "- v0.8.5 可把 refresh、current-day、dashboard、monitoring、remediation 聚合成 daily ops command center。",
            "",
            "## 13. 免责声明",
            "- This runbook is not an investment recommendation.",
            "- This runbook does not authorize trades.",
            "- This runbook does not connect broker.",
            "- This runbook does not place orders.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_safe_action_checklist(payload: dict[str, Any]) -> str:
    lines = ["# A股 Safe Action Checklist", ""]
    for item in payload["safe_owner_action_checklist"].get("items", []):
        command = f" command=`{item['command_if_any']}`" if item.get("command_if_any") else ""
        lines.append(f"- [ ] {item['title_zh']} ({item['safe_action_type']}){command}")
    lines.extend(["", "- 所有 item 默认 allowed_to_execute_automatically=false。", "- checklist 是非交易动作，不是买卖建议。"])
    return "\n".join(lines) + "\n"


def render_data_guide(payload: dict[str, Any]) -> str:
    lines = [
        "# A Share Data Remediation Guide",
        "",
        "## data freshness issue handling",
        "- Open dataset_freshness_validation.json and data_gap_report.json.",
        "",
        "## schema issue handling",
        "- Open dataset_schema_validation.json and classify known nullable warnings.",
        "",
        "## coverage issue handling",
        "- Open dataset_coverage_summary.json and compare affected datasets.",
        "",
        "## provider fallback handling",
        "- Open provider_health_check.json and provider_fallback_report.json.",
        "",
        "## known data warnings handling",
        "- Document known non-blocking warnings when upstream audit passed.",
        "",
        "This guide is not an investment recommendation. This guide does not authorize trades. This guide does not connect broker. This guide does not place orders.",
    ]
    return "\n".join(lines) + "\n"


def render_workflow_guide(payload: dict[str, Any]) -> str:
    lines = [
        "# A Share Workflow Remediation Guide",
        "",
        "## current-day run failure handling",
        "- Open current_day_run_manifest.json and audit JSON.",
        "",
        "## workflow audit failure handling",
        "- Fail closed until the audit failure is reviewed.",
        "",
        "## missing artifact handling",
        "- Check remediation_input_availability.json for missing required artifact ids.",
        "",
        "## source trace failure handling",
        "- Source trace must be complete and free of forbidden source paths.",
        "",
        "## boundary failure handling",
        "- Boundary failure blocks release validation and requires developer review.",
        "",
        "This guide is not an investment recommendation. This guide does not authorize trades. This guide does not connect broker. This guide does not place orders.",
    ]
    return "\n".join(lines) + "\n"


def render_source_trace(payload: dict[str, Any]) -> str:
    trace = payload["remediation_source_trace"]
    lines = ["# A Share Remediation Source Trace", "", f"- source trace complete: {trace.get('source_trace_complete')}", ""]
    for group in ["source_artifacts", "output_artifacts"]:
        lines.extend([f"## {group}", ""])
        for row in trace.get(group, []):
            lines.append(f"- {row.get('path')} | exists={row.get('exists')} | sha256={row.get('sha256')}")
        lines.append("")
    return "\n".join(lines)


def render_audit(audit: dict[str, Any]) -> str:
    lines = [
        "# A Share Owner Remediation Audit",
        "",
        f"- Overall passed: {audit.get('overall_passed')}",
        f"- Blocking reasons: {_join(audit.get('blocking_reasons', []))}",
        f"- Warning count: {len(audit.get('warnings', []))}",
        f"- Recommended next version: {audit.get('recommended_next_version')}",
        "",
        "## Checks",
    ]
    for key, value in audit.get("checks", {}).items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines) + "\n"


def _bucket_lines(priority: dict[str, list[str]], key: str) -> list[str]:
    return [f"- {item}" for item in priority.get(key, [])] or ["- None"]


def _join(values: list[Any]) -> str:
    return ", ".join(str(value) for value in values) if values else "None"
