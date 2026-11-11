/* Cloudy Prompt Library — search, filters, copy (no dependencies) */
(function () {
  'use strict';
  var ROOT = document.documentElement.getAttribute('data-root') || './';
  var DATA = null;
  function $(s, el) { return (el || document).querySelector(s); }
  function $$(s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); }

  function load() {
    if (DATA) return Promise.resolve(DATA);
    return fetch(ROOT + 'data/prompts.json').then(function (r) { return r.json(); }).then(function (d) { DATA = d; return d; });
  }
  function byId(id) {
    if (!DATA) return null;
    var list = DATA.prompts || [];
    for (var i = 0; i < list.length; i++) if (list[i].id === id) return list[i];
    return null;
  }

  function copyText(text, btn) {
    function ok() {
      if (!btn) return;
      var prev = btn.getAttribute('data-label') || btn.textContent;
      btn.setAttribute('data-label', prev);
      btn.textContent = 'Copied';
      btn.classList.add('copied');
      setTimeout(function () { btn.textContent = prev; btn.classList.remove('copied'); }, 1600);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(ok).catch(function () { fallback(text, ok); });
    } else {
      fallback(text, ok);
    }
  }
  function fallback(text, ok) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed';
    ta.style.left = '-9999px';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); ok(); } catch (err) {}
    document.body.removeChild(ta);
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-copy-id], [data-copy-target]');
    if (!btn) return;
    e.preventDefault();
    var sel = btn.getAttribute('data-copy-target');
    if (sel) {
      var el = document.querySelector(sel);
      if (el) copyText(el.textContent.replace(/^\n+/, '').replace(/\n+$/, ''), btn);
      return;
    }
    var id = btn.getAttribute('data-copy-id');
    if (id) {
      load().then(function () {
        var p = byId(id);
        if (p) copyText(p.body, btn);
      });
    }
  });

  function applyFilters() {
    var grid = $('#dir-grid');
    if (!grid) return;
    load().then(function (d) {
      var q = (($('#f-q') && $('#f-q').value) || '').trim().toLowerCase();
      var cat = (($('#f-cat') && $('#f-cat').value) || '');
      var tool = (($('#f-tool') && $('#f-tool').value) || '').toLowerCase();
      var n = 0;
      (d.prompts || []).forEach(function (p) {
        var hay = (p.title + ' ' + p.summary + ' ' + (p.tags || []).join(' ') + ' ' + (p.worksWith || []).join(' ') + ' ' + (p.body || '')).toLowerCase();
        var ok = true;
        if (cat && p.category !== cat) ok = false;
        if (tool) {
          var tools = (p.worksWith || []).map(function (w) { return w.toLowerCase(); });
          if (tools.indexOf(tool) < 0) ok = false;
        }
        if (q && hay.indexOf(q) < 0) ok = false;
        var el = grid.querySelector('[data-id="' + p.id + '"]');
        if (el) el.style.display = ok ? '' : 'none';
        if (ok) n++;
      });
      var count = $('#dir-count');
      if (count) count.textContent = n + ' prompt' + (n === 1 ? '' : 's');
      var empty = $('#dir-empty');
      if (empty) empty.hidden = n > 0;
    });
  }

  function initDirectory() {
    if (!$('#dir-grid')) return;
    var params = new URLSearchParams(location.search);
    if ($('#f-q') && params.get('q')) $('#f-q').value = params.get('q');
    if ($('#f-cat') && params.get('cat')) $('#f-cat').value = params.get('cat');
    if ($('#f-tool') && params.get('tool')) $('#f-tool').value = params.get('tool');
    ['f-q', 'f-cat', 'f-tool'].forEach(function (id) {
      var el = $('#' + id);
      if (!el) return;
      el.addEventListener('input', applyFilters);
      el.addEventListener('change', applyFilters);
    });
    applyFilters();
  }

  function initHomeSearch() {
    var form = $('#home-search');
    if (!form) return;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var q = (($('#home-q') && $('#home-q').value) || '').trim();
      var url = form.getAttribute('data-action') || (ROOT + 'prompts/');
      if (q) url += (url.indexOf('?') >= 0 ? '&' : '?') + 'q=' + encodeURIComponent(q);
      location.href = url;
    });
  }

  initDirectory();
  initHomeSearch();
})();
