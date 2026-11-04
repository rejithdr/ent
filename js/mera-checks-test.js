/* Review page for the MERA Dizziness, Blocked Nose and Throat & Voice checks.
   Walks every answer path and lists each distinct result once, with the answers that reach it
   and a link that opens the check at that result. */
(function () {
  "use strict";
  var M = window.MERA_CHECKS, out = document.getElementById("mera-test");
  if (!M || !out) return;
  var PAGES = { dizzy: "mera-dizziness-check.html", nose: "mera-nose-check.html", throat: "mera-throat-check.html" };
  var L = "abcdefgh";
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  /* score presets: the whole score is filled at once, at its first question */
  var PRESETS = {
    nose: [["all 0", 0], ["all 1 (total 5)", 1], ["all 3 (total 15)", 3]],
    throat: [["all 0", 0], ["lump only = 1", "lump"], ["all 1 (total 6)", 1]]
  };

  function choices(tool, id) {
    var q = M.text[tool].q[id];
    if (q.multi) return [["none"]].concat(q.opts.map(function (_, i) { return [L[i]]; }));
    if (q.yn) return ["y", "n"];
    return q.opts.map(function (_, i) { return L[i]; });
  }
  function label(tool, id, v) {
    var q = M.text[tool].q[id], C = M.text.common;
    if (q.multi) return v[0] === "none" ? C.none : q.opts[L.indexOf(v[0])];
    if (q.yn) return v === "y" ? C.yes : C.no;
    if (q.score) return String(v);
    return q.opts[L.indexOf(v)];
  }

  /* every path is walked; each result (and each extra note) is listed once, with its simplest example */
  function explore(tool) {
    var logic = M.tools[tool], best = {}, combos = 0;
    function consider(key, A, R, codes) {
      var size = codes.length + (R.adds ? R.adds.length : 0) + Object.keys(A).length / 100;
      if (!best[key] || size < best[key].size) best[key] = { A: JSON.parse(JSON.stringify(A)), R: R, codes: codes, size: size, key: key };
    }
    (function walk(A) {
      var id = logic.next(A);
      if (!id) {
        combos++;
        var R = logic.result(A), codes = M.sortCodes(tool, R.codes);
        codes.forEach(function (c) { consider(c, A, R, codes); });
        (R.adds || []).forEach(function (c) { consider(c, A, R, codes); });
        if (R.score && R.score.band) consider("score " + R.score.band, A, R, codes);
        return;
      }
      var q = M.text[tool].q[id];
      if (q.score) {
        PRESETS[tool].forEach(function (p) {
          var B = JSON.parse(JSON.stringify(A));
          logic.scoreIds.forEach(function (k) { B[k] = p[1] === "lump" ? (k === "t2" ? 1 : 0) : p[1]; });
          walk(B);
        });
        return;
      }
      choices(tool, id).forEach(function (v) { var B = JSON.parse(JSON.stringify(A)); B[id] = v; walk(B); });
    })({});
    var keys = Object.keys(M.text[tool].r).filter(function (k) { return best[k]; })
      .concat(Object.keys(best).filter(function (k) { return k.indexOf("score ") === 0; }));
    var rows = keys.map(function (k) { return best[k]; });
    rows.combos = combos;
    return rows;
  }

  var html = "";
  ["dizzy", "nose", "throat"].forEach(function (tool) {
    var TX = M.text[tool], rows = explore(tool), logic = M.tools[tool];
    html += '<h2 id="' + tool + '">' + esc(TX.name) + "</h2><p>" + rows.length + " results and notes, from " + rows.combos + " answer combinations.</p>";
    html += '<p><a href="' + PAGES[tool] + '">Open the check</a></p><ol class="test-list">';
    rows.forEach(function (row) {
      var steps = logic.order.filter(function (k) { return row.A[k] != null && !(TX.q[k].score); })
        .map(function (k) { return "<li><strong>" + esc(TX.q[k].label) + ":</strong> " + esc(label(tool, k, row.A[k])) + "</li>"; }).join("");
      if (row.R.score) steps += "<li><strong>" + esc(row.R.score.name) + ":</strong> " + row.R.score.total + "/" + row.R.score.max + (row.R.score.band ? " (" + row.R.score.band + ")" : "") + "</li>";
      var res = '<span class="test-key">' + esc(row.key) + "</span> " + row.codes.map(function (c) { return "<strong>" + c + "</strong> " + esc(TX.r[c].when); }).join("; ");
      if (row.R.adds && row.R.adds.length) res += "; plus " + row.R.adds.join(", ");
      html += "<li><p>" + res + ' <a href="' + PAGES[tool] + "#t=" + encodeURIComponent(JSON.stringify(row.A)) + '">open this result</a></p><ul>' + steps + "</ul></li>";
    });
    html += "</ol>";
  });
  out.innerHTML = html;
})();
