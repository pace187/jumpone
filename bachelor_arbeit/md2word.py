#!/usr/bin/env python3
"""
md2word.py
Bereitet einen Google-Docs-Export der Arbeit fuer das FH-Word-Template auf und
ruft pandoc auf. Die Quelldatei wird nicht veraendert.

Warum es dieses Skript gibt: Der Export bringt fuenf Dinge mit, an denen pandoc
scheitert oder die im Word-Dokument falsch landen.
  1. Die Bilder stecken als base64 in der Datei - und zwar um Faktor 2-3
     herunterskaliert. Die Originale liegen als PNG daneben.
  2. Die Codeausschnitte sind kein Code, sondern Fliesstext mit Escapes.
  3. Abschnitte stehen teils auf der falschen Ueberschriftenebene.
  4. Die Bild- und Tabellentitel sind Ueberschriften (####). So landen sie im
     Inhaltsverzeichnis statt im Abbildungs- bzw. Tabellenverzeichnis.
  5. Die Kapitelnummern stehen im Text, obwohl die Vorlagen des Templates
     ("Ueberschrift 1/2/3", alle an numId=4) selbst nummerieren. Sonst steht
     im Word-Dokument "3 1. Introduction".

Aufruf:
  python3 md2word.py "Bachelor Thesis Grubmair - JumpOne(5).md"
  python3 md2word.py <datei.md> --md-only        # nur die bereinigte Markdown
  python3 md2word.py <datei.md> --out kap6.docx
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import zipfile

TEMPLATE = "BMT_Bachelorthesis__EN.docx"
DEFAULT_SRC = "Bachelor Thesis Grubmair - JumpOne(5).md"

# Reihenfolge des Auftretens im Dokument. Geprueft ueber die Bildabmessungen:
# die eingebetteten base64-Fassungen sind dieselben Abbildungen, nur kleiner.
IMAGES = {
    "image1": "fig_3_1_1_level.png",
    "image2": "fig_4_4_1_klassenverteilung.png",
    "image3": "fig_4_6_1_verteilungen.png",
    "image4": "fig_5_1_protokolle.png",
    "image5": "fig_5_4_pausen_artefakt.png",
    "image6": "fig_5_5_baender.png",
    "image7": "fig_5_7_zeitverlauf.png",
}

# Ein Codeblock beginnt mit einer Kommentarzeile, die eine Quelldatei nennt.
# Das ist im Export das einzige verlaessliche Merkmal - ausgezeichnet ist
# nichts. Zeilennummern waeren bei jedem neuen Export wieder falsch.
CODE_START = re.compile(r"^\s*(?:\\?#|//)\s*(?:ml\\?_pipeline|src)/\S+\.(py|ts)")
PROSE_LEN = 130   # Codezeilen sind kurz, Absaetze im Export lang


def unescape(s):
    """Escapes des Google-Docs-Exports entfernen. Nur fuer Codebloecke und
    Ueberschriften: im Fliesstext interpretiert pandoc sie korrekt."""
    return re.sub(r"\\([_\[\]#=+<>~*.\\-])", r"\1", s)


def fenced_spans(lines):
    """Indizes, die bereits in einem ```-Block liegen. Solche Bereiche werden
    unveraendert durchgereicht - sonst frisst die Ueberschriftenregel die
    Kommentarzeilen im Code, und der Blockfinder zaeunt doppelt ein."""
    inside, spans = False, set()
    for k, ln in enumerate(lines):
        if ln.lstrip().startswith("```"):
            spans.add(k)
            inside = not inside
            continue
        if inside:
            spans.add(k)
    return spans


def find_code_blocks(lines):
    """Liefert {startindex: (endindex, sprache)}. Ein Block laeuft bis zur
    ersten Leerzeile, auf die eine Ueberschrift oder ein langer Absatz folgt."""
    blocks, i, n = {}, 0, len(lines)
    fenced = fenced_spans(lines)
    while i < n:
        m = CODE_START.match(lines[i]) if i not in fenced else None
        if not m:
            i += 1
            continue
        lang = "python" if m.group(1) == "py" else "typescript"
        j = i + 1
        last = i
        while j < n:
            s = lines[j].strip()
            if not s:
                j += 1
                continue
            if s.startswith("#") or len(lines[j]) > PROSE_LEN:
                break
            last = j
            j += 1
        blocks[i] = (last, lang)
        i = last + 1
    return blocks


def clean_caption(s):
    s = unescape(s).strip()
    s = re.sub(r"^(Figure|Table)\s+[\d.]+\s*[-—]\s*", "", s)
    return s.rstrip(":").strip()


def build(lines):
    out, i, n = [], 0, len(lines)
    code = find_code_blocks(lines)
    fenced = fenced_spans(lines)
    seen_numbered = False

    while i < n:
        line = lines[i]

        # Bereits eingezaeunter Code geht unveraendert durch.
        if i in fenced:
            out.append(line)
            i += 1
            continue

        if i in code:
            end, lang = code[i]
            out.append(f"```{lang}")
            for j in range(i, end + 1):
                out.append(unescape(lines[j]).rstrip())
            out.append("```")
            i = end + 1
            continue

        # leere Ueberschrift aus dem Export
        if re.match(r"^#{1,6}\s*$", line.strip()):
            i += 1
            continue

        # Abbildung: Ueberschrift + Bildverweis -> echte Bildunterschrift
        m = re.match(r"^#{1,4}\s+(Figure\s+[\d.]+\s*\\?-.*?)\s*$", line)
        if m:
            caption = clean_caption(m.group(1))
            tag, j = None, i
            while j < n and j < i + 4:
                tag = re.search(r"!\[\]\[(image\d+)\]", lines[j])
                if tag:
                    break
                j += 1
            if tag:
                out += [f"![{caption}]({IMAGES[tag.group(1)]})", ""]
                # Bei 5.4.1 folgt Prosa ohne Leerzeile, bei 4.6.1 steht das
                # Bild selbst in einer Ueberschrift - davon bleiben Rauten.
                rest = re.sub(r"!\[\]\[image\d+\]", "", lines[j])
                rest = re.sub(r"^#{1,6}\s*", "", rest.strip()).strip()
                if rest:
                    out.append(rest)
                i = j + 1
                continue

        # Tabelle: Ueberschrift -> pandoc-Beschriftung unter der Tabelle
        m = re.match(r"^#{1,4}\s+(Table\s+[\d.]+\s*[\\—-].*?)\s*$", line)
        if m:
            caption = clean_caption(m.group(1))
            j = i + 1
            while j < n and not lines[j].lstrip().startswith("|"):
                j += 1
            k = j
            while k < n and lines[k].lstrip().startswith("|"):
                k += 1
            out += lines[j:k] + ["", f": {caption}", ""]
            i = k
            continue

        # Kapitel- und Abschnittsueberschriften: Nummern raus, Ebene aus der
        # Nummer ableiten. Titel und Abstract entfallen - das Template hat
        # beides schon, und als Ebene-1-Ueberschriften wuerden sie den
        # Kapitelzaehler verschieben.
        m = re.match(r"^(#{1,3})\s+(.*?)\s*$", line)
        if m and not re.match(r"^#{1,4}\s+(Figure|Table)\s", line):
            level, title = len(m.group(1)), unescape(m.group(2)).strip()
            num = re.match(r"^(\d+(?:\.\d+)*)\.?\s+(.*)$", title)
            if num:
                level = len(num.group(1).split("."))
                title = num.group(2).strip()
                seen_numbered = True
            elif level == 1 and not seen_numbered:
                i += 1          # Titelblattzeile oder Abstract
                continue
            out.append("#" * level + " " + title)
            i += 1
            continue

        # Bildverweisdefinitionen am Dateiende
        if re.match(r"^\[image\d+\]:", line):
            i += 1
            continue

        out.append(line)
        i += 1

    return "\n".join(out)


# pandoc verweist auf eigene Formatvorlagen, die es mit --reference-doc nicht
# immer definiert - Word formatiert solche Absaetze dann als "Standard".
# Betroffen sind ausgerechnet die Beschriftungen, ohne die Word weder ein
# Abbildungs- noch ein Tabellenverzeichnis bauen kann.
#
# Feste Vorlagen-IDs helfen hier nicht: pandoc BENENNT die erkannten Vorlagen
# des Templates auf seine eigenen IDs um ("berschrift1" -> "Heading1",
# "Textkrper" -> "BodyText"), und zwar nicht in jedem Dokument gleich. Die
# Zuordnung geht deshalb ueber den Anzeigenamen der Vorlage, der stabil ist.
STYLE_MAP = {           # pandoc-ID -> gesuchter Anzeigename im Template
    "ImageCaption": "caption",
    "TableCaption": "Tabellenbeschriftung",
    "CaptionedFigure": "Bild",
    "Compact": "Standard_Tabelle",
    "FirstParagraph": "Body Text",
    "BlockText": "Body Text",
}

# Im Anhang duerfen die Ueberschriften NICHT am Kapitelzaehler haengen, sonst
# nummeriert Word sie als Kapitel 8, 9, 10 weiter. Das Template haelt dafuer
# "Anhang Ueberschrift 1/2" bereit, beide ohne Nummerierung.
APPENDIX_MAP = {"heading 1": "anhang überschrift 1",
                "heading 2": "anhang überschrift 1",
                "heading 3": "anhang überschrift 2"}


def remap_styles(path, appendix=False):
    """Verweise auf undefinierte Vorlagen auf die des Templates ziehen. Was
    pandoc bereits sauber uebernommen hat, bleibt unangetastet."""
    with zipfile.ZipFile(path) as z:
        styles = z.read("word/styles.xml").decode("utf-8")
        doc = z.read("word/document.xml").decode("utf-8")
        items = [(i, z.read(i.filename)) for i in z.infolist()]

    by_name, defined = {}, set()
    for m in re.finditer(r'w:styleId="([^"]+)"[^>]*>\s*<w:name w:val="([^"]+)"',
                         styles):
        defined.add(m.group(1))
        by_name.setdefault(m.group(2).lower(), m.group(1))

    changed = []
    for pandoc_id, wanted in STYLE_MAP.items():
        if pandoc_id in defined:
            continue                       # pandoc hat sie selbst definiert
        target = by_name.get(wanted.lower())
        if not target:
            continue
        if f'w:pStyle w:val="{pandoc_id}"' in doc:
            doc = doc.replace(f'w:pStyle w:val="{pandoc_id}"',
                              f'w:pStyle w:val="{target}"')
            changed.append(f"{pandoc_id}->{target}")

    if appendix:
        for src_name, dst_name in APPENDIX_MAP.items():
            src_id, dst_id = by_name.get(src_name), by_name.get(dst_name)
            if src_id and dst_id and f'w:pStyle w:val="{src_id}"' in doc:
                doc = doc.replace(f'w:pStyle w:val="{src_id}"',
                                  f'w:pStyle w:val="{dst_id}"')
                changed.append(f"{src_id}->{dst_id}")

    # "References" ist kein nummeriertes Kapitel. Das Template fuehrt
    # Verzeichnisse unter "Anhang Ueberschrift 1", die nicht am Kapitelzaehler
    # haengt.
    anhang = by_name.get("anhang überschrift 1") or by_name.get("anhang uberschrift 1")
    h1 = by_name.get("heading 1")
    if not appendix and anhang and h1:
        doc = re.sub(
            r'(<w:p\b(?:(?!</w:p>).)*?)w:pStyle w:val="%s"'
            r'((?:(?!</w:p>).)*?<w:t[^>]*>References</w:t>)' % re.escape(h1),
            r'\1w:pStyle w:val="%s"\2' % anhang, doc, flags=re.S)

    tmp = path + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as dst:
        for item, data in items:
            if item.filename == "word/document.xml":
                data = doc.encode("utf-8")
            dst.writestr(item, data)
    shutil.move(tmp, path)
    print("   Vorlagen zugeordnet: " + (", ".join(changed) or "nichts noetig"))

    # Kontrolle: kein Verweis darf ins Leere gehen.
    with zipfile.ZipFile(path) as z:
        d = z.read("word/document.xml").decode("utf-8")
        s = z.read("word/styles.xml").decode("utf-8")
    used = set(re.findall(r'w:pStyle w:val="([^"]+)"', d))
    missing = [u for u in used if f'w:styleId="{u}"' not in s]
    print("   " + (f"WARNUNG - undefinierte Vorlagen: {missing}" if missing
                   else "alle verwendeten Vorlagen sind definiert"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", nargs="?", default=DEFAULT_SRC)
    ap.add_argument("--out", default="thesis_body.docx")
    ap.add_argument("--md-only", action="store_true")
    ap.add_argument("--appendix", action="store_true",
                    help="Ueberschriften auf die unnummerierten "
                         "Anhang-Vorlagen des Templates ziehen")
    args = ap.parse_args()

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    if not os.path.exists(args.src):
        sys.exit(f"{args.src} nicht gefunden.")
    missing = [f for f in IMAGES.values() if not os.path.exists(f)]
    if missing:
        sys.exit("Fehlende Abbildungen: " + ", ".join(missing))

    lines = open(args.src, encoding="utf-8").read().split("\n")
    blocks = find_code_blocks(lines)
    print(f"{len(blocks)} Codebloecke erkannt:")
    for s, (e, lang) in sorted(blocks.items()):
        print(f"   Z.{s+1}-{e+1:<5} {lang:<11} {unescape(lines[s]).strip()[:58]}")

    text = re.sub(r"\n{3,}", "\n\n", build(lines))
    # Der Zwischenname darf niemals die Quelldatei treffen - sonst
    # ueberschreibt der Lauf seine eigene Eingabe.
    md_out = os.path.splitext(args.out)[0] + "_pandoc.md"
    if os.path.abspath(md_out) == os.path.abspath(args.src):
        sys.exit(f"Zwischendatei {md_out} waere die Quelldatei. --out aendern.")
    open(md_out, "w", encoding="utf-8").write(text)
    print(f"\n{md_out} geschrieben ({len(text):,} Zeichen, ohne base64).")
    if args.md_only:
        return

    subprocess.run(["pandoc", md_out, "-o", args.out,
                    f"--reference-doc={TEMPLATE}",
                    "--from", "markdown+pipe_tables+table_captions-auto_identifiers",
                    "--dpi=200"], check=True)
    remap_styles(args.out, appendix=args.appendix)
    print(f"{args.out} geschrieben. Inhalt in eine Kopie des Templates einfuegen.")


if __name__ == "__main__":
    main()
