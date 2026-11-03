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
    used = set()

    def new_id(_kind, txt):
        base = re.sub(r"[^a-z0-9]+", "-", txt.lower()).strip("-")[:50] or "h"
        hid, n = base, 2
        while hid in used:
            hid, n = f"{base}-{n}", n + 1
        used.add(hid)
        return hid

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
            hid = new_id("h", plain(p["elements"]))
            toc.append((hid, plain(p["elements"])))
            out.append(f'<h2 id="{hid}">{text}</h2>')
        elif style == "HEADING_2":
            hid = new_id("h", plain(p["elements"]))
            toc.append((hid, plain(p["elements"])))
            out.append(f'<h2 id="{hid}">{text}</h2>')
        elif style == "HEADING_3":
            out.append(f'<h3 id="{new_id("h", plain(p["elements"]))}">{text}</h3>')
        elif style.startswith("HEADING"):
            out.append(f'<h4 id="{new_id("h", plain(p["elements"]))}">{text}</h4>')
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
.xref {{ text-decoration: underline dotted; }}
:target {{ background: #fff6d6; scroll-margin-top: 1rem; }}
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

# ---------------------------------------------------------------- cross-links
# Terms that link to the section that defines them. (pattern, page, heading prefix, only_on_page)
TERMS = [
    (r"Grade I – Partial Tonsillotomy|Partial Tonsillotomy", "tonsil", "Grade I – Partial Tonsillotomy", None),
    (r"Grade II – Subtotal Intracapsular Tonsillectomy|Subtotal Intracapsular Tonsillectomy", "tonsil", "Grade II – Subtotal Intracapsular", None),
    (r"Grade III – Near Total Intracapsular Tonsillectomy|Near[- ]Total Intracapsular Tonsillectomy", "tonsil", "Grade III – Near Total Intracapsular", None),
    (r"Grade IVA – Partial / Subtotal Hybrid Tonsillectomy|Subtotal Hybrid Tonsillectomy", "tonsil", "Grade IVA", None),
    (r"Grade IVB – Total Hybrid Tonsillectomy|Total Hybrid Tonsillectomy", "tonsil", "Grade IVB", None),
    (r"Grade IVA / IVB – Hybrid Tonsillectomy|Hybrid Tonsillectomy", "tonsil", "Grade IVA", None),
    (r"Grade V – Total Extracapsular Tonsillectomy|Total Extracapsular Tonsillectomy", "tonsil", "Grade V – Total Extracapsular", None),
    (r"Grade (?:I|II|III|IV|V)(?: \([a-z -]+\))? adenoidectomy", "adenoidectomy", "GRADE", None),
    (r"Grade (?:I|II|III|IVA|IVB|V)(?: \([a-z -]+\))? (?:intracapsular )?(?:tonsillectomy|tonsillotomy)", "tonsil", "GRADE", None),
    (r"Adenotomy|Debulking Adenoidectomy", "adenoidectomy", "Grade I – Adenotomy", None),
    (r"Subtotal Adenoidectomy", "adenoidectomy", "Grade II – Subtotal Adenoidectomy", None),
    (r"Near[- ]Total Adenoidectomy", "adenoidectomy", "Grade III – Near Total Adenoidectomy", None),
    (r"Hybrid Adenoidectomy", "adenoidectomy", "Grade IV – Hybrid Adenoidectomy", None),
    (r"(?<!Near )(?<!Near-)Total Adenoidectomy", "adenoidectomy", "Grade V – Total Adenoidectomy", None),
    (r"Extrafascial Adenoidectomy", "adenoidectomy", "Extrafascial Adenoidectomy", None),
    (r"Stage (?:IVA|IVB|IVC|III|II|IV|V|I)\b", "vertigo", None, "vertigo"),
    (r"MVSP|MIDAS Vertigo Spectrum Management Protocol", "vertigo", "", None),
    (r"Variation [ABCD]\b", "adult-osa", None, "adult-osa"),
    (r"section \d{1,2}\b", None, None, None),
    (r"NOT test|Noise Occlusion Test", "sudden-hearing-loss", "NOT (Noise Occlusion Test)", None),
    (r"hum test", "sudden-hearing-loss", "Hum Test for Patient Self-Triage", None),
    (r"SOM protocol", "som", "", None),
    (r"(?:MIDAS )?Nasal Obstruction Protocol", "nasal-obstruction", "", None),
    (r"(?:MIDAS )?Allergic Rhinitis Protocol|allergic rhinitis protocol", "allergic-rhinitis", "", None),
    (r"(?:MIDAS )?Rhinosinusitis Protocol", "rhinosinusitis", "", None),
    (r"(?:MIDAS )?Adult OSA [Pp]rotocol", "adult-osa", "", None),
    (r"(?:Age )?Group [ABCD]\b|AGE GROUP [ABCD]\b", "paediatric-airway", None, "paediatric-airway"),
]

rendered = {slug: render_section(sections[slug]) for _, slug, _, _ in PROTOCOLS}
HEADS = {}  # page -> [(id, text)]
for slug, (content, _) in rendered.items():
    HEADS[slug] = [(m.group(2), html.unescape(re.sub("<[^>]+>", "", m.group(3))))
                   for m in re.finditer(r'<h([234]) id="([^"]+)">(.*?)</h\1>', content)]


def find_anchor(page, prefix):
    if prefix == "":
        return ""
    for hid, text in HEADS[page]:
        if text.startswith(prefix):
            return hid
    return None


def target_for(term, page_now):
    """(page, anchor) for a matched term, or None."""
    for pat, page, prefix, only in TERMS:
        if not re.fullmatch(pat, term, flags=re.I):
            continue
        if only and page_now != only:
            return None
        if pat.startswith("section"):
            n = term.split()[1]
            hid = next((h for h, t in HEADS[page_now] if re.match(rf"{n}\.\s", t)), None)
            return (page_now, hid) if hid else None
        if prefix == "GRADE":  # "Grade II (subtotal) adenoidectomy" -> the Grade II definition
            num = term.split()[1]
            hid = next((h for h, t in HEADS[page] if t.startswith(f"Grade {num} –")), None)
            return (page, hid) if hid else None
        if prefix is None:  # stage / variation / group: heading containing the term
            key = term.upper().replace("AGE ", "")
            hid = next((h for h, t in HEADS[page] if t.upper().replace("AGE ", "").startswith(key)
                        or t.upper().startswith("AGE " + key)), None)
            return (page, hid) if hid else None
        hid = find_anchor(page, prefix)
        return (page, hid) if hid is not None else None
    return None


TERM_RE = re.compile("|".join(f"(?:{p})" for p, *_ in TERMS), flags=re.I)


def link_terms(page_now, content):
    parts = re.split(r"(<[^>]+>)", content)
    out, in_a, in_h, current = [], 0, 0, None
    for part in parts:
        if part.startswith("<"):
            if part.startswith("<a "): in_a += 1
            elif part == "</a>": in_a -= 1
            m = re.match(r'<h[234] id="([^"]+)"', part)
            if m:
                in_h += 1; current = m.group(1)
            elif re.match(r"</h[234]>", part):
                in_h -= 1
            out.append(part)
            continue
        if in_a or in_h or not part.strip():
            out.append(part)
            continue
        def sub(m):
            t = target_for(m.group(0), page_now)
            if not t or (t[0] == page_now and (t[1] == current or t[1] == "")):
                return m.group(0)
            href = ("" if t[0] == page_now else f"{t[0]}.html") + (f"#{t[1]}" if t[1] else "")
            return f'<a class="xref" href="{href}">{m.group(0)}</a>'
        out.append(TERM_RE.sub(sub, part))
    return "".join(out)


meta = []
for start, slug, short, group in PROTOCOLS:
    content, toc = rendered[slug]
    content = link_terms(slug, content)
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
