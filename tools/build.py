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

NAV = [
    ("index.html", "Home"),
    ("about.html", "About Dr Rejith"),
    ("hospitals.html", "Clinics & timings"),
    ("snoring.html", "Snoring & sleep apnoea"),
    ("adenoids.html", "Adenoids"),
    ("vertigo.html", "Vertigo"),
    ("earsurgery.html", "Ear"),
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
<link rel="stylesheet" href="css/site.css">
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
        <p><a href="tel:{PHONE_TEL}">Call {PHONE_SHOW}</a><br><a href="{WHATSAPP}">Message on WhatsApp</a></p>
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
  <li><a href="earsurgery.html">Endoscopic ear surgery</a></li>
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

<div class="video">
  <iframe src="https://www.youtube-nocookie.com/embed/1kbIIYia3Ug" title="Snoring and sleep apnoea explained" loading="lazy" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
</div>

<h2>What is snoring?</h2>
<p>Snoring is the sound made when the airway in the nose and throat partly narrows during sleep, and the soft tissues vibrate as air passes through.</p>
<p>Snoring sits on a range:</p>
<ul>
  <li><strong>Simple snoring:</strong> noise only, with no breathing pauses and no effect on health. Treatment is optional.</li>
  <li><strong>Upper airway resistance:</strong> breathing takes more effort and sleep is disturbed, even without full pauses. Worth treating before it progresses.</li>
  <li><strong>Obstructive sleep apnoea (OSA):</strong> breathing repeatedly stops or becomes very shallow for 10 seconds or more during sleep. This needs treatment. <a href="sleepapnoea.html">More about sleep apnoea</a>.</li>
</ul>

<h2 id="children">Snoring in children</h2>
<img class="hero" src="mouthbreathing.jpg" alt="Child sleeping with mouth open, a sign of mouth breathing">
<p>Children should not snore regularly. Regular snoring, especially with mouth breathing, usually means the airway is narrowed, most often by enlarged <a href="adenoids.html">adenoids</a> or <a href="tonsil.html">tonsils</a>.</p>

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

<h2>What are adenoids?</h2>
<p>Adenoids are a small mass of immune tissue behind the nose. All children have them. They grow from about 1 year of age, reach their largest size around 7 years, and usually shrink away by about 11 years. So adenoids are normal.</p>

<h2>Do adenoids need treatment?</h2>
<p>Normal adenoids don't need treatment. We treat them only when they cause disease.</p>

<h2>Common adenoid problems</h2>
<ul>
  <li><strong>Adenoid hypertrophy:</strong> enlargement that blocks breathing through the nose</li>
  <li><strong>Adenoiditis:</strong> infection or inflammation of the adenoids</li>
</ul>

<h2>Signs your child may have enlarged adenoids</h2>
<ul>
  <li>Snoring and mouth breathing, the most common signs</li>
  <li>Hearing difficulty due to fluid behind the eardrum</li>
  <li>Poor attention or hyperactivity, which can be linked with sleep apnoea</li>
  <li>Teeth growing out of position</li>
</ul>

<h2>How are enlarged adenoids diagnosed?</h2>
<p>With an X-ray of the back of the nose, or a nasal endoscopy in older children.</p>

<h2>How are they treated?</h2>
<p>The aim is to stop mouth breathing and improve ear function. We first try medical treatment. If it doesn't work, adenoidectomy may be needed.</p>

<h2>Won't adenoids disappear by 11 years? Why not wait?</h2>
<ul>
  <li>Normal adenoids shrink by 11 years. Diseased adenoids may not.</li>
  <li>Children naturally breathe through the nose. Mouth breathing is not normal.</li>
  <li>Normal development of the face, teeth, nose and sinuses needs nasal breathing.</li>
  <li>The longer a child mouth-breathes, the greater the effect on development.</li>
</ul>

<h2>How is adenoidectomy done?</h2>
<p>The adenoid is removed under direct endoscopic view, using coblation or a microdebrider. We follow a defined, graded protocol: the amount of tissue removed is planned according to the child's age and the reason for surgery. It is usually done as <a href="daycare.html">day-care surgery</a>, and most children have little pain afterwards.</p>

<h2>Why is tonsil surgery sometimes done with adenoidectomy?</h2>
<ul>
  <li>Enlarged tonsils can keep blocking the airway after the adenoids are removed.</li>
  <li>Tonsils that are large enough to block the airway can be partly removed (intracapsular surgery).</li>
  <li>Tonsils with repeated infections may need complete removal.</li>
</ul>
<p>Read more about <a href="tonsil.html">tonsil surgery</a> and <a href="snoring.html">snoring in children</a>.</p>
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
  <li>Closing a hole in the eardrum (tympanoplasty)</li>
  <li>Draining fluid from the middle ear (myringotomy)</li>
  <li>Repairing the ear bones (ossiculoplasty)</li>
  <li>Removing limited bone-eroding disease (cholesteatoma)</li>
</ul>

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
