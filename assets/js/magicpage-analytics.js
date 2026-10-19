jQuery(document).ready(function ($) {
	var config = typeof magicpageAnalytics !== 'undefined' ? magicpageAnalytics : (typeof MagicPageAnalytics !== 'undefined' ? MagicPageAnalytics : null);
	if (!config) {
		console.error('Magic Page Analytics: config not found.');
		return;
	}

	var perPage = parseInt(config.per_page, 10) || 25;
	var i18n = config.i18n || {};
	var chartObjects = {};
	var requestId = 0;

	var state = {
		locationsAll: [],
		topPagesAll: [],
		locPage: 1,
		pagesPage: 1,
		range: { range: '30', start: '', end: '' }
	};

	var deviceColors = {
		desktop: 'rgba(59, 130, 246, 0.85)',
		mobile: 'rgba(34, 197, 94, 0.85)',
		tablet: 'rgba(245, 158, 11, 0.85)',
		unknown: 'rgba(148, 163, 184, 0.85)'
	};

	function esc(s) {
		if (s == null || s === '') {
			return '—';
		}
		return String(s)
			.replace(/&/g, '&amp;')
			.replace(/</g, '&lt;')
			.replace(/>/g, '&gt;')
			.replace(/"/g, '&quot;')
			.replace(/'/g, '&#039;');
	}

	function pageCount(total, size) {
		return Math.max(1, Math.ceil(total / size));
	}

	function sprintfPageOf(cur, tot) {
		var t = i18n.page_of || 'Page %1$s of %2$s';
		return t.replace('%1$s', String(cur)).replace('%2$s', String(tot));
	}

	function bindPager($wrap, page, totalItems, onPage) {
		if (!$wrap.length) {
			return;
		}
		var totalPages = pageCount(totalItems, perPage);
		if (totalItems === 0 || totalPages <= 1) {
			$wrap.attr('hidden', true).empty();
			return;
		}
		$wrap.removeAttr('hidden');
		var prevDis = page <= 1 ? ' disabled' : '';
		var nextDis = page >= totalPages ? ' disabled' : '';
		var html = '<div class="mpe-pager-inner">' +
			'<button type="button" class="button mpe-pager-prev"' + prevDis + '>' + esc(i18n.prev || '« Previous') + '</button>' +
			'<span class="mpe-pager-status">' + esc(sprintfPageOf(page, totalPages)) + '</span>' +
			'<button type="button" class="button mpe-pager-next"' + nextDis + '>' + esc(i18n.next || 'Next »') + '</button>' +
			'</div>';
		$wrap.html(html);
		$wrap.find('.mpe-pager-prev').on('click', function () {
			if (page > 1) {
				onPage(page - 1);
			}
		});
		$wrap.find('.mpe-pager-next').on('click', function () {
			if (page < totalPages) {
				onPage(page + 1);
			}
		});
	}

	function renderLocationsSlice() {
		var locationsTbody = document.getElementById('locations-tbody');
		var $pager = $('#mpe-locations-pager');
		if (!locationsTbody) {
			return;
		}

		var all = state.locationsAll;
		if (!all.length) {
			locationsTbody.innerHTML = '<tr><td colspan="6">' + esc(i18n.no_locations) + '</td></tr>';
			$pager.attr('hidden', true).empty();
			return;
		}

		var start = (state.locPage - 1) * perPage;
		var slice = all.slice(start, start + perPage);
		locationsTbody.innerHTML = slice.map(function (loc) {
			return '<tr><td>' + esc(loc.label) + '</td><td>' + esc(loc.region) + '</td><td>' + (loc.pages || 0) + '</td><td>' + (loc.visits || 0).toLocaleString() + '</td><td>' + (loc.clicks || 0).toLocaleString() + '</td><td>' + (loc.ctr != null ? loc.ctr + '%' : '—') + '</td></tr>';
		}).join('');

		bindPager($pager, state.locPage, all.length, function (p) {
			state.locPage = p;
			renderLocationsSlice();
		});
	}

	function renderTopPagesSlice() {
		var topPagesTbody = document.getElementById('top-pages-tbody');
		var $pager = $('#mpe-top-pages-pager');
		if (!topPagesTbody) {
			return;
		}

		var all = state.topPagesAll;
		if (!all.length) {
			topPagesTbody.innerHTML = '<tr><td colspan="4">' + esc(i18n.no_pages) + '</td></tr>';
			$pager.attr('hidden', true).empty();
			return;
		}

		var start = (state.pagesPage - 1) * perPage;
		var slice = all.slice(start, start + perPage);
		topPagesTbody.innerHTML = slice.map(function (p) {
			return '<tr><td>' + esc(p.title) + '</td><td>' + (p.count || 0).toLocaleString() + '</td><td>' + (p.clicks || 0).toLocaleString() + '</td><td>' + (p.ctr != null ? p.ctr + '%' : '—') + '</td></tr>';
		}).join('');

		bindPager($pager, state.pagesPage, all.length, function (p) {
			state.pagesPage = p;
			renderTopPagesSlice();
		});
	}

	function renderNotFound(paths) {
		var tbody = document.getElementById('not-found-tbody');
		if (!tbody) {
			return;
		}
		if (!paths || !paths.length) {
			tbody.innerHTML = '<tr><td colspan="3">' + esc(i18n.no_404_paths) + '</td></tr>';
			return;
		}
		tbody.innerHTML = paths.map(function (row) {
			return '<tr><td>' + esc(row.path) + '</td><td>' + (row.count || 0).toLocaleString() + '</td><td>' + esc(row.last_display || row.last || '') + '</td></tr>';
		}).join('');
	}

	function setCanvas(id, message) {
		var canvas = document.getElementById(id);
		if (!canvas) {
			return null;
		}
		if (chartObjects[id]) {
			chartObjects[id].destroy();
			delete chartObjects[id];
		}
		var note = canvas.parentNode.querySelector('.mpe-no-data');
		if (message) {
			canvas.style.display = 'none';
			if (!note) {
				note = document.createElement('p');
				note.className = 'mpe-no-data';
				canvas.parentNode.appendChild(note);
			}
			note.hidden = false;
			note.textContent = message;
			return null;
		}
		canvas.style.display = '';
		if (note) {
			note.hidden = true;
		}
		return canvas;
	}

	function drawChart(id, message, config) {
		var canvas = setCanvas(id, message);
		if (!canvas) {
			return;
		}
		chartObjects[id] = new Chart(canvas, config);
	}

	function seriesHasValues(series) {
		return Object.keys(series || {}).some(function (key) {
			return (series[key] || 0) > 0;
		});
	}

	function rangeFromUi() {
		return {
			range: $('#mpe-range').val() || '30',
			start: $('#mpe-range-start').val() || '',
			end: $('#mpe-range-end').val() || ''
		};
	}

	function rangeIsValid(next) {
		if (next.range !== 'custom') {
			return true;
		}
		return !!(next.start && next.end && next.start <= next.end);
	}

	function exportHref(format, next) {
		var url = config.export_url || '';
		url += '&format=' + encodeURIComponent(format);
		url += '&range=' + encodeURIComponent(next.range);
		if (next.range === 'custom') {
			url += '&start=' + encodeURIComponent(next.start);
			url += '&end=' + encodeURIComponent(next.end);
		}
		return url;
	}

	function setLoading(isLoading) {
		$('#mpe-range-apply').prop('disabled', isLoading);
		var status = document.getElementById('mpe-range-status');
		if (status && isLoading) {
			status.textContent = i18n.loading || 'Loading…';
		}
	}

	function showFailure() {
		var failed = i18n.failed || 'Failed to load data.';
		var top = document.getElementById('top-pages-tbody');
		if (top) {
			top.innerHTML = '<tr><td colspan="4">' + esc(failed) + '</td></tr>';
		}
		var locations = document.getElementById('locations-tbody');
		if (locations) {
			locations.innerHTML = '<tr><td colspan="6">' + esc(failed) + '</td></tr>';
		}
		var missing = document.getElementById('not-found-tbody');
		if (missing) {
			missing.innerHTML = '<tr><td colspan="3">' + esc(failed) + '</td></tr>';
		}
	}

	function renderPayload(data) {
		var s = data.summary || {};
		var locEl = document.getElementById('mpe-stat-locations');
		var visEl = document.getElementById('mpe-stat-visits');
		var clkEl = document.getElementById('mpe-stat-clicks');
		var ctrEl = document.getElementById('mpe-stat-ctr');
		var nfEl = document.getElementById('mpe-stat-404');
		if (locEl) {
			locEl.textContent = s.total_locations != null ? s.total_locations : '—';
		}
		if (visEl) {
			visEl.textContent = s.total_visits != null ? s.total_visits.toLocaleString() : '—';
		}
		if (clkEl) {
			clkEl.textContent = s.total_clicks != null ? s.total_clicks.toLocaleString() : '—';
		}
		if (ctrEl) {
			ctrEl.textContent = s.overall_ctr != null ? s.overall_ctr + '%' : '—';
		}
		if (nfEl) {
			nfEl.textContent = s.not_found != null ? s.not_found.toLocaleString() : '—';
		}

		var status = document.getElementById('mpe-range-status');
		if (status) {
			status.textContent = (data.range && data.range.label) ? data.range.label : (s.range_label || '');
		}

		state.locationsAll = data.locations_all || data.top_locations || [];
		state.topPagesAll = data.top_pages_all || data.top_pages || [];
		state.locPage = 1;
		state.pagesPage = 1;
		renderLocationsSlice();
		renderTopPagesSlice();
		renderNotFound(data.not_found_paths || []);

		var visitsOverTime = data.visits_over_time || {};
		var votLabels = Object.keys(visitsOverTime);
		var votData = votLabels.map(function (key) {
			return visitsOverTime[key];
		});
		drawChart(
			'chart-page-visits-over-time',
			votLabels.length ? '' : (i18n.no_visits_range || 'No visit data for this date range yet.'),
			{
				type: 'line',
				data: {
					labels: votLabels,
					datasets: [{
						label: i18n.visits || 'Visits',
						data: votData,
						borderColor: 'rgb(59, 130, 246)',
						backgroundColor: 'rgba(59, 130, 246, 0.1)',
						fill: true,
						tension: 0.2
					}]
				},
				options: {
					responsive: true,
					maintainAspectRatio: false,
					plugins: { legend: { display: false } },
					scales: {
						x: { ticks: { maxRotation: 45 } },
						y: { beginAtZero: true }
					}
				}
			}
		);

		var locations = state.locationsAll.slice();
		var topLocations = locations.slice(0, 10);
		drawChart(
			'chart-locations-visits',
			topLocations.length ? '' : (i18n.no_data || 'No data yet.'),
			{
				type: 'bar',
				data: {
					labels: topLocations.map(function (l) { return l.label; }),
					datasets: [{
						label: i18n.visits || 'Visits',
						data: topLocations.map(function (l) { return l.visits; }),
						backgroundColor: 'rgba(34, 197, 94, 0.7)',
						borderColor: 'rgb(34, 197, 94)',
						borderWidth: 1
					}]
				},
				options: {
					indexAxis: 'y',
					responsive: true,
					maintainAspectRatio: false,
					plugins: { legend: { display: false } },
					scales: {
						x: { beginAtZero: true },
						y: { ticks: { maxRotation: 0 } }
					}
				}
			}
		);

		drawChart(
			'chart-locations-clicks',
			topLocations.length ? '' : (i18n.no_data || 'No data yet.'),
			{
				type: 'bar',
				data: {
					labels: topLocations.map(function (l) { return l.label; }),
					datasets: [{
						label: i18n.conversions || 'Conversions',
						data: topLocations.map(function (l) { return l.clicks; }),
						backgroundColor: 'rgba(59, 130, 246, 0.7)',
						borderColor: 'rgb(59, 130, 246)',
						borderWidth: 1
					}]
				},
				options: {
					indexAxis: 'y',
					responsive: true,
					maintainAspectRatio: false,
					plugins: { legend: { display: false } },
					scales: {
						x: { beginAtZero: true },
						y: { ticks: { maxRotation: 0 } }
					}
				}
			}
		);

		var devices = data.devices || [];
		drawChart(
			'chart-devices',
			devices.length ? '' : (i18n.no_devices || 'No device data for this date range yet.'),
			{
				type: 'doughnut',
				data: {
					labels: devices.map(function (d) { return d.label; }),
					datasets: [{
						data: devices.map(function (d) { return d.count; }),
						backgroundColor: devices.map(function (d) {
							return deviceColors[d.key] || deviceColors.unknown;
						})
					}]
				},
				options: {
					responsive: true,
					maintainAspectRatio: false
				}
			}
		);

		var notFoundSeries = data.not_found_over_time || {};
		var nfLabels = Object.keys(notFoundSeries);
		var nfMessage = seriesHasValues(notFoundSeries) ? '' : (i18n.no_404s || 'No 404s recorded for this date range.');
		drawChart(
			'chart-404s',
			nfMessage,
			{
				type: 'line',
				data: {
					labels: nfLabels,
					datasets: [{
						label: i18n.not_found || '404s',
						data: nfLabels.map(function (key) { return notFoundSeries[key]; }),
						borderColor: 'rgb(244, 63, 94)',
						backgroundColor: 'rgba(244, 63, 94, 0.1)',
						fill: true,
						tension: 0.2
					}]
				},
				options: {
					responsive: true,
					maintainAspectRatio: false,
					plugins: { legend: { display: false } },
					scales: {
						x: { ticks: { maxRotation: 45 } },
						y: { beginAtZero: true }
					}
				}
			}
		);
	}

	function loadAnalytics() {
		var id = ++requestId;
		var requested = {
			range: state.range.range,
			start: state.range.start,
			end: state.range.end
		};
		setLoading(true);
		$.post(config.ajax_url, {
			action: 'magicpage_analytics_data',
			nonce: config.nonce,
			range: requested.range,
			start: requested.start,
			end: requested.end
		}, function (response) {
			if (id !== requestId) {
				return;
			}
			setLoading(false);
			if (!response.success) {
				showFailure();
				return;
			}
			renderPayload(response.data || {});
		}).fail(function () {
			if (id !== requestId) {
				return;
			}
			setLoading(false);
			console.error('Analytics AJAX failed.');
			showFailure();
		});
	}

	$('#mpe-range').on('change', function () {
		var custom = $(this).val() === 'custom';
		$('#mpe-custom-range').prop('hidden', !custom);
		if (!custom) {
			state.range = rangeFromUi();
			loadAnalytics();
		}
	});

	$('#mpe-range-apply').on('click', function () {
		var next = rangeFromUi();
		if (!rangeIsValid(next)) {
			window.alert(i18n.range_invalid || 'Choose a valid start and end date.');
			return;
		}
		state.range = next;
		loadAnalytics();
	});

	$('#mpe-export-csv, #mpe-export-json').on('click', function (event) {
		var next = rangeFromUi();
		if (!rangeIsValid(next)) {
			event.preventDefault();
			window.alert(i18n.range_invalid || 'Choose a valid start and end date.');
			return;
		}
		state.range = next;
		this.href = exportHref($(this).data('format') || 'json', next);
	});

	$('#mpe-clear-unassigned-stats').on('click', function () {
		var msg = i18n.clear_unassigned_confirm || 'Clear unassigned stats?';
		if (!window.confirm(msg)) {
			return;
		}
		var $btn = $(this);
		$btn.prop('disabled', true);
		$.post(config.ajax_url, {
			action: 'magicpage_analytics_clear_unassigned',
			nonce: config.nonce
		}, function (response) {
			if (!response.success) {
				window.alert(i18n.clear_failed || 'Could not clear stats.');
				$btn.prop('disabled', false);
				return;
			}
			var d = response.data || {};
			var done = i18n.clear_unassigned_done || 'Cleared %1$s page(s).';
			done = done.replace('%1$s', String(d.cleared_posts != null ? d.cleared_posts : 0));
			window.alert(done);
			window.location.reload();
		}).fail(function () {
			window.alert(i18n.request_failed || 'Request failed.');
			$btn.prop('disabled', false);
		});
	});

	loadAnalytics();
});
