# Agents

## Plugin facts

- **Plugin:** Magic Page Essentials 1.3.0
- **Main file:** `magic-page-essentials.php`
- **Text domain:** `magic-page-essentials`
- **Prefix:** `magic_page_essentials_` on functions, hooks, constants, and most options. AJAX actions, the 404 log option, and analytics post meta use `magicpage_`.
- **PHP:** 7.4. **WordPress:** 5.8.
- **Author:** Duppins Technology. **Owner and copyright holder:** Duppins Technology (https://duppinstech.com).
- **License:** GPL-2.0-or-later
- **Updater:** `Magic_Page_Essentials_GitHub_Updater` reads releases for `duppinstech/magic-page-essentials`. Disable with `MAGIC_PAGE_ESSENTIALS_DISABLE_GITHUB_UPDATER`.

## What this is

Magic Page Essentials is a WordPress companion to the Magic Page plugin. Magic Page generates large sets of SEO pages. This plugin keeps wp-admin usable and records how those pages perform.

It filters the Pages list, adds an analytics dashboard, and records views and outbound clicks. It does not replace Magic Page. Magic Page is a separate product. Duppins Technology does not make Magic Page.

## Architecture

- `magic-page-essentials.php` — constants, updater and Plugins-screen boot, activation defaults, text domain, and module init on `plugins_loaded`.
- `includes/class-magic-page-essentials-github-updater.php` — GitHub release checks and the Dashboard → Updates offer.
- `includes/class-magic-page-essentials-plugin-info.php` — Plugins-screen links and the View details modal from `readme.txt` and `assets/wporg/`.
- `includes/class-essentials-settings.php` — Magic Pages → Essentials toggles: Yoast bridge, analytics, static pages, performance scope.
- `includes/performance-scope.php` — strips Magic Page hooks outside Magic Page requests.
- `includes/class-admin-dashboard.php` — analytics screens, visit/click/404 recording, CSV and JSON export.
- `includes/class-yoast-bridge.php` — optional Yoast `%%mpp_*%%` replacements. `MPE_Yoast_Bridge` is an alias.
- `includes/admin-functions.php` — Pages list views and the group and location filters.
- `includes/class-magic-pages-table.php` — alternate list table. The bootstrap does not load it.
- `assets/js/` — jQuery for the dashboard, the per-page modal, and front-end tracking. No build step. Chart.js 4.4.0 is `assets/js/vendor/chart.umd.min.js`.
- `assets/css/magicpage-analytics.css` — analytics styles. `assets/admin.css` is empty and not enqueued.
- `assets/wporg/` — banner, icon, and screenshots for the Plugins screen.
- `uninstall.php` — deletes the updater release cache and old release transients.
- `tests/HarnessTest.php` — proves PHPUnit runs. It does not cover plugin behavior.

## Commands

Install dev dependencies (PHPUnit) before lint or test:

```
composer install
```

Lint (syntax-check this plugin's PHP; skips `vendor/`):

```
composer lint
```

Test:

```
composer test
```

Build: none.

Check `composer.json` (warnings do not fail the command):

```
composer validate
```

`composer install` changes `vendor/`. Do not commit dev packages. `composer install --no-dev` leaves no production packages. Leave `vendor/` unstaged unless a production dependency changed.

## Conventions

- Indent PHP, CSS, and JS with tabs. `composer.json` uses 4 spaces. YAML and other JSON use 2 spaces.
- Line endings are LF. `*.ps1`, `*.bat`, and `*.cmd` are CRLF.
- Commits use Conventional Commits (`type: summary`). Branches look like `type/short-description`.
- Plugin version and the `readme.txt` Stable tag move together. A release is a GitHub tag `vX.Y.Z`.
- The committed test suite only proves PHPUnit runs. It does not cover plugin behavior.

## Hard rules

Do not touch:

- Plugin behavior in `magic-page-essentials.php`, `includes/`, and `assets/`, unless the task is a product change.
- `vendor/` by hand.
- `SECURITY.md` and `LICENSE.md`, unless the task is those files.
- `.env`, `.env.*`, `CLAUDE.local.md`, and `.claude/settings.local.json`.
- Pushing, tagging, releasing, or deploying, unless the user asks.

## Agents

| Agent | Role |
| --- | --- |
| `finance-reviewer` | Running cost, tiers, and anything a customer might pay for |
| `legal-reviewer` | License, copyright, bundled assets, privacy |
| `marketing-reviewer` | Customer-facing copy, screenshots, release highlights |
| `product-reviewer` | `INTENT.md`, `PLAN.md`, and scope |
| `release-ops-reviewer` | Zip contents, uninstall, migrations, rollback |
| `research` | WordPress, library, and third-party API questions. Does not edit code |
| `security-reviewer` | AJAX, admin-post, the updater, and superglobals |
| `support-docs-reviewer` | `README.md`, `readme.txt`, `CHANGELOG.md`, admin copy, i18n |
| `test-writer` | PHPUnit tests after a feature or fix |
| `ux-reviewer` | Admin and front-end layout, accessibility, and performance |

Shared commands: `/review`, `/department-review`, `/deploy`, `/scaffold`. Department notes live in `.claude/memory/project-context.md`.
