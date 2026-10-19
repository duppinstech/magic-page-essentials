jQuery(function ($) {
	var config = window.magicpagePageAnalytics;
	if (!config) {
		return;
	}

	var i18n = config.i18n || {};
	var postId = 0;
	var requestId = 0;
	var modal = document.getElementById('mpe-page-analytics-modal');
	if (!modal) {
		return;
	}

	function esc(s) {
		return String(s == null ? '' : s)
			.replace(/&/g, '&amp;')
			.replace(/</g, '&lt;')
			.replace(/>/g, '&gt;')
			.replace(/"/g, '&quot;')
			.replace(/'/g, '&#039;');
	}

	function closeModal() {
		modal.hidden = true;
		postId = 0;
	}

	function render(data) {
		var title = document.getElementById('mpe-page-analytics-title');
		var meta = document.getElementById('mpe-page-analytics-meta');
		var note = document.getElementById('mpe-page-analytics-note');
		var stats = document.getElementById('mpe-page-analytics-stats');
		var list = document.getElementById('mpe-page-analytics-clicks');
		if (title) {
			title.textContent = data.title || '';
		}

		var bits = [];
		if (data.location && data.location !== '—') {
			bits.push(data.location);
		}
		if (data.range) {
			bits.push(data.range);
		}
		if (meta) {
			var html = esc(bits.join(' · '));
			if (data.url && /^https?:\/\//i.test(data.url)) {
				html += (html ? ' · ' : '') + '<a href="' + esc(data.url) + '" target="_blank" rel="noopener noreferrer">' + esc(i18n.view || 'View page') + '</a>';
			}
			meta.innerHTML = html;
		}

		if (note) {
			if (data.tracked === false) {
				note.hidden = false;
				note.textContent = i18n.untracked || '';
			} else {
				note.hidden = true;
				note.textContent = '';
			}
		}

		var devices = (data.devices || []).map(function (device) {
			return (device.label || '') + ' ' + (device.count || 0).toLocaleString();
		}).join(', ');

		if (stats) {
			stats.innerHTML =
				'<div class="mpe-modal-stat"><span class="mpe-stat-value">' + (data.visits || 0).toLocaleString() + '</span><span class="mpe-stat-label">' + esc(i18n.visits || 'Visits') + '</span></div>' +
				'<div class="mpe-modal-stat"><span class="mpe-stat-value">' + (data.clicks || 0).toLocaleString() + '</span><span class="mpe-stat-label">' + esc(i18n.clicks || 'Clicks') + '</span></div>' +
				'<div class="mpe-modal-stat"><span class="mpe-stat-value">' + (data.ctr != null ? data.ctr + '%' : '—') + '</span><span class="mpe-stat-label">' + esc(i18n.ctr || 'CTR') + '</span></div>' +
				'<p class="mpe-modal-devices"><strong>' + esc(i18n.devices || 'Devices') + '</strong> ' + esc(devices || '—') + '</p>';
		}

		if (!list) {
			return;
		}
		var clicks = data.clicks_recent || [];
		if (!clicks.length) {
			list.innerHTML = '<li>' + esc(i18n.no_clicks || 'No clicks in this date range.') + '</li>';
			return;
		}
		list.innerHTML = clicks.map(function (click) {
			var href = (click.href && /^https?:\/\//i.test(click.href)) ? click.href : '';
			var label = click.text || href || '—';
			var when = '<span class="mpe-click-when">' + esc(click.display || '') + '</span> ';
			if (href) {
				return '<li>' + when + '<a href="' + esc(href) + '" target="_blank" rel="noopener noreferrer">' + esc(label) + '</a></li>';
			}
			return '<li>' + when + esc(label) + '</li>';
		}).join('');
	}

	function showError() {
		var title = document.getElementById('mpe-page-analytics-title');
		if (title) {
			title.textContent = i18n.failed || 'Could not load analytics for this page.';
		}
		var stats = document.getElementById('mpe-page-analytics-stats');
		if (stats) {
			stats.innerHTML = '';
		}
		var list = document.getElementById('mpe-page-analytics-clicks');
		if (list) {
			list.innerHTML = '';
		}
	}

	function load() {
		var id = ++requestId;
		var title = document.getElementById('mpe-page-analytics-title');
		if (title) {
			title.textContent = i18n.loading || 'Loading…';
		}
		$.post(config.ajax_url, {
			action: 'magicpage_page_analytics',
			nonce: config.nonce,
			post_id: postId,
			range: $('#mpe-page-range').val() || '30'
		}, function (response) {
			if (id !== requestId) {
				return;
			}
			if (!response || !response.success) {
				showError();
				return;
			}
			render(response.data || {});
		}).fail(function () {
			if (id !== requestId) {
				return;
			}
			showError();
		});
	}

	$(document).on('click', '.mpe-open-page-analytics', function (event) {
		event.preventDefault();
		postId = parseInt($(this).data('post-id'), 10) || 0;
		if (!postId) {
			return;
		}
		$('#mpe-page-range').val('30');
		modal.hidden = false;
		load();
		var closeButton = modal.querySelector('.mpe-modal-close');
		if (closeButton) {
			closeButton.focus();
		}
	});

	$(modal).on('click', '[data-mpe-close]', function (event) {
		event.preventDefault();
		closeModal();
	});

	$('#mpe-page-range').on('change', function () {
		if (postId && !modal.hidden) {
			load();
		}
	});

	$(document).on('keydown', function (event) {
		if (event.key === 'Escape' && !modal.hidden) {
			closeModal();
		}
	});
});
