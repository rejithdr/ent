"""Builds the MIDAS ENT team protocol pages from the MIDAS ENT Protocol Google Doc.

Usage: python3 team_build.py <doc.json> <plain_out_dir>

<doc.json> is the Google Docs API document (the "content" object of a read).
The pages written to <plain_out_dir> are READABLE and must never be committed:
team_publish.sh encrypts them into team/ in the repo. This script holds no
protocol text itself.
"""
import html
import json
import re
import sys
from pathlib import Path

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

# Protocols in reading order: (H1 title starts with, page slug, short title, group)
PROTOCOLS = [
    ("MIDAS ENT Otitis Externa", "otitis-externa", "Otitis externa", "Ear"),
    ("Treatment Protocol for Otomycosis", "otomycosis", "Otomycosis", "Ear"),
    ("Treatment Protocol for Acute Otitis Media", "aom", "Acute otitis media", "Ear"),
    ("Midas Preserve™ Protocol for Chronic Otitis Media – Mucosal", "com-mucosal", "Chronic otitis media: mucosal", "Ear"),
    ("Midas Preserve™ Protocol for Chronic Otitis Media – Squamous", "com-squamous", "Chronic otitis media: squamous", "Ear"),
    ("Midas Preserve™ Protocol for Cerumen", "cerumen", "Cerumen and keratosis obturans", "Ear"),
    ("Midas Preserve™ Protocol for Serous Otitis Media", "som", "Serous otitis media", "Ear"),
    ("Sudden Hearing Loss", "sudden-hearing-loss", "Sudden hearing loss, NOT and hum test", "Hearing"),
    ("Chronic Unilateral Hearing Loss", "unilateral-hearing-loss", "Chronic unilateral hearing loss", "Hearing"),
    ("Chronic Bilateral Hearing Loss", "bilateral-hearing-loss", "Chronic bilateral hearing loss", "Hearing"),
    ("MIDAS Vertigo Spectrum", "vertigo", "Vertigo (MVSP)", "Vertigo"),
    ("Pediatric Mouth Breathing", "paediatric-airway", "Paediatric mouth breathing, SDB and adenotonsillar disease", "Children's airway"),
    ("MIDAS Classification and Indications for Tonsil Surgery", "tonsil", "Tonsil surgery: classification and indications", "Children's airway"),
    ("MIDAS Classification and Surgical Protocol for Adenoidectomy", "adenoidectomy", "Adenoidectomy: classification and technique", "Children's airway"),
    ("MIDAS Nasal Obstruction Protocol", "nasal-obstruction", "Nasal obstruction", "Nose and sinus"),
    ("MIDAS Allergic Rhinitis Protocol", "allergic-rhinitis", "Allergic rhinitis", "Nose and sinus"),
    ("MIDAS Rhinosinusitis Protocol", "rhinosinusitis", "Rhinosinusitis", "Nose and sinus"),
    ("MIDAS Adult OSA Protocol", "adult-osa", "Adult obstructive sleep apnoea", "Sleep"),
    ("Treatment Protocol – Earlobe Tear", "earlobe-tear", "Earlobe tear", "Other"),
    ("MIDAS PRESERVE", "philosophy", "Surgical philosophy", "Other"),
]
GROUPS = ["Ear", "Hearing", "Vertigo", "Children's airway", "Nose and sinus", "Sleep", "Other"]

doc = json.loads(SRC.read_text(encoding="utf-8"))
tab = doc["tabs"][0]["documentTab"]
LISTS = tab.get("lists", {})
body = tab["body"]["content"]

ORDERED = {"DECIMAL", "ZERO_DECIMAL", "UPPER_ALPHA", "ALPHA", "UPPER_ROMAN", "ROMAN"}


def is_ordered(list_id, level):
    try:
        lv = LISTS[list_id]["listProperties"]["nestingLevels"][level]
    except (KeyError, IndexError):
        return False
    return lv.get("glyphType", "") in ORDERED


def runs(elements):
    out = []
    for el in elements:
        tr = el.get("textRun")
        if not tr:
            continue
        t = tr["content"].replace("\n", "").replace("\u000b", " ")
        if not t:
            continue
        st = tr.get("textStyle", {})
        h = html.escape(t)
        if st.get("link", {}).get("url"):
            h = f'<a href="{html.escape(st["link"]["url"])}">{h}</a>'
        if st.get("bold"):
            h = f"<strong>{h}</strong>"
        if st.get("italic"):
            h = f"<em>{h}</em>"
        out.append(h)
    return "".join(out).replace("</strong><strong>", "").strip()


def plain(elements):
    return "".join(el.get("textRun", {}).get("content", "") for el in elements).strip()


def para_text(cell_content):
    return "<br>".join(runs(c["paragraph"]["elements"]) for c in cell_content if "paragraph" in c)


# Split the body into protocols by matching H1 titles
sections, current, intro = {}, None, []
for e in body:
    if "paragraph" in e:
        p = e["paragraph"]
        if p["paragraphStyle"].get("namedStyleType") == "HEADING_1":
            title = plain(p["elements"])
            for start, slug, short, group in PROTOCOLS:
                if title.startswith(start):
                    current = slug
                    sections[slug] = []
                    break
    (sections[current] if current else intro).append(e)

missing = [s for _, s, _, _ in PROTOCOLS if s not in sections]
if missing:
    sys.exit(f"Protocol headings not found in the doc: {missing}")

version = next((plain(e["paragraph"]["elements"]) for e in intro if "paragraph" in e
                and plain(e["paragraph"]["elements"]).startswith("Version")), "")
intro_html = "".join(f"<p>{runs(e['paragraph']['elements'])}</p>" for e in intro
                     if "paragraph" in e and plain(e["paragraph"]["elements"])
                     and plain(e["paragraph"]["elements"]) != "Document control")


def render_section(elems):
    """Returns (html, list of (id, h2 text)) for one protocol."""
    out, toc, stack = [], [], []  # stack of (tag, level)

    def close_lists(to_level=-1):
        while stack and stack[-1][1] > to_level:
            out.append(f"</li></{stack.pop()[0]}>")

    first_h1 = True
    for e in elems:
        if "table" in e:
            close_lists()
            rows = e["table"]["tableRows"]
            trs = "".join("<tr>" + "".join(f"<td>{para_text(c['content'])}</td>" for c in r["tableCells"]) + "</tr>" for r in rows)
            out.append(f'<div class="table-scroll"><table>{trs}</table></div>')
            continue
        if "paragraph" not in e:
            continue
        p = e["paragraph"]
        text = runs(p["elements"])
        style = p["paragraphStyle"].get("namedStyleType", "NORMAL_TEXT")
        if not text:
            continue
        bullet = p.get("bullet")
        if bullet and style == "NORMAL_TEXT":
            lvl = bullet.get("nestingLevel", 0)
            tag = "ol" if is_ordered(bullet["listId"], lvl) else "ul"
            close_lists(lvl)
            if stack and stack[-1][1] == lvl and stack[-1][0] != tag:
                close_lists(lvl - 1)
            if stack and stack[-1][1] == lvl:
                out.append(f"</li><li>{text}")
            else:
                stack.append((tag, lvl)); out.append(f"<{tag}><li>{text}")
            continue
        close_lists()
        if style == "HEADING_1":
            if first_h1:
                first_h1 = False
                continue  # the page title is rendered separately
            hid = f"s{len(toc) + 1}"
            toc.append((hid, plain(p["elements"])))
            out.append(f'<h2 id="{hid}">{text}</h2>')
        elif style == "HEADING_2":
            hid = f"s{len(toc) + 1}"
            toc.append((hid, plain(p["elements"])))
            out.append(f'<h2 id="{hid}">{text}</h2>')
        elif style == "HEADING_3":
            out.append(f"<h3>{text}</h3>")
        elif style.startswith("HEADING"):
            out.append(f"<h4>{text}</h4>")
        else:
            out.append(f"<p>{text}</p>")
    close_lists()
    return "\n".join(out), toc


HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{title}</title>
<link rel="stylesheet" href="../css/site.css">
<style>
.team-bar {{ background: #13493b; color: #fff; padding: .6rem 0; font-size: 15px; }}
.team-bar a {{ color: #fff; }}
.team-note {{ color: #a3261b; font-weight: 600; font-size: 14px; }}
.toc {{ border: 1px solid #dde5e1; border-radius: 8px; padding: .4rem 1rem; margin: 1rem 0; }}
.toc ol {{ margin: .4rem 0 .4rem 1.2rem; }}
.proto h2 {{ border-top: 1px solid #dde5e1; padding-top: 1rem; }}
.proto li {{ margin: .2rem 0; }}
.proto td {{ border: 1px solid #dde5e1; padding: .4rem; vertical-align: top; }}
#q {{ width: 100%; font-size: 17px; padding: .6rem; border: 1px solid #9db8ad; border-radius: 8px; }}
.grp h2 {{ margin-bottom: .3rem; }}
.grp ul {{ margin-top: .2rem; }}
</style>
</head>
<body>
<div class="team-bar"><div class="wrap"><a href="index.html"><strong>MIDAS ENT Protocols</strong></a> · team only</div></div>
<main class="wrap proto">
"""
FOOT = """
<p class="team-note">MIDAS ENT team only. Do not share or forward. Clinical judgement overrides the protocol for the individual patient. {version}</p>
</main>
</body>
</html>
"""

meta = []
for start, slug, short, group in PROTOCOLS:
    content, toc = render_section(sections[slug])
    full_title = plain(next(e["paragraph"]["elements"] for e in sections[slug] if "paragraph" in e))
    toc_html = ""
    if len(toc) > 2:
        toc_html = '<details class="toc"><summary>Sections</summary><ol>' + "".join(
            f'<li><a href="#{i}">{html.escape(t)}</a></li>' for i, t in toc) + "</ol></details>"
    page = (HEAD.format(title=html.escape(short) + " | MIDAS ENT Protocols")
            + f'<p><a href="index.html">← All protocols</a></p>\n<h1>{html.escape(full_title)}</h1>\n{toc_html}\n{content}\n'
            + FOOT.format(version=html.escape(version)))
    (OUT / f"{slug}.html").write_text(page, encoding="utf-8")
    meta.append((slug, short, group, " ".join(t for _, t in toc)))

groups_html = ""
for g in GROUPS:
    items = [m for m in meta if m[2] == g]
    if not items:
        continue
    groups_html += f'<section class="grp"><h2>{html.escape(g)}</h2><ul>' + "".join(
        f'<li data-k="{html.escape((short + " " + g + " " + k).lower())}"><a href="{slug}.html">{html.escape(short)}</a></li>'
        for slug, short, _, k in items) + "</ul></section>"

index = (HEAD.format(title="MIDAS ENT Protocols")
         + f"""<h1>MIDAS ENT Protocols</h1>
<p class="lead">The written protocols of MIDAS ENT, for the team. Search, or pick a protocol.</p>
<input id="q" type="search" placeholder="Search: SOM, tonsil grade, epistaxis, DISE…" autocomplete="off">
{groups_html}
<details class="toc"><summary>About this manual</summary>{intro_html}</details>
<script>
var q = document.getElementById("q");
q.addEventListener("input", function () {{
  var w = q.value.toLowerCase().trim().split(/\\s+/);
  document.querySelectorAll("li[data-k]").forEach(function (li) {{
    li.hidden = !w.every(function (x) {{ return li.dataset.k.indexOf(x) !== -1; }});
  }});
  document.querySelectorAll(".grp").forEach(function (g) {{ g.hidden = !g.querySelector("li:not([hidden])"); }});
}});
</script>
""" + FOOT.format(version=html.escape(version)))
(OUT / "index.html").write_text(index, encoding="utf-8")
print(len(meta), "protocols;", version)
