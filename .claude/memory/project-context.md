# Project context

_Shared, committed memory. Keep it factual and current. If the repo is public, so is this file._

- **Product:** Magic Page Essentials, a WordPress plugin. Author: Duppins Technology. Owner and copyright holder: Duppins Technology (https://duppinstech.com).
- **Repo:** https://github.com/duppinstech/magic-page-essentials (public). Git origin is https://github.com/oduppinsjr/magic-page-essentials.git.
- **Current release:** 1.3.0 in the plugin header and the `readme.txt` Stable tag. Latest git tag is `1.2.5` (2026-04-24). There is no `1.3.0` or `v1.3.0` tag.
- **Distribution:** GitHub releases through `Magic_Page_Essentials_GitHub_Updater` for `duppinstech/magic-page-essentials`. Sites see updates under Dashboard → Updates. Not WordPress.org.
- **Key dependencies:** PHP >= 7.4. Dev: `phpunit/phpunit` ^9.6. Bundled: Chart.js 4.4.0 (`assets/js/vendor/chart.umd.min.js`). `composer.json` `require` has no packages. Runtime companion: the Magic Page plugin. Optional: Yoast SEO.
- **Integrations:** GitHub Releases API. Yoast SEO when the bridge toggle is on and Yoast is installed. Magic Page post type `magicpage` and meta `_location_id` and `_group_id`.
- **CI:** `.github/workflows/ci.yml` runs `composer lint` and `composer test` on PHP 8.2 for pull requests. `release.yml` builds a zip on `v*` tags.

## Review watchlist
Known items each department re-checks on every review until fixed. Remove lines when they're resolved.
- **Security:** none yet
- **Legal:** Visits, clicks, device type, and 404 paths are stored in post meta and `magicpage_404_log`. No privacy notice is in the repo.
- **Finance:** none yet
- **Product:** none yet
- **Marketing:** none yet
- **Support:** none yet
- **Ops:** `uninstall.php` deletes the updater release cache and old repo transients. It leaves `magic_page_essentials_settings`, `magicpage_404_log`, `magic_page_essentials_logged_missing_mp_classes`, and analytics post meta (`magicpage_visit_count`, `magicpage_visits`, `magicpage_clicks`, `magicpage_click_count`).
- **UX:** none yet
