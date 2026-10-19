# Architectural decisions

Append-only log. Format: `## YYYY-MM-DD — Title`, then **Context** / **Decision** / **Consequences**. Owner waivers of High findings are recorded here too.

## 2025-07-07 — Visit and click counts are post meta

**Context** The first upload stored analytics on each post (`0d60ffc`).

**Decision** Visits and clicks use post meta `magicpage_visits`, `magicpage_visit_count`, `magicpage_clicks`, and `magicpage_click_count`.

**Consequences** Deleting the plugin does not remove those keys. On 2026-10-18 (`fc50a30`) 404s were added as the option `magicpage_404_log`, which uninstall also leaves in place.

## 2026-04-24 — Chart.js is bundled in the plugin

**Context** Plugin Check (`70eb103`). Changelog 1.2.4.

**Decision** Dashboard charts load `assets/js/vendor/chart.umd.min.js` (Chart.js 4.4.0, MIT notice in the file) instead of a remote script.

**Consequences** No chart request leaves the site. Do not replace that file with a CDN URL.

## 2026-10-17 — The committed suite only proves PHPUnit runs

**Context** Pull-request checks (`bb9fc93`).

**Decision** `tests/HarnessTest.php` asserts true. `composer test` runs it. CI runs lint and that test on PHP 8.2.

**Consequences** A behavior change is not caught until a regression test exists.

## 2026-10-18 — Updates come from GitHub releases

**Context** The plugin is hosted outside WordPress.org (`54369e5`).

**Decision** `Magic_Page_Essentials_GitHub_Updater` checks releases for `duppinstech/magic-page-essentials`. `MAGIC_PAGE_ESSENTIALS_DISABLE_GITHUB_UPDATER` turns that off.

**Consequences** `release.yml` builds a zip only for tags matching `v*`. The latest git tag is `1.2.5` (2026-04-24), which does not match. Header version 1.3.0 has no tag.

## 2026-10-18 — The Plugins screen reads readme.txt and assets/wporg

**Context** Privately distributed plugins have no WordPress.org listing (`5047f18`, `8fd59e2`).

**Decision** `Magic_Page_Essentials_Plugin_Info` fills View details, row links, and the banner, icon, and screenshots from `readme.txt` and `assets/wporg/`.

**Consequences** Screenshot and banner updates belong in `assets/wporg/` and `readme.txt`, kept in step with the Stable tag.
