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
    var b = wk / Math.pow(hc / 100, 2), v = b > 30 ? "10" : (b >= 25 ? "5" : "0");
    out.textContent = "Your BMI is " + b.toFixed(1) + (b > 30 ? " (obese)" : b >= 25 ? " (overweight)" : " (normal)");
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
