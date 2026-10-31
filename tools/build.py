"""Builds the entmidas.com site into the repo folder given as argv[1]."""
import json
import re
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
SITE = "https://entmidas.com"
PHONE_TEL = "+918139005150"
PHONE_SHOW = "81390 05150"
WHATSAPP = "https://wa.me/918139005150"
UPDATED = "October 2026"

import hashlib


def asset(path):
    """Adds a short content hash so browsers fetch the new file after each change."""
    h = hashlib.md5((OUT / path).read_bytes()).hexdigest()[:8]
    return f"{path}?v={h}"


NAV = [
    ("index.html", "Home"),
    ("about.html", "About Dr Rejith"),
    ("hospitals.html", "Clinics & timings"),
    ("snoring.html", "Snoring & sleep apnoea"),
]

# All condition pages, grouped. Keywords help the search box find a page
# when people use everyday words.
CONDITIONS = [
    ("Sleep", [
        ("snoring.html", "Snoring in children and adults", "snore snoring mouth breathing child sleep"),
        ("sleepapnoea.html", "Obstructive sleep apnoea", "osa apnea apnoea sleepy tired cpap breathing pauses"),
        ("sleep-score.html", "MERA Sleep Apnoea Score (self-check)", "score test check quiz questionnaire sleep apnoea snoring self check"),
        ("child-sleep-score.html", "MERA Child Sleep Apnoea Score", "child children kid score test check quiz adenoid snoring mouth breathing"),
    ]),
    ("Ear and balance", [
        ("earsurgery.html", "Ear discharge, hearing loss and ear surgery", "ear discharge pus hole eardrum deaf deafness hearing loss tympanoplasty interlay wax"),
        ("balloon-et.html", "Blocked ear and balloon Eustachian tube dilation", "blocked ear ear block fullness popping eustachian tube balloon dilation tuboplasty pressure flying"),
        ("vertigo.html", "Vertigo, dizziness and imbalance", "vertigo giddiness dizziness dizzy spinning balance bppv ear balance"),
    ]),
    ("Nose and sinus", [
        ("septum.html", "Blocked nose and deviated septum", "nose block blocked septum deviated septoplasty nosebleed"),
        ("polyp.html", "Nasal polyps and sinus surgery", "polyp polyps sinus sinusitis smell"),
        ("balloon-sinus.html", "Balloon sinus surgery", "balloon sinus sinusitis sinuplasty sinus headache"),
        ("migraine.html", "Headache and migraine", "headache migraine head pain"),
    ]),
    ("Throat and neck", [
        ("adenoids.html", "Adenoids", "adenoid adenoids mouth breathing child snoring"),
        ("tonsil.html", "Tonsils and tonsil surgery", "tonsil tonsils tonsillitis throat infection quinsy tonsillectomy stones"),
        ("voice.html", "Voice change and hoarseness", "voice hoarse hoarseness throat nodule polyp"),
        ("thyroid.html", "Thyroid swelling and thyroid surgery", "thyroid neck swelling goitre nodule"),
        ("sial.html", "Salivary gland swelling and stones", "salivary saliva gland stone swelling sialendoscopy jaw"),
    ]),
    ("Specialised surgery", [
        ("skullbase.html", "Skull base surgery", "skull base pituitary csf leak facial nerve palsy"),
        ("daycare.html", "Day-care surgery", "day care daycare same day discharge"),
    ]),
]

PAGES = {}


def page(slug, title, description, body, h1=None, schema=None):
    PAGES[slug] = dict(title=title, description=description, body=body, schema=schema)


def render(slug, p):
    url = SITE + "/" + ("" if slug == "index.html" else slug)
    nav = "\n      ".join(
        f'<a href="{href}"{" aria-current=\"page\"" if href == slug else ""}>{label}</a>'
        for href, label in NAV
    )
    in_conditions = any(href == slug for _, items in CONDITIONS for href, _, _ in items)
    cond_html = "\n".join(
        '              <div class="cond-group"><h3>' + group + '</h3><ul>'
        + "".join(
            f'<li data-k="{label.lower()} {kw}"><a href="{href}"'
            + (' aria-current="page"' if href == slug else "")
            + f'>{label}</a></li>'
            for href, label, kw in items
        )
        + "</ul></div>"
        for group, items in CONDITIONS
    )
    schema = ""
    if p["schema"]:
        schema = (
            '<script type="application/ld+json">\n'
            + json.dumps(p["schema"], indent=2, ensure_ascii=False)
            + "\n</script>\n"
        )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{p["title"]}</title>
<meta name="description" content="{p["description"]}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{p["title"]}">
<meta property="og:description" content="{p["description"]}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="website">
<link rel="icon" href="favicon.ico">
<link rel="preload" href="fonts/manjari-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{asset('css/site.css')}">
{schema}</head>
<body>

<a class="skip" href="#content">Skip to content</a>

<header class="site">
  <div class="wrap bar">
    <a class="brand" href="index.html">
      <span class="name">Dr Rejith R S</span>
      <span class="role">ENT Surgeon, Thrissur</span>
    </a>
    <div class="actions">
      <a class="btn" href="tel:{PHONE_TEL}">Call {PHONE_SHOW}</a>
      <a class="btn quiet" href="{WHATSAPP}">WhatsApp</a>
    </div>
  </div>
  <nav class="main" aria-label="Main">
    <div class="wrap">
      {nav}
      <details class="conditions"{" data-current=\"1\"" if in_conditions else ""}>
        <summary>All conditions</summary>
        <div class="cond-panel">
          <div class="wrap">
            <label class="cond-search-label" for="cond-search">Search conditions</label>
            <input id="cond-search" class="cond-search" type="search" placeholder="For example: tonsils, giddiness, ear discharge" autocomplete="off">
            <div class="cond-groups">
{cond_html}
            </div>
            <p class="cond-none" hidden>No matching page. Please call <a href="tel:{PHONE_TEL}">{PHONE_SHOW}</a> and we'll help.</p>
          </div>
        </div>
      </details>
    </div>
  </nav>
</header>

<main id="content" class="wrap">
{p["body"].strip()}
</main>

<footer class="site">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <p class="foot-name">Dr Rejith R S</p>
        <p>MBBS, DLO, Consultant ENT Surgeon, Thrissur</p>
        <p><a href="tel:{PHONE_TEL}">Call {PHONE_SHOW}</a><br><a href="{WHATSAPP}">Message on WhatsApp</a><br><a href="https://www.youtube.com/@Entdoctormidas">Videos on YouTube</a></p>
      </div>
      <div>
        <p class="foot-name">MIDAS ENT clinics</p>
        <p><a href="midas.html">MIDAS Hospital, Ollur</a><br><a href="metropolitan.html">MIDAS ENT at Metropolitan Hospital, Thrissur</a></p>
        <p><a href="hospitals.html">All timings</a></p>
      </div>
    </div>
    <p class="fine">This website provides general information and is not a substitute for medical advice. Please consult a doctor about your own symptoms. Written and reviewed by Dr Rejith R S. Last updated {UPDATED}.</p>
  </div>
</footer>

<script src="{asset('js/site.js')}" defer></script>

<div class="dock" aria-label="Book a consultation">
  <a href="tel:{PHONE_TEL}">Call</a>
  <a href="{WHATSAPP}">WhatsApp</a>
</div>

</body>
</html>
"""


def redirect(target):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex">
<link rel="canonical" href="{SITE}/{target}">
<meta http-equiv="refresh" content="0; url={target}">
<title>Page moved</title>
</head>
<body>
<p>This page has moved. Please visit <a href="{target}">{target}</a>.</p>
</body>
</html>
"""


CHANNEL = "https://www.youtube.com/@Entdoctormidas"


def video(vid, title):
    return f"""
<figure class="video-fig">
  <div class="video">
    <iframe src="https://www.youtube-nocookie.com/embed/{vid}" title="{title}" loading="lazy" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
  </div>
  <figcaption>Video by Dr Rejith R S: {title}</figcaption>
</figure>
"""


def ask_ai(prompt_text, topic):
    return f"""
<section class="ai-help" aria-labelledby="ai-{topic}">
  <h2 id="ai-{topic}">Ask your AI assistant</h2>
  <p>Many patients like to read more before their visit. You can copy this question into ChatGPT, Gemini, Claude or any AI assistant, and change the details to match your own situation.</p>
  <div class="prompt-box">
    <p class="prompt-text" id="prompt-{topic}">{prompt_text}</p>
    <button type="button" class="btn copy-btn" data-copy="prompt-{topic}">Copy question</button>
  </div>
  <p class="ai-note">AI assistants can give wrong or outdated answers, and they can't examine you. Use the answer to understand your condition, not to diagnose or treat yourself. Bring your questions to the clinic and we'll go through them with you.</p>
</section>
"""


def chat(items, topic):
    rows = "".join(
        f'<div class="msg q"><span class="who">Patient</span><p>{q}</p></div>'
        f'<div class="msg a"><span class="who">Dr Rejith</span><p>{a}</p></div>'
        for q, a in items
    )
    return f"""
<section class="chat" aria-labelledby="chat-{topic}">
  <h2 id="chat-{topic}">Questions patients ask</h2>
  <p class="chat-note">Common questions from the clinic, with answers written by Dr Rejith R S.</p>
  <div class="thread">{rows}</div>
</section>
"""


BOOK = f"""
<h2>Book a consultation</h2>
<p>Call <a href="tel:{PHONE_TEL}">{PHONE_SHOW}</a> or message on <a href="{WHATSAPP}">WhatsApp</a>. See <a href="hospitals.html">clinics and timings</a>.</p>
"""

# ---------------------------------------------------------------- Home
page(
    "index.html",
    "ENT Doctor in Thrissur | Dr Rejith R S, ENT Surgeon",
    "Dr Rejith R S, ENT surgeon in Thrissur. Snoring and sleep apnoea, adenoids and tonsils, vertigo, ear surgery, sinus, voice and thyroid care, with day-care surgery.",
    f"""
<section class="intro">
  <div class="intro-text">
    <h1>ENT care in Thrissur, for children and adults</h1>
    <p class="lead">Snoring, a blocked nose, dizziness, ear trouble, or a child who breathes through the mouth. Dr Rejith R S and team treat problems of the ear, nose, throat and neck, and most operations need no overnight stay.</p>
    <p class="intro-actions"><a class="btn" href="tel:{PHONE_TEL}">Call {PHONE_SHOW}</a> <a class="btn quiet" href="hospitals.html">Clinics and timings</a></p>
  </div>
  <img class="intro-photo" src="photo.jpg" alt="Dr Rejith R S, ENT surgeon, Thrissur" width="250" height="300">
</section>

<p class="tagline"><strong>MIDAS MERA</strong>: Maximising Effectiveness, Retaining Anatomy. Treat what's diseased. Protect what works.</p>

<h2>What brings you here?</h2>
<ul class="paths">
  <li><a href="snoring.html"><strong>Snoring or sleep apnoea</strong><span>Loud snoring, pauses in breathing, tired all day</span></a></li>
  <li><a href="adenoids.html"><strong>A child who breathes through the mouth</strong><span>Snoring, open-mouth sleep, blocked nose, ear fluid</span></a></li>
  <li><a href="vertigo.html"><strong>Vertigo or dizziness</strong><span>Spinning on turning in bed, imbalance</span></a></li>
  <li><a href="earsurgery.html"><strong>Ear discharge or hearing loss</strong><span>Hole in the eardrum, blocked ear, sudden deafness</span></a></li>
  <li><a href="septum.html"><strong>Blocked nose or sinus trouble</strong><span>Deviated septum, polyps, sinusitis</span></a></li>
  <li><a href="voice.html"><strong>Voice change</strong><span>Hoarseness that doesn't settle</span></a></li>
</ul>

<h2>What does an ENT specialist treat?</h2>
<p>Diseases of the ear, nose, throat and neck, including hearing loss, ear infections, vertigo, nasal blockage, sinusitis, snoring, voice problems, tonsil and adenoid problems, and thyroid swellings.</p>

<h2>How is a patient assessed?</h2>
<ul>
  <li>We listen to your complaints and examine you. Endoscopy is often used to complete the examination.</li>
  <li>After a provisional diagnosis, we either start treatment or arrange tests.</li>
  <li>Tests may include blood tests, X-rays, scans, hearing tests, endoscopy or biopsy.</li>
</ul>

<h2>Treatment</h2>
<ul>
  <li>Procedures in the clinic, such as wax removal and <a href="vertigo.html">vertigo correction manoeuvres</a></li>
  <li>Medicines for allergy, sinusitis, infections and voice problems</li>
  <li>Vestibular rehabilitation and voice therapy</li>
  <li>Surgery, mostly as <a href="daycare.html">day-care surgery</a>: <a href="tonsil.html">tonsils</a>, <a href="adenoids.html">adenoids</a>, <a href="septum.html">nasal septum</a>, <a href="polyp.html">sinus and polyps</a>, <a href="snoring.html">snoring</a>, <a href="earsurgery.html">hole in the eardrum</a>, <a href="voice.html">voice problems</a> and <a href="thyroid.html">thyroid</a></li>
</ul>

<h2>Areas of practice</h2>
<ul>
  <li><a href="snoring.html">Snoring and sleep apnoea clinic</a>, for children and adults</li>
  <li><a href="adenoids.html">Endoscopic coblation adenoidectomy</a> and <a href="tonsil.html">intracapsular tonsil surgery</a></li>
  <li><a href="vertigo.html">Vertigo and balance clinic</a></li>
  <li><a href="earsurgery.html">Endoscopic ear surgery</a>, including endoscopic interlay tympanoplasty</li>
  <li><a href="balloon-et.html">Balloon Eustachian tube dilation</a> for blocked ears</li>
  <li><a href="balloon-sinus.html">Balloon sinus surgery</a></li>
  <li><a href="septum.html">Endoscopic nasal and septal surgery</a> and <a href="polyp.html">nasal polyps</a></li>
  <li><a href="voice.html">Voice clinic (laryngology)</a></li>
  <li><a href="thyroid.html">Thyroid surgery</a></li>
  <li><a href="sial.html">Sialendoscopy for salivary gland problems</a></li>
  <li><a href="skullbase.html">Skull base surgery</a></li>
  <li><a href="migraine.html">Headache and migraine clinic</a></li>
</ul>
{BOOK}
""",
    schema={
        "@context": "https://schema.org",
        "@type": "Physician",
        "name": "Dr Rejith R S",
        "description": "ENT surgeon in Thrissur, Kerala",
        "medicalSpecialty": "Otolaryngologic",
        "url": SITE + "/",
        "image": SITE + "/photo.jpg",
        "telephone": PHONE_TEL,
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Thrissur",
            "addressRegion": "Kerala",
            "addressCountry": "IN",
        },
        "areaServed": "Thrissur",
    },
)

# ---------------------------------------------------------------- About
page(
    "about.html",
    "About Dr Rejith R S, ENT Surgeon in Thrissur",
    "Dr Rejith R S, MBBS, DLO, Government Medical College Trivandrum. ENT surgeon in Thrissur with an interest in sleep apnoea, vertigo and day-care ENT surgery.",
    f"""
<img class="portrait" src="photo.jpg" alt="Dr Rejith R S, ENT surgeon, Thrissur">
<h1>Dr Rejith R S</h1>
<p class="lead">Consultant ENT Surgeon, Thrissur</p>
<p>ENT surgeon since 2010, with a special interest in snoring and sleep apnoea, vertigo, endoscopic ear surgery and day-care ENT surgery. He also works on medical innovation and on training young ENT surgeons.</p>

<h2>Education</h2>
<p>MBBS and postgraduate Diploma in Otorhinolaryngology (DLO) from Government Medical College, Thiruvananthapuram.</p>

<h2>Positions held</h2>
<ul>
  <li>Senior Consultant ENT Surgeon, <a href="midas.html">MIDAS Hospital and Surgical Centre</a>, Ollur, Thrissur (since 2024)</li>
  <li>Senior Consultant ENT Surgeon, Daya General Hospital, Thrissur (2017–2023)</li>
  <li>Consultant ENT Surgeon, Muthoot Medical Centre, Pathanamthitta</li>
  <li>ENT Surgeon, Meditrina Hospital, Thiruvananthapuram</li>
  <li>Lecturer, Government Medical College, Thiruvananthapuram</li>
</ul>

<h2>Our approach: MIDAS MERA</h2>
<p><strong>Maximising Effectiveness, Retaining Anatomy.</strong> Every operation is planned around what needs to be treated and what should be protected. Where tissue is diseased, it is treated fully. Where it still works, we try to keep it.</p>
<p>For children's adenoid and tonsil surgery, this means a defined, graded protocol: the amount of tissue removed is planned according to the child's age and the problem being treated.</p>
{BOOK}
""",
)

# ---------------------------------------------------------------- Clinics
page(
    "hospitals.html",
    "MIDAS ENT Clinics and Timings in Thrissur | Dr Rejith ENT",
    "Consultation timings for Dr Rejith R S and the MIDAS ENT team at MIDAS Hospital, Ollur, and the MIDAS ENT evening clinic at Metropolitan Hospital, Thrissur.",
    f"""
<h1>MIDAS ENT Clinics and Timings</h1>
<p class="lead">Please call before visiting, as timings can change on holidays.</p>
<div class="table-scroll">
<table class="stack">
  <tr><th>Clinic</th><th>Location</th><th>Days</th><th>Time</th></tr>
  <tr><td data-label="Clinic"><a href="midas.html">MIDAS Hospital and Surgical Centre</a></td><td data-label="Location">Ollur, Thrissur</td><td data-label="Days">Monday to Saturday</td><td data-label="Time">3:00 pm to 5:00 pm</td></tr>
  <tr><td data-label="Clinic"><a href="metropolitan.html">MIDAS ENT at Metropolitan Hospital</a></td><td data-label="Location">Thrissur</td><td data-label="Days">Monday to Saturday</td><td data-label="Time">5:45 pm to 6:45 pm, by appointment only</td></tr>
</table>
</div>
<p>More MIDAS ENT clinics are planned in Thrissur. New branches will be listed here when they open.</p>
{BOOK}
""",
)


def clinic(slug, name, place, timing, img, alt, tel, tel_show, extra=""):
    page(
        slug,
        f"{name}, {place} | Dr Rejith ENT",
        f"ENT consultation with Dr Rejith R S at {name}, {place}. {timing}",
        f"""
{f'<img class="hero" src="{img}" alt="{alt}">' if img else ""}
<h1>{name}</h1>
<p class="lead">{place}</p>
<div class="box"><strong>ENT clinic timings:</strong> {timing}</div>
{extra}
<p><a class="btn" href="tel:{tel}">Call {tel_show} to book</a></p>
<p><a href="hospitals.html">See all clinics and timings</a></p>
""",
    )


clinic("midas.html", "ENT Clinic at MIDAS Hospital and Surgical Centre", "Ollur, Thrissur",
       "Monday to Saturday, 3:00 pm to 5:00 pm.", "midas.jpg",
       "MIDAS Hospital and Surgical Centre, Ollur, Thrissur", PHONE_TEL, PHONE_SHOW,
       "<p>A day-care surgical hospital, where most ENT operations are done with same-day discharge.</p>")
clinic("metropolitan.html", "MIDAS ENT at Metropolitan Hospital", "Thrissur",
       "Monday to Saturday, 5:45 pm to 6:45 pm. By appointment only.", None,
       "", PHONE_TEL, PHONE_SHOW,
       "<p>An evening ENT clinic of MIDAS ENT, where patients are seen by Dr Rejith R S. Please book an appointment before visiting.</p>")

SLEEP_CHAT = chat([
    ("I only snore. Why do I need a sleep test?",
     "Snoring alone can be harmless. But loud snoring with daytime sleepiness, pauses in breathing noticed by your family, or high blood pressure may mean sleep apnoea. A sleep study is the only way to know how severe it is, and the right treatment depends on that."),
    ("Is the sleep study done at home or in hospital?",
     "Both are possible. A home sleep study is convenient and suits many adults. A full study in hospital gives more detail and is better for some patients. We'll suggest which suits you."),
    ("Will surgery cure my sleep apnoea?",
     "It can in selected patients, especially when there is a clear blockage such as large tonsils or a blocked nose. For many adults, CPAP works best. Before airway surgery we often do sleep endoscopy (DISE) to see exactly where your airway closes, so the operation is planned for your airway."),
    ("I tried CPAP and couldn't tolerate it. What now?",
     "That's common, and often fixable. The mask fit, the pressure setting or a blocked nose is frequently the problem. If CPAP still doesn't work for you, an oral device or surgery planned with sleep endoscopy may help."),
    ("Does losing weight help?",
     "Yes. Weight loss reduces sleep apnoea for most people, and sometimes removes it. For moderate or severe sleep apnoea, it works best alongside other treatment rather than as the only plan."),
], "sleep")

SLEEP_AI = ask_ai(
    "I am a 45-year-old man. I snore loudly, my wife says I sometimes stop breathing at night, and I feel sleepy during the day. In simple language, please explain what obstructive sleep apnoea is, what can happen if it is not treated, how it is tested, and what treatments are available. Also list 5 questions I should ask my ENT doctor.",
    "sleep")

CHILD_CHAT = chat([
    ("My child snores only when he has a cold. Is that a problem?",
     "Snoring only during colds is usually not a concern. Snoring on most nights, especially with mouth breathing, is worth getting checked."),
    ("Will my child need surgery?",
     "Not always. Many children improve with nasal sprays and treatment of allergy, so we usually try medicines first and review. Surgery is advised when breathing, sleep or growth don't improve."),
    ("I've been told adenoids disappear by themselves. What happens if my child snores and breathes through the mouth, or keeps getting ear infections or fluid in the ear, and I decide to wait instead of surgery?",
     "Normal adenoids do shrink, usually by about 11 years. But waiting has a cost when a child is clearly affected. Sleep apnoea can slow a child's growth, in both weight and height. Long-term mouth breathing affects how the face, jaw and teeth develop. And a chronic adenoid infection that doesn't settle, rather than the size of the adenoid, causes fluid behind the eardrum. That fluid reduces hearing, which can show up as poor school performance and difficulty mixing with other children. These effects build up over the years of waiting, so when they are present we don't advise waiting."),
    ("Will the adenoids grow back after surgery?",
     "It depends on how much adenoid tissue was removed, and that is planned according to the child's age, the type of disease and the symptoms. After a total or near-total adenoidectomy, where the tissue is removed down to the underlying layer (the fascia), regrowth is very unlikely, and it rarely causes blockage again. After a partial or subtotal adenoidectomy, where some tissue is deliberately kept to preserve its function in a young child, some regrowth can happen."),
    ("Is adenoid surgery painful?",
     "Most children have little pain after endoscopic coblation adenoidectomy and go home the same day. After tonsil surgery, recovery depends on the type: intracapsular surgery usually means less pain."),
    ("Should I send my child's sleep video on WhatsApp?",
     "No, please don't. Record it as described on this page, keep it on your phone, and show it to us in the clinic."),
], "child")

CHILD_AI = ask_ai(
    "My 6-year-old child snores most nights and sleeps with the mouth open. In simple language, please explain the common causes in children, why mouth breathing matters for a growing child, when I should see an ENT doctor, and what treatments are usually tried first. Also list 5 questions I should ask the doctor.",
    "child")

# ---------------------------------------------------------------- Snoring (new page)
page(
    "snoring.html",
    "Snoring and Sleep Apnoea Treatment in Thrissur | Dr Rejith ENT",
    "Snoring and sleep apnoea care for children and adults in Thrissur. Warning signs, when to see a doctor, and treatment options, from Dr Rejith R S, ENT surgeon.",
    f"""
<h1>Snoring and Sleep Apnoea Treatment in Thrissur, for Children and Adults</h1>
<p class="lead">Snoring is common, but it isn't always harmless. Sometimes it's a sign that breathing is being blocked during sleep. This page explains what to look for, when to see a doctor, and how it can be treated.</p>
<p class="tagline">MIDAS MERA: Maximising Effectiveness, Retaining Anatomy. Treat what's diseased. Protect what works.</p>

<div class="choose">
  <a href="#children">My child snores</a>
  <a href="#adults">I snore, or my partner does</a>
  <a href="#doctors">I'm a doctor referring a patient</a>
</div>

{video("1kbIIYia3Ug", "Snoring: is it normal? Should you consult a doctor?")}

<h2>What is snoring?</h2>
<p>Snoring is the sound made when the airway in the nose and throat partly narrows during sleep, and the soft tissues vibrate as air passes through.</p>
<p>Snoring sits on a range:</p>
<ul>
  <li><strong>Simple snoring:</strong> noise only, with no breathing pauses and no effect on health. Treatment is optional.</li>
  <li><strong>Upper airway resistance:</strong> breathing takes more effort and sleep is disturbed, even without full pauses. Worth treating before it progresses.</li>
  <li><strong>Obstructive sleep apnoea (OSA):</strong> breathing repeatedly stops or becomes very shallow for 10 seconds or more during sleep. This needs treatment. <a href="sleepapnoea.html">More about sleep apnoea</a>.</li>
</ul>

<h2 id="children">Snoring in children</h2>
{video("s2h-rO01osY", "Is snoring and mouth breathing in children normal?")}
<p>Children should not snore regularly. Regular snoring, especially with mouth breathing, usually means the airway is narrowed, most often by enlarged <a href="adenoids.html">adenoids</a> or <a href="tonsil.html">tonsils</a>.</p>

<div class="box"><strong>Check your child:</strong> take the free <a href="child-sleep-score.html">MERA Child Sleep Apnoea Score</a>.</div>

<h3>Signs parents often miss</h3>
<ul>
  <li>Snoring most nights</li>
  <li>Sleeping with the mouth open, or breathing through the mouth during the day</li>
  <li>Restless sleep, unusual sleeping positions, or frequent waking</li>
  <li>Pauses in breathing, gasping or choking during sleep</li>
  <li>Bedwetting after the child had stopped</li>
  <li>Tiredness, irritability, hyperactivity or poor attention at school</li>
  <li>Poor weight gain or slow growth</li>
</ul>

<h3>Why it matters</h3>
<p>Long-term mouth breathing and poor sleep can affect a child's growth, behaviour, learning, and the development of the face and teeth. Early assessment gives the best chance to correct it.</p>

<div class="urgent">
  <strong>Seek urgent medical care</strong> if your child has long pauses in breathing, turns blue or pale during sleep, or is struggling hard to breathe.
</div>

<h3>Recording a sleep video at home</h3>
<p>A short video helps us see how your child breathes during sleep. Please record it like this:</p>
<ul>
  <li>Record during deep sleep, about 1–2 hours after your child falls asleep, or in the early morning.</li>
  <li>If possible, your child should be lying on their back.</li>
  <li>Show the chest, at least up to the collarbones, and ideally the whole chest, so we can see the breathing effort.</li>
  <li>Make sure there is enough light to see breathing clearly.</li>
  <li>Record for 2–3 minutes, including any snoring, pauses or struggling.</li>
</ul>
<div class="box">
  <strong>Your child's privacy matters to us.</strong> We never ask you to send your child's video by WhatsApp or any other app. Keep it on your phone and show it to us during the consultation.
</div>

<h3>How we treat children</h3>
<p>Many children improve with medical treatment, such as nasal sprays and treatment of allergy, especially when symptoms are mild. We usually try this first and review progress.</p>
<p>When surgery is needed, we follow a defined, graded protocol. The amount of adenoid and tonsil tissue removed is planned according to your child's age and the problem being treated. Put simply, <strong>we remove only what is needed, and protect what works.</strong></p>
<ul>
  <li>Endoscopic coblation adenoidectomy, with the surgeon viewing the area directly</li>
  <li>Intracapsular tonsil surgery when appropriate, which usually means less pain and faster recovery</li>
  <li>Most children go home the same day</li>
</ul>
<p>If mouth breathing has affected the teeth or jaw, we may also suggest an orthodontic assessment.</p>

<h2 id="adults">Snoring and sleep apnoea in adults</h2>
<p>In adults, loud snoring can be a sign of obstructive sleep apnoea. Many people with sleep apnoea don't know they have it, because it happens while they're asleep.</p>

<div class="box"><strong>Check yourself:</strong> take the free <a href="sleep-score.html">MERA Sleep Apnoea Score</a> to see how likely sleep apnoea is.</div>

<h3>Warning signs</h3>
<ul>
  <li>Loud snoring, often noticed by a partner</li>
  <li>Someone has seen you stop breathing, gasp or choke during sleep</li>
  <li>Feeling tired or falling asleep during the day, even after a full night in bed</li>
  <li>Morning headaches, a dry mouth, or poor concentration</li>
  <li>High blood pressure</li>
  <li>Being overweight, or having a thick neck</li>
</ul>

<div class="urgent">
  <strong>Drowsy while driving?</strong> If you feel sleepy at the wheel, please don't drive until you have been assessed. Sleep apnoea is a recognised cause of road accidents.
</div>

<h3>Why it matters</h3>
<p>Untreated sleep apnoea is linked with high blood pressure, heart disease, stroke, diabetes, low mood and poor memory. Treatment can improve sleep, energy and long-term health.</p>

<h3>How sleep apnoea is assessed</h3>
<ul>
  <li><strong>Consultation and examination</strong> of the nose, throat and airway</li>
  <li><strong>Sleep study</strong> to confirm the diagnosis and measure severity</li>
  <li><strong>Sleep endoscopy (DISE)</strong> in selected patients, to see exactly where the airway collapses during sleep before planning surgery</li>
</ul>

<h3>Treatment options</h3>
<p>There is no single treatment for everyone. The right choice depends on how severe the sleep apnoea is and where the airway is blocked.</p>
<div class="table-scroll">
<table>
  <tr><th>Treatment</th><th>Who it helps</th></tr>
  <tr><td>Lifestyle changes, including weight loss and avoiding alcohol at night</td><td>Everyone, as part of any treatment plan</td></tr>
  <tr><td>Treating nasal blockage (allergy, sinusitis, deviated septum)</td><td>People whose nose is part of the problem</td></tr>
  <tr><td>CPAP (a small mask and machine worn during sleep)</td><td>The most effective treatment for moderate to severe sleep apnoea</td></tr>
  <tr><td>Oral devices from a dentist</td><td>Selected people with mild to moderate sleep apnoea</td></tr>
  <tr><td>Airway surgery</td><td>Selected people, especially those who can't use CPAP, planned according to where the airway is blocked</td></tr>
</table>
</div>

{CHILD_CHAT}
{CHILD_AI}

<h2 id="doctors">For doctors: referring a patient</h2>
<p>We welcome referrals from paediatricians, pulmonologists, physicians, dentists and orthodontists.</p>
<h3>Consider referring</h3>
<ul>
  <li>Children with habitual snoring, mouth breathing, witnessed apnoeas, enuresis, behavioural or growth concerns</li>
  <li>Adults with suspected or confirmed OSA who are CPAP-intolerant, have nasal obstruction affecting CPAP use, or are being considered for surgery</li>
  <li>Patients needing sleep endoscopy (DISE) for treatment planning</li>
</ul>
<div class="box">
  <strong>We keep you informed.</strong> After every referral, we send you a short update on our assessment and plan, and the patient returns to you for ongoing care.
</div>
<p>To refer a patient, call or WhatsApp <a href="tel:{PHONE_TEL}">{PHONE_SHOW}</a>.</p>
{BOOK}
""",
)

# ---------------------------------------------------------------- Sleep apnoea
page(
    "sleepapnoea.html",
    "Obstructive Sleep Apnoea Treatment in Thrissur | Dr Rejith ENT",
    "Causes, symptoms, tests and treatment of obstructive sleep apnoea, including sleep study, DISE, CPAP, oral devices and airway surgery, in Thrissur.",
    f"""
<img class="hero" src="osa.jpg" alt="Diagram of normal breathing and obstructive sleep apnoea">
<h1>Obstructive Sleep Apnoea</h1>

<h2>What causes obstructive sleep apnoea?</h2>
<p>During deep sleep, the muscles that keep the upper airway open relax. The airway narrows, and with each breath it is sucked further inwards. Breathing effort continues, but air cannot pass freely.</p>

<h2>Symptoms</h2>
<ul>
  <li>Loud, irregular snoring with pauses in the pattern</li>
  <li>Daytime sleepiness and tiredness</li>
  <li>Poor memory, irritability and reduced interest in sex</li>
</ul>

<div class="box"><strong>Check yourself:</strong> take the free <a href="sleep-score.html">MERA Sleep Apnoea Score</a> to see how likely sleep apnoea is.</div>

<h2>Tests for sleep apnoea</h2>
<ul>
  <li><strong>Sleep study:</strong> shows the type and severity of sleep apnoea</li>
  <li><strong>Sleep endoscopy (DISE):</strong> identifies the areas causing obstruction</li>
  <li><strong>Dynamic MRI:</strong> useful in selected patients</li>
</ul>

<h2>Can sleep apnoea be cured?</h2>
<p>CPAP, BiPAP and oral devices control sleep apnoea very effectively while they are used, but they do not cure it. Weight reduction and surgery can cure it in selected patients.</p>

<h2>Treatment options</h2>
<ul>
  <li>Lifestyle changes</li>
  <li>Medicines for nasal blockage and acid reflux</li>
  <li>Custom-made mandibular advancement devices</li>
  <li>Myofunctional therapy (exercises for the mouth, tongue and throat muscles), through a dentist we refer you to</li>
  <li>Surgery to relieve the obstruction:
    <ul>
      <li>Correcting fixed blockages, such as nasal blockage and enlarged adenoids and tonsils</li>
      <li>Palatal surgery, such as expansion pharyngoplasty or Z-palatoplasty</li>
      <li>Tongue base reduction using coblation</li>
      <li>Epiglottopexy, which moves the epiglottis forward to relieve obstruction</li>
      <li>Maxillomandibular advancement (MMA)</li>
    </ul>
  </li>
  <li>Bariatric surgery for some patients with a BMI over 40</li>
  <li>In children, <a href="adenoids.html">adenoidectomy</a> and <a href="tonsil.html">tonsil surgery</a></li>
</ul>
{SLEEP_CHAT}
{SLEEP_AI}

<p>Read more about <a href="snoring.html">snoring in children and adults</a>.</p>
{BOOK}
""",
)

# ---------------------------------------------------------------- Adenoids
page(
    "adenoids.html",
    "Adenoid Surgery (Coblation Adenoidectomy) in Thrissur | Dr Rejith ENT",
    "Adenoid enlargement in children: signs, tests, when medicines are enough, and endoscopic coblation adenoidectomy using a graded protocol, in Thrissur.",
    f"""
<img class="hero" src="adenoid.jpg" alt="Diagram of normal adenoids and enlarged adenoids blocking the airway">
<h1>Adenoids and Adenoid Surgery</h1>
{video("s2h-rO01osY", "Is snoring and mouth breathing in children normal?")}

<h2>What are adenoids?</h2>
<p>Adenoids are a small mass of immune tissue behind the nose. All children have them. They grow from about 1 year of age, reach their largest size around 7 years, and usually shrink away by about 11 years. So adenoids are normal.</p>

<h2>Do adenoids need treatment?</h2>
<p>Normal adenoids don't need treatment. We treat them only when they cause disease.</p>

<h2>Common adenoid problems</h2>
<ul>
  <li><strong>Adenoid hypertrophy:</strong> enlargement that blocks breathing through the nose</li>
  <li><strong>Adenoiditis:</strong> chronic infection or inflammation of the adenoids</li>
</ul>
<p>These cause different problems. Enlarged adenoids mainly cause snoring, mouth breathing and sleep apnoea. Chronic adenoid infection, even when the adenoid is not very large, is what usually causes fluid behind the eardrum and repeated ear infections.</p>

<h2>Signs to look for</h2>
<ul>
  <li>Snoring and mouth breathing, the most common signs</li>
  <li>Poor weight gain or slow growth in height, which can be caused by sleep apnoea</li>
  <li>Poor attention, hyperactivity or tiredness, also linked with sleep apnoea</li>
  <li>Hearing difficulty from fluid behind the eardrum, often noticed as poor school performance or a child who is less social</li>
  <li>Repeated ear infections or a constantly runny nose</li>
  <li>Teeth growing out of position</li>
</ul>

<div class="box"><strong>Check your child:</strong> take the free <a href="child-sleep-score.html">MERA Child Sleep Apnoea Score</a>.</div>

<h2>How are enlarged adenoids diagnosed?</h2>
<p>With an X-ray of the back of the nose, or a nasal endoscopy in older children.</p>

<h2>How are they treated?</h2>
<p>The aim is to stop mouth breathing and improve ear function. We first try medical treatment. If it doesn't work, adenoidectomy may be needed.</p>

<h2>Won't adenoids disappear by 11 years? Why not wait?</h2>
<ul>
  <li>Normal adenoids shrink by about 11 years. Diseased adenoids may not.</li>
  <li>Sleep apnoea can slow a child's growth in both weight and height during the years of waiting.</li>
  <li>Children naturally breathe through the nose. Normal development of the face, jaw, teeth and sinuses needs nasal breathing.</li>
  <li>Fluid behind the eardrum from chronic adenoid infection reduces hearing, which can affect school performance and how a child mixes with others.</li>
  <li>The longer these problems continue, the greater their effect.</li>
</ul>

<h2>How is adenoidectomy done?</h2>
<p>The adenoid is removed through the mouth under direct endoscopic view, so the surgeon can see exactly how much tissue is removed and what is kept. It is usually done as <a href="daycare.html">day-care surgery</a>, and most children have little pain afterwards.</p>
<p><strong>"Coblation adenoidectomy"</strong> simply means the adenoid is removed with a coblation device, which uses low-temperature plasma energy. A microdebrider (a fine shaver) can also be used, and sometimes both are used together.</p>

<h2>Different degrees of adenoidectomy</h2>
<p>Adenoid surgery is not the same for every child. We follow a defined, graded protocol, and the amount of tissue removed is planned according to the child's age, the type of disease and the symptoms:</p>
<ul>
  <li><strong>Partial adenoidectomy:</strong> only the bulk that blocks the airway is reduced. Used in very young children, to keep the adenoid's role in immunity.</li>
  <li><strong>Subtotal adenoidectomy:</strong> most of the adenoid is removed, keeping a thin layer of tissue.</li>
  <li><strong>Near-total adenoidectomy:</strong> almost all the tissue is removed, down to the underlying layer.</li>
  <li><strong>Total adenoidectomy:</strong> all the adenoid tissue is removed down to the fascia. Used mainly for chronic adenoid infection and fluid in the ear.</li>
</ul>
<p>In children with a repaired or at-risk palate, tissue in a specific area is deliberately kept to protect speech and swallowing.</p>

<h2>Will the adenoids grow back?</h2>
<p>After total or near-total adenoidectomy, regrowth is very unlikely and rarely causes blockage again. After partial or subtotal adenoidectomy, where some tissue is kept on purpose, some regrowth can happen. We'll explain which approach suits your child and why.</p>

<h2>Why is tonsil surgery sometimes done with adenoidectomy?</h2>
<ul>
  <li>Enlarged tonsils can keep blocking the airway after the adenoids are removed.</li>
  <li>Tonsils large enough to block the airway can be partly removed with <strong>intracapsular tonsillectomy</strong>, which keeps the tonsil's capsule and usually means less pain, less bleeding risk and faster recovery.</li>
  <li>Tonsils with repeated infections may need complete (extracapsular) removal.</li>
</ul>
<p>Read more about <a href="tonsil.html">tonsil surgery</a> and <a href="snoring.html">snoring in children</a>.</p>
{CHILD_CHAT}
{BOOK}
""",
)

# ---------------------------------------------------------------- Tonsils
page(
    "tonsil.html",
    "Tonsil Surgery (Intracapsular Tonsillectomy) in Thrissur | Dr Rejith ENT",
    "Tonsil problems and types of tonsillectomy, including coblation intracapsular tonsil surgery, recovery time and risks, from Dr Rejith R S, ENT surgeon, Thrissur.",
    f"""
<img class="hero" src="tonsil.jpg" alt="Tonsils">
<h1>Tonsils and Tonsil Surgery</h1>
{video("pjgPvwq3RKE", "Tonsillectomy: explaining extracapsular and intracapsular tonsillectomy")}

<h2>Tonsil problems</h2>
<ul>
  <li>Enlarged tonsils (tonsillar hypertrophy)</li>
  <li>Tonsillitis: acute, chronic and recurrent</li>
  <li>Tonsil stones</li>
  <li>Peritonsillar abscess (quinsy)</li>
</ul>

<h2>Types of tonsil surgery</h2>
<ul>
  <li><strong>Extracapsular (total) tonsillectomy:</strong> the whole tonsil and its capsule are removed, by dissection, electrocautery, coblation, LigaSure or harmonic scalpel</li>
  <li><strong>Intracapsular tonsillectomy:</strong> most of the tonsil is removed with coblation or a microdebrider, while the capsule is preserved</li>
  <li><strong>Tonsillotomy:</strong> partial reduction of the tonsil</li>
</ul>

<h2>Which tonsil surgery is best?</h2>
<p>It depends on the patient's age and the disease:</p>
<ul>
  <li>For recurrent tonsillitis, extracapsular tonsillectomy is usually better.</li>
  <li>For <a href="snoring.html">snoring</a> and <a href="sleepapnoea.html">sleep apnoea</a>, intracapsular surgery is usually preferred.</li>
  <li>With <a href="adenoids.html">adenoidectomy</a>, tonsils may be reduced to prevent them blocking the airway later.</li>
</ul>

<h2>Recovery and risks</h2>
<div class="table-scroll">
<table>
  <tr><th></th><th>Extracapsular</th><th>Intracapsular</th></tr>
  <tr><td>Healing</td><td>The raw muscle and vessels heal over 2–3 weeks</td><td>The capsule protects the muscle underneath</td></tr>
  <tr><td>Pain</td><td>More pain</td><td>Least pain</td></tr>
  <tr><td>Bleeding</td><td>Can occur in the first 24 hours, or between days 7 and 10 due to infection of the healing area, sometimes needing admission</td><td>Low risk of significant bleeding</td></tr>
  <tr><td>Hospital stay</td><td>Usually overnight</td><td>Usually <a href="daycare.html">day care</a></td></tr>
  <tr><td>Back to normal activities</td><td>About 2 weeks</td><td>3–5 days</td></tr>
  <tr><td>Later</td><td>No tonsil tissue remains</td><td>Remaining tonsil tissue can occasionally regrow or get infected</td></tr>
</table>
</div>
{BOOK}
""",
)

# ---------------------------------------------------------------- Vertigo
page(
    "vertigo.html",
    "Vertigo and Balance Clinic in Thrissur | BPPV Treatment | Dr Rejith ENT",
    "Vertigo, dizziness and imbalance: causes, BPPV and repositioning manoeuvres, vestibular rehabilitation and when to seek emergency care, in Thrissur.",
    f"""
<img class="hero" src="vertigoclinic.jpg" alt="Vertigo and balance clinic">
<h1>Vertigo and Balance Clinic in Thrissur</h1>

{video("E-4NMVUT89k", "Which specialist to consult for thalakarakam (vertigo, dizziness, fainting)?")}

<h2>Is vertigo a disease?</h2>
<p>No. Vertigo is a feeling caused by an underlying disease. We treat the disease, not just the feeling.</p>

<h2>Are vertigo, dizziness and imbalance the same?</h2>
<ul>
  <li><strong>Vertigo</strong> is a spinning sensation, of yourself or your surroundings.</li>
  <li><strong>Dizziness or giddiness</strong> is a light-headed or floating feeling.</li>
  <li><strong>Imbalance</strong> is difficulty sitting, standing or walking steadily.</li>
  <li>Changes in vision or blacking out are different complaints again.</li>
</ul>

<h2>What could be causing your vertigo?</h2>
<ul>
  <li>Vertigo with sudden head movements or turning in bed is likely to be <strong>benign paroxysmal positional vertigo (BPPV)</strong>.</li>
  <li>Vertigo with hearing loss or ringing in one ear suggests an inner ear disease, such as Ménière's disease or labyrinthitis.</li>
</ul>
<div class="urgent">
  <strong>Go to the emergency department</strong> if vertigo is severe even when lying completely still, or comes with weakness, numbness, slurred speech, double vision or difficulty walking. These can be signs of a stroke.
</div>

{video("6WHuKi_fpwQ", "How to manage sudden-onset vertigo")}

<h2>What is the "ear balance" problem people talk about?</h2>
<p>This usually means BPPV, the most common cause of vertigo.</p>

<h2>How is BPPV treated?</h2>
<p>BPPV is caused by tiny crystals moving inside the balance canals of the inner ear. There are three canals in each ear, six in total.</p>
<ul>
  <li>To find the affected canal, the doctor moves your head in specific positions, for example from sitting to lying, or turning sideways. The Dix–Hallpike test is one such test.</li>
  <li>Once the canal is identified, the doctor moves your head in a sequence that guides the crystals out of the canal.</li>
  <li>When the crystals settle in a safe place, the spinning stops.</li>
</ul>
<p>This is called a canalith repositioning manoeuvre. Examples include the Epley, Semont, barbecue roll and deep head-hanging manoeuvres.</p>

<h2>How is imbalance treated?</h2>
<ul>
  <li>Treating the underlying cause</li>
  <li>Vestibular rehabilitation exercises, done in stages</li>
</ul>

<h2>Is surgery needed?</h2>
<p>Rarely. Injections into the ear help in selected cases, and surgery is reserved for vertigo that does not respond to other treatment.</p>

<h2>Do I need a scan?</h2>
<ul>
  <li>Most ear-related vertigo is diagnosed clinically with hearing tests, without a CT or MRI.</li>
  <li>MRI is preferred if a neurological cause is suspected.</li>
  <li>Videonystagmography (VNG) is useful in selected cases.</li>
</ul>
{BOOK}
""",
)

# ---------------------------------------------------------------- Ear
page(
    "earsurgery.html",
    "Endoscopic Ear Surgery in Thrissur | Ear Discharge and Hearing Loss | Dr Rejith ENT",
    "Ear discharge, hearing loss and endoscopic ear surgery through the ear canal: tympanoplasty, myringotomy, ossiculoplasty and limited cholesteatoma, in Thrissur.",
    f"""
<h1>Ear Problems and Endoscopic Ear Surgery</h1>

<h2>What ear discharge can tell us</h2>
<ul>
  <li><strong>Watery:</strong> usually from the skin of the ear canal, and not serious</li>
  <li><strong>Pus:</strong> infection of the outer or middle ear</li>
  <li><strong>Sticky (mucoid):</strong> usually means a hole in the eardrum</li>
</ul>

<h2>Hearing loss</h2>
<ul>
  <li>Gradual hearing loss is common with age, as the hearing nerve weakens.</li>
  <li>Blockage of the ear canal, such as wax, can reduce hearing.</li>
  <li>A hole in the eardrum causes hearing loss.</li>
</ul>
<div class="urgent">
  <strong>Sudden hearing loss is an emergency.</strong> Sudden sensorineural hearing loss can often be treated if treatment starts early, but may become permanent if delayed. See an ENT doctor the same day.
</div>

<h2>Vertigo</h2>
<p>Vertigo can come from the inner ear. <a href="vertigo.html">Read more about vertigo</a>.</p>

<h2>When is ear surgery needed?</h2>
<p>Most ear problems are treated with medicines first. Surgery is needed when a hole in the eardrum doesn't heal, the ear bones don't move properly, or there is disease eroding bone.</p>

<h2>How is ear surgery done?</h2>
<p>Using either a microscope or an endoscope, with very fine instruments. Most ear operations are done as <a href="daycare.html">day-care surgery</a>.</p>

<h2>Microscopic or endoscopic ear surgery?</h2>
<p>Both give similar success rates. Microscopic surgery usually needs a cut behind or in front of the ear for access. Endoscopic surgery is done through the ear canal, and any small cut needed for the graft is placed in a hidden area.</p>

<h2>What can be done endoscopically?</h2>
<ul>
  <li>Closing a hole in the eardrum (tympanoplasty), including <a href="#interlay">endoscopic interlay tympanoplasty</a></li>
  <li>Draining fluid from the middle ear (myringotomy)</li>
  <li>Repairing the ear bones (ossiculoplasty)</li>
  <li>Removing limited bone-eroding disease (cholesteatoma)</li>
</ul>

<h2 id="interlay">Endoscopic interlay tympanoplasty</h2>
<p>The eardrum has three thin layers. In the usual method (underlay), the graft that closes the hole is placed underneath the whole eardrum. In the <strong>interlay</strong> method, the graft is slipped between the outer skin layer and the middle layer of the eardrum, where it sits very securely.</p>
<ul>
  <li>Done through the ear canal with an endoscope, so no cut is needed behind the ear for access.</li>
  <li>The graft is usually your own tissue (temporalis fascia), taken through a small cut hidden in the hairline. In selected small holes, PRF (a healing membrane made from your own blood) may be used.</li>
  <li>The method is chosen during surgery: interlay is used when the ear bones are working well. If they aren't, we use the underlay method and repair the ear bones at the same time.</li>
  <li>Usually done as <a href="daycare.html">day-care surgery</a>.</li>
</ul>
<p>Published studies of endoscopic interlay tympanoplasty report high rates of successful closure and good hearing results. It is technically demanding, so it is offered at relatively few centres.</p>
<p>A blocked or poorly working Eustachian tube can make holes in the eardrum come back. In selected patients, <a href="balloon-et.html">balloon Eustachian tube dilation</a> may be advised as well.</p>

<h2>How long is the rest after ear surgery?</h2>
<p>Usually 4–6 weeks of avoiding strain and keeping water out of the ear. After myringotomy alone, no rest is needed.</p>
{BOOK}
""",
)

# ---------------------------------------------------------------- Day care
page(
    "daycare.html",
    "Day-Care ENT Surgery in Thrissur | Same-Day Discharge | Dr Rejith ENT",
    "Day-care (ambulatory) ENT surgery in Thrissur: which operations can be done with same-day discharge, its benefits, and who should stay in hospital.",
    f"""
<img class="hero" src="ot.jpg" alt="Operation theatre">
<h1>Day-Care ENT Surgery in Thrissur</h1>

<h2>What is day-care surgery?</h2>
<p>Day-care (ambulatory) surgery means you go home a few hours after your operation, on the same day. It can be done under local, regional or general anaesthesia.</p>

<h2>Why choose day-care surgery?</h2>
<ul>
  <li>Newer techniques allow most ENT operations to be done as day care.</li>
  <li>It reduces the cost of treatment.</li>
  <li>Insurance companies accept day-care surgery.</li>
  <li>You recover in the comfort of your own home.</li>
</ul>

<h2>Which ENT operations can be done as day care?</h2>
<ul>
  <li><a href="adenoids.html">Coblation adenoid surgery</a></li>
  <li><a href="tonsil.html">Coblation intracapsular tonsil surgery</a></li>
  <li><a href="septum.html">Nasal septum surgery</a> and <a href="polyp.html">endoscopic sinus and polyp surgery</a></li>
  <li><a href="earsurgery.html">Endoscopic ear surgery to close a hole in the eardrum</a></li>
  <li><a href="balloon-sinus.html">Balloon sinus surgery</a> and <a href="balloon-et.html">balloon Eustachian tube dilation</a></li>
  <li>Coblation snoring surgery</li>
  <li><a href="voice.html">Surgery for vocal nodules or polyps</a></li>
  <li>Procedures under local anaesthesia</li>
</ul>

<h2>Who may need to stay in hospital?</h2>
<ul>
  <li>People with uncontrolled high blood pressure, diabetes, or heart or lung disease</li>
  <li>Children under 3 years and adults over 65</li>
  <li>People living more than an hour by road from the hospital</li>
</ul>
<p>Your surgeon and anaesthetist will advise what is safest for you.</p>
{BOOK}
""",
)

# ---------------------------------------------------------------- Septum
page(
    "septum.html",
    "Nasal Septum Surgery (Septoplasty) in Thrissur | Dr Rejith ENT",
    "Deviated nasal septum: symptoms, diagnosis, septoplasty as day-care surgery, minimum age and recovery, from Dr Rejith R S, ENT surgeon, Thrissur.",
    f"""
<img class="hero" src="endoscopy.jpg" alt="Nasal endoscopy examination">
<h1>Nasal Septum Surgery</h1>

<h2>When is septal surgery needed?</h2>
<p>When a deviated nasal septum causes persistent nasal blockage, headache, repeated sinusitis, nosebleeds or <a href="sleepapnoea.html">sleep apnoea</a>.</p>

<h2>How is a deviated septum diagnosed?</h2>
<p>A clinical examination is usually enough, with nasal endoscopy for more detail. A CT scan of the sinuses is taken if there is sinusitis.</p>

<h2>How is it treated?</h2>
<p>Only when it causes significant symptoms. Treatment is surgical: septoplasty or submucous resection.</p>

<h2>Is there a minimum age?</h2>
<p>Submucous resection is done only after about 17 years of age. Septoplasty has no strict age limit.</p>

<h2>Recovery</h2>
<p>Septoplasty can be done as <a href="daycare.html">day-care surgery</a>, usually without nasal packing. Avoid heavy physical strain for 2 weeks.</p>
{BOOK}
""",
)

# ---------------------------------------------------------------- Polyp
page(
    "polyp.html",
    "Nasal Polyps Treatment in Thrissur | Endoscopic Sinus Surgery | Dr Rejith ENT",
    "Nasal polyps: symptoms, types, medical treatment and endoscopic polypectomy as day-care surgery, in Thrissur.",
    f"""
<h1>Nasal Polyps</h1>

<h2>When to suspect nasal polyps</h2>
<p>Nasal blockage that keeps getting worse, often with loss of smell.</p>

<h2>Types of nasal polyps</h2>
<ul>
  <li><strong>Ethmoidal polyps:</strong> multiple polyps on both sides of the nose</li>
  <li><strong>Antrochoanal (AC) polyp:</strong> usually a single polyp</li>
</ul>

<h2>Treatment</h2>
<p>Ethmoidal polyps are treated with medicines first, and many respond well. Polyps that don't respond, and AC polyps, need surgery.</p>

<p>For sinusitis without polyps, <a href="balloon-sinus.html">balloon sinus surgery</a> may be an option.</p>

<h2>How is polypectomy done?</h2>
<p>Under endoscopic view, using a microdebrider. It can be done as <a href="daycare.html">day-care surgery</a>.</p>
{BOOK}
""",
)

# ---------------------------------------------------------------- Voice
page(
    "voice.html",
    "Voice Clinic in Thrissur | Hoarseness and Voice Change | Dr Rejith ENT",
    "Voice change and hoarseness: what to do, when to see an ENT doctor, warning signs, and treatment of vocal nodules, polyps and cysts, in Thrissur.",
    f"""
<img class="hero" src="voice.jpg" alt="Voice">
<h1>Voice Change and Hoarseness</h1>
<p class="lead">Voice is produced by the vocal cords, then shaped by the throat, mouth and tongue.</p>

<h2>What to do when your voice changes</h2>
<ul>
  <li>If it has lasted only a day, rest your voice and drink water.</li>
  <li>If it doesn't improve in 1–2 days, see a doctor, preferably an ENT specialist.</li>
  <li>If it doesn't improve after a course of medicines, an ENT doctor should examine your vocal cords with an endoscope, through the mouth or through the nose.</li>
</ul>
<div class="urgent">
  <strong>See an ENT doctor without delay</strong> if hoarseness lasts more than 3 weeks, especially if you smoke, or if it comes with difficulty swallowing, difficulty breathing, coughing blood or a lump in the neck.
</div>

<h2>Over-the-counter medicines can do more harm</h2>
<p>Cold medicines are often taken for voice change, but they can delay recovery. Steroids give quick relief but can damage the vocal cords if used without examination.</p>

<h2>Is voice change linked to cancer?</h2>
<p>Voice change that keeps getting worse can be a sign of throat cancer. Sudden hoarseness from vocal cord paralysis can be caused by disease of the <a href="thyroid.html">thyroid</a>, food pipe, lung or lymph nodes.</p>

<h2>Common causes of long-standing voice change</h2>
<ul>
  <li><strong>Vocal nodules</strong> ("singer's" or "teacher's" nodules) from voice overuse: treated with voice therapy</li>
  <li><strong>Vocal cord polyp:</strong> non-cancerous, needs surgery</li>
  <li><strong>Laryngeal papilloma:</strong> caused by a virus, needs removal</li>
  <li><strong>Vocal cord cyst:</strong> can be removed</li>
  <li><strong>Sulcus vocalis:</strong> can be improved with surgery</li>
  <li><strong>Muscle tension dysphonia:</strong> treated with voice therapy</li>
</ul>
{BOOK}
""",
)

# ---------------------------------------------------------------- Thyroid
page(
    "thyroid.html",
    "Thyroid Surgery in Thrissur | Thyroid Nodules and Thyroidectomy | Dr Rejith ENT",
    "Thyroid disease: symptoms, tests, when surgery is needed, types of thyroidectomy including endoscopic options, and advice on thyroid medicines, in Thrissur.",
    f"""
<img class="hero" src="thyroid.jpg" alt="Thyroid gland">
<h1>Thyroid Disease and Thyroid Surgery</h1>

<h2>Types of thyroid disease</h2>
<ul>
  <li>Hormone problems: an underactive (hypothyroid) or overactive (hyperthyroid) gland</li>
  <li>Thyroid nodules: non-cancerous or cancerous</li>
  <li>Infection or inflammation (thyroiditis)</li>
</ul>

<h2>Tests</h2>
<ul>
  <li><strong>Hormone problems:</strong> a thyroid function blood test is usually enough.</li>
  <li><strong>Nodules:</strong> ultrasound scan and FNAC (a needle sample).</li>
  <li><strong>Thyroiditis:</strong> both blood tests and a scan.</li>
</ul>

<h2>Warning signs</h2>
<h3>Underactive thyroid (hypothyroidism)</h3>
<p>Tiredness, slow heart rate, weight gain, irregular periods, feeling cold, dry skin and a puffy face.</p>
<h3>Overactive thyroid (hyperthyroidism)</h3>
<p>Anxiety, fine tremor, weight loss, bulging eyes, palpitations and an irregular heartbeat.</p>
<h3>Thyroid nodule</h3>
<p>A lump felt in the neck, or found by chance on a scan. <strong>A change in voice with a thyroid nodule is a warning sign</strong> and needs prompt assessment.</p>
<h3>Thyroiditis</h3>
<p>Features of an underactive or overactive thyroid, sometimes with pain in the neck.</p>

<h2>Does all thyroid disease need surgery?</h2>
<p>No. Thyroidectomy is done when cancer is suspected, when the gland is large enough to press on the windpipe or food pipe, or in some cases of overactive thyroid.</p>

<h2>Types of thyroid surgery</h2>
<ul>
  <li><strong>Total thyroidectomy:</strong> the whole gland is removed, usually when cancer is suspected</li>
  <li><strong>Subtotal thyroidectomy:</strong> for an overactive thyroid, to reduce hormone production</li>
  <li><strong>Hemithyroidectomy:</strong> half the gland is removed, for a suspicious nodule in one lobe. This can often be done as <a href="daycare.html">day-care surgery</a>.</li>
</ul>

<h2>Is keyhole thyroid surgery possible?</h2>
<p>Endoscopic thyroidectomy can be done through the armpit or through the mouth, leaving no visible scar on the neck. It is suitable for selected patients; very large glands and confirmed cancers are usually better treated with open surgery.</p>

<h2>Advice for people on thyroid tablets</h2>
<ul>
  <li>Take your tablet every day.</li>
  <li>Take it on an empty stomach, at least 30 minutes before tea, coffee or food.</li>
  <li>If you miss a dose, ask your doctor whether to take two doses the next day.</li>
  <li>After any change in dose, or if you stop the tablets, check your TSH after 6 weeks and review with your doctor.</li>
  <li>Women who are pregnant or planning pregnancy should discuss their target TSH with their doctor.</li>
</ul>
{BOOK}
""",
)

# ---------------------------------------------------------------- Migraine
page(
    "migraine.html",
    "Headache and Migraine Clinic in Thrissur | Dr Rejith ENT",
    "Migraine triggers, symptoms and treatment, including preventive medicines and Botox, and how ENT problems can cause headache, in Thrissur.",
    f"""
<h1>Headache and Migraine</h1>
<p class="lead">Migraine is a neurological condition. It is set off by certain triggers and often runs in families.</p>

<h2>Common triggers</h2>
<p>Work stress, exams, pain elsewhere in the body, hunger, bright or poor-quality light, neck and shoulder pain, irregular sleep, and certain foods and smells.</p>

<h2>Symptoms</h2>
<ul>
  <li>Headache on one side, which can spread or switch sides</li>
  <li>Severe headache that worsens with light or sound</li>
  <li>Nausea and vomiting</li>
  <li>Seeing black spots or flashes of light</li>
</ul>
<div class="urgent">
  <strong>Seek urgent care</strong> for a sudden, severe "worst ever" headache, or headache with fever and neck stiffness, weakness, confusion or loss of vision.
</div>

<h2>Treatment</h2>
<ul>
  <li><strong>Fewer than 2 attacks a month:</strong> medicines taken at the time of the attack</li>
  <li><strong>More than 2 attacks a month:</strong> daily medicines to prevent attacks</li>
  <li><strong>15 or more headache days a month despite medicines:</strong> Botox injections may be considered</li>
  <li>Lifestyle changes to avoid triggers</li>
</ul>
<p>Some headaches come from the nose and sinuses, such as sinusitis or a <a href="septum.html">deviated septum</a>, and an ENT examination helps tell these apart.</p>
{BOOK}
""",
)

# ---------------------------------------------------------------- Sialendoscopy
page(
    "sial.html",
    "Sialendoscopy in Thrissur | Salivary Gland Stones and Swelling | Dr Rejith ENT",
    "Sialendoscopy for salivary gland stones, duct narrowing and recurrent swelling: a minimally invasive, gland-preserving treatment, in Thrissur.",
    f"""
<h1>Sialendoscopy for Salivary Gland Problems</h1>
<p class="lead">Sialendoscopy uses a very thin endoscope passed through the natural opening of the salivary duct inside the mouth, to diagnose and treat salivary gland problems without removing the gland.</p>

<h2>Symptoms of salivary gland problems</h2>
<p>Pain and swelling under the jaw or in front of the ear, often while eating; a dry mouth; or repeated infections of the gland.</p>

<h2>Conditions treated</h2>
<h3>Salivary stones (sialolithiasis)</h3>
<p>Hard deposits form in the gland or duct and block the flow of saliva, causing pain and swelling at mealtimes.</p>
<ul>
  <li><strong>Tests:</strong> ultrasound scan, and sometimes a CT scan</li>
  <li><strong>Treatment:</strong> small stones can be removed through the endoscope with a tiny basket; larger stones may need a small cut inside the mouth or stone fragmentation</li>
</ul>

<h3>Duct narrowing (stricture)</h3>
<p>Narrowing of the duct slows saliva flow and leads to repeated swelling and infection.</p>
<ul>
  <li><strong>Tests:</strong> ultrasound, and sialendoscopy to see the narrowing directly</li>
  <li><strong>Treatment:</strong> widening the duct through the endoscope, with steroid rinses</li>
</ul>

<h3>Chronic inflammation and recurrent infection</h3>
<p>Repeated swelling from inflammation, infections or autoimmune disease.</p>
<ul>
  <li><strong>Tests:</strong> ultrasound and blood tests where an autoimmune cause is suspected</li>
  <li><strong>Treatment:</strong> washing out the duct and steroid irrigation through the endoscope, with medical treatment of the cause</li>
</ul>

<h2>Benefits</h2>
<p>Sialendoscopy aims to preserve the gland, avoids a cut on the face or neck in most cases, and usually allows going home the same day.</p>
{BOOK}
""",
)

# ---------------------------------------------------------------- Skull base
page(
    "skullbase.html",
    "Endoscopic Skull Base Surgery in Thrissur | Dr Rejith ENT",
    "Endoscopic skull base surgery for pituitary adenoma and CSF leak, facial nerve decompression after injury, and labyrinthectomy for severe vertigo, in Thrissur.",
    f"""
<h1>Skull Base Surgery</h1>
<p class="lead">The skull base is the complex region at the base of the skull. Many conditions here can now be treated through the nose with an endoscope, without cuts on the face or head. Care is provided with a team that includes a skull base surgeon.</p>

<h2>Pituitary adenoma</h2>
<p>A non-cancerous tumour of the pituitary gland, which can affect hormone production or press on nearby nerves. Symptoms include headache, vision problems, and hormone effects such as milk discharge, irregular periods or acromegaly.</p>
<ul>
  <li><strong>Tests:</strong> MRI and CT scans to assess size, position and the surgical approach; hormone blood tests such as prolactin and growth hormone; and an eye examination for visual field defects</li>
  <li><strong>Treatment:</strong> endoscopic transsphenoidal surgery through the nose; medicines for some hormone-producing tumours; radiotherapy for tumours that cannot be fully removed</li>
</ul>

<h2>CSF leak from the nose (CSF rhinorrhoea)</h2>
<p>Cerebrospinal fluid (CSF) surrounds the brain. When it leaks through a defect in the skull base into the nose, it causes a clear, watery nasal discharge. Leaks can come from one site or several.</p>
<ul>
  <li><strong>Tests:</strong> CT scan and MR cisternography to locate the leak; beta-2 transferrin test to confirm the fluid is CSF; intrathecal fluorescein dye during surgery in selected cases</li>
  <li><strong>Treatment:</strong> bed rest, stool softeners and medicines at first; endoscopic repair if the leak continues; a lumbar drain for a short period when CSF pressure is high</li>
</ul>

<h2>Facial nerve weakness after injury</h2>
<p>A fracture of the temporal bone can press on the facial nerve and cause partial or complete facial paralysis. Decompression surgery relieves the pressure to help the nerve recover.</p>
<ul>
  <li><strong>Tests:</strong> HRCT of the temporal bone to look for bone pressing on the nerve; nerve studies (EMG) to judge the extent of injury and timing of surgery</li>
  <li><strong>Treatment:</strong> steroids and physiotherapy; surgery when bone is pressing on the nerve, the nerve is cut, or there is no recovery with medical treatment</li>
</ul>

<h2>Labyrinthectomy for severe vertigo</h2>
<p>For severe, disabling vertigo that has not responded to any other treatment, the balance organ of the inner ear can be deactivated, either with gentamicin injections into the ear or by surgery. Both can cause permanent hearing loss in that ear, so this is considered only after careful discussion. <a href="vertigo.html">Read more about vertigo</a>.</p>
{BOOK}
""",
)

# ---------------------------------------------------------------- MERA Sleep Apnoea Score
def q(name, legend, options, hint=""):
    """options: list of (label, value); value 'na' means not counted."""
    opts = "".join(
        f'<label class="opt"><input type="radio" name="{name}" value="{v}" required> <span>{lab}</span></label>'
        for lab, v in options
    )
    hint_html = f'<p class="q-hint">{hint}</p>' if hint else ""
    return f'<fieldset class="q" data-q="{name}"><legend>{legend}</legend>{hint_html}<div class="opts">{opts}</div></fieldset>'


SCORE_FORM = "\n".join([
    '<h2>Snoring and breathing</h2>',
    q("snore", "How loud is the snoring?", [
        ("Can be heard from another room", 10), ("Can be heard in the bedroom", 5),
        ("No snoring", 0), ("I sleep alone, or I don't know", "na")]),
    q("pause", "Have you or anyone else noticed pauses in your breathing?", [
        ("I wake up choking or gasping", 10), ("My partner or room-mate has seen me stop breathing", 8),
        ("The snoring gets louder and softer without me changing position", 6),
        ("None of these", 0), ("I sleep alone, or I don't know", "na")]),
    '<h2>Sleepiness during the day</h2>',
    q("drive", "Sleepiness while driving in the daytime", [
        ("I have fallen asleep while the vehicle was moving", 15), ("I have felt sleepy while driving", 10),
        ("I have fallen asleep while stopped at a traffic signal", 7), ("I have fallen asleep while briefly stopped", 3),
        ("Never sleepy while driving", 0), ("I don't drive", "na")]),
    q("talk", "While talking with someone during the day", [
        ("I have dozed off", 3), ("I usually feel sleepy", 1), ("Never sleepy", 0)]),
    q("meet", "In a meeting or discussion during the day", [
        ("I have dozed off", 2), ("I usually feel sleepy", 1), ("Never sleepy", 0)]),
    q("zoom", "On a video call (Zoom, Meet) during the day", [
        ("I have dozed off", 2), ("I usually feel sleepy", 1), ("Never sleepy", 0), ("I don't use video calls", "na")]),
    q("phone", "Watching your phone while sitting", [
        ("I have dozed off while scrolling reels or shorts", 2), ("I have dozed off while watching long videos", 1),
        ("Never dozed off", 0), ("I don't watch videos or social media on my phone", "na")]),
    q("audience", "Sitting in an audience during the day (church, temple, programme, TV, movie, presentation)", [
        ("I have dozed off", 1), ("I usually feel sleepy", 0.5), ("Never sleepy", 0)]),
    q("idle", "Sitting idle during the day", [
        ("I have dozed off", 1), ("I usually feel sleepy", 0.5), ("Never sleepy", 0)]),
    '<h2>Mornings</h2>',
    q("wake", "When you wake up in the morning", [
        ("I feel I haven't slept enough and want to go back to sleep", 4), ("I feel tired but not sleepy", 1),
        ("I feel fresh and energetic", 0)]),
    q("headache", "Do you wake up with a headache?", [
        ("Most mornings", 2), ("Sometimes", 1), ("No", 0)]),
    '<h2>Health</h2>',
    q("dm", "Diabetes", [
        ("Not controlled, on more than 2 medicines", 3), ("Not controlled, on 1 medicine", 2),
        ("Controlled", 1), ("I don't have diabetes", 0)]),
    q("bp", "High blood pressure", [
        ("Not controlled, on more than 2 medicines", 5), ("Not controlled, on 1 medicine", 2),
        ("Controlled", 1), ("I don't have high blood pressure", 0)]),
    q("libido", "Interest in sex (optional)", [
        ("Not interested", 3), ("Reduced", 2), ("Normal", 0), ("Prefer not to say", "na")]),
    """<fieldset class="q" data-q="weight"><legend>Weight</legend>
<p class="q-hint">Enter your height and weight, or choose a description if you don't know them.</p>
<div class="bmi-row">
  <label>Height (cm) <input type="number" id="h-cm" inputmode="decimal" min="100" max="230"></label>
  <label>Weight (kg) <input type="number" id="w-kg" inputmode="decimal" min="25" max="300"></label>
</div>
<p class="bmi-out" id="bmi-out" aria-live="polite"></p>
<div class="opts">
  <label class="opt"><input type="radio" name="weight" value="10"> <span>I'm clearly overweight</span></label>
  <label class="opt"><input type="radio" name="weight" value="5"> <span>I'm a little overweight</span></label>
  <label class="opt"><input type="radio" name="weight" value="0"> <span>My weight is normal</span></label>
</div></fieldset>""",
])

page(
    "sleep-score.html",
    "MERA Sleep Apnoea Score: Free Self-Check | Dr Rejith ENT, Thrissur",
    "A free self-check for adults who snore: answer a few questions to see how likely obstructive sleep apnoea is. Nothing you enter is stored.",
    f"""
<h1>MERA Sleep Apnoea Score</h1>
<p class="lead">A self-check for adults who snore or feel sleepy during the day. Answer each question, and you'll see how likely obstructive sleep apnoea is.</p>
<div class="box">This is a self-check, not a diagnosis. Only a sleep study can confirm sleep apnoea. Your answers stay on your phone or computer and are not stored or sent anywhere. For children, see <a href="snoring.html#children">snoring in children</a>.</div>

<form id="mera-score" class="score-form" novalidate>
{SCORE_FORM}
<p class="score-missing" id="score-missing" hidden></p>
<p><button type="submit" class="btn">See my score</button></p>
</form>

<section class="score-result" id="score-result" hidden aria-live="polite">
  <h2>Your result</h2>
  <div class="urgent" id="drive-warning" hidden><strong>Please avoid driving until you've been assessed.</strong> Sleepiness at the wheel is a serious risk to you and others, whatever your score.</div>
  <p class="score-big"><span id="score-pct"></span>%</p>
  <p id="score-detail" class="score-detail"></p>
  <p id="score-band" class="score-band"></p>
  <p>Take a screenshot of this result and show it at your consultation.</p>
  <p class="intro-actions"><a class="btn" href="tel:{PHONE_TEL}">Call {PHONE_SHOW}</a> <a class="btn quiet" href="{WHATSAPP}">WhatsApp</a></p>
</section>

<p>Read more about <a href="sleepapnoea.html">obstructive sleep apnoea</a> and <a href="snoring.html">snoring</a>.</p>
""",
)

# ---------------------------------------------------------------- MERA Child Sleep Apnoea Score
def qa(name, legend, options, hint="", minage=None, maxage=None):
    """Like q(), but the question is hidden and not counted outside the age range."""
    html = q(name, legend, options, hint)
    attrs = ""
    if minage is not None:
        attrs += f' data-minage="{minage}"'
    if maxage is not None:
        attrs += f' data-maxage="{maxage}"'
    return html.replace('<fieldset class="q"', '<fieldset class="q"' + attrs, 1)


CHILD_FORM = "\n".join([
    """<fieldset class="q" data-q="age"><legend>Your child's age</legend>
<div class="bmi-row"><label>Age (years) <input type="number" id="c-age" inputmode="decimal" min="1" max="18" step="0.5"></label></div>
<p class="q-hint">Some questions only apply to certain ages, and they'll appear or disappear when you enter the age.</p>
</fieldset>""",
    '<h2>Sleep and breathing</h2>',
    qa("snore", "Does your child snore?", [
        ("Always", 10), ("Only in certain sleeping positions", 6), ("Only when they have a cold or infection", 3), ("No snoring", 0)]),
    qa("block", "Have you seen your child's breathing stop or get blocked during sleep?", [
        ("Yes, many times", 20), ("Yes, a few times", 10), ("Not seen", 0)]),
    qa("effort", "Have you seen your child breathe with effort (laboured breathing) during sleep?", [
        ("Yes, even with the mouth open and without a cold", 15), ("Yes, with the mouth closed, without a cold", 10),
        ("Yes, only during a cold", 5), ("Not seen", 0)]),
    qa("position", "Does your child change position during sleep?", [
        ("Frequently", 3), ("Occasionally", 2), ("No change in position", 0)]),
    qa("neck", "Does your child sleep with the head tilted back (as if looking up)?", [
        ("Always", 3), ("Only during a cold", 2), ("Occasionally", 1), ("Never noticed", 0)]),
    qa("mouthsleep", "Does your child sleep with the mouth open?", [
        ("Yes, always", 10), ("Only during a cold", 5), ("No", 0)]),
    qa("mouthawake", "Does your child breathe through the mouth while awake?", [
        ("Yes, always", 10), ("Only during a cold", 5), ("No", 0)]),
    qa("bedwet", "Does your child wet the bed during sleep?", [
        ("Yes", 5), ("No", 0)], hint="Asked only from 5 years, as bedwetting is normal in younger children.", minage=5),
    '<h2>During the day</h2>',
    qa("restless", "Is your child restless?", [
        ("Always running around, won't sit still for long (except for a favourite programme)", 5),
        ("Hard to get them to sit and listen or study", 3), ("No such problems", 0)],
        hint="Asked only for children aged 4 to 12.", minage=4, maxage=12),
    qa("yawn", "Does your child yawn repeatedly?", [
        ("Always", 5), ("Occasionally", 2), ("Never", 0)]),
    qa("classsleep", "Does your child fall asleep in class?", [
        ("Always", 10), ("Occasionally", 5), ("Never", 0), ("Not in school yet", "na")]),
    qa("games", "Does your child fall asleep while playing video games?", [
        ("Always", 15), ("Occasionally", 10), ("Never", 0), ("Doesn't play video games", "na")]),
    qa("school", "How is your child doing at school?", [
        ("Poor", 3), ("Below average", 2), ("Average or above", 0)], hint="Asked only from 5 years.", minage=5),
    '<h2>Growth</h2>',
    qa("gain", "Is your child not gaining weight?", [
        ("Not gaining, even though they eat enough", 10), ("Not gaining, and they don't eat enough", 5),
        ("Gaining weight normally", 0)]),
    """<fieldset class="q" data-q="height"><legend>Height and weight</legend>
<p class="q-hint">Enter them if you know them. They'll be shown on the result for your doctor to plot on the growth chart.</p>
<div class="bmi-row">
  <label>Height (cm) <input type="number" id="c-cm" inputmode="decimal" min="40" max="200"></label>
  <label>Weight (kg) <input type="number" id="c-kg" inputmode="decimal" min="2" max="150"></label>
</div>
<p class="q-hint"><strong>Compared with other children in the class or of the same age, your child is:</strong></p>
<div class="opts">
  <label class="opt"><input type="radio" name="height" value="10"> <span>Among the shortest</span></label>
  <label class="opt"><input type="radio" name="height" value="5"> <span>Shorter than average</span></label>
  <label class="opt"><input type="radio" name="height" value="0"> <span>Height is OK</span></label>
</div></fieldset>""",
])

page(
    "child-sleep-score.html",
    "MERA Child Sleep Apnoea Score: Free Check for Parents | Dr Rejith ENT, Thrissur",
    "A free check for parents of children who snore or breathe through the mouth: see how likely sleep apnoea is. Nothing you enter is stored.",
    f"""
<h1>MERA Child Sleep Apnoea Score</h1>
<p class="lead">A check for parents of children who snore or breathe through the mouth. Answer each question, and you'll see how likely obstructive sleep apnoea is.</p>
<div class="box">This is a check, not a diagnosis. Your answers stay on your phone or computer and are not stored or sent anywhere. For adults, use the <a href="sleep-score.html">adult MERA Sleep Apnoea Score</a>.</div>

<form id="mera-child" class="score-form" novalidate>
{CHILD_FORM}
<p class="score-missing" id="c-missing" hidden></p>
<p><button type="submit" class="btn">See the score</button></p>
</form>

<section class="score-result" id="c-result" hidden aria-live="polite">
  <h2>Your child's result</h2>
  <p class="score-big"><span id="c-pct"></span>%</p>
  <p id="c-detail" class="score-detail"></p>
  <p id="c-growth" class="score-detail"></p>
  <p id="c-band" class="score-band"></p>
  <p>Take a screenshot of this result and show it at your consultation.</p>
  <p class="intro-actions"><a class="btn" href="tel:{PHONE_TEL}">Call {PHONE_SHOW}</a> <a class="btn quiet" href="{WHATSAPP}">WhatsApp</a></p>
</section>

<p>Read more about <a href="snoring.html#children">snoring in children</a> and <a href="adenoids.html">adenoids</a>.</p>
""",
)

# ---------------------------------------------------------------- Balloon Eustachian tube
page(
    "balloon-et.html",
    "Blocked Ear Treatment and Balloon Eustachian Tube Dilation in Thrissur | Dr Rejith ENT",
    "Eustachian tube dysfunction: blocked ear, fullness, popping and fluid behind the eardrum. Medical treatment and balloon Eustachian tube dilation as day-care surgery in Thrissur.",
    f"""
<h1>Blocked Ear and Balloon Eustachian Tube Dilation</h1>
<p class="lead">The Eustachian tube connects the back of the nose to the middle ear. It opens briefly when you swallow or yawn, to balance the pressure in the ear and let it drain.</p>

<h2>Signs the tube isn't working well</h2>
<ul>
  <li>A blocked or full feeling in the ear that doesn't clear</li>
  <li>Muffled hearing</li>
  <li>Popping or crackling sounds</li>
  <li>Ear discomfort with pressure changes, such as flying or travelling to the hills</li>
  <li>Repeated fluid behind the eardrum, or an eardrum that is pulled inwards</li>
  <li>A hole in the eardrum that keeps coming back after surgery</li>
</ul>

<h2>Common causes</h2>
<p>Colds, allergy, sinusitis, acid reflux, and enlarged adenoids in children.</p>

<h2>Tests</h2>
<p>Examination of the ear and nose with an endoscope, a pressure test of the eardrum (tympanometry) and a hearing test. A CT scan is needed in some patients.</p>

<h2>Treatment starts with medicines</h2>
<ul>
  <li>Treating allergy, sinusitis or reflux</li>
  <li>Steroid nasal spray and medicines to thin mucus</li>
  <li>Exercises to open the tube gently, as we show you in the clinic</li>
</ul>
<p>We avoid routine antihistamines unless there is clear allergy, because drying the secretions can slow the tube's recovery.</p>

<h2>When is balloon dilation advised?</h2>
<p>For selected patients whose symptoms continue despite proper medical treatment, for example:</p>
<ul>
  <li>Long-standing blocked ear or repeated fluid behind the eardrum in adults</li>
  <li>An eardrum that keeps pulling inwards</li>
  <li>Repeat ear surgery, or eardrum grafts that haven't held</li>
</ul>
<p>In children, adenoid treatment comes first. Balloon dilation is considered only in selected older children, usually above 12 years.</p>

<h2>How is it done?</h2>
<ul>
  <li>Under anaesthesia, an endoscope is passed through the nose to the opening of the Eustachian tube.</li>
  <li>A small balloon is placed in the tube and gently inflated with saline for about two minutes, then removed.</li>
  <li>There are no cuts, and it is usually <a href="daycare.html">day-care surgery</a>. It can be combined with other nose or ear surgery.</li>
</ul>

<h2>Is it suitable for everyone?</h2>
<p>No. It is not used when the tube stays abnormally open (patulous Eustachian tube), and a CT scan is reviewed first when needed. We'll explain whether it suits you.</p>

<h2>After the procedure</h2>
<p>Improvement is usually gradual over a few weeks. Avoid forceful nose-blowing and flying for a short period, as advised. Side effects are usually minor, such as a small nosebleed or temporary ear discomfort; serious complications are rare.</p>
<p>Studies, including a randomised trial, have shown better results with balloon dilation plus medical treatment than with medical treatment alone in selected patients.</p>
<p>Read more about <a href="earsurgery.html">ear problems and ear surgery</a>.</p>
{BOOK}
""",
)

# ---------------------------------------------------------------- Balloon sinus
page(
    "balloon-sinus.html",
    "Balloon Sinus Surgery in Thrissur | Balloon Sinuplasty | Dr Rejith ENT",
    "Balloon sinus surgery for selected patients with chronic or repeated sinusitis: how it works, who it suits, benefits, risks and recovery, in Thrissur.",
    f"""
<h1>Balloon Sinus Surgery</h1>
<p class="lead">A minimally invasive way to open blocked sinus drainage pathways by widening them with a small balloon, without removing bone or the lining of the nose.</p>

<h2>Who is it for?</h2>
<p>Selected patients with chronic sinusitis, or sinusitis that keeps coming back, affecting the maxillary, frontal or sphenoid sinuses, when:</p>
<ul>
  <li>symptoms continue despite a proper course of medicines, and</li>
  <li>a CT scan of the sinuses confirms the blocked pathways.</li>
</ul>

<h2>Who is it not for?</h2>
<p>It is not suitable for nasal polyps, widespread sinus disease, fungal sinusitis or growths. These need <a href="polyp.html">endoscopic sinus surgery</a>. Sometimes balloon and conventional techniques are combined, or done with <a href="septum.html">septum surgery</a>.</p>

<h2>How is it done?</h2>
<ul>
  <li>An endoscope is used to see inside the nose.</li>
  <li>A thin guide places a small balloon in the opening of the blocked sinus.</li>
  <li>The balloon is inflated to widen the opening, then removed. The sinus can be washed out at the same time.</li>
</ul>

<h2>Benefits</h2>
<ul>
  <li>The natural lining of the nose is preserved</li>
  <li>Less bleeding, and usually no nasal packing</li>
  <li>Usually <a href="daycare.html">day-care surgery</a>, with a quicker return to normal activities</li>
</ul>

<h2>Risks</h2>
<p>Usually minor, such as bleeding or infection. Rare risks are the same as for any sinus surgery, including injury near the eye or the base of the skull. We'll discuss these with you before surgery.</p>

<h2>After surgery</h2>
<p>Saline nasal rinses for a few weeks, and a follow-up endoscopy to check healing.</p>
{BOOK}
""",
)

# ---------------------------------------------------------------- write
for slug, p in PAGES.items():
    (OUT / slug).write_text(render(slug, p), encoding="utf-8")

# Old URLs kept as redirects so links and search results keep working.
REDIRECTS = {
    "home.html": "index.html",
    "oldhome.html": "index.html",
    "rejiths.html": "hospitals.html",
    "daya.html": "hospitals.html",
    "karunya.html": "hospitals.html",
    "mmc.html": "hospitals.html",
    "ephphartha.html": "hospitals.html",
    "adnoids.html": "adenoids.html",
    "mother.html": "hospitals.html",
    "elixir.html": "hospitals.html",
    "apollo.html": "hospitals.html",
    "cooph.html": "hospitals.html",
}
for slug, target in REDIRECTS.items():
    (OUT / slug).write_text(redirect(target), encoding="utf-8")

(OUT / "404.html").write_text(render("404.html", dict(
    title="Page not found | Dr Rejith ENT",
    description="Page not found.",
    schema=None,
    body="<h1>Page not found</h1><p>Sorry, this page doesn't exist. Please go to the <a href=\"index.html\">home page</a> or see <a href=\"hospitals.html\">clinics and timings</a>.</p>",
)), encoding="utf-8")

urls = "\n".join(
    f"  <url><loc>{SITE}/{'' if s == 'index.html' else s}</loc></url>" for s in PAGES
)
(OUT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    f"{urls}\n</urlset>\n",
    encoding="utf-8",
)
(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
(OUT / "CNAME").write_text("entmidas.com\n")
(OUT / ".nojekyll").write_text("")
(OUT / "README.md").write_text("Website for Dr Rejith R S, ENT surgeon, Thrissur: https://entmidas.com\n")
print(len(PAGES), "pages,", len(REDIRECTS), "redirects")
