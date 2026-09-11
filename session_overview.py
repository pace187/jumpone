#!/usr/bin/env python3
"""
session inventory of a telemetry export; can remove sessions (section 4.3).
  python3 session_overview.py [--sql FILE] [--clean N | --delete ID ...] [--dry-run]
"""

import re
import sys
import shutil
import argparse
from collections import Counter
from pathlib import Path
from datetime import datetime

SQL_FILE = Path(__file__).parent / "telemetry_rows.sql"

# session_id is the 3rd field of every tuple, e.g. '1776361825555-7uxl0qicu'
SESSION_PATTERN = re.compile(r"\(\d+,\s*'[^']+',\s*'([^']+)'")

# captures session_id (group 1) and state (group 2, 12th field)
# fields: id, ts, session_id, x, y, vx, vy, speed, f8, f9, f10, 'State'
SESSION_STATE_PATTERN = re.compile(
    r"\(\d+,\s*'[^']+',\s*'([^']+)'"   # id, ts, session_id
    r"(?:,\s*[^,]+){8}"                 # skip 8 numeric fields
    r",\s*'([^']+)'"                     # state string
)

# matches one value tuple: (...), (...), ...
# no line-based split - the file may be a single long line.
ROW_PATTERN = re.compile(r"\([^()]+\)")


def _extract_prefix_and_tuples(content: str):
    """returns (prefix, tuples): everything before the first data tuple, and the
    list of tuple strings like '(62171, ...)'."""
    # the first data tuple starts with '(\d+,' (integer id)
    first_data = re.search(r"\(\d+,", content)
    if first_data is None:
        return "", []
    prefix = content[:first_data.start()].rstrip()
    # extract all tuples from the rest
    rest = content[first_data.start():]
    all_tuples = ROW_PATTERN.findall(rest)
    return prefix, all_tuples


def print_overview(sessions: Counter, last_states: dict):
    total_entries = sum(sessions.values())
    total_sessions = len(sessions)

    W = 78
    print(f"\n{'─'*W}")
    print(f"  {total_sessions} sessions | {total_entries} rows in total")
    print(f"{'─'*W}")
    print(f"  {'session id':<35} {'rows':>8}  {'share':>7}  {'last state':<14}")
    print(f"{'─'*W}")

    for session_id, count in sessions.most_common():
        pct = count / total_entries * 100
        bar = "█" * int(pct / 2)
        state = last_states.get(session_id, "?")
        print(f"  {session_id:<35} {count:>8}  {pct:>6.1f}%  {state:<14}  {bar}")

    print(f"{'─'*W}")
    avg = total_entries / total_sessions
    print(f"  Ø {avg:.0f} rows per session")
    print(f"{'─'*W}\n")


def clean_sql(sessions: Counter, min_entries: int, dry_run: bool):
    remove_ids = {sid for sid, cnt in sessions.items() if cnt < min_entries}
    keep_ids   = {sid for sid, cnt in sessions.items() if cnt >= min_entries}

    if not remove_ids:
        print(f"  no sessions with fewer than {min_entries} rows. nothing to do.")
        return

    print(f"\n  sessions to remove ({len(remove_ids)}):")
    for sid in sorted(remove_ids):
        print(f"    ✗  {sid}  ({sessions[sid]} rows)")

    print(f"\n  sessions to keep ({len(keep_ids)}):")
    for sid, cnt in sessions.most_common():
        if sid in keep_ids:
            print(f"    ✓  {sid}  ({cnt} rows)")

    if dry_run:
        removed = sum(sessions[sid] for sid in remove_ids)
        kept    = sum(sessions[sid] for sid in keep_ids)
        print(f"\n  [dry-run] would remove {removed} rows, keep {kept}.")
        print(f"  [dry-run] no file was changed.\n")
        return

    # write a backup first
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = SQL_FILE.with_name(f"{SQL_FILE.stem}_backup_{ts}.sql")
    shutil.copy2(SQL_FILE, backup)
    print(f"\n  backup written: {backup.name}")

    print(f"  filtering ...")
    content = SQL_FILE.read_text(encoding="utf-8")

    def keep_row(m: re.Match) -> bool:
        """true if the row belongs to a session that is kept."""
        inner = m.group()
        hit = SESSION_PATTERN.search(inner)
        if hit is None:
            return True  # no session field -> keep (e.g. the insert header)
        return hit.group(1) in keep_ids

    print(f"  filtering ...")
    content = SQL_FILE.read_text(encoding="utf-8")

    prefix, all_tuples = _extract_prefix_and_tuples(content)
    filtered = []
    for t in all_tuples:
        m = SESSION_PATTERN.search(t)
        if m is None or m.group(1) in keep_ids:
            filtered.append(t)

    removed_count = len(all_tuples) - len(filtered)
    new_content = prefix + "\n" + ",\n".join(filtered) + ";\n"
    SQL_FILE.write_text(new_content, encoding="utf-8")

    print(f"  ✓ done: {removed_count} rows removed, {len(filtered)} kept.")
    print(f"  file: {SQL_FILE.name}\n")


def delete_sessions(sessions: Counter, delete_ids: list[str], dry_run: bool):
    """removes the given session ids from the sql file."""
    unknown = [sid for sid in delete_ids if sid not in sessions]
    if unknown:
        print(f"  ⚠ Unbekannte Session-IDs (werden ignoriert):")
        for sid in unknown:
            print(f"    {sid}")

    to_remove = [sid for sid in delete_ids if sid in sessions]
    if not to_remove:
        print("  no valid session ids given.")
        return

    print(f"\n  sessions to delete ({len(to_remove)}):")
    for sid in to_remove:
        print(f"    ✗  {sid}  ({sessions[sid]} rows)")

    removed_entries = sum(sessions[sid] for sid in to_remove)
    kept_entries    = sum(sessions.values()) - removed_entries

    if dry_run:
        print(f"\n  [dry-run] would remove {removed_entries} rows, keep {kept_entries}.")
        print(f"  [dry-run] no file was changed.\n")
        return

    # write a backup first
    ts     = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = SQL_FILE.with_name(f"{SQL_FILE.stem}_backup_{ts}.sql")
    shutil.copy2(SQL_FILE, backup)
    print(f"\n  backup written: {backup.name}")

    print(f"  filtering ...")
    content = SQL_FILE.read_text(encoding="utf-8")

    remove_set = set(to_remove)
    prefix, all_tuples = _extract_prefix_and_tuples(content)
    filtered = []
    for t in all_tuples:
        m = SESSION_PATTERN.search(t)
        if m is None or m.group(1) not in remove_set:
            filtered.append(t)

    removed_count = len(all_tuples) - len(filtered)
    new_content = prefix + "\n" + ",\n".join(filtered) + ";\n"
    SQL_FILE.write_text(new_content, encoding="utf-8")

    print(f"  ✓ done: {removed_count} rows removed, {len(filtered)} kept.")
    print(f"  file: {SQL_FILE.name}\n")


def main():
    global SQL_FILE
    parser = argparse.ArgumentParser(description="session overview and filtering for a telemetry sql export")
    parser.add_argument(
        "--clean", metavar="MIN_ENTRIES", type=int,
        help="remove sessions with fewer than MIN_ENTRIES rows from the sql file"
    )
    parser.add_argument(
        "--delete", metavar="SESSION_ID", nargs="+",
        help="delete one or more session ids (space-separated)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="preview only, do not change the file"
    )
    parser.add_argument(
        "--sql", metavar="PFAD", default=None,
        help=f"path to the sql export (default: {SQL_FILE.name})"
    )
    args = parser.parse_args()

    # module-global because clean_sql()/delete_sessions() read it.
    if args.sql:
        SQL_FILE = Path(args.sql)

    if not SQL_FILE.exists():
        print(f"file not found: {SQL_FILE}")
        sys.exit(1)

    print(f"reading {SQL_FILE.name} ...")
    content = SQL_FILE.read_text(encoding="utf-8")

    sessions = Counter(SESSION_PATTERN.findall(content))

    if not sessions:
        print("no sessions found.")
        sys.exit(1)

    # last state per session (last match wins)
    last_states: dict[str, str] = {}
    for session_id, state in SESSION_STATE_PATTERN.findall(content):
        last_states[session_id] = state

    print_overview(sessions, last_states)

    if args.clean is not None:
        clean_sql(sessions, min_entries=args.clean, dry_run=args.dry_run)

    if args.delete:
        delete_sessions(sessions, delete_ids=args.delete, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
