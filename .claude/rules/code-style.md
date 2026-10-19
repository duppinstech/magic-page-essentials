---
paths:
  - "**/*.php"
  - "**/*.js"
  - "**/*.css"
---

# Code style

## PHP
- Target **PHP 7.4**. For PHP 7.4 that means no `match`, enums, `readonly`, constructor promotion, `?->`, union types, or `str_contains` without a polyfill.
- WordPress Coding Standards: spaces inside parentheses, Yoda conditions for literals; match the file's array syntax and indentation. Don't reformat lines you didn't change.
- Prefix global functions, hooks, transients, and most options with `magic_page_essentials_`. AJAX actions (`wp_ajax_magicpage_*` and `wp_ajax_nopriv_magicpage_*`), the option `magicpage_404_log`, and analytics post meta (`magicpage_visit_count`, `magicpage_visits`, `magicpage_clicks`, `magicpage_click_count`) use `magicpage_`. Text domain `magic-page-essentials` on every translatable string.
- Docblock on every public method and every hook the plugin fires.
- No PHP namespace and no Composer autoload for plugin classes. `magic-page-essentials.php` loads modules with `require_once`.
- Class names use `Magic_Page_Essentials_` (`Settings`, `GitHub_Updater`, `Yoast_Bridge`, `Plugin_Info`). Names already in the tree that differ: `MagicPage_Analytics_Dashboard`, `Magic_Pages_List_Table`. `MPE_Yoast_Bridge` is an alias of the Yoast bridge.
- `Magic_Page_Essentials_Settings::init()` and `Magic_Page_Essentials_Yoast_Bridge::init()` register hooks from `plugins_loaded`. `MagicPage_Analytics_Dashboard::maybe_boot()` does the same. The updater and plugin info use `boot()` at load time. Page-list and performance-scope behavior is global functions in `includes/admin-functions.php` and `includes/performance-scope.php`.
- No field library. Settings are the option array `magic_page_essentials_settings`.

## JavaScript
- Data from PHP arrives through `wp_localize_script` or `wp_add_inline_script`; never inline secrets.
- jQuery, one file per screen, no bundler and no `package.json`. `assets/js/magicpage-analytics.js` is the dashboard, `assets/js/magicpage-page-analytics.js` is the per-page modal, `assets/js/magicpage-frontend-analytics.js` records visits, clicks, and 404s. Chart.js 4.4.0 is the committed file `assets/js/vendor/chart.umd.min.js`.

## CSS
- Scope front-end CSS under a plugin wrapper or body class so it doesn't leak into themes or wp-admin.
- Don't edit vendored libraries (`*.min.*`, third-party bundles).

## Comments
- Explain *why*, not *what*.
