/* asset.dev — navegação dos slides planos e autoteste. Nada é desenhado aqui: o HTML já vem pronto.
   Avançar: → espaço PageDown Enter ou clique. Voltar: ← PageUp Backspace. Home/End. G: modo gravação; Esc: sai dele. */
(function () {
  "use strict";
  var stage = document.getElementById("stage");
  var slides = Array.prototype.slice.call(document.querySelectorAll(".slide"));
  var cur = 0;
  var params = new URLSearchParams(location.search);

  function fit() {
    var s = Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
    stage.style.transform = "translate(-50%, -50%) scale(" + s + ")";
    return s;
  }
  function show(i) {
    cur = Math.max(0, Math.min(slides.length - 1, i));
    slides.forEach(function (el, k) { el.classList.toggle("active", k === cur); });
    if (history.replaceState) history.replaceState(null, "", location.pathname + location.search + "#p" + (cur + 1));
  }
  function fromHash() {
    var m = /^#p(\d+)$/.exec(location.hash);
    return m ? parseInt(m[1], 10) - 1 : 0;
  }
  function recording(on) { document.body.classList.toggle("recording", on); }

  document.addEventListener("keydown", function (ev) {
    var k = ev.key;
    if (k === "ArrowRight" || k === " " || k === "PageDown" || k === "Enter") { show(cur + 1); ev.preventDefault(); }
    else if (k === "ArrowLeft" || k === "PageUp" || k === "Backspace") { show(cur - 1); ev.preventDefault(); }
    else if (k === "Home") show(0);
    else if (k === "End") show(slides.length - 1);
    else if (k === "g" || k === "G") recording(!document.body.classList.contains("recording"));
    else if (k === "Escape") recording(false);
  });
  document.addEventListener("click", function (ev) { if (ev.button === 0) show(cur + 1); });
  window.addEventListener("resize", fit);
  window.addEventListener("hashchange", function () { show(fromHash()); });

  fit();
  show(fromHash());
  if (params.get("rec") === "1") recording(true);
  if (params.get("selftest") === "1") selftest();

  /* ---------------- autoteste (navegador headless; resultado num <pre>) ---------------- */
  function selftest() {
    var checks = [];
    function check(name, pass, detail) { checks.push({ name: name, pass: !!pass, detail: detail || "" }); }
    function r(el) { return el.getBoundingClientRect(); }
    function inter(a, b) { return !(a.right <= b.left + 0.5 || b.right <= a.left + 0.5 || a.bottom <= b.top + 0.5 || b.bottom <= a.top + 0.5); }
    var done = function () {
      var scale = fit();
      check("doze slides", slides.length === 12, slides.length);
      check("sem controles clicáveis", document.querySelectorAll("button,input,select,textarea,a,[role=button],[tabindex],nav,dialog").length === 0);
      check("fontes do manual carregadas", document.fonts.check('700 54px "Space Grotesk"') && document.fonts.check('400 20px "Inter"') && document.fonts.check('500 20px "JetBrains Mono"'));
      var st = r(stage);
      check("palco cabe na janela", st.left >= -1 && st.top >= -1 && st.right <= window.innerWidth + 1 && st.bottom <= window.innerHeight + 1,
            [Math.round(st.width), Math.round(st.height), window.innerWidth, window.innerHeight].join("x"));
      slides.forEach(function (sl, i) {
        show(i);
        var id = sl.getAttribute("data-page");
        check(id + " visível sozinho", slides.filter(function (s) { return getComputedStyle(s).display !== "none"; }).length === 1 && sl.classList.contains("active"));
        var box = r(sl), out = [];
        Array.prototype.forEach.call(sl.querySelectorAll("*"), function (el) {
          var b = r(el);
          if (b.width === 0 && b.height === 0) return;
          var cn = typeof el.className === "string" ? el.className : (el.className && el.className.baseVal) || "";
          if (b.left < box.left - 1 || b.right > box.right + 1 || b.top < box.top - 1 || b.bottom > box.bottom + 1) out.push(el.tagName + "." + cn);
        });
        check(id + " nada fora do slide", out.length === 0, out.slice(0, 4).join(", "));
        var order = [".kicker", ".title", ".subtitle", ".body", ".sources", ".foot"].map(function (q) { return sl.querySelector(q); }).filter(Boolean);
        var overlap = [];
        for (var k = 1; k < order.length; k++) if (r(order[k - 1]).bottom > r(order[k]).top + 0.5) overlap.push(order[k - 1].className + "/" + order[k].className);
        check(id + " título, subtítulo, corpo e rodapé sem sobreposição", overlap.length === 0, overlap.join(", "));
        var body = sl.querySelector(".body"), spill = [];
        if (body) {
          var bb = r(body);
          Array.prototype.forEach.call(body.querySelectorAll("*"), function (el) {
            var b = r(el);
            if (b.width && b.height && (b.bottom > bb.bottom + 1 || b.right > bb.right + 1)) spill.push(el.tagName);
          });
          Array.prototype.forEach.call(body.querySelectorAll(".card, td, p, h3, h4, li"), function (el) {
            if (el.scrollHeight > el.clientHeight + 2 || el.scrollWidth > el.clientWidth + 2) spill.push("transborda:" + el.tagName);
          });
        }
        check(id + " corpo contém o conteúdo", spill.length === 0, spill.slice(0, 4).join(", "));
        var labels = Array.prototype.slice.call(sl.querySelectorAll("svg text")), hits = [];
        for (var a = 0; a < labels.length; a++) for (var c = a + 1; c < labels.length; c++)
          if (inter(r(labels[a]), r(labels[c]))) hits.push(labels[a].textContent + "×" + labels[c].textContent);
        check(id + " rótulos dos gráficos sem colisão", hits.length === 0, hits.slice(0, 4).join(", "));
      });
      show(0);
      show(1); check("seta avança", (function () { document.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowRight" })); return cur === 2; })());
      document.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowLeft" })); check("seta volta", cur === 1);
      document.dispatchEvent(new KeyboardEvent("keydown", { key: "End" })); check("End vai ao último", cur === 11);
      document.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowRight" })); check("não passa do último", cur === 11);
      document.dispatchEvent(new KeyboardEvent("keydown", { key: "Home" })); check("Home volta ao primeiro", cur === 0);
      check("endereço da página", location.hash === "#p1");
      show(4);
      document.dispatchEvent(new KeyboardEvent("keydown", { key: "g" }));
      var cam = r(document.getElementById("camera")), sb = r(slides[4]);
      check("modo gravação reduz o slide", document.body.classList.contains("recording") && Math.abs(sb.width / scale - 1920 * 0.84) < 2);
      check("modo gravação libera a área da câmera", !inter(sb, cam));
      document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape" }));
      check("Esc sai do modo gravação", !document.body.classList.contains("recording"));
      show(0);
      var failed = checks.filter(function (x) { return !x.pass; }).length;
      var pre = document.createElement("pre");
      pre.id = "selftest-result";
      pre.style.display = "none";
      pre.textContent = JSON.stringify({ status: failed ? "failed" : "passed", failed: failed, checks: checks });
      document.body.appendChild(pre);
    };
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(done); else done();
  }
})();
