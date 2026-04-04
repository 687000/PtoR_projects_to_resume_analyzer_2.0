"""
Usage:
  python -m src.cli upload --file project.pdf
  python -m src.cli upload --text "paste project text here"
  python -m src.cli upload --url https://example.com/project
  python -m src.cli list
  python -m src.cli get <id>
  python -m src.cli delete <id>
  python -m src.cli update <id>
"""
import argparse
import sys

from dotenv import load_dotenv

from src.analyzer import analyze_project
from src.parser import parse_input
from src.store import delete_project, get_project, load_projects, save_project, update_project


def cmd_upload(args: argparse.Namespace) -> None:
    load_dotenv()

    source = args.file or args.text or args.url
    if not source:
        print("Error: provide --file <path>, --text <string>, or --url <url>", file=sys.stderr)
        sys.exit(1)

    print("\nParsing input...")
    try:
        parsed = parse_input(source)
    except (ValueError, FileNotFoundError, ImportError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    raw_text = parsed["raw_text"]
    print(f"Source type : {parsed['source_type']}")
    print(f"Characters  : {len(raw_text)}")
    print("\n--- Extracted text preview (first 400 chars) ---")
    print(raw_text[:400].strip())
    print("---\n")

    context = _prompt_context_form()

    print("\nAnalyzing project...")
    try:
        analysis = analyze_project(raw_text, context)
    except Exception as e:
        print(f"Analysis failed: {e}", file=sys.stderr)
        sys.exit(1)

    _print_analysis(analysis)

    answer = input("\nSave this project? [y/N]: ").strip().lower()
    if answer != "y":
        print("Discarded. Project not saved.")
        return

    project = {**analysis, "raw_text": raw_text, "source_metadata": parsed["metadata"]}
    saved = save_project(project)
    print(f"\nProject saved. ID: {saved['id']}")
    print(f"Total projects in store: {len(load_projects())}")


def cmd_list(args: argparse.Namespace) -> None:
    projects = load_projects()

    if not projects:
        print("No projects saved yet. Run: python -m src.cli upload --file <path>")
        return

    print(f"\n{'='*60}")
    print(f"  Projects ({len(projects)} total)")
    print(f"{'='*60}")

    for i, p in enumerate(projects, 1):
        tags = ", ".join(p.get("tags", [])) or "—"
        print(f"\n[{i}] {p.get('title', 'Untitled')}")
        print(f"    ID       : {p['id']}")
        print(f"    Category : {p.get('category', '—')}")
        print(f"    Tags     : {tags}")
        print(f"    Created  : {p.get('created_at', '—')}")
        summary = p.get("summary", "")
        if summary:
            print(f"    Summary  : {summary[:120]}{'...' if len(summary) > 120 else ''}")

    print()


def cmd_get(args: argparse.Namespace) -> None:
    project = get_project(args.id)
    if not project:
        print(f"Error: no project found with ID '{args.id}'", file=sys.stderr)
        sys.exit(1)
    _print_analysis(project)
    print(f"\nID      : {project['id']}")
    print(f"Created : {project.get('created_at', '—')}")
    if project.get("updated_at"):
        print(f"Updated : {project['updated_at']}")
    meta = project.get("source_metadata", {})
    if meta:
        print(f"Source  : {meta}")


def cmd_delete(args: argparse.Namespace) -> None:
    project = get_project(args.id)
    if not project:
        print(f"Error: no project found with ID '{args.id}'", file=sys.stderr)
        sys.exit(1)

    print(f"Project : {project.get('title', 'Untitled')}")
    print(f"ID      : {project['id']}")
    answer = input("Delete this project? [y/N]: ").strip().lower()
    if answer != "y":
        print("Cancelled.")
        return

    delete_project(args.id)
    print("Deleted.")
    print(f"Remaining projects: {len(load_projects())}")


def cmd_update(args: argparse.Namespace) -> None:
    project = get_project(args.id)
    if not project:
        print(f"Error: no project found with ID '{args.id}'", file=sys.stderr)
        sys.exit(1)

    print(f"\nUpdating: {project.get('title', 'Untitled')}")
    print("Press Enter to keep current value.\n")

    current_context = project.get("context", {})
    new_context = _prompt_context_form(defaults=current_context)

    print("\nRe-analyzing...")
    try:
        raw_text = project.get("raw_text", "")
        analysis = analyze_project(raw_text, new_context)
    except Exception as e:
        print(f"Analysis failed: {e}", file=sys.stderr)
        sys.exit(1)

    _print_analysis(analysis)

    answer = input("\nSave updated project? [y/N]: ").strip().lower()
    if answer != "y":
        print("Cancelled. Project not changed.")
        return

    updated = update_project(args.id, {**analysis, "context": new_context})
    print(f"\nProject updated. ID: {updated['id']}")


def _prompt_context_form(defaults: dict | None = None) -> dict:
    d = defaults or {}

    def ask(label: str, key: str) -> str:
        current = d.get(key, "")
        hint = f" [{current[:60]}...]" if len(current) > 60 else f" [{current}]" if current else ""
        return input(f"{label}{hint}: ").strip() or current

    print("=== Context Form ===")
    print("Provide context to improve accuracy. Press Enter to skip.\n")

    print("-- Background (NOT your work) --")
    business_background = ask("Business/project background", "business_background")
    team_client_requirements = ask("Team/client requirements", "team_client_requirements")
    pm_decisions = ask("PM product decisions", "pm_decisions")

    print("\n-- Your Contributions --")
    t1_responsibilities = ask("T1 responsibilities (scope, API/interface design)", "t1_responsibilities")
    t2_responsibilities = ask("T2 responsibilities (implementation, web dev)", "t2_responsibilities")
    architecture_details = ask("Architecture details (models, stores, APIs)", "architecture_details")
    coordination = ask("Cross-platform/cross-functional coordination", "coordination")
    challenges = ask("Challenges, constraints, tradeoffs", "challenges")
    outcomes = ask("Outcomes and impact", "outcomes")

    return {
        "business_background": business_background,
        "team_client_requirements": team_client_requirements,
        "pm_decisions": pm_decisions,
        "t1_responsibilities": t1_responsibilities,
        "t2_responsibilities": t2_responsibilities,
        "architecture_details": architecture_details,
        "coordination": coordination,
        "challenges": challenges,
        "outcomes": outcomes,
    }


def _print_analysis(analysis: dict) -> None:
    sep = "-" * 60

    print(f"\n{'='*60}")
    print(f"  Analysis Results")
    print(f"{'='*60}")

    print(f"\nTitle    : {analysis.get('title', '—')}")
    print(f"Category : {analysis.get('category', '—')}")
    print(f"Tags     : {', '.join(analysis.get('tags', []))}")

    print(f"\n{sep}")
    print("Summary")
    print(sep)
    print(analysis.get("summary", ""))

    print(f"\n{sep}")
    print("Ownership")
    print(sep)
    print(analysis.get("ownership_description", ""))

    print(f"\n{sep}")
    print("Technical Highlights")
    print(sep)
    for item in analysis.get("technical_highlights", []):
        print(f"  • {item}")

    print(f"\n{sep}")
    print("Resume Bullets")
    print(sep)
    for item in analysis.get("resume_bullets", []):
        print(f"  • {item}")

    print(f"\n{sep}")
    print("Self-Introduction")
    print(sep)
    print(analysis.get("self_intro", ""))

    print(f"\n{sep}")
    print("Interview Talking Points")
    print(sep)
    for item in analysis.get("talking_points", []):
        print(f"  • {item}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="src.cli",
        description="Project-to-Resume Analyzer CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    upload_p = sub.add_parser("upload", help="Upload and analyze a project")
    group = upload_p.add_mutually_exclusive_group()
    group.add_argument("--file", metavar="PATH", help="Path to PDF, text, HTML, or image file")
    group.add_argument("--text", metavar="TEXT", help="Raw project text (inline)")
    group.add_argument("--url", metavar="URL", help="URL or Notion link to scrape")
    upload_p.set_defaults(func=cmd_upload)

    list_p = sub.add_parser("list", help="List all saved projects")
    list_p.set_defaults(func=cmd_list)

    get_p = sub.add_parser("get", help="Show full detail for a project")
    get_p.add_argument("id", help="Project ID")
    get_p.set_defaults(func=cmd_get)

    delete_p = sub.add_parser("delete", help="Delete a project")
    delete_p.add_argument("id", help="Project ID")
    delete_p.set_defaults(func=cmd_delete)

    update_p = sub.add_parser("update", help="Re-analyze a project with updated context")
    update_p.add_argument("id", help="Project ID")
    update_p.set_defaults(func=cmd_update)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
