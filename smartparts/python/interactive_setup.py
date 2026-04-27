"""
interactive_setup — reusable first-run wizard and preflight check pattern.

Used in: model-bench, (future scripts)

── How to load in a uv script ────────────────────────────────────────────────
Add this near the top of any ~/bin script that needs it:

    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path.home() / ".local/share/chezmoi/smartparts/python"))
    from interactive_setup import CheckItem, run_preflight, run_tutorial, run_setup_wizard

── Pattern summary ────────────────────────────────────────────────────────────
1. Define your requirements as a list[CheckItem] — each has a test(), a hint,
   and an optional suggested fix command.
2. Define tutorial pages as list[tuple[str, str]] — (title, rich-markup content).
3. Call run_setup_wizard(title, description, checks, pages, setup_file, console)
   once.  It handles: first-run detection, interactive check-and-fix loop,
   paginated tutorial, and writing the setup state file.
4. On subsequent runs, call run_quick_preflight(checks, console) for a
   non-interactive version that just warns on failures.
"""
from __future__ import annotations

import json
import datetime
import pathlib
import subprocess
from dataclasses import dataclass
from typing import Callable

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule


@dataclass
class CheckItem:
    """One preflight requirement.

    Attributes:
        name        Short label shown in the check list.
        description One sentence explaining why this is needed.
        optional    If True, failure is a warning not a blocker.
        test        Zero-argument callable returning True when the check passes.
        fix_hint    Human-readable instructions (may be multi-line).
        fix_cmd     A shell command to suggest / run (None if too context-specific).
    """
    name:        str
    description: str
    optional:    bool
    test:        Callable[[], bool]
    fix_hint:    str
    fix_cmd:     str | None = None


def run_interactive_check(item: CheckItem, console: Console) -> bool:
    """
    Show status for one CheckItem.  If failing, enter an interactive fix loop:
      [R] run fix_cmd now  |  [C] custom command  |  [M] manual  |  [S] skip

    Returns True when the check passes (or after a successful fix), False if skipped.
    """
    if item.test():
        console.print(f"  [green]✓[/green]  {item.name}")
        return True

    marker = "[yellow]~[/yellow]" if item.optional else "[red]✗[/red]"
    flag   = "  [dim](optional)[/dim]" if item.optional else ""
    console.print(f"  {marker}  {item.name}{flag}")
    console.print(f"      [dim]{item.description}[/dim]")
    console.print()
    for line in item.fix_hint.splitlines():
        console.print(f"      {line}")
    console.print()

    while True:
        options: list[tuple[str, str]] = []
        if item.fix_cmd:
            options.append(("R", f"Run:  {item.fix_cmd}"))
        options.append(("C", "Custom command  (type the command yourself)"))
        options.append(("M", "Manual  (I'll run it in another terminal — press Enter when done)"))
        skip_note = "optional" if item.optional else "may cause errors later"
        options.append(("S", f"Skip  [{skip_note}]"))

        for key, label in options:
            console.print(f"      [[bold]{key}[/bold]]  {label}")

        raw = console.input("\n      → ").strip().lower()

        run_cmd: str | None = None
        if raw in ("r", "run") and item.fix_cmd:
            run_cmd = item.fix_cmd
        elif raw in ("c", "custom"):
            custom = console.input("      Command to run: ").strip()
            if custom:
                run_cmd = custom
        elif raw in ("m", "manual", ""):
            console.print("      Run the command above, then press [bold]Enter[/bold] to re-check…")
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                pass
        elif raw in ("s", "skip"):
            if not item.optional:
                console.print(f"      [yellow]Warning:[/yellow] {item.name} is required; some features may fail.")
            console.print()
            return False
        else:
            continue  # unrecognised input — redisplay menu

        if run_cmd:
            console.print(f"\n      [dim]$ {run_cmd}[/dim]\n")
            subprocess.run(run_cmd, shell=True)  # live output, not captured
            console.print()

        if item.test():
            console.print(f"      [green]✓[/green]  {item.name} — ready!\n")
            return True
        console.print(f"      [yellow]Still not detected.[/yellow] Try again or skip.\n")


def run_preflight(checks: list[CheckItem], console: Console) -> bool:
    """
    Run all checks interactively.
    Returns False if any required (non-optional) check remains unmet after the loop.
    """
    console.print(Rule("[bold]Preflight checks[/bold]", style="dim"))
    console.print()

    skipped:  list[str] = []
    all_good: bool      = True

    for item in checks:
        if not run_interactive_check(item, console):
            skipped.append(item.name)
            if not item.optional:
                all_good = False

    if skipped:
        console.print(f"[dim]Skipped: {', '.join(skipped)}[/dim]\n")

    if not all_good:
        console.print(
            "[yellow]One or more required checks did not pass.[/yellow]\n"
            "Fix them and re-run with [bold]--setup[/bold].\n"
        )

    return all_good


def run_quick_preflight(checks: list[CheckItem], console: Console) -> bool:
    """
    Non-interactive preflight — just checks and warns.  Used on subsequent runs
    (after first-run setup is done).  Returns False if any required check fails.
    """
    failed = [c for c in checks if not c.optional and not c.test()]
    warned = [c for c in checks if c.optional and not c.test()]

    for c in warned:
        console.print(f"[yellow]⚠[/yellow]  {c.name} not available  [dim](optional)[/dim]")
    for c in failed:
        console.print(f"[red]✗[/red]  {c.name} not available  [dim](required)[/dim]")
        console.print(f"   {c.fix_hint.splitlines()[0]}")

    return not failed


def run_tutorial(pages: list[tuple[str, str]], console: Console) -> None:
    """
    Display a paginated tutorial.  Each page is a (title, rich-markup-content) tuple.
    User presses Enter to advance; Ctrl-C or EOF exits early without error.
    """
    total = len(pages)
    for i, (title, content) in enumerate(pages, 1):
        console.print()
        console.print(
            Panel(
                content,
                title=f"[bold]{title}[/bold]",
                subtitle=f"[dim]{i} / {total}[/dim]",
                border_style="dim",
                padding=(1, 2),
            )
        )
        if i < total:
            try:
                console.input("[dim]  Press Enter for next…[/dim]  ")
            except (EOFError, KeyboardInterrupt):
                console.print()
                break
        else:
            console.print()


def run_setup_wizard(
    title:       str,
    description: str,
    checks:      list[CheckItem],
    pages:       list[tuple[str, str]],
    setup_file:  pathlib.Path,
    console:     Console,
) -> bool:
    """
    Full first-run experience: welcome panel → preflight checks → optional tutorial
    → write setup_file.

    Returns True if all required checks passed.
    """
    console.print()
    console.print(
        Panel(
            f"[bold]{title}[/bold]\n\n{description}",
            border_style="cyan",
            padding=(1, 2),
        )
    )
    console.print()

    ok = run_preflight(checks, console)
    console.print()

    if pages:
        try:
            ans = console.input(
                "[bold]Show the quick-start guide?[/bold]  "
                "[[bold]Y[/bold]]es / [[bold]N[/bold]]o  → "
            ).strip().lower()
        except (EOFError, KeyboardInterrupt):
            ans = "n"
            console.print()

        if ans not in ("n", "no"):
            run_tutorial(pages, console)

    setup_file.parent.mkdir(parents=True, exist_ok=True)
    setup_file.write_text(json.dumps({
        "setup_completed_at": datetime.datetime.utcnow().isoformat(),
        "preflight_ok": ok,
    }, indent=2))

    rule_style = "green" if ok else "yellow"
    rule_text  = "[bold green]Setup complete[/bold green]" if ok else "[bold yellow]Setup complete with warnings[/bold yellow]"
    console.print(Rule(rule_text, style=rule_style))
    console.print()

    return ok
