// Clickable window mockups: inside a .mock figure, a button with data-tab="x" or data-go="x" shows the page data-page="x";
// data-back returns to the page shown before. Tabs that name the shown page are highlighted.
(function () {
  function show(fig, id) {
    var pages = fig.querySelectorAll('.mpage'), found = false;
    pages.forEach(function (p) { var on = p.getAttribute('data-page') === id; p.hidden = !on; if (on) found = true; });
    if (!found) return false;
    fig.querySelectorAll('[data-tab]').forEach(function (t) {
      var on = t.getAttribute('data-tab') === id || (t.getAttribute('data-also') || '').split(' ').indexOf(id) >= 0;
      t.classList.toggle('on', on); t.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    return true;
  }
  function init(fig) {
    var hist = [];
    var first = fig.querySelector('.mpage:not([hidden])') || fig.querySelector('.mpage');
    if (first) show(fig, first.getAttribute('data-page'));
    fig.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b || !fig.contains(b)) return;
      var cur = (fig.querySelector('.mpage:not([hidden])') || {}).getAttribute;
      var curId = cur ? fig.querySelector('.mpage:not([hidden])').getAttribute('data-page') : null;
      if (b.hasAttribute('data-back')) { if (hist.length) show(fig, hist.pop()); e.preventDefault(); return; }
      var id = b.getAttribute('data-tab') || b.getAttribute('data-go');
      if (id && id !== curId && show(fig, id)) { if (b.hasAttribute('data-go') && curId) hist.push(curId); else hist = []; e.preventDefault(); }
    });
  }
  function boot() { document.querySelectorAll('figure.mock').forEach(init); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
// redesign: chip filters (trees page), the "/" search shortcut, and the rail closed by default on phones
(function () {
  document.querySelectorAll('.chips[data-filter]').forEach(function (bar) {
    bar.addEventListener('click', function (e) {
      var b = e.target.closest('.chip'); if (!b) return;
      bar.querySelectorAll('.chip').forEach(function (c) { c.classList.toggle('on', c === b); c.setAttribute('aria-pressed', c === b ? 'true' : 'false'); });
      var k = b.getAttribute('data-k');
      document.querySelectorAll('[data-group]').forEach(function (g) { g.hidden = k !== 'all' && g.getAttribute('data-group') !== k; });
    });
  });
  document.addEventListener('keydown', function (e) {
    var t = document.activeElement && document.activeElement.tagName;
    if (e.key === '/' && t !== 'INPUT' && t !== 'TEXTAREA') { var q = document.getElementById('q'); if (q) { e.preventDefault(); q.focus(); } }
  });
  var rb = document.querySelector('.railbox');
  if (rb && window.matchMedia && window.matchMedia('(max-width: 900px)').matches) rb.open = false;
  var on = document.querySelector('.rail a.on'); if (on && rb && rb.open) { try { on.scrollIntoView({ block: 'center' }); window.scrollTo(0, 0); } catch (x) {} }
})();
