/* MERA Dizziness, Blocked Nose and Throat & Voice checks.
   Adaptive: one question at a time. All text is in mera-checks-text.js. Nothing is stored or sent.
   Answers: single choice "a".."d"; yes/no "y"/"n"; tick-any arrays (["none"] when nothing applies); scores 0..3. */
(function () {
  "use strict";
  var T = window.MERA_TEXT, CFG = window.MERA_CONFIG || { emergencyNumber: "108" };
  if (!T) return;
  var L = "abcdefgh";
  function ticked(v) { return Array.isArray(v) && v.length && v[0] !== "none"; }
  function fill(s) { return String(s).replace(/\{EMERGENCY\}/g, CFG.emergencyNumber); }

  /* ================= DECISION LOGIC (from Dr Rejith's spec, November 2026) ================= */
  var TOOLS = {};

  TOOLS.dizzy = {
    order: ["em", "feel", "dur", "d4a", "d4b", "d4c", "d5b", "d5a", "d5d", "d5c", "d6a", "d6c", "d6b"],
    next: function (A) {
      if (A.em == null) return "em";
      if (ticked(A.em)) return null;
      if (!A.feel) return "feel";
      if (A.feel !== "a") return null;
      if (!A.dur) return "dur";
      var step5 = A.dur === "b";
      if (A.dur === "a" || A.dur === "d") {
        if (!A.d4a) return "d4a";
        if (A.d4a === "n") { if (A.dur === "d") step5 = true; else return null; }
        else { if (!A.d4b) return "d4b"; if (A.d4b === "y") return null; if (!A.d4c) return "d4c"; return null; }
      }
      if (step5) {
        var s = ["d5b", "d5a", "d5d", "d5c"];  /* asked in priority order; stops at the first yes */
        for (var i = 0; i < s.length; i++) { if (!A[s[i]]) return s[i]; if (A[s[i]] === "y") return null; }
        return null;
      }
      if (A.dur === "c") {
        if (!A.d6a) return "d6a";
        if (A.d6a === "a") return A.d6c ? null : "d6c";
        return A.d6b ? null : "d6b";
      }
      return null;
    },
    result: function (A) {
      if (ticked(A.em)) return { codes: ["E"] };
      if (A.feel === "b") return { codes: ["F"] };
      if (A.feel === "c") return { codes: ["U"] };
      if (A.feel === "d") return { codes: ["P"] };
      if (A.dur === "a" || (A.dur === "d" && A.d4a === "y")) {
        if (A.d4a === "n" || A.d4b === "y") return { codes: ["A3"] };
        return { codes: [A.d4c === "y" ? "A1" : "A2"] };
      }
      if (A.dur === "b" || A.dur === "d") {
        if (A.d5b === "y") return { codes: ["H"] };
        if (A.d5a === "y") return { codes: ["B1"] };
        if (A.d5d === "y") return { codes: ["B2"] };
        if (A.d5c === "y") return { codes: ["B3"] };
        return { codes: ["B4"] };
      }
      if (A.d6a === "a") return { codes: ["C1"], adds: A.d6c === "y" ? ["C1h"] : [] };
      return { codes: [A.d6b === "y" ? "C2" : "C3"] };
    }
  };

  var NOSE_S = ["s1", "s2", "s3", "s4", "s5"];
  TOOLS.nose = {
    order: ["age", "em", "rf", "dur", "n4a", "n4b", "n5a", "n6a", "n6b", "n6c", "n6d", "n6e", "n6f", "n7a", "n7b", "n7c"].concat(NOSE_S),
    scoreIds: NOSE_S,
    next: function (A) {
      if (!A.age) return "age";
      if (A.age === "b") return null;
      if (A.em == null) return "em";
      if (ticked(A.em)) return null;
      if (A.rf == null) return "rf";
      if (ticked(A.rf)) return null;
      if (!A.dur) return "dur";
      var toScore = false;
      if (A.dur === "a") {
        if (!A.n4a) return "n4a";
        if (A.n4a === "n" && !A.n4b) return "n4b";
        toScore = true;
      } else if (A.dur === "b") {
        if (!A.n5a) return "n5a";
        if (A.n5a === "y") toScore = true;
      }
      if (!toScore) {
        var s6 = ["n6a", "n6b", "n6c", "n6d", "n6e", "n6f"];  /* all asked: every result that applies is shown */
        for (var i = 0; i < s6.length; i++) if (!A[s6[i]]) return s6[i];
        if (A.n6c === "y") {
          if (!A.n7a) return "n7a";
          if (A.n7a !== "c") {
            if (!A.n7b) return "n7b";
            if (A.n7b === "n" && A.n7a !== "a" && !A.n7c) return "n7c";
          }
        }
      }
      for (var k = 0; k < NOSE_S.length; k++) if (A[NOSE_S[k]] == null) return NOSE_S[k];
      return null;
    },
    result: function (A) {
      if (A.age === "b") return { codes: ["CHILD"] };
      if (ticked(A.em)) {
        /* watery fluid after a head injury (option d) is a possible CSF leak, not a spreading infection */
        var csf = A.em.indexOf("d") !== -1, other = A.em.some(function (x) { return x !== "d"; });
        return { codes: csf && other ? ["E", "ECSF"] : csf ? ["ECSF"] : ["E"] };
      }
      if (ticked(A.rf)) return { codes: ["R"] };
      var r = { codes: [], adds: [], score: scoreOf(A, NOSE_S, T.nose) };
      if (A.dur === "a") r.codes.push(A.n4a === "y" || A.n4b === "y" ? "S1" : "S2");
      else if (A.dur === "b" && A.n5a === "y") r.codes.push("S3");
      else {
        if (A.n6a === "y") r.codes.push("L1");
        if (A.n6b === "y") r.codes.push("L2");
        if (A.n6c === "y") r.codes.push("L3");
        if (A.n6d === "y") r.codes.push("L4");
        if (!r.codes.length) r.codes.push("L6");
        if (A.n6c === "y" && A.n7a && A.n7a !== "c") {
          if (A.n7b === "y") r.codes.push("N1");
          else if (A.n7a === "a") r.codes.push("N2");
          else if (A.n7c === "y") r.codes.push("N3");
        }
        if (A.n6e === "y") r.adds.push("L5");
        if (A.n6f === "y") r.adds.push("SLEEP");
      }
      return r;
    }
  };

  var THROAT_S = ["t1", "t2", "t3", "t4", "t5", "t6"];
  TOOLS.throat = {
    order: ["age", "em", "rf", "main"].concat(THROAT_S, ["v5b", "v5c", "v5d", "v5e", "v5a", "k6a", "k6b"]),
    scoreIds: THROAT_S,
    next: function (A) {
      if (!A.age) return "age";
      if (A.age === "b") return null;
      if (A.em == null) return "em";
      if (ticked(A.em)) return null;
      if (A.rf == null) return "rf";
      if (ticked(A.rf)) return null;
      if (!A.main) return "main";
      if (A.main === "a") { for (var i = 0; i < THROAT_S.length; i++) if (A[THROAT_S[i]] == null) return THROAT_S[i]; return null; }
      if (A.main === "b") {
        var v = ["v5b", "v5c", "v5d", "v5e"];  /* priority order; stops at the first yes */
        for (var j = 0; j < v.length; j++) { if (!A[v[j]]) return v[j]; if (A[v[j]] === "y" || (v[j] === "v5e" && A.v5e === "a")) return null; }
        return A.v5a ? null : "v5a";
      }
      if (!A.k6a) return "k6a";
      if (A.k6a === "a" && !A.k6b) return "k6b";
      return null;
    },
    result: function (A) {
      if (A.age === "b") return { codes: ["CHILD"] };
      if (ticked(A.em)) return { codes: ["E"] };
      if (ticked(A.rf)) return { codes: ["R"] };
      if (A.main === "a") {
        var sc = scoreOf(A, THROAT_S, T.throat), others = THROAT_S.filter(function (k) { return k !== "t2"; });
        var lumpOnly = A.t2 >= 1 && others.every(function (k) { return A[k] === 0; });
        return { codes: [sc.total >= 6 ? "T1" : lumpOnly ? "T2" : "T3"], score: sc };
      }
      if (A.main === "b") {
        if (A.v5b === "y") return { codes: ["V1"] };
        if (A.v5c === "y") return { codes: ["V2"] };
        if (A.v5d === "y") return { codes: ["V3"] };
        if (A.v5e === "a") return { codes: ["V4"] };
        return { codes: [A.v5a === "y" ? "V5" : "V6"] };
      }
      if (A.k6a === "b" || A.k6a === "c") return { codes: ["K1"] };
      return { codes: [A.k6b === "y" ? "K2" : "K3"] };
    }
  };

  function scoreOf(A, ids, txt) {
    if (!ids.every(function (k) { return A[k] != null; })) return null;
    var total = ids.reduce(function (s, k) { return s + A[k]; }, 0), max = ids.length * 3, band = null;
    if (txt.bands) for (var i = 0; i < txt.bands.length; i++) if (total <= txt.bands[i][0]) { band = txt.bands[i][1]; break; }
    return { total: total, max: max, band: band, name: txt.scoreName };
  }

  var RANK = { emergency: 0, high: 1, mid: 2, low: 3 };
  function sortCodes(tool, codes) {
    var r = T[tool].r;
    return codes.slice().sort(function (x, y) { return RANK[r[x].level] - RANK[r[y].level]; });
  }

  window.MERA_CHECKS = { tools: TOOLS, text: T, sortCodes: sortCodes, ticked: ticked };

  /* ================= RENDERING ================= */
  var box = document.getElementById("mera-check");
  if (box) render(box);

  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  function render(box) {
    var tool = box.getAttribute("data-tool"), LOGIC = TOOLS[tool], TX = T[tool], C = T.common;
    if (!LOGIC) return;
    var A = {}, path = [], sent = false;

    function opts(id) {
      var q = TX.q[id];
      if (q.yn) return [[C.yes, "y"], [C.no, "n"]];
      if (q.score) return TX.scoreOpts.map(function (t, i) { return [t, i]; });
      return q.opts.map(function (t, i) { return [t, L[i]]; });
    }
    function answer(id, v) { A[id] = v; path.push(id); show(); }
    function back() { if (path.length) { delete A[path.pop()]; show(); } }
    function restart() { A = {}; path = []; history.replaceState(null, "", location.pathname); show(); }
    function navRow(withNext) {
      var n = el("div", "flow-nav");
      if (path.length) { var b = el("button", "btn quiet", esc(C.back)); b.type = "button"; b.onclick = back; n.appendChild(b); }
      if (withNext) { var c = el("button", "btn", esc(C.cont)); c.type = "submit"; n.appendChild(c); }
      return n;
    }
    function question(id) {
      var q = TX.q[id], card = el("form", "flow-card");
      card.setAttribute("novalidate", "");
      card.appendChild(el("p", "flow-step", esc(q.step || (C.question + " " + (path.length + 1)))));
      var h = el("h2", "flow-q"); h.textContent = q.q; card.appendChild(h);
      if (!q.multi) {
        var o = el("div", "opts");
        opts(id).forEach(function (p) { var b = el("button", "opt opt-btn"); b.type = "button"; b.textContent = p[0]; b.onclick = function () { answer(id, p[1]); }; o.appendChild(b); });
        card.appendChild(o); card.appendChild(navRow(false));
        return card;
      }
      card.appendChild(el("p", "q-hint", esc(C.tickAll)));
      var mo = el("div", "opts"), err = el("p", "score-missing"); err.hidden = true;
      q.opts.concat([C.none]).forEach(function (t, i) {
        var val = i < q.opts.length ? L[i] : "none";
        var lab = el("label", "opt"), cb = el("input"); cb.type = "checkbox"; cb.value = val;
        cb.onchange = function () {
          if (!cb.checked) return;
          mo.querySelectorAll("input").forEach(function (x) { if (x !== cb && (val === "none" || x.value === "none")) x.checked = false; });
        };
        lab.appendChild(cb); lab.appendChild(el("span", null, esc(t))); mo.appendChild(lab);
      });
      card.appendChild(mo); card.appendChild(err); card.appendChild(navRow(true));
      card.onsubmit = function (e) {
        e.preventDefault();
        var v = Array.prototype.map.call(mo.querySelectorAll("input:checked"), function (x) { return x.value; });
        if (!v.length) { err.textContent = C.tickOne.replace("{none}", C.none); err.hidden = false; return; }
        answer(id, v);
      };
      return card;
    }
    function ansText(id) {
      var v = A[id], q = TX.q[id];
      if (q.multi) return v[0] === "none" ? C.none : v.map(function (x) { return q.opts[L.indexOf(x)]; }).join("; ");
      var hit = opts(id).filter(function (p) { return p[1] === v; })[0];
      return hit ? hit[0] : String(v);
    }
    function result() {
      var R = LOGIC.result(A), codes = sortCodes(tool, R.codes), top = TX.r[codes[0]];
      var emergency = top.level === "emergency", card = el("section", "score-result flow-result");
      card.setAttribute("aria-live", "polite");
      card.appendChild(el("h2", null, esc(C.result)));
      if (emergency) card.appendChild(el("div", "urgent", "<strong>" + esc(top.when) + "</strong>"));
      else card.appendChild(el("p", "score-band " + top.level, esc(top.when)));
      codes.forEach(function (c) {
        var r = TX.r[c];
        card.appendChild(el("p", codes.length > 1 ? "flow-add" : null, esc(fill(r.text))));
        if (r.link) card.appendChild(el("p", null, '<a href="' + esc(r.link.href) + '">' + esc(r.link.text) + "</a>"));
      });
      (R.adds || []).forEach(function (c) {
        var r = TX.r[c];
        card.appendChild(el("p", "flow-add", esc(fill(r.text))));
        if (r.link) card.appendChild(el("p", null, '<a href="' + esc(r.link.href) + '">' + esc(r.link.text) + "</a>"));
      });
      if (R.score) {
        var s = C.score.replace("{name}", R.score.name).replace("{total}", R.score.total).replace("{max}", R.score.max)
          .replace(" ({band})", R.score.band ? " (" + R.score.band + ")" : "");
        card.appendChild(el("p", "score-band low", esc(s)));
        card.appendChild(el("p", "q-hint", esc(C.scoreShow)));
      }
      card.appendChild(el("p", "q-hint", "<strong>" + esc(C.notDiagnosis) + "</strong>"));
      var d = el("details", "flow-answers");
      d.appendChild(el("summary", null, esc(C.answers) + " (" + path.length + ")"));
      var ul = el("ul");
      path.forEach(function (id) { ul.appendChild(el("li", null, "<strong>" + esc(TX.q[id].label) + ":</strong> " + esc(ansText(id)))); });
      d.appendChild(ul); card.appendChild(d);
      var tel = box.getAttribute("data-tel"), telShow = box.getAttribute("data-tel-show"), wa = box.getAttribute("data-wa"), book = box.getAttribute("data-book") || "hospitals.html";
      var acts = el("p", "intro-actions");
      if (emergency) {
        acts.innerHTML = '<a class="btn" href="tel:' + esc(CFG.emergencyNumber) + '">' + esc(fill(C.callEmergency)) + "</a>"
          + ' <a class="btn quiet" href="' + esc(book) + '">' + esc(C.book) + "</a>";
      } else {
        var msg = C.waMsg.replace("{check}", TX.name).replace("{when}", top.when + (R.score ? "; " + R.score.name.replace(/ \(proposed\)/, "") + " " + R.score.total + "/" + R.score.max : ""));
        acts.innerHTML = (wa ? '<a class="btn" href="' + esc(wa) + "?text=" + encodeURIComponent(msg) + '">' + esc(C.sendWa) + "</a> " : "")
          + '<a class="btn quiet" href="' + esc(book) + '">' + esc(C.book) + "</a>"
          + (tel ? ' <a class="btn quiet" href="tel:' + esc(tel) + '">' + esc(C.call) + " " + esc(telShow) + "</a>" : "");
      }
      card.appendChild(acts);
      card.appendChild(el("p", "q-hint", esc(TX.footer)));
      card.appendChild(el("p", "q-hint", esc(C.copyright)));
      var n = el("div", "flow-nav");
      var b = el("button", "btn quiet", esc(C.back)); b.type = "button"; b.onclick = back; n.appendChild(b);
      var rs = el("button", "btn quiet", esc(C.again)); rs.type = "button"; rs.onclick = restart; n.appendChild(rs);
      card.appendChild(n);
      if (!sent && window.gtag) { sent = true; window.gtag("event", "check_complete", { check_name: "mera_" + tool }); }
      return card;
    }
    function show() {
      box.innerHTML = "";
      var id = LOGIC.next(A), node = id ? question(id) : result();
      box.appendChild(node);
      var f = node.querySelector(".flow-q, h2");
      if (f && path.length) { f.tabIndex = -1; f.focus({ preventScroll: true }); box.scrollIntoView({ behavior: "smooth", block: "start" }); }
    }
    /* test replay: #t=<answers as JSON> jumps straight to that path (used by the test page) */
    if (location.hash.indexOf("#t=") === 0) {
      try {
        var given = JSON.parse(decodeURIComponent(location.hash.slice(3))), id;
        while ((id = LOGIC.next(A)) && given.hasOwnProperty(id)) { A[id] = given[id]; path.push(id); }
      } catch (e) { A = {}; path = []; }
    }
    window.MERA_CHECK_STATE = { answers: function () { return A; }, next: function () { return LOGIC.next(A); }, result: function () { return LOGIC.result(A); } };
    show();
  }
})();
