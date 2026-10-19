---
paths:
  - "tests/**"
  - "includes/**/*.php"
  - "magic-page-essentials.php"
---

# Testing standard

## Minimum (every change)
1. `php -l` passes on every changed PHP file (the PostToolUse hook does this).
2. Manual smoke test on a WordPress site with `WP_DEBUG` on:
   - The plugin activates without notices or errors.
   - Pages → All Pages: All, Magic Pages, and Non-Magic Pages, with the Group and Location filters. Non-Magic Pages is the default.
   - Magic Pages → Essentials: Yoast bridge, analytics, static pages, and performance scope. The Yoast toggle stays off until Yoast SEO is active.
   - Magic Pages → Analytics: a date range, charts, tables, and CSV and JSON export.
   - Analytics on a Magic Pages row and on a `magicpage` row.
   - Front end: a tracked view records a visit with device type, an outbound click, and a 404 path.
3. If you touched the updater, test the Check Again flow against a draft release.

## Automated tests
`composer test` runs PHPUnit 9.6 (`phpunit.xml.dist`, bootstrap `vendor/autoload.php`). The only test is `tests/HarnessTest.php`, which asserts true. It does not cover plugin behavior. See `PLAN.md`: no further product work is queued.
- There is no `tests/unit/` or `tests/integration/` tree, and no Brain Monkey or wp-phpunit package.
- Every bug fix ships with a regression test that fails before the fix. Unit tests never hit the network.
- CI (`.github/workflows/ci.yml`) runs `composer lint` and `composer test` on PHP 8.2 for pull requests.

## Priority test targets
- `Magic_Page_Essentials_GitHub_Updater` — release HTTP, the Bearer token, and `MAGIC_PAGE_ESSENTIALS_DISABLE_GITHUB_UPDATER`.
- `MagicPage_Analytics_Dashboard` — nopriv visit, click, and 404 handlers, logged-in analytics AJAX, and CSV/JSON export.
- `Magic_Page_Essentials_Settings::sanitize` — feature flags, including Yoast forced off when Yoast is absent.
- `magic_page_essentials_filter_pages_by_magic_page_group` and `magic_page_essentials_filter_pages_by_magic_page_location` — Pages list queries.
- `Magic_Page_Essentials_Yoast_Bridge` — location term lookup and `%%mpp_*%%` replacement.
