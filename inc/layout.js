/**
 * Load shared header and footer into #layout-header and #layout-footer.
 * Sets current menu item based on location.pathname.
 * Script must be loaded from inc/layout.js (path is derived from script src).
 */
(function() {
	var script = document.currentScript;
	if (!script) return;
	var base = script.src.replace(/\/[^/]*$/, '');
	var headerEl = document.getElementById('layout-header');
	var footerEl = document.getElementById('layout-footer');

	function norm(p) {
		p = (p || '').toLowerCase().replace(/\/?index\.html$/i, '') || '/';
		return p === '' ? '/' : p;
	}

	function setCurrentNav(container) {
		if (!container) return;
		var path = norm(location.pathname);
		container.querySelectorAll('.menu a[href]').forEach(function(a) {
			var href = a.getAttribute('href');
			if (href.indexOf('://') !== -1) return;
			var linkPath = norm(href);
			var isCurrent = (path === linkPath) || (path === '/' && (linkPath === '/' || linkPath === ''));
			// dataset-pages.html?name=xxx still counts as "datasets" section
			if (!isCurrent && path.indexOf('dataset-pages.html') !== -1 && linkPath.indexOf('datasets') !== -1) isCurrent = true;
			var li = a.closest('li');
			if (li) {
				if (isCurrent) {
					li.classList.add('current-menu-item');
					a.setAttribute('aria-current', 'page');
				} else {
					li.classList.remove('current-menu-item');
					a.removeAttribute('aria-current');
				}
			}
		});
	}

	function updateTopbarDateTime() {
		var dateEl = document.getElementById('bloglo-date');
		var timeEl = document.getElementById('bloglo-time');
		if (!dateEl || !timeEl) return;
		var d = new Date();
		var pad = function(n) { return (n < 10 ? '0' : '') + n; };
		dateEl.textContent = d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
		timeEl.textContent = pad(d.getHours()) + ':' + pad(d.getMinutes()) + ':' + pad(d.getSeconds());
	}

	function inject(html, into) {
		if (!into) return;
		var wrap = document.createElement('div');
		wrap.innerHTML = html.trim();
		while (wrap.firstChild) into.appendChild(wrap.firstChild);
		setCurrentNav(into);
		if (into === headerEl) {
			updateTopbarDateTime();
			setInterval(updateTopbarDateTime, 1000);
		}
	}

	function load() {
		Promise.all([
			headerEl ? fetch(base + '/header.html').then(function(r) { return r.ok ? r.text() : Promise.reject(); }) : Promise.resolve(''),
			footerEl ? fetch(base + '/footer.html').then(function(r) { return r.ok ? r.text() : Promise.reject(); }) : Promise.resolve('')
		]).then(function(results) {
			if (headerEl && results[0]) inject(results[0], headerEl);
			if (footerEl && results[1]) inject(results[1], footerEl);
		}).catch(function() {
			if (headerEl) headerEl.innerHTML = '<p class="layout-load-error">Failed to load header.</p>';
			if (footerEl) footerEl.innerHTML = '<p class="layout-load-error">Failed to load footer.</p>';
		});
	}

	if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load);
	else load();
})();
