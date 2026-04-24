=== Magic Page Essentials ===
Contributors: duppinstech
Tags: magic-page, admin, analytics, pages
Requires at least: 5.8
Tested up to: 6.8
Requires PHP: 7.4
Stable tag: 1.2.4
License: GPLv2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

Admin UI and analytics companion for the Magic Page plugin: filtered Pages list, optional Yoast bridge, and visit/click analytics.

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

= 1.2.4 =
Developer filters were renamed to use the `magic_page_essentials_*` prefix (for example `magic_page_essentials_analytics_tracked_post_ids` instead of `mpe_analytics_tracked_post_ids`). Update any custom code that hooked the old names.

== Changelog ==

= 1.2.4 =
* WordPress Plugin Check compatibility (prefixes, i18n, escaping, local Chart.js bundle).
* Optional updates from GitHub releases (`Magic_Page_Essentials_GitHub_Updater`).
* `readme.txt` headers for directory-style scanners.
