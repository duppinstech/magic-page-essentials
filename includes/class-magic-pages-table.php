<?php
/**
 * Optional WP_List_Table for Magic Pages (not loaded by default).
 *
 * @package Magic_Page_Essentials
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

if ( ! class_exists( 'WP_List_Table' ) ) {
	require_once ABSPATH . 'wp-admin/includes/class-wp-list-table.php';
}

/**
 * Admin list table for pages that have Magic Page `_location_id` meta.
 */
class Magic_Pages_List_Table extends WP_List_Table {

	/**
	 * @return void
	 */
	public function __construct() {
		parent::__construct(
			array(
				'singular' => 'custom_magic_page',
				'plural'   => 'custom_magic_pages',
				'ajax'     => false,
			)
		);
	}

	/**
	 * @return array<string,string>
	 */
	public function get_columns() {
		return array(
			'cb'     => __( 'Select', 'magic-page-essentials' ),
			'title'  => __( 'Title', 'magic-page-essentials' ),
			'author' => __( 'Author', 'magic-page-essentials' ),
			'date'   => __( 'Date', 'magic-page-essentials' ),
		);
	}

	/**
	 * @return array<string,array{0:string,1:bool}>
	 */
	public function get_sortable_columns() {
		return array(
			'title'  => array( 'title', false ),
			'author' => array( 'author', false ),
			'date'   => array( 'date', false ),
		);
	}

	/**
	 * @param object $item        Row object.
	 * @param string $column_name Column key.
	 * @return string
	 */
	public function column_default( $item, $column_name ) {
		if ( isset( $item->$column_name ) ) {
			return esc_html( (string) $item->$column_name );
		}
		return '—';
	}

	/**
	 * @param object $item Row object.
	 * @return string
	 */
	public function column_cb( $item ) {
		return sprintf( '<input type="checkbox" name="post[]" value="%s" />', esc_attr( (string) $item->ID ) );
	}

	/**
	 * @param object $item Row object.
	 * @return string
	 */
	public function column_title( $item ) {
		$raw_title = isset( $item->title ) ? (string) $item->title : '';
		$post_obj  = get_post( $item->ID );

		$processed_title = $raw_title;

		if ( function_exists( 'get_magic_page_title' ) && $post_obj instanceof WP_Post ) {
			$processed_title = get_magic_page_title( $raw_title, $post_obj );
		}

		if ( function_exists( 'parse_magic_page_if_shortcode' ) ) {
			$processed_title = parse_magic_page_if_shortcode( $processed_title );
		}

		if ( function_exists( 'apply_spintax_filter' ) ) {
			$processed_title = apply_spintax_filter( $processed_title );
		}

		if ( has_filter( 'cities' ) || has_shortcode( $processed_title, '' ) ) {
			// phpcs:ignore WordPress.NamingConventions.PrefixAllGlobals.NonPrefixedHooknameFound -- Magic Page vendor filter.
			$processed_title = apply_filters( 'cities', do_shortcode( $processed_title ) );
		}

		$edit_link = get_edit_post_link( $item->ID );
		$view_link = get_permalink( $item->ID );

		$actions = array(
			'edit' => sprintf( '<a href="%s">%s</a>', esc_url( $edit_link ), esc_html__( 'Edit', 'magic-page-essentials' ) ),
			'view' => sprintf( '<a href="%s" rel="permalink">%s</a>', esc_url( $view_link ), esc_html__( 'View', 'magic-page-essentials' ) ),
		);

		return sprintf(
			'<strong><a href="%s">%s</a></strong> %s',
			esc_url( $edit_link ),
			wp_kses_post( $processed_title ),
			wp_kses_post( $this->row_actions( $actions ) )
		);
	}

	/**
	 * @param object $item Row object.
	 * @return string
	 */
	public function column_author( $item ) {
		$author = get_userdata( (int) $item->author );
		return esc_html( $author ? $author->display_name : '' );
	}

	/**
	 * @param object $item Row object.
	 * @return string
	 */
	public function column_date( $item ) {
		return esc_html( mysql2date( get_option( 'date_format' ), $item->date ) );
	}

	/**
	 * @return void
	 */
	public function prepare_items() {
		global $wpdb;

		$per_page     = 20;
		$current_page = $this->get_pagenum();
		$offset       = ( $current_page - 1 ) * $per_page;

		$orderby_map = array(
			'title'  => 'p.post_title',
			'author' => 'p.post_author',
			'date'   => 'p.post_date',
		);

		// phpcs:disable WordPress.Security.NonceVerification.Recommended -- Sort keys are validated against $orderby_map; order is ASC|DESC only.
		$orderby_key = isset( $_REQUEST['orderby'] ) ? sanitize_key( wp_unslash( $_REQUEST['orderby'] ) ) : '';
		$order_raw   = isset( $_REQUEST['order'] ) ? strtoupper( sanitize_text_field( wp_unslash( $_REQUEST['order'] ) ) ) : 'DESC';
		// phpcs:enable WordPress.Security.NonceVerification.Recommended

		$orderby = isset( $orderby_map[ $orderby_key ] ) ? $orderby_map[ $orderby_key ] : 'p.post_date';
		$order   = ( 'ASC' === $order_raw ) ? 'ASC' : 'DESC';

		// phpcs:disable WordPress.DB.DirectDatabaseQuery.DirectQuery,WordPress.DB.DirectDatabaseQuery.NoCaching,WordPress.DB.PreparedSQL.InterpolatedNotPrepared,PluginCheck.Security.DirectDB.UnescapedDBParameter -- ORDER BY is from $orderby_map / ASC|DESC whitelist only.
		$total_items = (int) $wpdb->get_var(
			"SELECT COUNT(DISTINCT p.ID)
			FROM {$wpdb->posts} p
			INNER JOIN {$wpdb->postmeta} pm ON p.ID = pm.post_id
			WHERE p.post_type = 'page'
			AND pm.meta_key = '_location_id'
			AND p.post_status IN ('publish','draft','pending')"
		);

		$results = $wpdb->get_results(
			$wpdb->prepare(
				"SELECT p.ID, p.post_title AS title, p.post_author AS author, p.post_date AS date
				FROM {$wpdb->posts} p
				INNER JOIN {$wpdb->postmeta} pm ON p.ID = pm.post_id
				WHERE p.post_type = 'page'
				AND pm.meta_key = '_location_id'
				AND p.post_status IN ('publish','draft','pending')
				ORDER BY {$orderby} {$order}
				LIMIT %d OFFSET %d",
				$per_page,
				$offset
			),
			OBJECT
		);
		// phpcs:enable WordPress.DB.DirectDatabaseQuery.DirectQuery,WordPress.DB.DirectDatabaseQuery.NoCaching,WordPress.DB.PreparedSQL.InterpolatedNotPrepared,PluginCheck.Security.DirectDB.UnescapedDBParameter

		$this->items = is_array( $results ) ? $results : array();

		$columns  = $this->get_columns();
		$hidden   = array();
		$sortable = $this->get_sortable_columns();
		$this->_column_headers = array( $columns, $hidden, $sortable );

		$this->set_pagination_args(
			array(
				'total_items' => $total_items,
				'per_page'    => $per_page,
				'total_pages' => $per_page > 0 ? (int) ceil( $total_items / $per_page ) : 0,
			)
		);
	}

	/**
	 * @return void
	 */
	public function no_items() {
		esc_html_e( 'No Magic Pages found.', 'magic-page-essentials' );
	}
}
