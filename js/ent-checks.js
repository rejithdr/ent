/* MIDAS ENT self-checks: blocked nose, hearing, dizziness.
   One question at a time; based on the MIDAS ENT protocols (draft spec, November 2026).
   No treatment advice is given. Nothing is stored or sent. */
(function () {
  "use strict";
  var box = document.getElementById("ent-check");
  if (!box) return;
  var L = "abcdefghij";
  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]; }); }
  function inSet(v, s) { return v != null && s.indexOf(v) !== -1; }
  function any(arr, s) { return Array.isArray(arr) && arr.some(function (x) { return s.indexOf(x) !== -1; }); }
  var YN = ["Yes", "No"];

  /* ================= BLOCKED NOSE ================= */
  var NOSE_OPTS = ["Not a problem", "Very mild problem", "Moderate problem", "Fairly bad problem", "Severe problem"];
  var NOSE_ITEMS = ["Nasal congestion or stuffiness", "Nasal blockage or obstruction", "Trouble breathing through my nose", "Trouble sleeping", "Unable to get enough air through my nose during exercise or exertion"];
  var nose = {
    Q: {
      rf: {multi: true, none: "d", label: "Warning signs", q: "Do you have any of these?", hint: "Tick all that apply.",
        opts: ["Blockage on one side only, with bleeding or blood-stained mucus", "Swelling around the eye, double vision or reduced vision", "Numbness or swelling of the cheek", "None of these"]},
      dur: {label: "How long", q: "How long has your nose been blocked?", opts: ["Less than 2 weeks, with a cold", "2 to 4 weeks", "More than a month"]},
      pat: {label: "Pattern", q: "How does the blockage behave?", opts: ["It switches between sides, or is worse lying down or at night", "It is always on the same side and doesn't change", "Not sure"]},
      alg: {multi: true, none: "d", label: "Allergy signs", q: "Do you have any of these?", hint: "Tick all that apply.", opts: ["Sneezing bouts", "Itchy nose or eyes", "Watery runny nose", "None of these"]},
      tx: {label: "Treatment so far", q: "Have you been treated by a doctor for the blocked nose?", opts: ["Yes, for 6 weeks or more, and it is still blocked", "Yes, but for less than 6 weeks", "Not yet"]},
      ha: {label: "One-sided headache", q: "Do you get a headache or heaviness on one side of the face?", opts: YN},
      sn: {label: "Snoring", q: "Do you snore, or breathe through your mouth at night?", opts: YN}
    },
    order: ["rf", "dur", "n1", "n2", "n3", "n4", "n5", "pat", "alg", "tx", "ha", "sn"],
    next: function (A) {
      if (!A.rf) return "rf";
      if (any(A.rf, "abc")) return null;
      if (!A.dur) return "dur";
      if (A.dur === "a") return null;
      var rest = ["n1", "n2", "n3", "n4", "n5", "pat", "alg", "tx", "ha", "sn"];
      for (var i = 0; i < rest.length; i++) if (A[rest[i]] == null) return rest[i];
      return null;
    },
    result: function (A) {
      var r = {adds: []};
      if (any(A.rf, "abc")) return {level: "high", title: "See an ENT doctor within a few days", text: "These signs need a nasal endoscopy, a simple look inside the nose with a thin camera, to find the cause.", adds: []};
      if (A.dur === "a") return {level: "low", title: "Likely a cold", text: "A blocked nose with a cold usually settles in 1 to 2 weeks. See an ENT doctor if it lasts longer.", adds: []};
      var sum = 0; for (var i = 1; i <= 5; i++) sum += L.indexOf(A["n" + i]);
      var s = sum * 5;
      r.score = "NOSE score " + s + " out of 100";
      if (s >= 55 && A.tx === "a") { r.level = "high"; r.title = "Severe blockage that hasn't settled with treatment"; r.text = "See an ENT doctor. A nasal endoscopy, a simple look inside the nose with a thin camera, will show which structure is causing it. Surgery is considered only if the endoscopy confirms a structural blockage."; }
      else if (s >= 55) { r.level = "high"; r.title = "Severe blockage"; r.text = "See an ENT doctor to find the cause. Most people improve without surgery once the cause is treated."; }
      else if (s >= 30) { r.level = "mid"; r.title = "Moderate blockage"; r.text = "See an ENT doctor if it is affecting your sleep or daily life."; }
      else { r.level = "low"; r.title = "Mild blockage"; r.text = "See an ENT doctor if it gets worse or lasts."; }
      if (A.pat === "a") r.adds.push("The turbinates are normal swellings inside the nose that everyone has. They swell and shrink through the day, often taking turns between the two sides. When they stay enlarged, often because of allergy, they block the nose. This is the most common cause of a blocked nose.");
      if (A.pat === "b") r.adds.push("The nasal septum is the wall dividing the two sides of the nose. When it is bent, it can narrow one side or both, and the blockage doesn't change." + (A.ha === "a" ? " A bent septum can also cause a headache on one side." : ""));
      if (any(A.alg, "abc")) r.adds.push("Sneezing, itching and a watery nose suggest allergy, which commonly keeps the turbinates swollen.");
      if (A.sn === "a") r.link = {href: box.getAttribute("data-mera") || "sleep-score.html", text: "Snoring can be a sign of sleep apnoea. Take the MERA Sleep Apnoea Check."};
      return r;
    }
  };
  for (var ni = 0; ni < 5; ni++) nose.Q["n" + (ni + 1)] = {label: NOSE_ITEMS[ni], step: "NOSE score, " + (ni + 1) + " of 5", q: "Over the past month, how much of a problem was this for you: " + NOSE_ITEMS[ni].toLowerCase() + "?", opts: NOSE_OPTS};

  /* ================= HEARING ================= */
  var HUM = ["In the ear that hears less", "In the better ear", "In the middle, or equally in both ears", "Not sure"];
  var hearing = {
    Q: {
      who: {label: "Who", q: "Who is this check for?", opts: ["Me (adult)", "My child"]},
      onset: {label: "Onset", q: "How did the hearing loss start?", opts: ["Suddenly, over minutes to 3 days", "Gradually, over weeks or months", "Not sure"]},
      rf: {label: "Stroke signs", q: "Along with the hearing loss, do you have weakness or numbness of the face, arm or leg, or slurred speech?", opts: YN},
      when: {label: "When it started", q: "When did the hearing loss start?", opts: ["Within the last 3 days", "3 to 7 days ago", "More than a week ago"]},
      ear: {label: "Which ear", q: "Which ear hears less?", opts: ["Right ear", "Left ear", "Both ears"]},
      ring: {label: "Ringing", q: "Do you have ringing, buzzing or hissing in that ear?", opts: YN},
      spin: {label: "Spinning", q: "Do you have any spinning or imbalance?", opts: YN},
      h1: {label: "Hum test, ears open", step: "Hum test, step 1 of 2",
        q: "Keep both ears open and hum a steady \"hmm\" with your mouth closed. Where do you hear the hum?", opts: HUM},
      h2: {label: "Hum test, ears closed", step: "Hum test, step 2 of 2",
        q: "Now close both ears by pressing the small flaps in front of them with your fingers, and hum again. Where do you hear it now?", opts: HUM},
      side: {label: "Which ear", q: "Is the hearing loss in one ear or both?", opts: ["One ear", "Both ears"]},
      one: {multi: true, none: "f", label: "With it", q: "Do you have any of these as well?", hint: "Tick all that apply.",
        opts: ["Ringing or buzzing in that ear", "Dizziness", "Numbness or weakness of the face", "A blocked or full feeling in that ear", "Blocked nose, nosebleeds or a lump in the neck", "None of these"]},
      both: {multi: true, none: "e", label: "About you", q: "Do any of these apply?", hint: "Tick all that apply.",
        opts: ["I am over 60", "Years of loud noise at work", "Family members with hearing loss", "Discharge from the ears", "None of these"]},
      csign: {multi: true, none: "f", label: "Hearing signs", q: "Have you or a teacher noticed any of these?", hint: "Tick all that apply.",
        opts: ["Often asks \"what?\" or needs things repeated", "Keeps the TV or phone volume high", "Doesn't respond when called", "Teacher is concerned about hearing", "Speech is behind other children of the same age", "None of these"]},
      cold: {label: "Recent infection", q: "Has your child had an ear infection or a cold in the last 3 months?", opts: YN},
      csnore: {label: "Snoring", q: "Does your child snore or breathe through the mouth?", opts: YN}
    },
    order: ["who", "onset", "rf", "when", "ear", "ring", "spin", "h1", "h2", "side", "one", "both", "csign", "cold", "csnore"],
    next: function (A) {
      if (!A.who) return "who";
      if (!A.onset) return "onset";
      var sudden = A.onset === "a" || (A.onset === "c" && A.who === "a");
      if (sudden) {
        if (!A.rf) return "rf";
        if (A.rf === "a") return null;
        var s = ["when", "ear", "ring", "spin"];
        for (var i = 0; i < s.length; i++) if (!A[s[i]]) return s[i];
        if (A.ear !== "c") { if (!A.h1) return "h1"; if (!A.h2) return "h2"; }
        return null;
      }
      if (A.who === "b") {
        if (!A.csign) return "csign";
        if (!A.cold) return "cold";
        if (!A.csnore) return "csnore";
        return null;
      }
      if (!A.side) return "side";
      if (A.side === "a" && !A.one) return "one";
      if (A.side === "b" && !A.both) return "both";
      return null;
    },
    result: function (A) {
      var r = {adds: []};
      var sudden = A.onset === "a" || (A.onset === "c" && A.who === "a");
      if (sudden) {
        if (A.rf === "a") return {level: "high", urgent: true, title: "Go to the emergency department now", text: "Hearing loss with weakness, numbness or slurred speech can be a sign of a stroke.", adds: []};
        /* NOT framework: conductive loss lateralises to the poorer ear, and centralises or stays there on closing both ears */
        var blockage = A.ear !== "c" && A.h1 === "a" && inSet(A.h2, "ac") && A.ring === "b";
        if (blockage) {
          r.level = "mid"; r.title = "Likely a blockage-type hearing loss";
          r.text = "See an ENT doctor within the next couple of days at least. It is best to be seen and have a hearing test within 72 hours of when it started.";
          r.adds.push("The hum going to the ear that hears less, and not moving to the better ear when both ears are closed, suggests something in the ear canal or middle ear is stopping sound, such as wax, fluid behind the eardrum, a hole in the eardrum or a problem with the tiny ear bones.");
          r.adds.push("Only an examination and a hearing test can confirm this. If the nerve turns out to be involved, recovery is much less likely after 72 hours.");
        } else {
          r.title = "Possible nerve hearing loss";
          if (A.when === "a") { r.level = "high"; r.urgent = true; r.text = "Emergency: see an ENT doctor today. Sudden nerve hearing loss has the best chance of recovery when treated within the first 72 hours. Don't wait for it to clear by itself."; }
          else if (A.when === "b") { r.level = "high"; r.text = "Urgent: see an ENT doctor within 24 hours. Recovery is less likely after 72 hours, but still possible."; }
          else { r.level = "high"; r.text = "See an ENT doctor this week. Some recovery may still be possible."; }
          if (A.ear === "c") r.adds.push("Sudden hearing loss in both ears needs to be seen with the same urgency.");
          else if (A.ring === "a") r.adds.push("Ringing with sudden hearing loss suggests the inner ear or hearing nerve may be involved. The hum test can miss high-pitched hearing loss, which often comes with ringing.");
          else r.adds.push("The hum test could not show a blockage-type cause, so the hearing nerve may be involved.");
        }
        if (A.spin === "a") r.adds.push("Spinning or imbalance suggests the balance part of the inner ear may also be affected. A scan of the hearing nerve may be needed.");
        return r;
      }
      if (A.who === "b") {
        if (any(A.csign, "abcde")) {
          r.level = "mid"; r.title = "Possible fluid behind the eardrum (glue ear)";
          r.text = "Glue ear is the most likely cause of hearing problems in children. It often follows a cold or ear infection, and most clears within 3 months. See an ENT doctor if it lasts beyond 3 months, if hearing is clearly affected, or if speech is behind.";
          if (A.csnore === "a") r.link = {href: box.getAttribute("data-mera-child") || "child-sleep-score.html", text: "Enlarged adenoids commonly cause both glue ear and snoring. Take the MERA Child Sleep Apnoea Check."};
        } else { r.level = "low"; r.title = "No clear hearing signs"; r.text = "If you are still worried, a hearing test is simple and can be done at any age."; }
        return r;
      }
      if (A.side === "a") {
        if (any(A.one, "e")) { r.level = "high"; r.title = "See an ENT doctor within a week"; r.text = "In adults, fluid behind one eardrum can come from a blockage at the back of the nose, which needs a nasal endoscopy to look at."; }
        else {
          r.level = "mid"; r.title = "See an ENT doctor for an ear check and hearing test";
          r.text = "Slowly worsening hearing in one ear can come from wax or fluid, but it can also come from a growth on the hearing nerve, even without other symptoms. An MRI scan may be needed.";
          if (any(A.one, "abc")) r.adds.push("Ringing, dizziness or face symptoms make it more likely that an MRI scan will be needed.");
        }
        return r;
      }
      if (any(A.both, "d")) { r.level = "mid"; r.title = "See an ENT doctor"; r.text = "Discharge with hearing loss usually means a middle ear problem that needs examination."; }
      else { r.level = "low"; r.title = "Book a hearing test"; r.text = any(A.both, "ab") ? "Hearing slowly weakens with age and with long noise exposure. A hearing test shows how much, and what will help." : "A hearing test shows how much hearing has changed and what will help."; }
      return r;
    }
  };

  /* ================= DIZZINESS ================= */
  var dizzy = {
    Q: {
      rf: {multi: true, none: "g", label: "Warning signs", q: "Along with the dizziness, do you have any of these?", hint: "Tick all that apply.",
        opts: ["Weakness or numbness of the face, arm or leg", "Slurred speech", "Double vision", "Can't stand or walk", "Sudden severe headache", "Sudden hearing loss", "None of these"]},
      feel: {label: "What it feels like", q: "What does it feel like?", opts: ["The room or I spin", "Light-headed, as if about to faint", "Unsteady when walking"]},
      when: {label: "When it comes on", q: "When does it come on?", opts: ["With head movement: lying down, turning in bed, looking up or bending", "On standing up from sitting or lying", "By itself, even when still"]},
      dur: {label: "How long each episode lasts", q: "How long does each episode last?", opts: ["Less than a minute", "Longer than a minute"]},
      still: {label: "Still happening", q: "Is it still happening?", opts: ["Yes, every day or most days", "It happened, but has settled"]},
      fac: {multi: true, none: "d", label: "Recent factors", q: "Do any of these apply?", hint: "Tick all that apply.", opts: ["A recent cold or fever", "Diabetes", "Migraine", "None of these"]},
      pat: {label: "Pattern", q: "Which best describes it?", opts: ["Constant for a day or more, starting after a cold or fever", "Attacks lasting hours, with ringing, ear fullness or hearing loss", "Attacks with headache or sensitivity to light", "None of these"]}
    },
    order: ["rf", "feel", "when", "dur", "still", "fac", "pat"],
    next: function (A) {
      if (!A.rf) return "rf";
      if (any(A.rf, "abcdef")) return null;
      if (!A.feel) return "feel";
      if (!A.when) return "when";
      if (A.when === "a") { if (!A.dur) return "dur"; if (!A.still) return "still"; if (!A.fac) return "fac"; return null; }
      if (A.when === "c" && A.feel !== "c" && !A.pat) return "pat";
      return null;
    },
    result: function (A) {
      var r = {adds: []};
      if (any(A.rf, "abcde")) return {level: "high", urgent: true, title: "Emergency: go to hospital now", text: "These can be signs of a stroke.", adds: []};
      if (any(A.rf, "f")) return {level: "high", urgent: true, title: "See an ENT doctor today", text: "Sudden hearing loss with dizziness needs urgent examination; recovery is best when it is treated early.", adds: [], link: {href: box.getAttribute("data-hearing") || "hearing-check.html", text: "Take the Hearing Check."}};
      if (A.when === "a") {
        if (A.dur === "b") { r.level = "mid"; r.title = "See an ENT doctor"; r.text = "The pattern is less typical of positional vertigo, so other causes need to be checked."; }
        else if (A.still === "a") { r.level = "mid"; r.title = "Book at the vertigo clinic"; r.text = "This is the pattern of positional vertigo, the commonest cause of spinning. Tiny crystals in the balance organ of the inner ear move into the wrong place and trigger spinning with head movement. Positional tests in the clinic show which part of the balance organ is involved."; }
        else { r.level = "low"; r.title = "Come for a review if it returns"; r.text = "This is likely a mild positional disturbance of the balance organ, which can settle by itself."; }
        if (any(A.fac, "abc")) r.adds.push("A recent cold, diabetes or migraine can make the balance organ more prone to positional vertigo.");
        return r;
      }
      if (A.when === "b") return {level: "mid", title: "See your doctor", text: "Light-headedness on standing is commonly caused by blood pressure dropping on standing, medicines, or too little fluid.", adds: []};
      if (A.feel === "c") return {level: "mid", title: "See a doctor", text: "Balance depends on the inner ear, nerves, eyesight and muscles, and each may need checking.", adds: []};
      if (A.pat === "a") return {level: "high", title: "See an ENT doctor soon", text: "Inflammation of the balance nerve can follow a viral infection.", adds: []};
      if (A.pat === "b") return {level: "mid", title: "See an ENT doctor; a hearing test is needed", text: "An inner ear condition such as Ménière's disease is possible.", adds: []};
      if (A.pat === "c") return {level: "mid", title: "See an ENT doctor or neurologist", text: "Migraine can cause dizziness attacks, sometimes without much headache.", adds: []};
      return {level: "mid", title: "See an ENT doctor", text: "Dizziness has many causes, and an examination will help find yours.", adds: []};
    }
  };

  /* ================= ENGINE ================= */
  var TOOL = {nose: nose, hearing: hearing, dizzy: dizzy}[box.getAttribute("data-tool")];
  if (!TOOL) return;
  var A = {}, path = [];

  function answer(id, v) { A[id] = v; path.push(id); show(); }
  function back() { if (!path.length) return; delete A[path.pop()]; show(); }
  function restart() { A = {}; path = []; show(); }
  function nav(withNext) {
    var n = el("div", "flow-nav");
    if (path.length) { var b = el("button", "btn quiet", "Back"); b.type = "button"; b.onclick = back; n.appendChild(b); }
    if (withNext) { var c = el("button", "btn", "Continue"); c.type = "submit"; n.appendChild(c); }
    return n;
  }
  function question(id) {
    var q = TOOL.Q[id], card = el("form", "flow-card");
    card.setAttribute("novalidate", "");
    card.appendChild(el("p", "flow-step", esc(q.step || ("Question " + (path.length + 1)))));
    var h = el("h2", "flow-q"); h.textContent = q.q; h.tabIndex = -1; card.appendChild(h);
    if (q.hint) card.appendChild(el("p", "q-hint", esc(q.hint)));
    if (!q.multi) {
      var o = el("div", "opts");
      q.opts.forEach(function (t, i) { var b = el("button", "opt opt-btn"); b.type = "button"; b.textContent = t; b.onclick = function () { answer(id, L[i]); }; o.appendChild(b); });
      card.appendChild(o); card.appendChild(nav(false));
      return card;
    }
    var mo = el("div", "opts"), err = el("p", "score-missing"); err.hidden = true;
    q.opts.forEach(function (t, i) {
      var lab = el("label", "opt"), cb = el("input"); cb.type = "checkbox"; cb.value = L[i];
      cb.onchange = function () {
        if (!cb.checked) return;
        if (L[i] === q.none) mo.querySelectorAll("input").forEach(function (x) { if (x !== cb) x.checked = false; });
        else { var n = mo.querySelector('input[value="' + q.none + '"]'); if (n) n.checked = false; }
      };
      lab.appendChild(cb); lab.appendChild(el("span", null, esc(t))); mo.appendChild(lab);
    });
    card.appendChild(mo); card.appendChild(err); card.appendChild(nav(true));
    card.onsubmit = function (e) {
      e.preventDefault();
      var v = Array.prototype.map.call(mo.querySelectorAll("input:checked"), function (x) { return x.value; });
      if (!v.length) { err.textContent = "Please tick at least one, or \"" + q.opts[L.indexOf(q.none)] + "\"."; err.hidden = false; return; }
      answer(id, v);
    };
    return card;
  }
  function ansText(id) {
    var q = TOOL.Q[id], v = A[id];
    return Array.isArray(v) ? v.map(function (x) { return q.opts[L.indexOf(x)]; }).join("; ") : q.opts[L.indexOf(v)];
  }
  function result() {
    var r = TOOL.result(A), card = el("section", "score-result flow-result");
    card.setAttribute("aria-live", "polite");
    card.appendChild(el("h2", null, "Your result"));
    if (r.urgent) card.appendChild(el("div", "urgent", "<strong>" + esc(r.title) + "</strong>"));
    else card.appendChild(el("p", "score-band " + r.level, esc(r.title)));
    if (r.score) card.appendChild(el("p", "q-hint", esc(r.score)));
    card.appendChild(el("p", null, esc(r.text)));
    r.adds.forEach(function (t) { card.appendChild(el("p", "flow-add", esc(t))); });
    if (r.link) card.appendChild(el("p", null, '<a href="' + esc(r.link.href) + '">' + esc(r.link.text) + "</a>"));
    card.appendChild(el("p", "q-hint", "This is a check, not a diagnosis. Only an examination by a doctor can confirm the cause."));
    var d = el("details", "flow-answers");
    d.appendChild(el("summary", null, "Your answers (" + path.length + ")"));
    var ul = el("ul");
    path.slice().sort(function (x, y) { return TOOL.order.indexOf(x) - TOOL.order.indexOf(y); })
      .forEach(function (id) { ul.appendChild(el("li", null, "<strong>" + esc(TOOL.Q[id].label) + ":</strong> " + esc(ansText(id)))); });
    d.appendChild(ul); card.appendChild(d);
    var tel = box.getAttribute("data-tel");
    if (tel && r.urgent) {
      card.appendChild(el("p", "intro-actions", '<a class="btn" href="tel:' + esc(tel) + '">Call ' + esc(box.getAttribute("data-tel-show")) + '</a>'));
    } else if (tel) {
      var names = {nose: "Blocked Nose Check", hearing: "Hearing Check", dizzy: "Dizziness Check"};
      var msg = "Hello, I did the " + (names[box.getAttribute("data-tool")] || "self-check") + " on entmidas.com.\nResult: " + r.title + "\nI would like to book a consultation.";
      card.appendChild(el("p", null, "Send your result on WhatsApp to book, or take a screenshot and show it at your consultation."));
      card.appendChild(el("p", "intro-actions", '<a class="btn" href="' + esc(box.getAttribute("data-wa")) + "?text=" + encodeURIComponent(msg) + '">Send my result on WhatsApp</a> <a class="btn quiet" href="tel:' + esc(tel) + '">Call ' + esc(box.getAttribute("data-tel-show")) + '</a>'));
    } else card.appendChild(el("p", null, "Take a screenshot of this result and show it to your doctor."));
    var n = el("div", "flow-nav");
    var b = el("button", "btn quiet", "Back"); b.type = "button"; b.onclick = back; n.appendChild(b);
    var s = el("button", "btn quiet", "Start again"); s.type = "button"; s.onclick = restart; n.appendChild(s);
    card.appendChild(n);
    return card;
  }
  var sent = false; /* analytics: records only that a check was completed, never answers or result */
  function show() {
    box.innerHTML = "";
    var id = TOOL.next(A), node = id ? question(id) : result();
    if (!id && !sent && window.gtag) { sent = true; gtag("event", "check_complete", {check_name: box.getAttribute("data-tool")}); }
    box.appendChild(node);
    var f = node.querySelector(".flow-q, h2");
    if (f && path.length) { f.tabIndex = -1; f.focus({preventScroll: true}); box.scrollIntoView({behavior: "smooth", block: "start"}); }
  }
  window.ENT_CHECK = {answers: function () { return A; }, result: function () { return TOOL.result(A); }};
  show();
})();
