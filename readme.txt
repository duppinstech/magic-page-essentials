=== Magic Page Essentials ===
Contributors: duppinstech
Tags: magic-page, admin, analytics, pages
Requires at least: 5.8
Tested up to: 6.9
Requires PHP: 7.4
Stable tag: 1.3.0
License: GPLv2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

Admin UI and analytics companion for the Magic Page plugin: filtered Pages list, optional Yoast bridge, and visit, click, device, and 404 analytics.

== Description ==

Magic Page Essentials extends WordPress admin for sites using the Magic Page plugin. It adds filtered views on the Pages screen, optional Yoast SEO replacement variables, performance scope controls, and an analytics dashboard.

Updates can be installed from GitHub releases when a newer tag is published (see plugin header Update URI).

== Installation ==

1. Upload the plugin folder to `/wp-content/plugins/`.
2. Activate the plugin through the Plugins screen.
3. Configure features under Magic Pages → Essentials.

== Frequently Asked Questions ==

= Does this replace Magic Page? =

No. Magic Page (or compatible stack) should remain installed; this plugin adds admin and analytics features.

== Upgrade Notice ==

= 1.3.0 =
Analytics adds a date range, CSV/JSON export, device and 404 charts, a location filter on Pages, and a per-page analytics modal. Older visit rows without a device count as Unknown.

= 1.2.5 =
Developer filters use the `magic_page_essentials_*` prefix (see 1.2.4 notes). The Yoast bridge class is `Magic_Page_Essentials_Yoast_Bridge`; `MPE_Yoast_Bridge` remains available as a class alias.

= 1.2.4 =
Developer filters were renamed to use the `magic_page_essentials_*` prefix (for example `magic_page_essentials_analytics_tracked_post_ids` instead of `mpe_analytics_tracked_post_ids`). Update any custom code that hooked the old names.

== Changelog ==

= 1.3.0 =
* Filter the Pages list by Magic Page location.
* Per-page analytics modal on the Magic Pages list.
* Record device type on visits and 404s from the front end.
* Export analytics as CSV or JSON.
* Choose a date range (including a custom range) on the analytics dashboard.

= 1.2.5 =
* Sync `readme.txt` (Tested up to, Stable tag) with plugin version; Yoast bridge class renamed to `Magic_Page_Essentials_Yoast_Bridge` with `MPE_Yoast_Bridge` alias.
* Fix PHPCS PreparedSQL usage in Magic Pages list table query.

= 1.2.4 =
* WordPress Plugin Check compatibility (prefixes, i18n, escaping, local Chart.js bundle).
* Optional updates from GitHub releases (`Magic_Page_Essentials_GitHub_Updater`).
* `readme.txt` headers for directory-style scanners.
