#!/usr/bin/env python3
"""
Übersicht über Sessions in telemetry_rows.sql
Zählt Einträge pro Session und kann Sessions entfernen.

Verwendung:
  python3 session_overview.py                          # nur Übersicht
  python3 session_overview.py --clean 100              # Sessions mit < 100 Einträgen entfernen
  python3 session_overview.py --clean 100 --dry-run    # Vorschau ohne Schreiben
  python3 session_overview.py --delete ID1 ID2 ...     # bestimmte Sessions löschen
  python3 session_overview.py --delete ID1 --dry-run   # Vorschau ohne Schreiben
"""

import re
import sys
import shutil
import argparse
from collections import Counter
from pathlib import Path
from datetime import datetime

SQL_FILE = Path(__file__).parent / "telemetry_rows.sql"

# Session-ID ist das 3. Feld in jedem Tupel, z.B. '1776361825555-7uxl0qicu'
SESSION_PATTERN = re.compile(r"\(\d+,\s*'[^']+',\s*'([^']+)'")

# Erfasst session_id (Gruppe 1) + State (Gruppe 2, 12. Feld)
# Felder: id, ts, session_id, x, y, vx, vy, speed, f8, f9, f10, 'State'
SESSION_STATE_PATTERN = re.compile(
    r"\(\d+,\s*'[^']+',\s*'([^']+)'"   # id, ts, session_id
    r"(?:,\s*[^,]+){8}"                 # 8 numerische Felder überspringen
    r",\s*'([^']+)'"                     # State-String
)

# Passt auf einen einzelnen INSERT-Wert-Block: (...), (...), ...
# Wir splitten auf Zeilenebene nicht – die Datei kann eine große Zeile sein.
ROW_PATTERN = re.compile(r"\([^()]+\)")


def _extract_prefix_and_tuples(content: str):
    """Gibt (prefix, all_data_tuples) zurück.
    prefix = alles vor dem ersten Daten-Tupel (inkl. VALUES-Keyword falls vorhanden).
    all_data_tuples = Liste aller Tupel-Strings wie '(62171, ...)'.
    """
    # Erstes Datentupel beginnt mit '(\d+,' (integer id)
    first_data = re.search(r"\(\d+,", content)
    if first_data is None:
        return "", []
    prefix = content[:first_data.start()].rstrip()
    # Alle Tupel aus dem Rest extrahieren
    rest = content[first_data.start():]
    all_tuples = ROW_PATTERN.findall(rest)
    return prefix, all_tuples


def print_overview(sessions: Counter, last_states: dict):
    total_entries = sum(sessions.values())
    total_sessions = len(sessions)

    W = 78
    print(f"\n{'─'*W}")
    print(f"  {total_sessions} Sessions | {total_entries} Einträge gesamt")
    print(f"{'─'*W}")
    print(f"  {'Session-ID':<35} {'Einträge':>8}  {'Anteil':>7}  {'Letzter State':<14}")
    print(f"{'─'*W}")

    for session_id, count in sessions.most_common():
        pct = count / total_entries * 100
        bar = "█" * int(pct / 2)
        state = last_states.get(session_id, "?")
        print(f"  {session_id:<35} {count:>8}  {pct:>6.1f}%  {state:<14}  {bar}")

    print(f"{'─'*W}")
    avg = total_entries / total_sessions
    print(f"  Ø {avg:.0f} Einträge pro Session")
    print(f"{'─'*W}\n")


def clean_sql(sessions: Counter, min_entries: int, dry_run: bool):
    remove_ids = {sid for sid, cnt in sessions.items() if cnt < min_entries}
    keep_ids   = {sid for sid, cnt in sessions.items() if cnt >= min_entries}

    if not remove_ids:
        print(f"  Keine Sessions mit weniger als {min_entries} Einträgen gefunden. Nichts zu tun.")
        return

    print(f"\n  Sessions, die ENTFERNT werden ({len(remove_ids)} Stück):")
    for sid in sorted(remove_ids):
        print(f"    ✗  {sid}  ({sessions[sid]} Einträge)")

    print(f"\n  Sessions, die BEHALTEN werden ({len(keep_ids)} Stück):")
    for sid, cnt in sessions.most_common():
        if sid in keep_ids:
            print(f"    ✓  {sid}  ({cnt} Einträge)")

    if dry_run:
        removed = sum(sessions[sid] for sid in remove_ids)
        kept    = sum(sessions[sid] for sid in keep_ids)
        print(f"\n  [Dry-run] Würde {removed} Einträge entfernen, {kept} behalten.")
        print(f"  [Dry-run] Keine Datei wurde verändert.\n")
        return

    # Backup anlegen
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = SQL_FILE.with_name(f"{SQL_FILE.stem}_backup_{ts}.sql")
    shutil.copy2(SQL_FILE, backup)
    print(f"\n  Backup gespeichert: {backup.name}")

    print(f"  Filtere Datei ...")
    content = SQL_FILE.read_text(encoding="utf-8")

    def keep_row(m: re.Match) -> bool:
        """True wenn die Zeile zu einer Session gehört, die behalten wird."""
        inner = m.group()
        hit = SESSION_PATTERN.search(inner)
        if hit is None:
            return True  # kein Session-Feld → behalten (z.B. INSERT-Header)
        return hit.group(1) in keep_ids

    print(f"  Filtere Datei ...")
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

    print(f"  ✓ Fertig! {removed_count} Einträge entfernt, {len(filtered)} behalten.")
    print(f"  Datei: {SQL_FILE.name}\n")


def delete_sessions(sessions: Counter, delete_ids: list[str], dry_run: bool):
    """Löscht gezielt die angegebenen Session-IDs aus der SQL-Datei."""
    unknown = [sid for sid in delete_ids if sid not in sessions]
    if unknown:
        print(f"  ⚠ Unbekannte Session-IDs (werden ignoriert):")
        for sid in unknown:
            print(f"    {sid}")

    to_remove = [sid for sid in delete_ids if sid in sessions]
    if not to_remove:
        print("  Keine gültigen Session-IDs zum Löschen angegeben.")
        return

    print(f"\n  Sessions, die GELÖSCHT werden ({len(to_remove)} Stück):")
    for sid in to_remove:
        print(f"    ✗  {sid}  ({sessions[sid]} Einträge)")

    removed_entries = sum(sessions[sid] for sid in to_remove)
    kept_entries    = sum(sessions.values()) - removed_entries

    if dry_run:
        print(f"\n  [Dry-run] Würde {removed_entries} Einträge entfernen, {kept_entries} behalten.")
        print(f"  [Dry-run] Keine Datei wurde verändert.\n")
        return

    # Backup anlegen
    ts     = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = SQL_FILE.with_name(f"{SQL_FILE.stem}_backup_{ts}.sql")
    shutil.copy2(SQL_FILE, backup)
    print(f"\n  Backup gespeichert: {backup.name}")

    print(f"  Filtere Datei ...")
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

    print(f"  ✓ Fertig! {removed_count} Einträge entfernt, {len(filtered)} behalten.")
    print(f"  Datei: {SQL_FILE.name}\n")


def main():
    global SQL_FILE
    parser = argparse.ArgumentParser(description="Telemetry SQL Session-Übersicht & Filterung")
    parser.add_argument(
        "--clean", metavar="MIN_ENTRIES", type=int,
        help="Entfernt Sessions mit weniger als MIN_ENTRIES Einträgen aus der SQL-Datei"
    )
    parser.add_argument(
        "--delete", metavar="SESSION_ID", nargs="+",
        help="Löscht eine oder mehrere Session-IDs (Leerzeichen-getrennt)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Nur Vorschau anzeigen, Datei nicht verändern"
    )
    parser.add_argument(
        "--sql", metavar="PFAD", default=None,
        help=f"Pfad zum SQL-Export (Standard: {SQL_FILE.name})"
    )
    args = parser.parse_args()

    # Modul-global, weil clean_sql()/delete_sessions() darauf zugreifen.
    if args.sql:
        SQL_FILE = Path(args.sql)

    if not SQL_FILE.exists():
        print(f"Datei nicht gefunden: {SQL_FILE}")
        sys.exit(1)

    print(f"Lese {SQL_FILE.name} ...")
    content = SQL_FILE.read_text(encoding="utf-8")

    sessions = Counter(SESSION_PATTERN.findall(content))

    if not sessions:
        print("Keine Sessions gefunden.")
        sys.exit(1)

    # Letzten State pro Session ermitteln (letzter Match gewinnt)
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
