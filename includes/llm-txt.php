<?php
/**
 * Serve /llm.txt for LLM discovery (plain text index of site content).
 *
 * @package Magic_Page_Essentials
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

add_action( 'init', 'mpe_llm_txt_intercept_request', 0 );

/**
 * Whether the current request targets llm.txt (works on subdirectory multisite, e.g. /site1/llm.txt).
 *
 * @return bool
 */
function mpe_llm_txt_request_matches() {
	$request_uri = isset( $_SERVER['REQUEST_URI'] ) ? wp_unslash( $_SERVER['REQUEST_URI'] ) : '';
	$path        = wp_parse_url( $request_uri, PHP_URL_PATH );
	if ( ! is_string( $path ) || '' === $path ) {
		return false;
	}
	$basename = basename( untrailingslashit( $path ) );

	return 'llm.txt' === $basename;
}

/**
 * Handle requests to /llm.txt (last path segment; supports subdirectory multisite).
 */
function mpe_llm_txt_intercept_request() {
	if ( is_admin() || ( defined( 'DOING_CRON' ) && DOING_CRON ) ) {
		return;
	}

	if ( ! mpe_llm_txt_request_matches() ) {
		return;
	}

	/**
	 * Allow disabling llm.txt output (e.g. on a specific subsite).
	 *
	 * @param bool $serve Whether to serve llm.txt for this request.
	 */
	if ( ! apply_filters( 'mpe_llm_txt_serve', true ) ) {
		return;
	}

	while ( ob_get_level() ) {
		ob_end_clean();
	}
	ob_start();

	$site_name   = get_bloginfo( 'name' );
	$description = get_bloginfo( 'description' );

	$content  = "# {$site_name}\n\n";
	$content .= "> {$description}\n\n";
	$content .= "## Pages\n\n";

	$pages = get_posts(
		[
			'post_type'      => 'page',
			'post_status'    => 'publish',
			'posts_per_page' => -1,
			'orderby'        => 'title',
			'order'          => 'ASC',
			'no_found_rows'  => true,
		]
	);

	foreach ( $pages as $page ) {
		$title   = mpe_llm_txt_resolve_title( $page );
		$permalink = get_permalink( $page->ID );
		if ( $permalink ) {
			$content .= '- [' . mpe_llm_txt_markdown_link_label( $title ) . '](' . esc_url( $permalink ) . ")\n";
		}
	}
	wp_reset_postdata();

	$content .= "\n## Posts\n\n";

	$posts = get_posts(
		[
			'post_type'      => 'post',
			'post_status'    => 'publish',
			'posts_per_page' => 50,
			'orderby'        => 'date',
			'order'          => 'DESC',
			'no_found_rows'  => true,
		]
	);

	foreach ( $posts as $post ) {
		$title     = mpe_llm_txt_resolve_title( $post );
		$permalink = get_permalink( $post->ID );
		if ( $permalink ) {
			$content .= '- [' . mpe_llm_txt_markdown_link_label( $title ) . '](' . esc_url( $permalink ) . ")\n";
		}
	}
	wp_reset_postdata();

	ob_end_clean();

	header( 'Content-Type: text/plain; charset=utf-8' );
	header( 'Cache-Control: public, max-age=86400' );
	echo $content; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- plain text llm.txt
	exit;
}

/**
 * Escape text for use as a Markdown link label ([label](url)).
 *
 * @param string $text Raw label text.
 * @return string
 */
function mpe_llm_txt_markdown_link_label( $text ) {
	$text = wp_strip_all_tags( (string) $text );
	// Unbalanced ] breaks link parsing; escape closing brackets in labels.
	return str_replace( ']', '\\]', $text );
}

/**
 * Resolve a post's display title through Magic Page helpers when available.
 *
 * @param WP_Post $post_obj Post object.
 * @return string
 */
function mpe_llm_txt_resolve_title( WP_Post $post_obj ) {
	$title = get_the_title( $post_obj );

	if ( function_exists( 'get_magic_page_title' ) ) {
		$title = get_magic_page_title( $title, $post_obj );
	}
	if ( function_exists( 'parse_magic_page_if_shortcode' ) ) {
		$title = parse_magic_page_if_shortcode( $title );
	}
	if ( function_exists( 'apply_spintax_filter' ) ) {
		$title = apply_spintax_filter( $title );
	}

	if ( has_filter( 'cities' ) || strpos( $title, '[' ) !== false ) {
		$title = apply_filters( 'cities', do_shortcode( $title ) );
	}

	return $title;
}
