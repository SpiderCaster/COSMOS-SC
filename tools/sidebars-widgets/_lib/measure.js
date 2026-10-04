/* Test-only measurement script. Runs in headless Chrome. Not shipped with any item. */
(function () {
  function parse(c) {
    var m = /rgba?\(([^)]+)\)/.exec(c || "");
    if (!m) return null;
    var p = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number);
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
  }
  function blend(t, b) {
    var a = t.a + b.a * (1 - t.a);
    if (a === 0) return { r: 0, g: 0, b: 0, a: 0 };
    return {
      r: (t.r * t.a + b.r * b.a * (1 - t.a)) / a,
      g: (t.g * t.a + b.g * b.a * (1 - t.a)) / a,
      b: (t.b * t.a + b.b * b.a * (1 - t.a)) / a, a: a };
  }
  function lin(v) { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }
  function lum(c) { return 0.2126 * lin(c.r) + 0.7152 * lin(c.g) + 0.0722 * lin(c.b); }
  function ratio(a, b) { var x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); }
  function bgOf(el) {
    var layers = [];
    for (var e = el; e; e = e.parentElement) {
      var c = parse(getComputedStyle(e).backgroundColor);
      if (c && c.a > 0) { layers.push(c); if (c.a >= 1) break; }
    }
    var out = { r: 255, g: 255, b: 255, a: 1 };
    if (layers.length && layers[layers.length - 1].a >= 1) out = layers.pop();
    while (layers.length) out = blend(layers.pop(), out);
    return out;
  }
  function visible(el) {
    if (el.checkVisibility) { if (!el.checkVisibility({ visibilityProperty: true })) return false; }
    else if (!el.getClientRects().length) return false;
    var r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  }
  function desc(el) {
    var s = el.tagName.toLowerCase();
    if (el.id) s += "#" + el.id;
    if (el.className && typeof el.className === "string") s += "." + el.className.trim().split(/\s+/).slice(0, 2).join(".");
    return s;
  }
  window.scMeasure = function (scope) {
    var out = { overflow: [], smallText: [], lowContrast: [], smallTargets: [], counts: {}, minContrast: 99 };
    var vw = window.innerWidth;
    out.docScrollWidth = document.documentElement.scrollWidth;
    out.viewport = vw;
    var all = scope.querySelectorAll("*");
    var texts = 0, targets = 0;
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      if (/^(SCRIPT|STYLE|TEMPLATE|NOSCRIPT)$/.test(el.tagName)) continue;
      if (!visible(el)) continue;
      var r = el.getBoundingClientRect();
      if (r.right > vw + 1 && !el.closest(".sc-scroll-x")) out.overflow.push(desc(el) + " right=" + Math.round(r.right));
      var own = "";
      for (var n = el.firstChild; n; n = n.nextSibling) if (n.nodeType === 3) own += n.nodeValue;
      own = own.trim();
      if (own && !el.closest("[data-sc-test-skip]")) {
        texts++;
        var cs = getComputedStyle(el);
        var fs = parseFloat(cs.fontSize);
        var big = /^(P|BUTTON|INPUT|TEXTAREA|SELECT)$/.test(el.tagName) || el.classList.contains("sc-body");
        var minpx = big ? 18 : 16;
        if (fs + 0.01 < minpx) out.smallText.push(desc(el) + " " + fs + "px<" + minpx);
        var fg = parse(cs.color), bg = bgOf(el);
        if (fg) {
          if (fg.a < 1) fg = blend(fg, bg);
          var cr = ratio(fg, bg);
          var large = fs >= 24 || (fs >= 18.66 && parseInt(cs.fontWeight, 10) >= 700);
          if (cr < out.minContrast) out.minContrast = Math.round(cr * 100) / 100;
          if (cr + 0.001 < (large ? 3 : 4.5)) out.lowContrast.push(desc(el) + " " + cr.toFixed(2));
        }
      }
      var isT = el.matches("a[href],button,select,textarea,summary,[role=button],input:not([type=hidden]):not([type=checkbox]):not([type=radio])");
      var isCk = el.matches("input[type=checkbox],input[type=radio]");
      if ((isT || isCk) && !el.closest("[hidden],[aria-hidden='true'],.sc-inline,[data-sc-test-skip]")) {
        var box = r;
        if (isCk) { var lb = el.closest("label"); if (lb) box = lb.getBoundingClientRect(); }
        targets++;
        if (box.height + 0.5 < 44 || box.width + 0.5 < 44) out.smallTargets.push(desc(el) + " " + Math.round(box.width) + "x" + Math.round(box.height));
      }
    }
    out.counts = { texts: texts, targets: targets };
    return out;
  };
})();
