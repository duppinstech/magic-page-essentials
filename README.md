# Magic Page Essentials

A companion plugin for WordPress that extends the [Magic Page Plugin](https://magicpageplugin.com/). Magic Page creates large numbers of SEO pages; this plugin keeps the admin organized and adds analytics so you can see how well those pages perform.

---

## Features

- **Filtered Pages list**  
  On **Pages → All Pages**, the default view is **Non-Magic Pages** so you don’t see hundreds of SEO pages. Tabs:
  - **All** – every page
  - **Magic Pages** – only pages with `_location_id` (Magic Page–generated)
  - **Non-Magic Pages** – regular pages only  
  Optional **Group** dropdown filters by `_group_id` (uses `_magic_page_groups` from the parent plugin).

- **Analytics dashboard**  
  Under **Magic Pages → Analytics**:
  - Charts: visits over time, by group, by location, top 10 pages, 404s (placeholder), device type (placeholder).
  - **Top 10 Magic Pages** table with **Visits**, **Clicks**, and **CTR %** (conversion rate).

- **Visit & click tracking**  
  On the front end, when someone views a `magicpage` post:
  - A page view is recorded via AJAX (stored in `magicpage_visits` / `magicpage_visit_count`).
  - Clicks on outbound links are recorded for CTR/conversion (stored in `magicpage_clicks` / `magicpage_click_count`).

- **Extensible**  
  Structured so you can add more filters, metrics, or export later.

---

## Project structure

```
magic-page-essentials/
├── assets/
│   ├── css/
│   │   └── magicpage-analytics.css
│   └── js/
│       ├── magicpage-analytics.js      (admin dashboard charts + table)
│       └── magicpage-frontend-analytics.js  (visit + link click tracking)
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

- **Pages screen:** Use **Non-Magic Pages** (default), **Magic Pages**, or **All**. Use **Group** to narrow by Magic Page group.
- **Analytics:** Open **Magic Pages → Analytics** to see visit trends, top pages, and CTR. Data is loaded via AJAX; the table shows visits, clicks, and CTR % per page.
- Tracking is automatic on singular `magicpage` views: one request records the view, and link clicks on the page are sent to `magicpage_record_click`.

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

- Filter by Magic Page location in the Pages list.
- Per-page analytics modal from the Magic Pages list.
- Real 404 and device logging from frontend tracking.
- Export analytics (CSV/JSON).
- Configurable date ranges.

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
