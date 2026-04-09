from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path


def run_cmd(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except Exception:
        return "N/A"


def generate_report() -> str:
    report_lines: list[str] = []

    report_lines.append("[OMNI REPORT]")
    report_lines.append(f"Generated: {datetime.now().isoformat()}")
    report_lines.append("")

    report_lines.append("=== SYSTEM ===")
    report_lines.append(f"OS: {run_cmd('uname -a')}")
    report_lines.append(f"Python: {run_cmd('python3 --version')}")
    report_lines.append("")

    report_lines.append("=== GIT ===")
    report_lines.append(f"Branch: {run_cmd('git branch --show-current')}")
    git_status = run_cmd("git status --short")
    report_lines.append("Status:")
    report_lines.append(git_status if git_status else "clean")
    report_lines.append("")

    log_path = Path("logs/scan_log.json")
    report_lines.append("=== LAST SCAN ===")

    if log_path.exists():
        try:
            data = json.loads(log_path.read_text(encoding="utf-8"))
            last = data[-1] if isinstance(data, list) else data
            scan_data = last.get("data", {})
            report_lines.append(f"Files: {scan_data.get('file_count', 'N/A')}")
            report_lines.append(f"Path: {scan_data.get('scan_path', 'N/A')}")

            category_summary = scan_data.get("category_summary")
            if isinstance(category_summary, dict) and category_summary:
                report_lines.append("Category Summary:")
                for category, count in sorted(category_summary.items()):
                    report_lines.append(f"- {category}: {count}")
        except Exception:
            report_lines.append("Log unreadable")
    else:
        report_lines.append("No scan log found")

    report_lines.append("")
    return "\n".join(report_lines)


def save_report() -> str:
    Path("reports").mkdir(parents=True, exist_ok=True)
    filename = f"reports/omni_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    content = generate_report()
    Path(filename).write_text(content, encoding="utf-8")

    print(f"[OMNI] Report saved -> {filename}")
    print(content)
    return filename


if __name__ == "__main__":
    save_report()
