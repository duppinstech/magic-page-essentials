<?php
/**
 * Yoast SEO replacement variables for Magic Page (%%mpp_*%%).
 *
 * @package Magic_Page_Essentials
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class MPE_Yoast_Bridge {

	public static function init() {
		add_action( 'wpseo_register_extra_replacements', [ __CLASS__, 'register_replacements' ] );
		add_action( 'template_redirect', [ __CLASS__, 'warm_term_cache' ], 25 );
	}

	/**
	 * @return WP_Term|null
	 */
	public static function get_location_term( $yoast_args = null ) {
		static $term = null;

		if ( $term instanceof WP_Term ) {
			return $term;
		}

		$t = self::try_resolve_location_term( $yoast_args );

		if ( $t && ! is_wp_error( $t ) ) {
			$term = $t;
			return $term;
		}

		return null;
	}

	/**
	 * @param object|null $yoast_args Yoast replace-vars context.
	 * @return WP_Term|null
	 */
	protected static function try_resolve_location_term( $yoast_args = null ) {
		global $wp_query;

		if ( $wp_query && $wp_query->get( 'magic_page_term' ) ) {
			$t = $wp_query->get( 'magic_page_term' );
			if ( $t && ! is_wp_error( $t ) ) {
				return self::freshen_location_term( $t );
			}
		}

		if ( function_exists( 'getMagicpageLocation' ) ) {
			$t = getMagicpageLocation();
			if ( $t && ! is_wp_error( $t ) ) {
				return self::freshen_location_term( $t );
			}
		}

		if ( function_exists( 'get_location_object' ) ) {
			$t = get_location_object();
			if ( $t && ! is_wp_error( $t ) ) {
				return self::freshen_location_term( $t );
			}
		}

		if ( $wp_query && function_exists( 'magic_page_default_post_slug' ) ) {
			$mp_slug = magic_page_default_post_slug();
			if ( ! empty( $wp_query->query[ $mp_slug ] )
				&& isset( $wp_query->query['post_type'] )
				&& $wp_query->query['post_type'] === $mp_slug ) {
				$t = get_term_by( 'slug', $wp_query->query[ $mp_slug ], 'location' );
				if ( $t && ! is_wp_error( $t ) ) {
					return self::freshen_location_term( $t );
				}
			}
		}

		$post_id = 0;
		if ( $yoast_args && is_object( $yoast_args ) ) {
			if ( ! empty( $yoast_args->ID ) ) {
				$post_id = (int) $yoast_args->ID;
			} elseif ( ! empty( $yoast_args->id ) ) {
				$post_id = (int) $yoast_args->id;
			}
		}
		if ( $post_id ) {
			$loc_id = get_post_meta( $post_id, '_location_id', true );
			if ( $loc_id ) {
				$t = get_term( (int) $loc_id, 'location' );
				if ( $t && ! is_wp_error( $t ) ) {
					return $t;
				}
			}
		}

		global $post;
		if ( $post && isset( $post->ID ) ) {
			$loc_id = get_post_meta( (int) $post->ID, '_location_id', true );
			if ( $loc_id ) {
				$t = get_term( (int) $loc_id, 'location' );
				if ( $t && ! is_wp_error( $t ) ) {
					return $t;
				}
			}
		}

		return null;
	}

	/**
	 * @param WP_Term|mixed $term Term object.
	 * @return WP_Term|null
	 */
	protected static function freshen_location_term( $term ) {
		if ( ! $term || is_wp_error( $term ) || empty( $term->term_id ) ) {
			return null;
		}
		$tax = isset( $term->taxonomy ) ? $term->taxonomy : 'location';
		$fresh = get_term( (int) $term->term_id, $tax );
		if ( $fresh && ! is_wp_error( $fresh ) ) {
			return $fresh;
		}
		return $term instanceof WP_Term ? $term : null;
	}

	/**
	 * @param string      $meta_key   Term meta key.
	 * @param object|null $yoast_args Optional Yoast context.
	 * @return string
	 */
	public static function term_meta( $meta_key, $yoast_args = null ) {
		$term = self::get_location_term( $yoast_args );
		if ( ! $term || ! isset( $term->term_id ) ) {
			return '';
		}
		$val = get_term_meta( $term->term_id, $meta_key, true );
		return is_scalar( $val ) ? (string) $val : '';
	}

	/**
	 * Resolve the location term for a specific post (e.g. static Magic Page export via _location_id).
	 * Does not use the request-scoped cache in get_location_term().
	 *
	 * @param int $post_id Post ID.
	 * @return WP_Term|null
	 */
	public static function get_location_term_for_post( $post_id ) {
		$post_id = (int) $post_id;
		if ( $post_id <= 0 ) {
			return null;
		}
		$loc_id = get_post_meta( $post_id, '_location_id', true );
		if ( $loc_id ) {
			$t = get_term( (int) $loc_id, 'location' );
			if ( $t && ! is_wp_error( $t ) ) {
				return self::freshen_location_term( $t );
			}
		}
		return null;
	}

	/**
	 * Replace %%mpp_*%% placeholders using an explicit location term (Yoast-style vars; works without Yoast).
	 *
	 * @param string         $text Title or fragment.
	 * @param WP_Term|null   $term Location term or null (placeholders become empty).
	 * @return string
	 */
	public static function replace_mpp_tokens_in_string( $text, $term ) {
		if ( ! is_string( $text ) || $text === '' || strpos( $text, '%%mpp_' ) === false ) {
			return $text;
		}

		$term_ok = ( $term instanceof WP_Term ) && ! is_wp_error( $term );

		$name = ( $term_ok && isset( $term->name ) ) ? (string) $term->name : '';
		$slug = ( $term_ok && isset( $term->slug ) ) ? (string) $term->slug : '';

		$tid = ( $term_ok && isset( $term->term_id ) ) ? (int) $term->term_id : 0;

		$region  = $tid ? (string) get_term_meta( $tid, 'region', true ) : '';
		$zip     = $tid ? (string) get_term_meta( $tid, 'zip', true ) : '';
		$county  = $tid ? (string) get_term_meta( $tid, 'county', true ) : '';
		$country = $tid ? (string) get_term_meta( $tid, 'country', true ) : '';
		$lat     = $tid ? (string) get_term_meta( $tid, 'lat', true ) : '';
		$lon     = $tid ? (string) get_term_meta( $tid, 'lon', true ) : '';

		$desc = '';
		if ( $tid ) {
			$desc = term_description( $tid );
			$desc = is_string( $desc ) ? $desc : '';
			/** This filter is documented in the Magic Page Essentials Yoast bridge. */
			$desc = apply_filters( 'magic_page_essentials_yoast_bridge_term_description', $desc, $term );
			$desc = wp_strip_all_tags( $desc );
		}

		$map = array(
			'%%mpp_location%%'    => $name,
			'%%mpp_slug%%'        => $slug,
			'%%mpp_region%%'      => $region,
			'%%mpp_zip%%'         => $zip,
			'%%mpp_county%%'      => $county,
			'%%mpp_country%%'     => $country,
			'%%mpp_lat%%'         => $lat,
			'%%mpp_lon%%'         => $lon,
			'%%mpp_description%%' => $desc,
		);

		$text = str_replace( array_keys( $map ), array_values( $map ), $text );

		// Typo / export glitch: closing `%%` written as single `%` (e.g. "in %%mpp_location%, %%mpp_region%%").
		foreach ( $map as $canonical => $value ) {
			$broken = substr( $canonical, 0, -1 ); // ...%  instead of ...%%.
			if ( $broken !== $canonical && strpos( $text, $broken ) !== false ) {
				$text = str_replace( $broken, $value, $text );
			}
		}

		return $text;
	}

	/**
	 * Run Yoast SEO replacement on a string for a specific post (admin/analytics-safe).
	 *
	 * @param string $text    Text that may contain %%variables%%.
	 * @param int    $post_id Post ID for context.
	 * @return string
	 */
	public static function replace_yoast_variables_in_string( $text, $post_id ) {
		if ( ! is_string( $text ) || $text === '' || strpos( $text, '%%' ) === false ) {
			return $text;
		}
		if ( ! defined( 'WPSEO_VERSION' ) || ! class_exists( 'WPSEO_Replace_Vars' ) ) {
			return $text;
		}

		$post_id = (int) $post_id;
		if ( $post_id <= 0 ) {
			return $text;
		}

		$post_row = get_post( $post_id, ARRAY_A );
		if ( ! is_array( $post_row ) ) {
			return $text;
		}

		$replacer = new WPSEO_Replace_Vars();
		return $replacer->replace( $text, $post_row );
	}

	public static function register_replacements() {
		if ( ! function_exists( 'wpseo_register_var_replacement' ) ) {
			return;
		}

		wpseo_register_var_replacement(
			'mpp_location',
			function ( $var_name = '', $args = null ) {
				$term = self::get_location_term( $args );
				return ( $term && ! is_wp_error( $term ) && isset( $term->name ) ) ? $term->name : '';
			},
			'basic',
			'Magic Page: current location name'
		);

		wpseo_register_var_replacement(
			'mpp_slug',
			function ( $var_name = '', $args = null ) {
				$term = self::get_location_term( $args );
				return ( $term && ! is_wp_error( $term ) && isset( $term->slug ) ) ? $term->slug : '';
			},
			'advanced',
			'Magic Page: location slug'
		);

		wpseo_register_var_replacement(
			'mpp_region',
			function ( $var_name = '', $args = null ) {
				return self::term_meta( 'region', $args );
			},
			'basic',
			'Magic Page: region (term meta)'
		);

		wpseo_register_var_replacement(
			'mpp_zip',
			function ( $var_name = '', $args = null ) {
				return self::term_meta( 'zip', $args );
			},
			'basic',
			'Magic Page: ZIP (term meta)'
		);

		wpseo_register_var_replacement(
			'mpp_county',
			function ( $var_name = '', $args = null ) {
				return self::term_meta( 'county', $args );
			},
			'basic',
			'Magic Page: county (term meta)'
		);

		wpseo_register_var_replacement(
			'mpp_country',
			function ( $var_name = '', $args = null ) {
				return self::term_meta( 'country', $args );
			},
			'basic',
			'Magic Page: country (term meta)'
		);

		wpseo_register_var_replacement(
			'mpp_lat',
			function ( $var_name = '', $args = null ) {
				return self::term_meta( 'lat', $args );
			},
			'advanced',
			'Magic Page: latitude (term meta)'
		);

		wpseo_register_var_replacement(
			'mpp_lon',
			function ( $var_name = '', $args = null ) {
				return self::term_meta( 'lon', $args );
			},
			'advanced',
			'Magic Page: longitude (term meta)'
		);

		wpseo_register_var_replacement(
			'mpp_description',
			function ( $var_name = '', $args = null ) {
				$term = self::get_location_term( $args );
				if ( ! $term || is_wp_error( $term ) || empty( $term->term_id ) ) {
					return '';
				}
				$text = term_description( $term->term_id );
				$text = is_string( $text ) ? $text : '';
				/** This filter is documented in the Magic Page Essentials Yoast bridge. */
				$text = apply_filters( 'magic_page_essentials_yoast_bridge_term_description', $text, $term );
				return wp_strip_all_tags( $text );
			},
			'advanced',
			'Magic Page: location taxonomy description (same as [description])'
		);
	}

	public static function warm_term_cache() {
		if ( is_admin() ) {
			return;
		}
		self::get_location_term();
	}
}

/**
 * Back-compat entry point for the Yoast bridge location resolver.
 *
 * @param object|null $yoast_args Optional Yoast replace-vars context.
 * @return WP_Term|null
 */
function magic_page_essentials_yoast_bridge_get_location_term( $yoast_args = null ) {
	return MPE_Yoast_Bridge::get_location_term( $yoast_args );
}
