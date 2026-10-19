jQuery(document).ready(function ($) {
	var cfg = window.MagicPageAnalyticsFrontend;
	if (!cfg) {
		return;
	}

	function deviceType() {
		var ua = navigator.userAgent || '';
		if (/iPad|Tablet|PlayBook|Silk|Android(?!.*Mobile)/i.test(ua)) {
			return 'tablet';
		}
		if (navigator.maxTouchPoints > 1 && /Macintosh/i.test(ua)) {
			return 'tablet';
		}
		if (/Mobi|Android|iPhone|iPod|webOS|BlackBerry|IEMobile|Opera Mini/i.test(ua)) {
			return 'mobile';
		}
		return 'desktop';
	}

	if (cfg.is_404) {
		if (!cfg.nonce_404) {
			return;
		}
		$.post(cfg.ajax_url, {
			action: 'magicpage_record_404',
			nonce: cfg.nonce_404,
			url: window.location.href,
			device: deviceType()
		});
		return;
	}

	if (!cfg.post_id) {
		return;
	}

	$.post(cfg.ajax_url, {
		action: 'magicpage_record_visit',
		nonce: cfg.nonce,
		post_id: cfg.post_id,
		device: deviceType()
	});

	$(document.body).on('click', 'a[href^="http"]', function () {
		var $link = $(this);
		var href = $link.attr('href');
		var text = ($link.text() || '').trim() || $link.attr('title') || '';
		if (!href) {
			return;
		}
		$.post(cfg.ajax_url, {
			action: 'magicpage_record_click',
			post_id: cfg.post_id,
			href: href,
			text: text,
			click_nonce: cfg.click_nonce
		});
	});
});
