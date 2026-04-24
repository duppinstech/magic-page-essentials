<?php
/**
 * Pages admin: Magic Pages submenu, list views, and filters.
 *
 * @package Magic_Page_Essentials
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Add "Magic Pages" as a submenu under Pages (same list, defaulting to magic pages only).
 *
 * @return void
 */
function magic_page_essentials_add_magic_pages_submenu_under_pages() {
	add_submenu_page(
		'edit.php?post_type=page',
		__( 'Magic Pages', 'magic-page-essentials' ),
		__( 'Magic Pages', 'magic-page-essentials' ),
		'edit_pages',
		'magic-pages-list',
		'magic_page_essentials_redirect_to_magic_pages_list'
	);
}
add_action( 'admin_menu', 'magic_page_essentials_add_magic_pages_submenu_under_pages', 20 );

/**
 * @return void
 */
function magic_page_essentials_redirect_to_magic_pages_list() {
	wp_safe_redirect( admin_url( 'edit.php?post_type=page&magic_pages=1' ) );
	exit;
}

/**
 * When viewing the magic-pages-filtered list, highlight "Magic Pages" in the submenu.
 *
 * @return void
 */
function magic_page_essentials_set_magic_pages_submenu_current() {
	global $pagenow, $submenu_file;

	// phpcs:disable WordPress.Security.NonceVerification.Recommended -- Admin list screen query args only.
	if ( $pagenow !== 'edit.php' || ! isset( $_GET['post_type'] ) || 'page' !== sanitize_key( wp_unslash( $_GET['post_type'] ) ) ) {
		return;
	}
	if ( isset( $_GET['magic_pages'] ) && '1' === sanitize_text_field( wp_unslash( $_GET['magic_pages'] ) ) ) {
		$submenu_file = 'magic-pages-list';
	}
	// phpcs:enable WordPress.Security.NonceVerification.Recommended
}
add_action( 'admin_menu', 'magic_page_essentials_set_magic_pages_submenu_current', 999 );

/**
 * Cached counts for All / Magic / Non-Magic page tabs.
 *
 * @return array{all:int,magic:int}
 */
function magic_page_essentials_get_page_view_counts() {
	$cache_key = 'magic_page_essentials_page_view_counts';
	$cached    = wp_cache_get( $cache_key, 'magic_page_essentials' );
	if ( false !== $cached && is_array( $cached ) && isset( $cached['all'], $cached['magic'] ) ) {
		return $cached;
	}

	global $wpdb;

	// phpcs:disable WordPress.DB.DirectDatabaseQuery.DirectQuery,WordPress.DB.DirectDatabaseQuery.NoCaching -- Aggregates for admin list tabs; cached above.
	$all_count = (int) $wpdb->get_var(
		"SELECT COUNT(ID) FROM {$wpdb->posts}
		WHERE post_type = 'page' AND post_status IN ('publish','draft','pending')"
	);

	$magic_count = (int) $wpdb->get_var(
		"SELECT COUNT(DISTINCT p.ID)
		FROM {$wpdb->posts} p
		INNER JOIN {$wpdb->postmeta} pm ON p.ID = pm.post_id
		WHERE p.post_type = 'page'
		AND pm.meta_key = '_location_id'
		AND p.post_status IN ('publish','draft','pending')"
	);
	// phpcs:enable WordPress.DB.DirectDatabaseQuery.DirectQuery,WordPress.DB.DirectDatabaseQuery.NoCaching

	$out = array(
		'all'   => $all_count,
		'magic' => $magic_count,
	);
	wp_cache_set( $cache_key, $out, 'magic_page_essentials', MINUTE_IN_SECONDS * 5 );

	return $out;
}

/**
 * Add view tabs to the Pages admin list.
 *
 * @param array<string,string> $views Views.
 * @return array<string,string>
 */
function magic_page_essentials_add_magic_pages_views( $views ) {
	$counts        = magic_page_essentials_get_page_view_counts();
	$all_count     = (int) $counts['all'];
	$magic_count   = (int) $counts['magic'];
	$non_magic_count = max( 0, $all_count - $magic_count );

	// phpcs:disable WordPress.Security.NonceVerification.Recommended -- Read-only admin list filter state.
	$current = '';
	if ( isset( $_GET['magic_pages'] ) ) {
		$current = sanitize_text_field( wp_unslash( $_GET['magic_pages'] ) );
	}
	// phpcs:enable WordPress.Security.NonceVerification.Recommended

	$views['all'] = sprintf(
		'<a href="%s"%s>%s <span class="count">(%d)</span></a>',
		esc_url( admin_url( 'edit.php?post_type=page' ) ),
		'' === $current ? ' class="current"' : '',
		esc_html__( 'All', 'magic-page-essentials' ),
		$all_count
	);

	$views['magic'] = sprintf(
		'<a href="%s"%s>%s <span class="count">(%d)</span></a>',
		esc_url( admin_url( 'edit.php?post_type=page&magic_pages=1' ) ),
		'1' === $current ? ' class="current"' : '',
		esc_html__( 'Magic Pages', 'magic-page-essentials' ),
		$magic_count
	);

	$views['non_magic'] = sprintf(
		'<a href="%s"%s>%s <span class="count">(%d)</span></a>',
		esc_url( admin_url( 'edit.php?post_type=page&magic_pages=0' ) ),
		'0' === $current ? ' class="current"' : '',
		esc_html__( 'Non-Magic Pages', 'magic-page-essentials' ),
		$non_magic_count
	);

	return $views;
}
add_filter( 'views_edit-page', 'magic_page_essentials_add_magic_pages_views' );

/**
 * Modify the main query based on magic_pages filter.
 *
 * @param WP_Query $query Query.
 * @return void
 */
function magic_page_essentials_filter_magic_pages_in_admin_query( $query ) {
	global $pagenow;

	// phpcs:disable WordPress.Security.NonceVerification.Recommended -- Admin list filter query vars.
	if ( is_admin() && 'edit.php' === $pagenow && $query->is_main_query() && 'page' === $query->get( 'post_type' ) && isset( $_GET['magic_pages'] ) ) {
		$magic_filter = sanitize_text_field( wp_unslash( $_GET['magic_pages'] ) );
		// phpcs:enable WordPress.Security.NonceVerification.Recommended

		if ( '1' === $magic_filter ) {
			$query->set(
				'meta_query',
				array(
					array(
						'key'     => '_location_id',
						'compare' => 'EXISTS',
					),
				)
			);
		} elseif ( '0' === $magic_filter ) {
			$query->set(
				'meta_query',
				array(
					array(
						'key'     => '_location_id',
						'compare' => 'NOT EXISTS',
					),
				)
			);
		}
	}
}
add_action( 'pre_get_posts', 'magic_page_essentials_filter_magic_pages_in_admin_query' );

/**
 * Default the Pages list to Non-Magic when no filters are applied.
 *
 * @return void
 */
function magic_page_essentials_redirect_pages_to_non_magic_default() {
	global $pagenow;

	if ( ! is_admin() ) {
		return;
	}

	// phpcs:disable WordPress.Security.NonceVerification.Recommended -- Admin list URL state only.
	if ( 'edit.php' === $pagenow && isset( $_GET['post_type'] ) && 'page' === sanitize_key( wp_unslash( $_GET['post_type'] ) ) ) {
		if ( ! isset( $_GET['magic_pages'] ) && ! isset( $_GET['s'] ) && ! isset( $_GET['post_status'] ) && ! isset( $_GET['paged'] ) ) {
			wp_safe_redirect( admin_url( 'edit.php?post_type=page&magic_pages=0' ) );
			exit;
		}
	}
	// phpcs:enable WordPress.Security.NonceVerification.Recommended
}
add_action( 'admin_init', 'magic_page_essentials_redirect_pages_to_non_magic_default' );

/**
 * Group filter dropdown on the Pages list.
 *
 * @return void
 */
function magic_page_essentials_add_magic_page_group_filter() {
	global $typenow;
	if ( 'page' !== $typenow ) {
		return;
	}

	$groups = get_option( '_magic_page_groups' );
	if ( ! $groups || ! is_array( $groups ) ) {
		return;
	}

	// phpcs:disable WordPress.Security.NonceVerification.Recommended -- GET filter for posts list.
	$selected = '';
	if ( isset( $_GET['_group_id'] ) ) {
		$selected = sanitize_text_field( wp_unslash( $_GET['_group_id'] ) );
	}
	// phpcs:enable WordPress.Security.NonceVerification.Recommended

	echo '<select name="_group_id">';
	echo '<option value="">' . esc_html__( 'All Groups', 'magic-page-essentials' ) . '</option>';
	foreach ( $groups as $group_id => $group_data ) {
		$title = is_array( $group_data ) && isset( $group_data['title'] ) ? $group_data['title'] : ( is_string( $group_data ) ? $group_data : (string) $group_id );
		printf(
			'<option value="%s"%s>%s</option>',
			esc_attr( (string) $group_id ),
			selected( $selected, (string) $group_id, false ),
			esc_html( $title )
		);
	}
	echo '</select>';
}
add_action( 'restrict_manage_posts', 'magic_page_essentials_add_magic_page_group_filter' );

/**
 * Filter pages by Magic Page group meta.
 *
 * @param WP_Query $query Query.
 * @return void
 */
function magic_page_essentials_filter_pages_by_magic_page_group( $query ) {
	global $pagenow;
	if ( ! is_admin() || 'edit.php' !== $pagenow || 'page' !== $query->get( 'post_type' ) ) {
		return;
	}

	// phpcs:disable WordPress.Security.NonceVerification.Recommended -- Admin list filter.
	if ( isset( $_GET['_group_id'] ) && '' !== $_GET['_group_id'] ) {
		$group_id = sanitize_text_field( wp_unslash( $_GET['_group_id'] ) );
		// phpcs:enable WordPress.Security.NonceVerification.Recommended

		$meta_query   = $query->get( 'meta_query' );
		$meta_query   = is_array( $meta_query ) ? $meta_query : array();
		$meta_query[] = array(
			'key'     => '_group_id',
			'value'   => $group_id,
			'compare' => '=',
		);
		$query->set( 'meta_query', $meta_query );
	}
}
add_action( 'pre_get_posts', 'magic_page_essentials_filter_pages_by_magic_page_group' );

/**
 * Invalidate cached tab counts when any post is saved.
 *
 * @return void
 */
function magic_page_essentials_bust_page_view_count_cache() {
	wp_cache_delete( 'magic_page_essentials_page_view_counts', 'magic_page_essentials' );
}
add_action( 'save_post', 'magic_page_essentials_bust_page_view_count_cache' );
