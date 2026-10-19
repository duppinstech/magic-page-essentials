# Magic Page Essentials

A Duppins Technology add-on for sites that use the third-party [Magic Page Plugin](https://magicpageplugin.com/). Magic Page is a separate product. Duppins Technology does not make Magic Page, and the two products are not affiliated. Magic Page creates large numbers of SEO pages; this add-on keeps the admin organized and adds analytics so you can see how well those pages perform.

---

## Features

- **Filtered Pages list**  
  On **Pages → All Pages**, the default view is **Non-Magic Pages** so you don’t see hundreds of SEO pages. Tabs:
  - **All** – every page
  - **Magic Pages** – only pages with `_location_id` (Magic Page–generated)
  - **Non-Magic Pages** – regular pages only  
  Optional **Group** and **Location** dropdowns filter by `_group_id` and `_location_id`.

- **Analytics dashboard**  
  Under **Magic Pages → Analytics**:
  - Date range: last 7, 30, or 90 days, last 12 months, all time, or a custom range (capped at 366 days).
  - Charts: visits over time, top locations, device type, and 404s.
  - Tables: locations, pages (visits, clicks, CTR %), and top 404 paths.
  - **Export CSV** and **Export JSON** for the selected range.

- **Per-page analytics**  
  On the Magic Pages list (and on `magicpage` posts), the row action **Analytics** opens a modal with that page’s visits, clicks, CTR, devices, and recent clicks.

- **Visit, click, device, and 404 tracking**  
  On the front end, when someone views a tracked `magicpage` (or an included static export):
  - A page view is recorded via AJAX, including device type (`desktop`, `mobile`, `tablet`).
  - Clicks on outbound links are recorded for CTR.
  - A missing URL records a 404 (path and device only; the same visitor and path are counted once per hour).

- **Extensible**  
  Developer filters use the `magic_page_essentials_*` prefix, including location choices and whether a 404 is stored.

---

## Project structure

```
magic-page-essentials/
├── assets/
│   ├── css/
│   │   └── magicpage-analytics.css
│   └── js/
│       ├── magicpage-analytics.js           (dashboard charts, ranges, export)
│       ├── magicpage-page-analytics.js      (per-page modal on the Pages list)
│       └── magicpage-frontend-analytics.js  (visits, clicks, device, 404s)
├── includes/
│   ├── admin-functions.php             (Pages list views + filters)
│   ├── class-admin-dashboard.php       (Analytics menu, AJAX, enqueue)
│   └── class-magic-pages-table.php     (optional list table; not loaded by default)
├── magic-page-essentials.php          (bootstrap, constants)
└── README.md
```

---

## Installation

1. Upload the plugin to `/wp-content/plugins/magic-page-essentials/`.
2. Activate it in **Plugins**. The parent **Magic Page Plugin** must be active.
3. Use **Pages → All Pages** (defaults to Non-Magic) and **Magic Pages → Analytics** for metrics.

---

## Usage

- **Pages screen:** Use **Non-Magic Pages** (default), **Magic Pages**, or **All**. Use **Group** and **Location** to narrow the list. On a Magic Page row, **Analytics** opens that page’s stats.
- **Analytics:** Open **Magic Pages → Analytics**, pick a date range, and export CSV or JSON. Charts and tables follow the range.
- Tracking is automatic on singular tracked views (device is sent with the page view) and on front-end 404s.

---

## GitHub and updates

This project is versioned on GitHub. To keep your repo and deployments in sync:

1. Commit and push after making changes:
   ```bash
   git add .
   git commit -m "Describe your change"
   git push origin main
   ```
2. Use tags for releases (e.g. `v1.0.0`) so you can track what’s deployed.

---

## Roadmap

The previous roadmap shipped in 1.3.0: location filter, per-page analytics, 404 and device logging, CSV/JSON export, and date ranges. No further product work is queued.

---

## License

Companion plugin for sites using Magic Page Plugin. Redistribution without permission is prohibited.

**Author:** [Odell Duppins Jr](https://github.com/oduppinsjr)  
**Company:** Duppins Technology

---

## Support

Open an issue on this repository or contact [Duppins Technology](https://duppinstech.com).

---

## Local development

- PHP 7.4 or newer, Composer, and WordPress 5.8 or newer.
- The parent Magic Page plugin must be installed and active.
- Production dependencies are already bundled in `vendor/`. Refresh them with `composer install --no-dev`.
- Copy this directory to `/wp-content/plugins/magic-page-essentials/` and activate it under Plugins.
- There is no build step.

## Tests

PHPUnit is a dev dependency and is not part of the bundled `vendor/` directory.

```bash
composer install
composer lint
composer test
```

`composer lint` syntax-checks this plugin's PHP and skips `vendor/`. `composer test` runs PHPUnit. The committed suite only checks that the harness runs.

## Release and deploy

There is no compile step. The plugin directory, including the bundled production `vendor/`, is what gets installed.

1. Bump the plugin version and the Stable tag in `readme.txt` together.
2. Tag `vX.Y.Z` and publish a GitHub release. The plugin can install updates from those releases.
3. Deploy by placing that release in `wp-content/plugins` and activating it.
