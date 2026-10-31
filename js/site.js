(function () {
  var d = document.querySelector("details.conditions");
  if (!d) return;
  var input = d.querySelector(".cond-search");
  var items = d.querySelectorAll("li[data-k]");
  var groups = d.querySelectorAll(".cond-group");
  var none = d.querySelector(".cond-none");
  input.addEventListener("input", function () {
    var q = input.value.trim().toLowerCase();
    var shown = 0;
    items.forEach(function (li) {
      var hit = !q || q.split(/\s+/).every(function (w) { return li.dataset.k.indexOf(w) !== -1; });
      li.hidden = !hit;
      if (hit) shown++;
    });
    groups.forEach(function (g) { g.hidden = !g.querySelector("li:not([hidden])"); });
    none.hidden = shown > 0;
  });
  d.addEventListener("toggle", function () { if (d.open && window.matchMedia("(min-width: 701px)").matches) input.focus(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && d.open) { d.open = false; d.querySelector("summary").focus(); } });
  document.addEventListener("click", function (e) { if (d.open && !d.contains(e.target)) d.open = false; });
})();

(function () {
  document.querySelectorAll(".copy-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var text = document.getElementById(btn.dataset.copy).innerText;
      var done = function () {
        var old = btn.textContent;
        btn.textContent = "Copied";
        setTimeout(function () { btn.textContent = old; }, 2000);
      };
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(done);
      } else {
        var r = document.createRange();
        r.selectNodeContents(document.getElementById(btn.dataset.copy));
        var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
        try { document.execCommand("copy"); done(); } catch (e) {}
      }
    });
  });
})();

/* MERA Sleep Apnoea Score */
(function () {
  var form = document.getElementById("mera-score");
  if (!form) return;
  var MAX = {snore:10, pause:10, drive:15, talk:3, meet:2, zoom:2, phone:2, audience:1, idle:1, wake:4, headache:2, dm:3, bp:5, libido:3, weight:10};
  var NAMES = {snore:"Snoring", pause:"Breathing pauses", drive:"Driving", talk:"Talking", meet:"Meetings", zoom:"Video calls", phone:"Phone", audience:"Audience", idle:"Sitting idle", wake:"Mornings", headache:"Headache", dm:"Diabetes", bp:"Blood pressure", libido:"Interest in sex", weight:"Weight"};
  var h = document.getElementById("h-cm"), w = document.getElementById("w-kg"), out = document.getElementById("bmi-out");
  function bmi() {
    var hc = parseFloat(h.value), wk = parseFloat(w.value);
    if (!(hc > 100 && wk > 25)) { out.textContent = ""; return; }
    var b = wk / Math.pow(hc / 100, 2), v = b > 30 ? "10" : b >= 25 ? "6" : b >= 23 ? "3" : "0";
    out.textContent = "Your BMI is " + b.toFixed(1) + (b > 30 ? " (obese)" : b >= 25 ? " (overweight)" : b >= 23 ? " (a little overweight)" : " (normal)");
    var r = form.querySelector('input[name="weight"][value="' + v + '"]');
    if (r) r.checked = true;
  }
  h.addEventListener("input", bmi); w.addEventListener("input", bmi);
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var got = 0, max = 0, missing = [];
    Object.keys(MAX).forEach(function (k) {
      var c = form.querySelector('input[name="' + k + '"]:checked');
      if (!c) { missing.push(NAMES[k]); return; }
      if (c.value === "na") return;
      got += parseFloat(c.value); max += MAX[k];
    });
    var m = document.getElementById("score-missing");
    if (missing.length) {
      m.textContent = "Please answer: " + missing.join(", ") + ".";
      m.hidden = false;
      var fs = Array.prototype.find.call(form.querySelectorAll("fieldset[data-q]"), function (f) { return !f.querySelector("input:checked"); });
      if (fs) fs.scrollIntoView({behavior: "smooth", block: "center"});
      return;
    }
    m.hidden = true;
    var pct = max ? Math.round(got / max * 100) : 0;
    document.getElementById("score-pct").textContent = pct;
    document.getElementById("score-detail").textContent = got + " out of " + max + " points (questions marked 'don't know' or 'don't drive' are left out).";
    var band = document.getElementById("score-band");
    band.className = "score-band " + (pct > 70 ? "high" : pct >= 20 ? "mid" : "low");
    band.textContent = pct > 70 ? "Strong possibility of sleep apnoea. A sleep study is advised. Please book a consultation."
      : pct >= 20 ? "Sleep apnoea is likely. Consider a sleep study and an ENT check."
      : "Sleep apnoea is less likely. If you still snore loudly or feel tired, see a doctor.";
    var d = form.querySelector('input[name="drive"]:checked');
    document.getElementById("drive-warning").hidden = !(d && d.value !== "na" && parseFloat(d.value) > 0);
    var res = document.getElementById("score-result");
    res.hidden = false;
    res.scrollIntoView({behavior: "smooth", block: "start"});
  });
})();

/* MERA Child Sleep Apnoea Score */
(function () {
  var form = document.getElementById("mera-child");
  if (!form) return;
  var MAX = {snore:10, block:20, effort:15, position:3, neck:3, mouthsleep:10, mouthawake:10, bedwet:5, restless:5, yawn:5, classsleep:10, games:15, school:3, gain:10, height:10};
  var NAMES = {snore:"Snoring", block:"Breathing blocked", effort:"Laboured breathing", position:"Sleeping position", neck:"Head tilted back", mouthsleep:"Open mouth in sleep", mouthawake:"Mouth breathing when awake", bedwet:"Bedwetting", restless:"Restlessness", yawn:"Yawning", classsleep:"Sleeping in class", games:"Video games", school:"School", gain:"Weight", height:"Height compared with others", sex:"Boy or girl"};
  var ageIn = document.getElementById("c-age");
  var ageMsg = document.getElementById("c-agemsg"), monIn = document.getElementById("c-mon");
  function age() {
    var y = parseInt(ageIn.value, 10), mo = parseInt(monIn.value, 10) || 0;
    if (isNaN(y)) return null;
    var a = y + Math.min(Math.max(mo, 0), 11) / 12;
    return a >= 2 && a < 18 ? a : null;
  }
  function ageText() { var y = parseInt(ageIn.value, 10), mo = parseInt(monIn.value, 10) || 0; return y + " years" + (mo ? " " + mo + " months" : ""); }
  /* WHO growth check */
  var cmIn = document.getElementById("c-cm"), kgIn = document.getElementById("c-kg"), whoOut = document.getElementById("c-who");
  function lms(key, months) {
    var T = window.WHO_LMS && window.WHO_LMS[key]; if (!T) return null;
    var m = Math.min(Math.max(months, 24), 216), i = Math.floor(m) - 24, f = m - Math.floor(m);
    var a = T[i], b = T[Math.min(i + 1, T.length - 1)];
    return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f];
  }
  function zs(x, p) { return p[0] === 0 ? Math.log(x / p[1]) / p[2] : (Math.pow(x / p[1], p[0]) - 1) / (p[0] * p[2]); }
  function pctl(z) { var t = 1 / (1 + 0.2316419 * Math.abs(z)), d = 0.3989423 * Math.exp(-z * z / 2);
    var p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
    return Math.round((z > 0 ? 1 - p : p) * 100); }
  function ord(n) { if (n < 1) return "below the 1st"; if (n > 99) return "above the 99th"; var s = (n % 100 > 10 && n % 100 < 14) ? "th" : ({1: "st", 2: "nd", 3: "rd"}[n % 10] || "th"); return "the " + n + s; }
  function setRadio(name, v) { var r = form.querySelector('input[name="' + name + '"][value="' + v + '"]'); if (r) r.checked = true; }
  var growth = "";
  function who() {
    growth = ""; whoOut.textContent = "";
    var a = age(), s = form.querySelector('input[name="sex"]:checked'), cm = parseFloat(cmIn.value), kg = parseFloat(kgIn.value);
    if (!a || !s || !(cm > 50)) { if (cm > 0 || kg > 0) whoOut.textContent = "Enter the age and choose boy or girl to check growth."; return; }
    var months = a * 12, parts = [];
    var hz = zs(cm, lms(s.value + "h", months));
    parts.push("Height: " + ord(pctl(hz)) + " percentile" + (hz < -3 ? " (very short for age)" : hz < -2 ? " (short for age)" : hz < -1 ? " (below average)" : ""));
    setRadio("height", hz < -3 ? "15" : hz < -2 ? "10" : hz < -1 ? "5" : "0");
    if (kg > 2) {
      var bmi = kg / Math.pow(cm / 100, 2), bz = zs(bmi, lms(s.value + "b", months)), u5 = a < 5;
      var obese = u5 ? bz > 3 : bz > 2, over = u5 ? bz > 2 : bz > 1;
      parts.push("BMI " + bmi.toFixed(1) + ": " + ord(pctl(bz)) + " percentile" + (obese ? " (obese)" : over ? " (overweight)" : bz < -2 ? " (thin for age)" : " (normal)"));
      var g = form.querySelector('input[name="gain"]:checked');
      if (obese) setRadio("gain", "10h"); else if (over) setRadio("gain", "5h");
      else if (g && /h$/.test(g.value)) setRadio("gain", "0");
    }
    growth = parts.join(". ") + " (WHO).";
    whoOut.textContent = growth;
  }
  [ageIn, monIn, cmIn, kgIn].forEach(function (el) { el.addEventListener("input", who); });
  form.querySelectorAll('input[name="sex"]').forEach(function (el) { el.addEventListener("change", who); });
  function applies(fs) {
    var a = age();
    if (a === null) return true;
    var mn = fs.getAttribute("data-minage"), mx = fs.getAttribute("data-maxage");
    return !((mn && a < parseFloat(mn)) || (mx && a > parseFloat(mx)));
  }
  function refresh() {
    var a = (parseInt(ageIn.value, 10) || 0) + (parseInt(monIn.value, 10) || 0) / 12;
    ageMsg.hidden = !(a > 0 && (a < 2 || a >= 18));
    ageMsg.innerHTML = a >= 18 ? 'From 18 years, please use the <a href="sleep-score.html">adult MERA Sleep Apnoea Score</a>.' : "For a child under 2 who snores, please see a doctor directly.";
    form.querySelectorAll("fieldset[data-minage],fieldset[data-maxage]").forEach(function (fs) { fs.hidden = !applies(fs); });
  }
  ageIn.addEventListener("input", refresh); monIn.addEventListener("input", refresh);
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var got = 0, max = 0, missing = [], firstMissing = null;
    if (!age()) { missing.push("Age (2 to 17 years)"); firstMissing = ageIn.closest("fieldset"); }
    if (!form.querySelector('input[name="sex"]:checked')) { missing.push("Boy or girl"); firstMissing = firstMissing || form.querySelector('fieldset[data-q="sex"]'); }
    Object.keys(MAX).forEach(function (k) {
      var fs = form.querySelector('fieldset[data-q="' + k + '"]');
      if (fs && !applies(fs)) return;
      var c = form.querySelector('input[name="' + k + '"]:checked');
      if (!c) { missing.push(NAMES[k]); firstMissing = firstMissing || fs; return; }
      if (c.value === "na") return;
      got += parseFloat(c.value);
      max += (k === "height" && (parseFloat(cmIn.value) > 0 || c.value === "15")) ? 15 : MAX[k];
    });
    var m = document.getElementById("c-missing");
    if (missing.length) {
      m.textContent = "Please answer: " + missing.join(", ") + ".";
      m.hidden = false;
      if (firstMissing) firstMissing.scrollIntoView({behavior: "smooth", block: "center"});
      return;
    }
    m.hidden = true;
    var pct = max ? Math.round(got / max * 100) : 0;
    document.getElementById("c-pct").textContent = pct;
    document.getElementById("c-detail").textContent = got + " out of " + max + " points (questions that don't apply at this age are left out).";
    var cm = parseFloat(cmIn.value), kg = parseFloat(kgIn.value);
    var g = "Age " + ageText();
    if (cm > 0) g += ", height " + cm + " cm";
    if (kg > 0) g += ", weight " + kg + " kg";
    document.getElementById("c-growth").textContent = g + ". " + growth;
    var band = document.getElementById("c-band");
    band.className = "score-band " + (pct > 70 ? "high" : pct >= 20 ? "mid" : "low");
    band.textContent = pct > 70 ? "Strong possibility of sleep apnoea. Please book an ENT consultation soon."
      : pct >= 20 ? "Sleep apnoea is likely. Please get an ENT check."
      : "Sleep apnoea is less likely. If your child still snores regularly or breathes through the mouth, see a doctor.";
    var res = document.getElementById("c-result");
    res.hidden = false;
    res.scrollIntoView({behavior: "smooth", block: "start"});
  });
})();
