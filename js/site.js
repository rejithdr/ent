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
