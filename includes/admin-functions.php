<?php

// Add "Magic Pages" as a submenu under Pages (same list, defaulting to magic pages only)
add_action( 'admin_menu', 'mpe_add_magic_pages_submenu_under_pages', 20 );
function mpe_add_magic_pages_submenu_under_pages() {
	add_submenu_page(
		'edit.php?post_type=page',
		__( 'Magic Pages', 'magic-page-essentials' ),
		__( 'Magic Pages', 'magic-page-essentials' ),
		'edit_pages',
		'magic-pages-list',
		'mpe_redirect_to_magic_pages_list'
	);
}

function mpe_redirect_to_magic_pages_list() {
	wp_safe_redirect( admin_url( 'edit.php?post_type=page&magic_pages=1' ) );
	exit;
}

// When viewing the magic-pages-filtered list, highlight "Magic Pages" in the submenu
add_action( 'admin_menu', 'mpe_set_magic_pages_submenu_current', 999 );
function mpe_set_magic_pages_submenu_current() {
	global $pagenow, $submenu_file;
	if ( $pagenow !== 'edit.php' || ! isset( $_GET['post_type'] ) || $_GET['post_type'] !== 'page' ) {
		return;
	}
	if ( isset( $_GET['magic_pages'] ) && $_GET['magic_pages'] === '1' ) {
		$submenu_file = 'magic-pages-list';
	}
}

// Add view tabs to the Pages admin list
function add_magic_pages_views( $views ) {
    global $wpdb;

    // Count all pages
    $all_count = $wpdb->get_var( "
        SELECT COUNT(ID) FROM {$wpdb->posts}
        WHERE post_type = 'page' AND post_status IN ('publish','draft','pending')
    " );

    // Count Magic Pages (have _location_id meta)
    $magic_count = $wpdb->get_var( "
        SELECT COUNT(DISTINCT p.ID)
        FROM {$wpdb->posts} p
        INNER JOIN {$wpdb->postmeta} pm ON p.ID = pm.post_id
        WHERE p.post_type = 'page' 
        AND pm.meta_key = '_location_id'
        AND p.post_status IN ('publish','draft','pending')
    " );

    // Non-Magic Pages count = all - magic
    $non_magic_count = $all_count - $magic_count;

    // Get current filter
    $current = isset($_GET['magic_pages']) ? $_GET['magic_pages'] : '';

    $views['all'] = sprintf(
        '<a href="%s"%s>%s <span class="count">(%d)</span></a>',
        admin_url( 'edit.php?post_type=page' ),
        $current === '' ? ' class="current"' : '',
        __('All'),
        intval($all_count)
    );

    $views['magic'] = sprintf(
        '<a href="%s"%s>%s <span class="count">(%d)</span></a>',
        admin_url( 'edit.php?post_type=page&magic_pages=1' ),
        $current === '1' ? ' class="current"' : '',
        __('Magic Pages'),
        intval($magic_count)
    );

    $views['non_magic'] = sprintf(
        '<a href="%s"%s>%s <span class="count">(%d)</span></a>',
        admin_url( 'edit.php?post_type=page&magic_pages=0' ),
        $current === '0' ? ' class="current"' : '',
        __('Non-Magic Pages'),
        intval($non_magic_count)
    );

    return $views;
}
add_filter( 'views_edit-page', 'add_magic_pages_views' );


// Modify the main query based on magic_pages filter
function filter_magic_pages_in_admin_query( $query ) {
    global $pagenow;

    if ( is_admin() && $pagenow === 'edit.php' && $query->is_main_query() && $query->get('post_type') === 'page' ) {
        
        // Grab filter param from $_GET, since it's not a registered query var
        if ( isset($_GET['magic_pages']) ) {
            $magic_filter = sanitize_text_field( $_GET['magic_pages'] );

            if ( $magic_filter === '1' ) {
                $query->set( 'meta_query', [
                    [
                        'key'     => '_location_id',
                        'compare' => 'EXISTS',
                    ],
                ]);
            } elseif ( $magic_filter === '0' ) {
                $query->set( 'meta_query', [
                    [
                        'key'     => '_location_id',
                        'compare' => 'NOT EXISTS',
                    ],
                ]);
            }
        }
    }
}
add_action( 'pre_get_posts', 'filter_magic_pages_in_admin_query' );

function redirect_pages_to_non_magic_default() {
    global $pagenow;

    if ( ! is_admin() ) {
        return;
    }

    // Only redirect on the pages admin list screen with no query params filtering
    if ( $pagenow === 'edit.php' && isset( $_GET['post_type'] ) && $_GET['post_type'] === 'page' ) {
        // If no filter set
        if ( ! isset( $_GET['magic_pages'] ) && ! isset( $_GET['s'] ) && ! isset( $_GET['post_status'] ) && ! isset( $_GET['paged'] ) ) {
            // Prevent redirect loop: only redirect if no redirect cookie (optional)
            wp_safe_redirect( admin_url( 'edit.php?post_type=page&magic_pages=0' ) );
            exit;
        }
    }
}
add_action( 'admin_init', 'redirect_pages_to_non_magic_default' );

add_action( 'restrict_manage_posts', 'add_magic_page_group_filter' );
function add_magic_page_group_filter() {
    global $typenow;
    if ( 'page' !== $typenow ) {
        return;
    }

    // Get groups from wp_options
    $groups = get_option( '_magic_page_groups' );
    if ( ! $groups || ! is_array( $groups ) ) {
        return;
    }

    // Get selected value from $_GET
    $selected = isset( $_GET['_group_id'] ) ? sanitize_text_field( $_GET['_group_id'] ) : '';

    echo '<select name="_group_id">';
    echo '<option value="">All Groups</option>';
    foreach ( $groups as $group_id => $group_data ) {
        $title = is_array( $group_data ) && isset( $group_data['title'] ) ? $group_data['title'] : ( is_string( $group_data ) ? $group_data : (string) $group_id ) ;
        printf(
            '<option value="%s"%s>%s</option>',
            esc_attr( $group_id ),
            selected( $selected, $group_id, false ),
            esc_html( $title )
        );
    }
    echo '</select>';
}

add_action( 'pre_get_posts', 'filter_pages_by_magic_page_group' );
function filter_pages_by_magic_page_group( $query ) {
    global $pagenow;
    if ( ! is_admin() || 'edit.php' !== $pagenow || $query->get( 'post_type' ) !== 'page' ) {
        return;
    }

    if ( isset( $_GET['_group_id'] ) && $_GET['_group_id'] !== '' ) {
        $meta_query = $query->get( 'meta_query' ) ?: array();
        $meta_query[] = array(
            'key'     => '_group_id',
            'value'   => sanitize_text_field( $_GET['_group_id'] ),
            'compare' => '='
        );
        $query->set( 'meta_query', $meta_query );
    }
}
