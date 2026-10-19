=== Magic Page Essentials ===
Contributors: duppinstech
Tags: magic-page, admin, analytics, pages
Requires at least: 5.8
Tested up to: 6.9
Requires PHP: 7.4
Stable tag: 1.3.0
License: GPLv2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

Add-on for the third-party Magic Page plugin: filter the Pages list and review visits, clicks, and 404s.

== Description ==

Magic Page Essentials is a Duppins Technology add-on for sites that already use Magic Page. Magic Page is a separate third-party plugin. Duppins Technology does not make Magic Page, and the two products are not affiliated.

Magic Page can create a large set of pages. This add-on keeps wp-admin usable and records how those pages perform.

= Features =

* On Pages, switch between All, Magic Pages, and Non-Magic Pages. Non-Magic Pages is the default view.
* Filter that list by group and by location.
* Turn features on or off under Magic Pages → Essentials. The toggles cover Yoast SEO replacement variables, the analytics dashboard, static exported pages in analytics, and performance scope.
* Open Magic Pages → Analytics for visits, clicks, click-through rate, devices, locations, and 404s.
* Choose a date range: 7, 30, or 90 days, 12 months, all time, or a custom range.
* Export the current range as CSV or JSON.
* On a Magic Page row, open Analytics for that page’s visits, clicks, click-through rate, devices, and recent clicks.

= Support =

Support: [support@duppinstech.com](mailto:support@duppinstech.com). Made by [Duppins Technology](https://duppinstech.com).

== Installation ==

1. Download `magic-page-essentials.zip` from the latest release.
2. In wp-admin, go to Plugins → Add New → Upload Plugin, choose the zip, and click Install Now.
3. Activate Magic Page Essentials. The third-party Magic Page plugin needs to be active as well.
4. Go to Magic Pages → Essentials and choose which features to use.

= Updates =

New releases appear under Dashboard → Updates.

== Frequently Asked Questions ==

= Does this replace Magic Page? =

No. Keep Magic Page installed. Magic Page Essentials only adds admin tools and analytics.

= Is Magic Page a Duppins Technology product? =

No. Magic Page is a third-party plugin. Duppins Technology does not make it, and the two products are not affiliated.

= Where are the settings? =

Open Magic Pages → Essentials. The link is shown to users who can manage options.

== Screenshots ==

1. Pages list with All, Magic Pages, and Non-Magic Pages, plus the location filter.
2. Essentials settings. The Yoast toggle stays off until Yoast SEO is active.
3. Analytics dashboard with a date range, CSV and JSON export, and location charts.

== Changelog ==

= 1.3.0 =
* Filter the Pages list by location.
* Open per-page analytics from the Magic Pages list and from magicpage posts.
* Record device type on visits, and show a device chart.
* Record 404s from the front end, and show a 404 chart and the top paths.
* Export analytics as CSV or JSON.
* Choose a date range: 7, 30, or 90 days, 12 months, all time, or a custom range.

= 1.2.5 =
* Match the readme to the plugin version.
* Rename the Yoast bridge class to `Magic_Page_Essentials_Yoast_Bridge`. The old name `MPE_Yoast_Bridge` still works.
* Fix the Magic Pages list query reported by Plugin Check.

= 1.2.4 =
* WordPress Plugin Check compatibility, including translated text, escaping, and a local Chart.js file.
* Install updates from GitHub releases.
* Add readme headers for directory-style scanners.

== Upgrade Notice ==

= 1.3.0 =
Analytics adds a date range, CSV and JSON export, device and 404 charts, a location filter on Pages, and a per-page analytics view. Older visit rows without a device count as Unknown.

= 1.2.5 =
The Yoast bridge class is `Magic_Page_Essentials_Yoast_Bridge`. `MPE_Yoast_Bridge` remains available as a class alias.

= 1.2.4 =
Developer filters now use the `magic_page_essentials_*` prefix. Update any custom code that hooked the old `mpe_*` names.
