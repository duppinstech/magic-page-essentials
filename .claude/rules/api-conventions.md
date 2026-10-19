---
paths:
  - "magic-page-essentials.php"
  - "includes/**/*.php"
---

# API conventions (REST, AJAX, admin-post, hooks)

## REST
- This plugin registers no REST routes. A new route registers on `rest_api_init` under `magic-page-essentials/v1`. Every route has a real `permission_callback`; never `__return_true` on routes that write.
- Validate and sanitize every argument with `args` → `sanitize_callback` / `validate_callback`. Return `WP_REST_Response` or `WP_Error`; never `echo`.

## admin-ajax
- Actions are `magicpage_record_visit`, `magicpage_record_click`, and `magicpage_record_404` (logged-in and nopriv), plus logged-in `magicpage_analytics_data`, `magicpage_page_analytics`, and `magicpage_analytics_clear_unassigned`.
- First lines of a logged-in handler: `check_ajax_referer()`, then the capability check. Respond with `wp_send_json_success()` / `wp_send_json_error()`.

## admin-post
- The export handler is `admin_post_magicpage_analytics_export`.
- Handlers call `check_admin_referer()` **and** `current_user_can()` before reading `$_POST` or `$_FILES`, and finish with `wp_safe_redirect()` then `exit`.

## Outbound HTTP
- `wp_remote_get()` / `wp_remote_post()` with a timeout; cache responses in transients where sensible. Keys come from settings; never log them.
- The updater calls the GitHub latest-release API with a 10 second timeout. An optional token is a Bearer header and must not follow a redirect.

## Hooks we expose
- New hooks are prefixed `magic_page_essentials_`, documented with a docblock, and listed here. Renaming or removing a public hook is a breaking change; deprecate first.
- This plugin fires no `do_action`.
- `magic_page_essentials_is_magic_page_context` — whether a post keeps full Magic Page behavior.
- `magic_page_essentials_location_id_indicates_magic_context` — whether a `_location_id` on a page or post means Magic Page context.
- `magic_page_essentials_performance_scope_skip_for_builder` — skip stripping Magic Page hooks for a builder or preview.
- `magic_page_essentials_yoast_bridge_term_description` — location term description before Yoast token replacement.
- `magic_page_essentials_analytics_tracked_post_ids` — post IDs included in analytics.
- `magic_page_essentials_analytics_track_static_page` — whether a static exported page is tracked.
- `magic_page_essentials_analytics_is_post_tracked` — whether one post is tracked.
- `magic_page_essentials_analytics_dashboard_hook_suffixes` — admin hooks that load the analytics dashboard.
- `magic_page_essentials_analytics_display_title` — title shown for a post in analytics.
- `magic_page_essentials_skip_clear_unassigned_analytics` — whether clearing unassigned analytics is skipped for a post.
- `magic_page_essentials_record_404` — whether a front-end 404 is stored.
- `magic_page_essentials_location_filter_choices` — location id to label options on the Pages list.
- `magic_page_essentials_github_updater_config` — updater owner, repo, token, TTLs, and icons. The tag is `{prefix}_github_updater_config` with prefix `magic_page_essentials`.
- `magic_page_essentials_github_release_http_args` — `wp_remote_get()` args for the latest-release request. The tag is `{prefix}_github_release_http_args`.
- The dashboard also passes titles through the core `the_title` filter. `includes/class-magic-pages-table.php` (not loaded by the bootstrap) passes titles through the existing `cities` filter. This plugin does not own those tags.
