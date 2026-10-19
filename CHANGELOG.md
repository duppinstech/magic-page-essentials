# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Repository docs, pull request checks, and agent tooling.

## [1.3.0]

### Added

- Location filter on the Pages list (`_location_id`, next to the group filter).
- Per-page analytics modal from the Magic Pages list and the `magicpage` list.
- Device type on front-end visit tracking, plus a device chart.
- 404 logging from front-end tracking, plus a 404 chart and top paths.
- CSV and JSON export for the analytics dashboard.
- Date ranges: 7, 30, and 90 days, 12 months, all time, and a custom range.

## [1.2.5]

### Changed

- Sync `readme.txt` (Tested up to, Stable tag) with the plugin version.
- Rename the Yoast bridge class to `Magic_Page_Essentials_Yoast_Bridge`, with `MPE_Yoast_Bridge` kept as an alias.

### Fixed

- PHPCS PreparedSQL usage in the Magic Pages list table query.

## [1.2.4]

### Changed

- WordPress Plugin Check compatibility (prefixes, internationalization, escaping, and a local Chart.js bundle).
- Optional updates from GitHub releases.
- `readme.txt` headers for directory-style scanners.
