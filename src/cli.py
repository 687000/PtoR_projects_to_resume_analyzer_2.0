#!/usr/bin/env python3
"""CLI interface for PtoR — Project-to-Resume Analyzer."""
import json
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from src import services, store, jd_store


def _print_json(obj: dict) -> None:
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def _collect_context() -> dict:
    print("\n-- Background (NOT your work) --")
    bg = {
        "business_background": input("Business / project background: ").strip(),
        "team_client_requirements": input("Team / client requirements: ").strip(),
        "pm_product_decisions": input("PM product decisions: ").strip(),
    }
    print("\n-- Your Contributions --")
    contrib = {
        "t1_responsibilities": input("T1 (scope analysis, API design): ").strip(),
        "t2_responsibilities": input("T2 (implementation, web dev): ").strip(),
        "architecture_details": input("Architecture details: ").strip(),
        "cross_functional_coordination": input("Cross-platform / cross-team coordination: ").strip(),
        "challenges_constraints_tradeoffs": input("Challenges / constraints / tradeoffs: ").strip(),
        "outcomes_impact": input("Outcomes and impact: ").strip(),
    }
    return {"background": bg, "contributions": contrib}


def cmd_upload(args: list) -> None:
    if not args:
        print("Usage: upload <text|file <path>|url <url>|notion <url>>")
        return

    mode = args[0]
    context = _collect_context()

    if mode == "text":
        print("Paste project text (end with a line containing only 'END'):")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        result = services.upload_and_analyze_text("\n".join(lines), context)
    elif mode == "file" and len(args) > 1:
        from src import parser, analyzer
        source = parser.parse_file(args[1])
        analysis = analyzer.analyze_project(source, context)
        result = services.save_analyzed_project(source, context, analysis)
    elif mode == "url" and len(args) > 1:
        from src import parser, analyzer
        source = parser.parse_url(args[1])
        analysis = analyzer.analyze_project(source, context)
        result = services.save_analyzed_project(source, context, analysis)
    elif mode == "notion" and len(args) > 1:
        from src import parser, analyzer
        source = parser.parse_notion(args[1])
        analysis = analyzer.analyze_project(source, context)
        result = services.save_analyzed_project(source, context, analysis)
    else:
        print("Invalid upload arguments")
        return

    print(f"\nSaved project: {result.get('id')} — {result.get('title')}")
    _print_json(result.get("analysis", {}))


def cmd_list(args: list) -> None:
    projects = store.list_projects()
    if not projects:
        print("No projects saved.")
        return
    for p in projects:
        print(f"{p['id'][:8]}  [{p.get('category', 'other')}]  {p.get('title', 'Untitled')}  ({p.get('created_at', '')[:10]})")


def cmd_get(args: list) -> None:
    if not args:
        print("Usage: get <id>")
        return
    project = store.get_project(args[0])
    if not project:
        print(f"Project {args[0]} not found")
        return
    _print_json(project)


def cmd_update(args: list) -> None:
    if not args:
        print("Usage: update <id>")
        return
    project = store.get_project(args[0])
    if not project:
        print(f"Project {args[0]} not found")
        return
    print(f"Editing context for: {project.get('title')}")
    context = _collect_context()
    result = services.update_project_context(args[0], context, reanalyze=True)
    print(f"Updated: {result.get('title')}")


def cmd_delete(args: list) -> None:
    if not args:
        print("Usage: delete <id>")
        return
    confirm = input(f"Delete project {args[0]}? [y/N] ").strip().lower()
    if confirm == "y":
        if store.delete_project(args[0]):
            print("Deleted.")
        else:
            print("Not found.")


def cmd_match(args: list) -> None:
    print("Paste job description (end with a line containing only 'END'):")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    jd_text = "\n".join(lines)
    jd = services.analyze_jd_text(jd_text)
    result = services.run_matching(jd)
    print(f"\nSeniority fit: {result.get('seniority_fit')} — {result.get('seniority_fit_reason')}")
    for mp in result.get("matched_projects", []):
        print(f"\n  [{mp['fit_score']}] {mp.get('project_title', mp['project_id'])}")
        print(f"  Reason: {mp.get('fit_reason', '')}")
        for b in mp.get("tailored_bullets", []):
            if b.get("included"):
                print(f"    • {b['bullet']}")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print("Commands: upload, list, get, update, delete, match")
        return

    cmd = args[0]
    rest = args[1:]
    commands = {
        "upload": cmd_upload,
        "list": cmd_list,
        "get": cmd_get,
        "update": cmd_update,
        "delete": cmd_delete,
        "match": cmd_match,
    }
    if cmd not in commands:
        print(f"Unknown command: {cmd}")
        print("Commands: upload, list, get, update, delete, match")
        return
    commands[cmd](rest)


if __name__ == "__main__":
    main()
