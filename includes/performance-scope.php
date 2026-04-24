<?php
/**
 * Strip Magic Page vendor hooks on non–Magic Page requests (Essentials-only; no vendor edits).
 *
 * Hook inventory (Magic Page 7.x wp-whiterail-seo):
 *
 * MagicPageShortcodesAndFilters:
 * - save_post (11) — skipped here; admin-only, not worth stripping on front.
 * - the_title, document_title_parts, the_content, the_excerpt (filters)
 * - option_blogname, option_blogdescription
 * - wpseo_title, wpseo_metadesc, wpseo_opengraph_title, wpseo_opengraph_desc, wpseo_canonical
 * - get_the_excerpt, tve_thrive_shortcodes, breadcrumb_trail
 * - aioseop_description, aioseop_title
 * - wp_head (head), wp_footer (footer)
 * - widget_text_content, widget_block_content (+ do_shortcode on same — core, not removed)
 * - wp: initXfields, customLocationFields
 *
 * MagicPagePublic:
 * - pre_get_posts (0, get_posts), template_redirect, wp_enqueue_scripts, wp_head (head),
 *   parse_query (parse), document_title_parts (title), wp_kses_allowed_html, get_post_metadata, wp_footer (check)
 *
 * @package Magic_Page_Essentials
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Whether the current singular post should keep full Magic Page behavior.
 *
 * @param WP_Post $post Post object.
 * @return bool
 */
function magic_page_essentials_is_magic_page_context( $post ) {
	if ( ! $post instanceof WP_Post ) {
		return (bool) apply_filters( 'magic_page_essentials_is_magic_page_context', false, $post );
	}

	$slug   = function_exists( 'magic_page_default_post_slug' ) ? magic_page_default_post_slug() : 'magicpage';
	$result = false;

	if ( $post->post_type === $slug ) {
		$result = true;
	} elseif ( in_array( $post->post_type, array( 'page', 'post' ), true ) ) {
		$lid = get_post_meta( $post->ID, '_location_id', true );
		if ( $lid !== '' && $lid !== false && $lid !== null ) {
			$result = (bool) apply_filters( 'magic_page_essentials_location_id_indicates_magic_context', true, $post, $lid );
		}
		if ( ! $result ) {
			$gid = get_post_meta( $post->ID, '_group_id', true );
			if ( $gid !== '' && $gid !== false && $gid !== null ) {
				$result = true;
			}
		}
	}

	return (bool) apply_filters( 'magic_page_essentials_is_magic_page_context', $result, $post );
}

/**
 * @return void
 */
function magic_page_essentials_log_performance_scope_class_mismatch() {
	if ( ! defined( 'WP_DEBUG' ) || ! WP_DEBUG ) {
		return;
	}
	if ( get_option( 'magic_page_essentials_logged_missing_mp_classes', false ) ) {
		return;
	}
	update_option( 'magic_page_essentials_logged_missing_mp_classes', true, false );
	// phpcs:ignore WordPress.PHP.DevelopmentFunctions.error_log_error_log -- WP_DEBUG-only diagnostic.
	error_log( 'Magic Page Essentials: MagicPageShortcodesAndFilters or MagicPagePublic not found; performance scope skipped. If Magic Page updated, verify class names.' );
}

/**
 * True when we should not strip hooks (builders / previews).
 *
 * @return bool
 */
function magic_page_essentials_performance_scope_skip_for_builder() {
	// phpcs:disable WordPress.Security.NonceVerification.Recommended -- Builder preview query flags, not form submissions.
	if ( isset( $_GET['elementor-preview'] ) || isset( $_GET['elementor-preview-id'] ) ) {
		return true;
	}
	if ( isset( $_GET['vc_action'] ) && 'vc_inline' === $_GET['vc_action'] ) {
		return true;
	}
	if ( ! empty( $_GET['fl_builder'] ) ) {
		return true;
	}
	if ( isset( $_GET['preview'] ) && isset( $_GET['preview_id'] ) ) {
		return true;
	}
	// phpcs:enable WordPress.Security.NonceVerification.Recommended

	return (bool) apply_filters( 'magic_page_essentials_performance_scope_skip_for_builder', false );
}

/**
 * Collect and remove all callbacks owned by Magic Page vendor classes.
 *
 * @return int Number of callbacks removed.
 */
function magic_page_essentials_remove_magic_page_vendor_callbacks() {
	global $wp_filter;

	$targets   = array( 'MagicPageShortcodesAndFilters', 'MagicPagePublic' );
	$to_remove = array();

	foreach ( $wp_filter as $tag => $hook ) {
		if ( ! $hook instanceof WP_Hook ) {
			continue;
		}
		foreach ( $hook->callbacks as $priority => $callbacks ) {
			foreach ( $callbacks as $cb ) {
				$fn = isset( $cb['function'] ) ? $cb['function'] : null;
				if ( ! is_array( $fn ) || ! isset( $fn[0] ) || ! is_object( $fn[0] ) ) {
					continue;
				}
				$cls = get_class( $fn[0] );
				if ( ! in_array( $cls, $targets, true ) ) {
					continue;
				}
				if ( 'save_post' === $tag && 'MagicPageShortcodesAndFilters' === $cls ) {
					continue;
				}
				$to_remove[] = array( $tag, $fn, (int) $priority );
			}
		}
	}

	$removed = 0;
	foreach ( $to_remove as $row ) {
		if ( remove_filter( $row[0], $row[1], $row[2] ) ) {
			++$removed;
		}
	}

	return $removed;
}

/**
 * @return void
 */
function magic_page_essentials_maybe_strip_magic_page_hooks() {
	if ( ! class_exists( 'Magic_Page_Essentials_Settings', false ) || ! Magic_Page_Essentials_Settings::is_feature_enabled( 'performance_scope' ) ) {
		return;
	}

	if ( is_admin() || wp_doing_ajax() || wp_doing_cron() || ( defined( 'REST_REQUEST' ) && REST_REQUEST ) ) {
		return;
	}

	if ( ! function_exists( 'is_magic_page_installed' ) || ! is_magic_page_installed() ) {
		return;
	}

	if ( ! class_exists( 'MagicPageShortcodesAndFilters', false ) && ! class_exists( 'MagicPagePublic', false ) ) {
		magic_page_essentials_log_performance_scope_class_mismatch();
		return;
	}

	if ( magic_page_essentials_performance_scope_skip_for_builder() ) {
		return;
	}

	if ( ! is_singular() ) {
		return;
	}

	global $post;
	if ( ! $post instanceof WP_Post ) {
		return;
	}

	if ( magic_page_essentials_is_magic_page_context( $post ) ) {
		return;
	}

	magic_page_essentials_remove_magic_page_vendor_callbacks();
}

add_action( 'wp', 'magic_page_essentials_maybe_strip_magic_page_hooks', 0 );
