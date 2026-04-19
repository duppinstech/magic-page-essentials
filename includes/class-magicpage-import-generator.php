<?php
/**
 * Magic Page import file generator (PHP port of generator/magicpage_from_txt.py).
 *
 * @package Magic_Page_Essentials
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Builds PHP-serialized spintax shortcodes for Magic Page import from raw Google Doc / pasted HTML text.
 */
class MPE_Magic_Page_Import_Generator {

	/**
	 * @param string $raw_text Raw document text (HTML from export or paste).
	 * @return array{serialized:string,bytes:int,debug:array}|WP_Error
	 */
	public static function generate( $raw_text ) {
		if ( ! is_string( $raw_text ) || '' === trim( $raw_text ) ) {
			return new WP_Error( 'mpe_empty', __( 'No content to process.', 'magic-page-essentials' ) );
		}

		try {
			return self::run( $raw_text );
		} catch ( Exception $e ) {
			return new WP_Error( 'mpe_generate', $e->getMessage() );
		}
	}

	/**
	 * @param string $raw_text Raw text.
	 * @return array{serialized:string,bytes:int,debug:array}
	 */
	private static function run( $raw_text ) {
		$debug = array();

		$h1_match = array();
		preg_match( '/<h1[^>]*>(.*?)<\/h1>/is', $raw_text, $h1_match );
		$detected_location = null;
		$detected_state    = null;
		$h1_text             = '';

		if ( ! empty( $h1_match[1] ) ) {
			$h1_text = trim( $h1_match[1] );
			$parts   = explode( ',', $h1_text );
			if ( count( $parts ) >= 2 ) {
				$state_part = trim( $parts[ count( $parts ) - 1 ] );
				$before     = trim( $parts[ count( $parts ) - 2 ] );
				$words      = preg_split( '/\s+/', $before );
				$location_words = array();
				for ( $wi = count( $words ) - 1; $wi >= 0; $wi-- ) {
					$word = $words[ $wi ];
					if ( ctype_digit( $word ) || in_array( strtolower( $word ), array( 'assistance', 'roadside', 'towing', 'service', 'services' ), true ) ) {
						break;
					}
					array_unshift( $location_words, $word );
				}
				if ( $location_words && strlen( $state_part ) === 2 && ctype_upper( $state_part ) ) {
					$detected_location = implode( ' ', $location_words );
					$detected_state    = $state_part;
				}
			}
		}

		$state_pattern = '/\b\w+(?:\s+\w+)*,\s+([A-Z]{2})\b/';
		preg_match_all( $state_pattern, $raw_text, $state_m );
		$found_states = array();
		if ( ! empty( $state_m[1] ) ) {
			$found_states = array_unique( $state_m[1] );
		}

		$common_states = array(
			'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
		);
		$actual_states = array_intersect( $found_states, $common_states );
		$use_state_shortcode = count( $actual_states ) > 1;

		$detected_company = self::detect_company_name( $raw_text );

		$h1_text_processed = $h1_match
			? self::apply_shortcodes( $h1_text, $detected_location, $detected_state, $use_state_shortcode, $detected_company, null )
			: '24/7 Roadside Assistance [location], [meta_region_code]';
		$h1_content        = '<h1>' . $h1_text_processed . '</h1>';

		$version_pattern = '/<H1[^>]*>.*?<\/H1>.*?(?=<H1[^>]*>|$)/is';
		preg_match_all( $version_pattern, $raw_text, $vm );
		$version_matches = ! empty( $vm[0] ) ? $vm[0] : array();

		preg_match_all( '/<H1[^>]*>(.*?)<\/H1>/is', $raw_text, $h1m );
		$h1_matches = ! empty( $h1m[1] ) ? $h1m[1] : array();

		$version_data          = array();
		$category_versions     = array(
			'roadside'  => array(),
			'heavy'     => array(),
			'towing'    => array(),
			'equipment' => array(),
		);
		$category_ul_items     = array();
		$category_version_counters = array();

		foreach ( $version_matches as $version_index => $version_content ) {
			preg_match_all( '/<H2[^>]*>(.*?)<\/H2>/is', $version_content, $h2m );
			$h2s = ! empty( $h2m[1] ) ? $h2m[1] : array();

			$detected_city = null;
			foreach ( $h2s as $h2_text ) {
				$city = self::detect_city_from_h2( $h2_text );
				if ( $city ) {
					$detected_city = $city;
					break;
				}
			}

			if ( isset( $h1_matches[ $version_index ] ) ) {
				$h1_text_v = trim( $h1_matches[ $version_index ] );
				$category  = self::categorize_by_h1( $h1_text_v );
				$h1_proc   = self::apply_shortcodes( $h1_text_v, $detected_location, $detected_state, $use_state_shortcode, $detected_company, $detected_city );
				$h1_block  = '<h1>' . $h1_proc . '</h1>';
			} else {
				$h1_block = '<h1>24/7 Roadside Assistance [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . '</h1>';
				$category = 'roadside';
			}

			$ul_items = array();
			$lines    = preg_split( '/\r\n|\r|\n/', $version_content );
			foreach ( $lines as $line ) {
				$line = trim( $line );
				if ( ( 0 === strpos( $line, '* ' ) || 0 === strpos( $line, '- ' ) )
					&& 0 !== stripos( $line, 'Button:' )
					&& 0 !== stripos( $line, 'Link:' ) ) {
					$item = trim( substr( $line, 2 ) );
					if ( $item && strlen( $item ) < 200
						&& ! preg_match( '/<H[1-6]/i', $item )
						&& ! preg_match( '/<p>/i', $item ) ) {
						$ul_items[] = self::apply_shortcodes_to_ul_item( $item, $detected_location, $detected_state, $use_state_shortcode, $detected_company );
					}
				}
			}

			$h2_sections = preg_split( '/<H2[^>]*>.*?<\/H2>/is', $version_content );
			$section_paragraphs = array();
			foreach ( $h2_sections as $section ) {
				$section_paras = array();
				$slines        = preg_split( '/\r\n|\r|\n/', trim( $section ) );
				foreach ( $slines as $sline ) {
					$sline = trim( $sline );
					$first = isset( $sline[0] ) ? $sline[0] : '';
					if ( $sline && '*' !== $first && strlen( $sline ) > 30
						&& 0 !== stripos( $sline, 'button:' )
						&& 0 !== stripos( $sline, 'link:' )
						&& 0 !== strpos( $sline, '_' )
						&& 0 !== stripos( $sline, 'tel:' )
						&& 0 !== strpos( $sline, '________________' ) ) {
						$p_text        = self::apply_shortcodes( $sline, $detected_location, $detected_state, $use_state_shortcode, $detected_company, $detected_city );
						$section_paras[] = '<p>' . $p_text . '</p>';
					}
				}
				$section_paragraphs[] = $section_paras;
			}

			$paragraphs = array();
			foreach ( $section_paragraphs as $si => $section_paras ) {
				if ( 0 === (int) $si ) {
					continue;
				}
				if ( $si <= 3 ) {
					foreach ( $section_paras as $sp ) {
						$paragraphs[] = $sp;
					}
				}
			}

			$h2_4_content = null;
			$paragraph_7 = null;
			$paragraph_8 = null;
			if ( count( $h2s ) >= 4 ) {
				$h2_4_text = $h2s[3];
				$h2_4_proc = self::apply_shortcodes( $h2_4_text, $detected_location, $detected_state, $use_state_shortcode, $detected_company, $detected_city );
				$h2_4_content = '<h2>' . $h2_4_proc . '</h2>';
				if ( isset( $section_paragraphs[4] ) && $section_paragraphs[4] ) {
					$h2_4_paras = $section_paragraphs[4];
					if ( count( $h2_4_paras ) >= 2 ) {
						$paragraph_7 = $h2_4_paras[0];
						$paragraph_8 = $h2_4_paras[1];
					} elseif ( count( $h2_4_paras ) === 1 ) {
						$paragraph_7 = $h2_4_paras[0];
					}
				}
			}

			$version_info = array(
				'h1'          => $h1_block,
				'h2s'         => array_slice( $h2s, 0, 3 ),
				'h2_4'        => $h2_4_content,
				'paragraph_7' => $paragraph_7,
				'paragraph_8' => $paragraph_8,
				'paragraphs'  => $paragraphs,
				'ul_items'    => $ul_items,
				'category'    => $category,
			);

			if ( ! isset( $category_ul_items[ $category ] ) ) {
				$category_ul_items[ $category ] = array();
			}
			if ( ! isset( $category_version_counters[ $category ] ) ) {
				$category_version_counters[ $category ] = 0;
			}
			$category_version_counters[ $category ]++;
			$version_ul_key = $category . '_version_' . $category_version_counters[ $category ];
			$category_ul_items[ $version_ul_key ] = $ul_items;

			$version_data[] = $version_info;
			$category_versions[ $category ][] = $version_info;
		}

		$raw_paragraphs = array();
		foreach ( $version_data as $v ) {
			foreach ( $v['paragraphs'] as $p ) {
				$raw_paragraphs[] = $p;
			}
		}

		$ctx = array(
			'detected_state'       => $detected_state,
			'use_state_shortcode'  => $use_state_shortcode,
			'detected_company'     => $detected_company,
			'version_data'         => $version_data,
			'category_versions'    => $category_versions,
			'category_ul_items'    => $category_ul_items,
			'raw_paragraphs'       => $raw_paragraphs,
			'h1_content'           => $h1_content,
		);

		$fields = self::build_spintax_fields( $ctx );

		if ( ! $use_state_shortcode && $detected_state ) {
			foreach ( $fields as $fid => &$field_data ) {
				if ( empty( $field_data['options'] ) || ! is_array( $field_data['options'] ) ) {
					continue;
				}
				foreach ( $field_data['options'] as $oid => $content ) {
					if ( is_string( $content ) && strpos( $content, '[meta_region_code]' ) !== false ) {
						$field_data['options'][ $oid ] = str_replace( '[meta_region_code]', $detected_state, $content );
					}
				}
			}
			unset( $field_data );
		}

		$structure  = array(
			'spintax-shortcodes' => $fields,
		);
		$serialized = serialize( $structure );
		$debug['versions'] = count( $version_data );
		$debug['company']  = $detected_company;

		return array(
			'serialized' => $serialized,
			'bytes'      => strlen( $serialized ),
			'debug'      => $debug,
		);
	}

	/**
	 * @param array $ctx Context from run().
	 * @return array
	 */
	private static function build_spintax_fields( $ctx ) {
		$detected_state      = $ctx['detected_state'];
		$use_state_shortcode = $ctx['use_state_shortcode'];
		$category_ul_items   = $ctx['category_ul_items'];
		$category_versions   = $ctx['category_versions'];
		$h1_content          = $ctx['h1_content'];

		$rs = function ( $content ) use ( $detected_state, $use_state_shortcode ) {
			return self::replace_state_shortcodes( $content, $detected_state, $use_state_shortcode );
		};

		$fields = array();

		$add = function ( $id, $label, $options ) use ( &$fields ) {
			$fields[ $id ] = array(
				'label'   => $label,
				'options' => $options,
			);
		};

		$roadside_p1 = self::get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, 'roadside', 0 );
		$roadside_p2 = self::get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, 'roadside', 1 );
		$roadside_p3 = self::get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, 'roadside', 2 );
		$roadside_p4 = self::get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, 'roadside', 3 );
		$roadside_p5 = self::get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, 'roadside', 4 );
		$roadside_p6 = self::get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, 'roadside', 4 );

		$heavy_p1 = self::get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, 'heavy', 0 );
		$heavy_p2 = self::get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, 'heavy', 1 );
		$heavy_p3 = self::get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, 'heavy', 2 );
		$heavy_p4 = self::get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, 'heavy', 3 );
		$heavy_p5 = self::get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, 'heavy', 4 );
		$heavy_p6 = self::get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, 'heavy', 4 );

		$equipment_p1 = self::get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, 'equipment', 0 );
		$equipment_p2 = self::get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, 'equipment', 1 );
		$equipment_p3 = self::get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, 'equipment', 2 );
		$equipment_p4 = self::get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, 'equipment', 3 );
		$equipment_p5 = self::get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, 'equipment', 4 );
		$equipment_p6 = self::get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, 'equipment', 5 );

		$towing_p1 = self::get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, 'towing', 0 );
		$towing_p2 = self::get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, 'towing', 1 );
		$towing_p3 = self::get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, 'towing', 2 );
		$towing_p4 = self::get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, 'towing', 3 );
		$towing_p5 = self::get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, 'towing', 4 );
		$towing_p6 = self::get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, 'towing', 5 );

		$roadside_p7 = self::get_paragraph_7_by_section( $category_versions, $detected_state, $use_state_shortcode, 'roadside' );
		$roadside_p8 = self::get_paragraph_8_by_section( $category_versions, $detected_state, $use_state_shortcode, 'roadside' );
		$heavy_p7    = self::get_paragraph_7_by_section( $category_versions, $detected_state, $use_state_shortcode, 'heavy' );
		$heavy_p8    = self::get_paragraph_8_by_section( $category_versions, $detected_state, $use_state_shortcode, 'heavy' );
		$equipment_p7 = self::get_paragraph_7_by_section( $category_versions, $detected_state, $use_state_shortcode, 'equipment' );
		$equipment_p8 = self::get_paragraph_8_by_section( $category_versions, $detected_state, $use_state_shortcode, 'equipment' );
		$towing_p7    = self::get_paragraph_7_by_section( $category_versions, $detected_state, $use_state_shortcode, 'towing' );
		$towing_p8    = self::get_paragraph_8_by_section( $category_versions, $detected_state, $use_state_shortcode, 'towing' );

		$add(
			'c0g3b1f',
			'roadside-meta-title',
			array(
				'8q6ubd' => '24/7 Emergency Roadside Assistance [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . ' | [xfield_company-name]',
			)
		);
		$add(
			'ex59ys',
			'roadside-meta-desc',
			array(
				'ttpvck' => '[xfield_company-name] provides 24/7 emergency roadside assistance in [location]. Call for fuel delivery, vehicle lockouts, battery jumps, & more.',
			)
		);
		$add( 'pgn00b', 'roadside-h1', array( '7xj2jn' => $h1_content ) );
		$add(
			'g92x2',
			'roadside-h2-1',
			array(
				'8mch6i' => '<h2>Emergency Roadside Services in [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . '</h2>',
			)
		);
		$add(
			'nyfvy',
			'roadside-img-1',
			array(
				'icqjo8'  => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_roadside-keyword] [location]', 'roadside' ) ),
				'zqtylq'  => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_roadside-keyword] [location]', 'roadside' ) ),
				'rznnlkg' => $rs( self::create_wp_image( 'placeholder.jpg', ' [xfield_roadside-keyword] [location]', 'roadside' ) ),
				'hcn5ub'  => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_roadside-keyword] [location]', 'roadside' ) ),
			)
		);
		$add(
			'a71va',
			'roadside-paragraph-1',
			array(
				'rc9iod' => $roadside_p1['version1'],
				'armq2'  => $roadside_p1['version2'],
				'x58wh'  => $roadside_p1['version3'],
				'u3ql0n' => $roadside_p1['version4'],
			)
		);
		$add(
			'wxkwza',
			'roadside-paragraph-2',
			array(
				'vl1dc'  => $roadside_p2['version1'],
				'zwqt7'  => $roadside_p2['version2'],
				'pqtkyq' => $roadside_p2['version3'],
				'jitca'  => $roadside_p2['version4'],
			)
		);
		$add(
			'3wnz47',
			'roadside-h2-2',
			array(
				'9zek4' => '<h2>Get Quick Roadside Assistance Near Me in [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . '</h2>',
			)
		);
		$add(
			'wirda',
			'roadside-img-2',
			array(
				'siiztr' => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_roadside-keyword] [location]', 'roadside' ) ),
				'iwruys' => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_roadside-keyword] [location]', 'roadside' ) ),
				'h495ns' => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_roadside-keyword] [location]', 'roadside' ) ),
				'3a1nii' => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_roadside-keyword] [location]', 'roadside' ) ),
			)
		);
		$add(
			'fldy3',
			'roadside-paragraph-3',
			array(
				'cz8bsk' => $roadside_p3['version1'],
				'yzjhed' => $roadside_p3['version2'],
				'dblfsd' => $roadside_p3['version3'],
				'n01p7o' => $roadside_p3['version4'],
			)
		);
		$add(
			'q5man',
			'roadside-paragraph-4',
			array(
				'r9x286' => $roadside_p4['version1'],
				'g6m6l'  => $roadside_p4['version2'],
				'9cyet8' => $roadside_p4['version3'],
				'o4p9w'  => $roadside_p4['version4'],
			)
		);
		$add( 'feebkl', 'roadside-ul', self::create_ul_block_for_category( 'roadside', $category_ul_items, $roadside_p7, $roadside_p8, $detected_state, $use_state_shortcode ) );
		$add(
			'52i9lm',
			'roadside-btn',
			array(
				'4lzqbp' => 'Call [xfield_company-name] for Roadside Assistance in [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . ' Now!',
				'wb7x8v' => 'Get Roadside Assistance in [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . ' Now!',
			)
		);
		$add(
			'ypk9mb',
			'roadside-paragraph-5',
			array(
				'0ltva'  => $roadside_p5['version1'],
				'cnsb2c' => $roadside_p5['version2'],
				'w00bpu' => $roadside_p5['version3'],
				'actg0a' => $roadside_p5['version4'],
			)
		);
		$add(
			'j3sasf',
			'roadside-paragraph-6',
			array(
				'dbs1hl'   => $roadside_p6['version1'],
				'1tffej'   => $roadside_p6['version2'],
				'70vbk8'   => $roadside_p6['version3'],
				'wpjh5s2'  => $roadside_p6['version4'],
			)
		);

		$add(
			'1e9th',
			'heavy-meta-title',
			array(
				'ocikhb' => '24/7 Heavy Duty Towing in [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . ' | [xfield_company-name]',
			)
		);
		$add(
			'j0eud5',
			'heavy-meta-desc',
			array(
				'9teic7' => '[xfield_company-name] provides 24/7 heavy duty towing in [location]. Call for heavy towing, heavy recovery, & heavy duty roadside assistance.',
			)
		);
		$add(
			's2bozf',
			'heavy-h1',
			array(
				'3gj4as' => '<h1>24/7 Heavy Tow Truck in [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . '</h1>',
			)
		);
		$add(
			'm8niv',
			'heavy-h2-1',
			array(
				'7mc6qu' => '<h2>24/7 Heavy Tow Truck in [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . '</h2>',
			)
		);
		$add(
			'fv2bh5',
			'heavy-img-1',
			array(
				'db7sl'  => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_heavy-keyword] [location]', 'heavy' ) ),
				'561yep' => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_heavy-keyword] [location]', 'heavy' ) ),
				'9oe81q' => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_heavy-keyword] [location]', 'heavy' ) ),
				'xjsi7d' => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_heavy-keyword] [location]', 'heavy' ) ),
			)
		);
		$add(
			'2nxs9j',
			'heavy-paragraph-1',
			array(
				'x6a6u' => $heavy_p1['version1'],
				'0l4o2' => $heavy_p1['version2'],
				'm9dc4' => $heavy_p1['version3'],
				'y49n57' => $heavy_p1['version4'],
			)
		);
		$add(
			'7m7bb',
			'heavy-paragraph-2',
			array(
				'nk6vo'  => $heavy_p2['version1'],
				'o4fgb'  => $heavy_p2['version2'],
				'odypac' => $heavy_p2['version3'],
				'uch4jf' => $heavy_p2['version4'],
			)
		);
		$add(
			'm6bsc',
			'heavy-h2-2',
			array(
				'm83upi' => '<h2>[location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . ' Heavy Duty Towing Services You Can Trust</h2>',
			)
		);
		$add(
			'aifese',
			'heavy-img-2',
			array(
				'sq4db'  => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_heavy-keyword] [location]', 'heavy' ) ),
				'24nwxr' => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_heavy-keyword] [location]', 'heavy' ) ),
				'2bguwo' => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_heavy-keyword]  [location]', 'heavy' ) ),
				'42hwv'  => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_heavy-keyword] [location]', 'heavy' ) ),
			)
		);
		$add(
			'matbz',
			'heavy-paragraph-3',
			array(
				'30etu0j' => $heavy_p3['version1'],
				'uhkrxs'  => $heavy_p3['version2'],
				'a2hz5n'  => $heavy_p3['version3'],
				'12beqh'  => $heavy_p3['version4'],
			)
		);
		$add(
			'dqke2',
			'heavy-paragraph-4',
			array(
				'jn80er' => $heavy_p4['version1'],
				'5cufpn' => $heavy_p4['version2'],
				'bss3r'  => $heavy_p4['version3'],
				'bt8hn6' => $heavy_p4['version4'],
			)
		);
		$add(
			'ej5zk',
			'heavy-h2-3',
			array(
				'21wavl' => '<h2>Heavy Duty Towing Near Me in [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . '</h2>',
			)
		);
		$add( '2runon', 'heavy-ul', self::create_ul_block_for_category( 'heavy', $category_ul_items, $heavy_p7, $heavy_p8, $detected_state, $use_state_shortcode ) );
		$add(
			'9gy7jf',
			'heavy-btn',
			array(
				'fx1lq'  => 'GET HEAVY TOWING IN [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . ' NOW',
				'tis9sj' => 'GET HEAVY TOWING NEAR ME IN [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . ' NOW',
			)
		);
		$add(
			'wmh9y',
			'heavy-paragraph-5',
			array(
				'eyn08k' => $heavy_p5['version1'],
				'tx9eio' => $heavy_p5['version2'],
				'ffe3cb' => $heavy_p5['version3'],
				'7mzgzu' => $heavy_p5['version4'],
			)
		);
		$add(
			'et1rzl',
			'heavy-paragraph-6',
			array(
				'lgvh2'  => $heavy_p6['version1'],
				'o5011'  => $heavy_p6['version2'],
				'oouf6v' => $heavy_p6['version3'],
				't1qp7r' => $heavy_p6['version4'],
			)
		);

		$add(
			'xqmzb',
			'equipment-meta-title',
			array(
				'tisq38' => '24/7 Heavy Equipment Towing in [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . ' | [xfield_company-name]',
			)
		);
		$add(
			'9eh081',
			'equipment-meta-desc',
			array(
				'wrmeis' => '[xfield_company-name] provides 24/7 heavy equipment towing and heavy machinery towing in [location].',
			)
		);
		$add(
			'5dnz3',
			'equipment-h1',
			array(
				'uj26t' => '<h1>24/7 Heavy Equipment Towing in [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . '</h1>',
			)
		);
		$add(
			'p14vgo',
			'equipment-h2-1',
			array(
				'vq96' => '<h2>[location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . ' Heavy Equipment & Machinery Towing Service</h2>',
			)
		);
		$add(
			'bguzaa',
			'equipment-img-1',
			array(
				'qgt4gn' => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_equipment-keyword] [location]', 'equipment' ) ),
				'6sk5sh' => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_equipment-keyword] [location]', 'equipment' ) ),
			)
		);
		$add(
			'msa63f',
			'equipment-paragraph-1',
			array(
				'vo9f1' => $equipment_p1['version1'],
				'7sjrl' => $equipment_p1['version2'],
				'i2om2t' => $equipment_p1['version3'],
				'4adix' => $equipment_p1['version4'],
			)
		);
		$add(
			'qh3mqq',
			'equipment-paragraph-2',
			array(
				'pzb65a' => $equipment_p2['version1'],
				'fq17l'  => $equipment_p2['version2'],
				'k3dbi'  => $equipment_p2['version3'],
				'0fte3'  => $equipment_p2['version4'],
			)
		);
		$add(
			'0q16o',
			'equipment-h2-2',
			array(
				'7vnrdm' => '<h2>Heavy Equipment Hauling Near Me in [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . '</h2>',
			)
		);
		$add(
			'niil7',
			'equipment-img-2',
			array(
				'l3zslj' => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_equipment-keyword] [location]', 'equipment' ) ),
				'73k7sd' => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_equipment-keyword] [location]', 'equipment' ) ),
			)
		);
		$add(
			'dmaz9b',
			'equipment-paragraph-3',
			array(
				'krgp86' => $equipment_p3['version1'],
				'ghffwc' => $equipment_p3['version2'],
				'm8zmf7' => $equipment_p3['version3'],
				'a86h8j' => $equipment_p3['version4'],
			)
		);
		$add(
			'ryze2',
			'equipment-paragraph-4',
			array(
				'j389re' => $equipment_p4['version1'],
				'd9067'  => $equipment_p4['version2'],
				'ojjjm'  => $equipment_p4['version3'],
				'mnrvn'  => $equipment_p4['version4'],
			)
		);
		$add( 'febl7d', 'equipment-ul', self::create_ul_block_for_category( 'equipment', $category_ul_items, $equipment_p7, $equipment_p8, $detected_state, $use_state_shortcode ) );
		$add(
			'5c6d9t',
			'equipment-btn',
			array(
				'ox60g8' => 'GET [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . ' HEAVY EQUIPMENT TOWING NOW',
			)
		);
		$add(
			'b4hwgn',
			'equipment-h2-3',
			array(
				'3z6t4e' => '<h2>Get Professional Heavy Equipment Towing in [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . '</h2>',
				'yydta'  => '<h2>Heavy Equipment Hauling Near Me in [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . '</h2>',
			)
		);
		$add(
			't87nie',
			'equipment-paragraph-5',
			array(
				'b8tlni' => $equipment_p5['version1'],
				'b2fj7j' => $equipment_p5['version2'],
				'65j5nw' => $equipment_p5['version3'],
				'9b94u'  => $equipment_p5['version4'],
			)
		);
		$add(
			'14qiq',
			'equipment-paragraph-6',
			array(
				'8i83tm' => $equipment_p6['version1'],
				'l8tccn' => $equipment_p6['version2'],
				'nel29c' => $equipment_p6['version3'],
				'tpd17'  => $equipment_p6['version4'],
			)
		);

		$add(
			'bbih6j',
			'towing-meta-title',
			array(
				'mlvcx' => '24/7 Towing Company in [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . ' | Tow Truck Near Me',
			)
		);
		$add(
			'b8xipc',
			'towing-meta-desc',
			array(
				'q5k557' => '[xfield_company-name] provides 24/7 emergency towing services in [location]. Call for a quick tow truck near me by a trusted towing company.',
			)
		);
		$add(
			'8byy4',
			'towing-h1',
			array(
				'1wm5sc' => '<h1>24/7 Towing Services in [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . '</h1>',
			)
		);
		$add(
			'xvtkuw',
			'towing-h2-1',
			array(
				'w2hfeu' => '<h2>Reliable Towing Services in [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . '</h2>',
			)
		);
		$add(
			'e84yns',
			'towing-img-1',
			array(
				'yndpz'   => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_towing-keyword] [location]', 'towing' ) ),
				'9dcnvc'  => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_towing-keyword] [location]', 'towing' ) ),
				'0o5bhj'  => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_towing-keyword] [location]', 'towing' ) ),
				'4hmfo'   => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_towing-keyword] [location]', 'towing' ) ),
			)
		);
		$add(
			'vxkind',
			'towing-paragraph-1',
			array(
				'ewqkze' => $towing_p1['version1'],
				'9nqx6t' => $towing_p1['version2'],
				'0qnoz'  => $towing_p1['version3'],
				'z1mrc'  => $towing_p1['version4'],
			)
		);
		$add(
			'06sn8r',
			'towing-paragraph-2',
			array(
				'rfz8aa' => $towing_p2['version1'],
				'yzuxfy' => $towing_p2['version2'],
				'm1r9d'  => $towing_p2['version3'],
				'zbmam'  => $towing_p2['version4'],
			)
		);
		$add(
			'dk4z9t',
			'towing-h2-2',
			array(
				'g8cl8' => '<h2>[location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . '\'s #1 Towing Company</h2>',
			)
		);
		$add(
			'3rilxj',
			'towing-img-2',
			array(
				'nle75'  => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_towing-keyword] [location]', 'towing' ) ),
				'sqaksd' => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_towing-keyword] [location]', 'towing' ) ),
				'6q8eek' => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_towing-keyword] [location]', 'towing' ) ),
				'nb42a1' => $rs( self::create_wp_image( 'placeholder.jpg', '[xfield_towing-keyword] [location]', 'towing' ) ),
			)
		);
		$add(
			'6x8ojn',
			'towing-paragraph-3',
			array(
				'31v258' => $towing_p3['version1'],
				'56cvdh' => $towing_p3['version2'],
				'l47dco' => $towing_p3['version3'],
				'kvpz4l' => $towing_p3['version4'],
			)
		);
		$add(
			'fn3cy',
			'towing-paragraph-4',
			array(
				'wfqzqh' => $towing_p4['version1'],
				'xc9e1'  => $towing_p4['version2'],
				'71o2ze' => $towing_p4['version3'],
				'2bhosg' => $towing_p4['version4'],
			)
		);
		$add(
			'bz4il',
			'towing-h2-3',
			array(
				'wq0gnm' => '<h2>Quick Tow Truck Services Near Me in [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . '</h2>',
			)
		);
		$add(
			'i2j7cm',
			'towing-paragraph-5',
			array(
				'0jrs7i' => $towing_p5['version1'],
				'ioti3'  => $towing_p5['version2'],
				'1d9sck' => $towing_p5['version3'],
				'ssl63'  => $towing_p5['version4'],
			)
		);
		$add(
			'xmipar',
			'towing-paragraph-6',
			array(
				'gmtus7' => $towing_p6['version1'],
				'64a6uo' => $towing_p6['version2'],
				'hyfh0f' => $towing_p6['version3'],
				'nibtr'  => $towing_p6['version4'],
			)
		);
		$add( 'g5jbni', 'towing-ul', self::create_ul_block_for_category( 'towing', $category_ul_items, $towing_p7, $towing_p8, $detected_state, $use_state_shortcode ) );
		$add(
			'bfwu4e',
			'towing-btn',
			array(
				'gro1ue' => 'Call a tow truck in [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ),
				'0of8hm' => 'QUICK TOW TRUCK [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . '!',
				'5yum8'  => 'Get a tow truck near me in [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . ' NOW!',
				'0z0wc'  => 'Get a Tow Truck now in [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . '!',
			)
		);
		$add(
			'v5q5va',
			'roadside-h2-3',
			array(
				'67z0iw' => '<h2>Your Local [location] Roadside Assistance Company</h2>',
			)
		);

		foreach ( array( 'roadside', 'heavy', 'equipment', 'towing' ) as $section ) {
			if ( empty( $category_versions[ $section ] ) ) {
				continue;
			}
			$has_h2_4 = false;
			foreach ( $category_versions[ $section ] as $ver ) {
				if ( ! empty( $ver['h2_4'] ) ) {
					$has_h2_4 = true;
					break;
				}
			}
			if ( $has_h2_4 ) {
				$h2_4_opts = self::get_h2_4_by_section( $category_versions, $detected_state, $use_state_shortcode, $section );
				$add( $section . '_h2_4', $section . '-h2-4', $h2_4_opts );
			}
		}

		foreach ( array( 'roadside', 'heavy', 'equipment', 'towing' ) as $section ) {
			if ( empty( $category_versions[ $section ] ) ) {
				continue;
			}
			$has_p7 = false;
			$has_p8 = false;
			foreach ( $category_versions[ $section ] as $ver ) {
				if ( ! empty( $ver['paragraph_7'] ) ) {
					$has_p7 = true;
				}
				if ( ! empty( $ver['paragraph_8'] ) ) {
					$has_p8 = true;
				}
			}
			if ( $has_p7 ) {
				$add( $section . '_p7', $section . '-p7', self::get_paragraph_7_by_section( $category_versions, $detected_state, $use_state_shortcode, $section ) );
			}
			if ( $has_p8 ) {
				$add( $section . '_p8', $section . '-p8', self::get_paragraph_8_by_section( $category_versions, $detected_state, $use_state_shortcode, $section ) );
			}
		}

		return $fields;
	}

	private static function resolve_state( $detected_state, $use_state_shortcode ) {
		return $use_state_shortcode ? '[meta_region_code]' : (string) $detected_state;
	}

	private static function replace_state_shortcodes( $content, $detected_state, $use_state_shortcode ) {
		if ( $use_state_shortcode ) {
			return $content;
		}
		return str_replace( '[meta_region_code]', (string) $detected_state, $content );
	}

	private static function detect_company_name( $text ) {
		// Double-quoted patterns so \x{2019} resolves (UTF-8 right single quotation mark).
		$patterns = array(
			"/\b(Bell['\x{2019}]s\s+Towing\s+&\s+Recovery)\b/iu",
			"/\bAt\s+([A-Z][a-z'\x{2019}]+(?:\s+[A-Z&][a-z'\x{2019}]+)+),\s+we\b/u",
			"/\b([A-Z][a-z'\x{2019}]+(?:\s+[A-Z&][a-z'\x{2019}]+)+)\s+(?:provides|operates|offers|delivers|serves)\b/u",
			"/\b(?:Call|Contact|Reach)\s+([A-Z][a-z'\x{2019}]+(?:\s+[A-Z&][a-z'\x{2019}]+)+)\s+(?:for|at|in)\b/u",
			"/\b([A-Z][a-z'\x{2019}]+(?:\s+[A-Z&][a-z'\x{2019}]+)+)\s+(?:is|has|offers|provides)\b/u",
			"/\b(?:We|Here)\s+at\s+([A-Z][a-z'\x{2019}]+(?:\s+[A-Z&][a-z'\x{2019}]+)+)\b/u",
			"/(?:That['\x{2019}]s\s+why|When\s+you\s+call)\s+([A-Z][a-z'\x{2019}]+(?:\s+[A-Z&][a-z'\x{2019}]+)+)/u",
			"/\b([A-Z][a-z'\x{2019}]+(?:\s+[A-Z&][a-z'\x{2019}]+)+)\s+(?:keeps|team|crew|fleet)\b/u",
			"/\b([A-Z][a-z'\x{2019}]+\s+Towing\s+&\s+[A-Z][a-z'\x{2019}]+)\b/u",
			"/\b([A-Z][a-z'\x{2019}]+\s+Wrecker\s+Service)\b/u",
		);
		$towing_keywords = array( 'towing', 'recovery', 'creeks', 'creek', 'bell', 'wrecker', 'service' );
		$prefixes        = array( 'why ', 'that\'s why ', 'when you call ', 'at ', 'here at ' );

		foreach ( $patterns as $pattern ) {
			if ( preg_match_all( $pattern, $text, $matches, PREG_SET_ORDER ) ) {
				foreach ( $matches as $m ) {
					$match = isset( $m[1] ) ? $m[1] : $m[0];
					$low   = strtolower( $match );
					foreach ( $towing_keywords as $kw ) {
						if ( strpos( $low, $kw ) !== false ) {
							$cleaned = trim( $match );
							foreach ( $prefixes as $prefix ) {
								if ( stripos( $cleaned, $prefix ) === 0 ) {
									$cleaned = trim( substr( $cleaned, strlen( $prefix ) ) );
								}
							}
							return $cleaned;
						}
					}
				}
			}
		}

		if ( preg_match_all( "/\b([A-Z][a-z'\x{2019}]+(?:\s+[A-Z&][a-z'\x{2019}]+)+)\b/u", $text, $fb ) ) {
			foreach ( $fb[1] as $match ) {
				$low = strtolower( $match );
				foreach ( $towing_keywords as $kw ) {
					if ( strpos( $low, $kw ) !== false ) {
						$cleaned = trim( $match );
						foreach ( $prefixes as $prefix ) {
							if ( stripos( $cleaned, $prefix ) === 0 ) {
								$cleaned = trim( substr( $cleaned, strlen( $prefix ) ) );
							}
						}
						return $cleaned;
					}
				}
			}
		}

		return null;
	}

	private static function detect_city_from_h2( $h2_text ) {
		$patterns = array(
			'/\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\?/u',
			'/\bnear\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\?/u',
			'/\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*,\s*[A-Z]{2}/u',
			'/\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*$/u',
		);
		$skip = array( 'me', 'you', 'us', 'now', 'today', 'here', 'there', 'service', 'services', 'towing', 'truck', 'trucks', 'assistance', 'help', 'call', 'get', 'need', 'want', 'find', 'near', 'in', 'for', 'with', 'and', 'or', 'the', 'a', 'an' );
		foreach ( $patterns as $pattern ) {
			if ( preg_match_all( $pattern, $h2_text, $matches ) ) {
				foreach ( $matches[1] as $match ) {
					$m = trim( $match );
					if ( strlen( $m ) > 2 && ! in_array( strtolower( $m ), $skip, true ) ) {
						return $m;
					}
				}
			}
		}
		return null;
	}

	private static function replace_city_in_text( $text, $city_name ) {
		if ( ! $city_name ) {
			return $text;
		}
		$pattern = '/\b' . preg_quote( $city_name, '/' ) . '\b/iu';
		return preg_replace( $pattern, '[location]', $text );
	}

	private static function apply_shortcodes_to_ul_item( $text, $detected_location, $detected_state, $use_state_shortcode, $detected_company ) {
		$sample_cities = array( 'Falls Church', 'Alexandria', 'Vienna', 'Gaithersburg' );
		foreach ( $sample_cities as $city ) {
			$text = str_replace( $city, '[location]', $text );
		}
		$text = preg_replace( '/,\s*[A-Z]{2}$/', ', [meta_region_code]', $text );
		if ( $detected_company ) {
			$text = str_replace( $detected_company, '[xfield_company-name]', $text );
		} else {
			$text = str_replace( "Bell's Towing & Recovery", '[xfield_company-name]', $text );
			$text = str_replace( 'Twin Creeks Towing', '[xfield_company-name]', $text );
			$text = str_replace( 'Andrus Towing', '[xfield_company-name]', $text );
			$text = str_replace( "Henry's Wrecker Service", '[xfield_company-name]', $text );
		}
		return $text;
	}

	private static function apply_shortcodes( $text, $detected_location, $detected_state, $use_state_shortcode, $detected_company, $detected_city ) {
		$text = preg_replace( '/\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2}\b/u', '[location], [meta_region_code]', $text );
		$text = preg_replace( '/\bSt\.\s+\[location\]/u', '[location]', $text );
		if ( $detected_city ) {
			$text = self::replace_city_in_text( $text, $detected_city );
		}
		if ( $detected_company ) {
			$text = str_replace( $detected_company, '[xfield_company-name]', $text );
		} else {
			$text = str_replace( "Bell's Towing & Recovery", '[xfield_company-name]', $text );
			$text = str_replace( 'Twin Creeks Towing', '[xfield_company-name]', $text );
			$text = str_replace( 'Andrus Towing', '[xfield_company-name]', $text );
			$text = str_replace( "Henry's Wrecker Service", '[xfield_company-name]', $text );
		}
		return $text;
	}

	private static function categorize_by_h1( $h1_text ) {
		$h1_lower = strtolower( $h1_text );
		if ( strpos( $h1_lower, 'roadside' ) !== false ) {
			return 'roadside';
		}
		if ( strpos( $h1_lower, 'heavy' ) !== false && strpos( $h1_lower, 'equipment' ) === false ) {
			return 'heavy';
		}
		if ( strpos( $h1_lower, 'equipment' ) !== false ) {
			return 'equipment';
		}
		if ( strpos( $h1_lower, 'towing' ) !== false && strpos( $h1_lower, 'heavy' ) === false ) {
			return 'towing';
		}
		return 'roadside';
	}

	private static function fallback_paragraph( $detected_state, $use_state_shortcode ) {
		return '<p>[xfield_company-name] provides professional service in [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . '.</p>';
	}

	private static function get_paragraphs_by_section( $category_versions, $detected_state, $use_state_shortcode, $section, $paragraph_index ) {
		$fallback = self::fallback_paragraph( $detected_state, $use_state_shortcode );
		$out      = array(
			'version1' => $fallback,
			'version2' => $fallback,
			'version3' => $fallback,
			'version4' => $fallback,
		);
		if ( empty( $category_versions[ $section ] ) ) {
			return $out;
		}
		$versions = $category_versions[ $section ];
		$n        = min( 4, count( $versions ) );
		for ( $i = 0; $i < 4; $i++ ) {
			$key = 'version' . ( $i + 1 );
			if ( $i < $n ) {
				$vp = $versions[ $i ]['paragraphs'];
				if ( isset( $vp[ $paragraph_index ] ) ) {
					$out[ $key ] = $vp[ $paragraph_index ];
				} elseif ( ! empty( $vp ) ) {
					$out[ $key ] = $vp[ $paragraph_index % count( $vp ) ];
				} else {
					$out[ $key ] = $fallback;
				}
			} else {
				$last = $versions[ count( $versions ) - 1 ]['paragraphs'];
				if ( isset( $last[ $paragraph_index ] ) ) {
					$out[ $key ] = $last[ $paragraph_index ];
				} elseif ( ! empty( $last ) ) {
					$out[ $key ] = $last[ $paragraph_index % count( $last ) ];
				} else {
					$out[ $key ] = $fallback;
				}
			}
		}
		return $out;
	}

	private static function get_h2_4_by_section( $category_versions, $detected_state, $use_state_shortcode, $section ) {
		$fallback = '<h2>Professional Service in [location], ' . self::resolve_state( $detected_state, $use_state_shortcode ) . '</h2>';
		$out      = array(
			'version1' => $fallback,
			'version2' => $fallback,
			'version3' => $fallback,
			'version4' => $fallback,
		);
		if ( empty( $category_versions[ $section ] ) ) {
			return $out;
		}
		$versions = $category_versions[ $section ];
		$n        = min( 4, count( $versions ) );
		for ( $i = 0; $i < 4; $i++ ) {
			$key = 'version' . ( $i + 1 );
			if ( $i < $n ) {
				$h = $versions[ $i ]['h2_4'] ?? null;
				$out[ $key ] = $h ? $h : $fallback;
			} else {
				$last = $versions[ count( $versions ) - 1 ]['h2_4'] ?? null;
				$out[ $key ] = $last ? $last : $fallback;
			}
		}
		return $out;
	}

	private static function get_paragraph_7_by_section( $category_versions, $detected_state, $use_state_shortcode, $section ) {
		$fallback = self::fallback_paragraph( $detected_state, $use_state_shortcode );
		$out      = array(
			'version1' => $fallback,
			'version2' => $fallback,
			'version3' => $fallback,
			'version4' => $fallback,
		);
		if ( empty( $category_versions[ $section ] ) ) {
			return $out;
		}
		$versions = $category_versions[ $section ];
		$n        = min( 4, count( $versions ) );
		for ( $i = 0; $i < 4; $i++ ) {
			$key = 'version' . ( $i + 1 );
			if ( $i < $n ) {
				$p = $versions[ $i ]['paragraph_7'] ?? null;
				$out[ $key ] = $p ? $p : $fallback;
			} else {
				$last = $versions[ count( $versions ) - 1 ]['paragraph_7'] ?? null;
				$out[ $key ] = $last ? $last : $fallback;
			}
		}
		return $out;
	}

	private static function get_paragraph_8_by_section( $category_versions, $detected_state, $use_state_shortcode, $section ) {
		$fallback = self::fallback_paragraph( $detected_state, $use_state_shortcode );
		$out      = array(
			'version1' => $fallback,
			'version2' => $fallback,
			'version3' => $fallback,
			'version4' => $fallback,
		);
		if ( empty( $category_versions[ $section ] ) ) {
			return $out;
		}
		$versions = $category_versions[ $section ];
		$n        = min( 4, count( $versions ) );
		for ( $i = 0; $i < 4; $i++ ) {
			$key = 'version' . ( $i + 1 );
			if ( $i < $n ) {
				$p = $versions[ $i ]['paragraph_8'] ?? null;
				$out[ $key ] = $p ? $p : $fallback;
			} else {
				$last = $versions[ count( $versions ) - 1 ]['paragraph_8'] ?? null;
				$out[ $key ] = $last ? $last : $fallback;
			}
		}
		return $out;
	}

	private static function create_wp_image( $src_filename, $alt_text ) {
		return '<img class="size-medium wp-image-1811 alignleft" src="' . $src_filename . '" alt="' . $alt_text . '" width="300" height="225" />';
	}

	/**
	 * @param string               $category Category key.
	 * @param array<string,array>  $category_ul_items Keys like roadside_version_1.
	 * @param array<string,string> $paragraph_7_dict version1..4.
	 * @param array<string,string> $paragraph_8_dict version1..4.
	 * @param string|null          $detected_state State.
	 * @param bool                 $use_state_shortcode Use shortcode.
	 * @return array<string,string> Option key => HTML.
	 */
	private static function create_ul_block_for_category( $category, $category_ul_items, $paragraph_7_dict, $paragraph_8_dict, $detected_state, $use_state_shortcode ) {
		$key_options = array(
			'9vxk2p', 'rddpm7', '6f5bza', 'q1gbzg', '7xj2jn', 'rc9iod', 'armq2', 'x58wh', 'u3ql0n', '2k8fgh',
			'cz8bsk', 'yzjhed', 'dblfsd', 'n01p7o', 'r9x286', 'g6m3k', 'h4n8p', 'j7q2w', 'k9r5t', 'l3s8v',
		);
		$default_p   = self::fallback_paragraph( $detected_state, $use_state_shortcode );
		$version_keys = array();
		foreach ( array_keys( $category_ul_items ) as $k ) {
			if ( strpos( $k, $category . '_version_' ) === 0 ) {
				$version_keys[] = $k;
			}
		}
		usort(
			$version_keys,
			function ( $a, $b ) {
				$na = (int) preg_replace( '/^.*_version_/', '', $a );
				$nb = (int) preg_replace( '/^.*_version_/', '', $b );
				return $na - $nb;
			}
		);
		if ( empty( $version_keys ) ) {
			return array(
				'9vxk2p' => '<p>Professional service available in your area.</p><ul><li>24/7 Emergency Response</li><li>Licensed & Insured</li><li>Fast Response Time</li></ul>',
			);
		}
		$ul_dict = array();
		foreach ( $version_keys as $i => $version_key ) {
			if ( $i >= count( $key_options ) ) {
				break;
			}
			$items = $category_ul_items[ $version_key ];
			$vn    = (int) preg_replace( '/^.*_version_/', '', $version_key );
			$p7    = isset( $paragraph_7_dict[ 'version' . $vn ] ) ? $paragraph_7_dict[ 'version' . $vn ] : '';
			$p8    = isset( $paragraph_8_dict[ 'version' . $vn ] ) ? $paragraph_8_dict[ 'version' . $vn ] : '';
			if ( $p7 && $p7 === $default_p ) {
				$p7 = '';
			}
			if ( $p8 && ( $p8 === $default_p || $p8 === $p7 ) ) {
				$p8 = '';
			}
			$paragraph_content = $p7 . $p8;
			$ul_content        = "<ul class='whiterail-ul'>";
			if ( $items ) {
				foreach ( $items as $item ) {
					$ul_content .= '<li>' . $item . '</li>';
				}
			} else {
				$ul_content .= '<li>Professional service available in your area</li>';
				$ul_content .= '<li>24/7 Emergency Response</li>';
				$ul_content .= '<li>Licensed & Insured</li>';
			}
			$ul_content .= '</ul>';
			$ul_dict[ $key_options[ $i ] ] = $paragraph_content . $ul_content;
		}
		return $ul_dict;
	}
}

/**
 * Admin UI: Magic Page → Import generator.
 */
class MPE_Magic_Page_Import_Generator_Admin {

	const PAGE_SLUG = 'magic-page-import-generator';

	public static function init() {
		add_action( 'admin_menu', array( __CLASS__, 'register_menu' ), 21 );
		add_action( 'admin_post_mpe_generate_magicpage_import', array( __CLASS__, 'handle_generate' ) );
	}

	public static function register_menu() {
		add_submenu_page(
			'edit.php?post_type=magicpage',
			__( 'Magic Page import generator', 'magic-page-essentials' ),
			__( 'Import generator', 'magic-page-essentials' ),
			'manage_options',
			self::PAGE_SLUG,
			array( __CLASS__, 'render_page' )
		);
	}

	public static function handle_generate() {
		if ( ! current_user_can( 'manage_options' ) ) {
			wp_die( esc_html__( 'You do not have permission to do this.', 'magic-page-essentials' ) );
		}
		check_admin_referer( 'mpe_generate_import' );

		$raw = '';
		$src = isset( $_POST['mpe_source'] ) ? sanitize_key( wp_unslash( $_POST['mpe_source'] ) ) : 'paste';

		if ( 'file' === $src && ! empty( $_FILES['mpe_file']['tmp_name'] ) ) {
			$file = $_FILES['mpe_file'];
			if ( ! empty( $file['error'] ) ) {
				self::redirect_error( __( 'File upload failed.', 'magic-page-essentials' ) );
			}
			$raw = file_get_contents( $file['tmp_name'] );
			if ( false === $raw ) {
				self::redirect_error( __( 'Could not read the uploaded file.', 'magic-page-essentials' ) );
			}
		} elseif ( 'gdoc' === $src && ! empty( $_POST['mpe_gdoc_url'] ) ) {
			$url = esc_url_raw( wp_unslash( $_POST['mpe_gdoc_url'] ) );
			$id  = self::extract_google_doc_id( $url );
			if ( ! $id ) {
				self::redirect_error( __( 'Could not find a Google Doc ID in that URL.', 'magic-page-essentials' ) );
			}
			$export = 'https://docs.google.com/document/d/' . rawurlencode( $id ) . '/export?format=txt';
			$resp   = wp_remote_get(
				$export,
				array(
					'timeout' => 30,
					'redirection' => 3,
					'headers' => array(
						'User-Agent' => 'WordPress/' . get_bloginfo( 'version' ) . '; ' . home_url( '/' ),
					),
				)
			);
			if ( is_wp_error( $resp ) ) {
				self::redirect_error( $resp->get_error_message() );
			}
			$code = wp_remote_retrieve_response_code( $resp );
			$raw  = wp_remote_retrieve_body( $resp );
			if ( $code < 200 || $code >= 300 || '' === trim( (string) $raw ) ) {
				self::redirect_error(
					__( 'Could not download the document. Set sharing to “Anyone with the link can view” or paste the text instead.', 'magic-page-essentials' )
				);
			}
		} else {
			if ( isset( $_POST['mpe_raw'] ) ) {
				$raw = wp_unslash( $_POST['mpe_raw'] );
			}
		}

		$result = MPE_Magic_Page_Import_Generator::generate( $raw );
		if ( is_wp_error( $result ) ) {
			self::redirect_error( $result->get_error_message() );
		}

		nocache_headers();
		header( 'Content-Type: text/plain; charset=utf-8' );
		header( 'Content-Disposition: attachment; filename="magicpage_import_from_txt.txt"' );
		// phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
		echo $result['serialized'];
		exit;
	}

	/**
	 * @param string $message Error message.
	 */
	private static function redirect_error( $message ) {
		$base = admin_url( 'edit.php?post_type=magicpage&page=' . self::PAGE_SLUG );
		$url  = add_query_arg( 'mpe_err', rawurlencode( $message ), $base );
		wp_safe_redirect( $url );
		exit;
	}

	/**
	 * @param string $url Google Docs URL.
	 * @return string|null Document ID.
	 */
	private static function extract_google_doc_id( $url ) {
		if ( preg_match( '#/document/d/([a-zA-Z0-9_-]+)#', $url, $m ) ) {
			return $m[1];
		}
		if ( preg_match( '#/document/d/([a-zA-Z0-9_-]+)/#', $url, $m ) ) {
			return $m[1];
		}
		if ( preg_match( '#/document/d/([a-zA-Z0-9_-]+)(?:/|$|\?)#', $url, $m ) ) {
			return $m[1];
		}
		if ( preg_match( '/[?&]id=([a-zA-Z0-9_-]+)/', $url, $m ) ) {
			return $m[1];
		}
		return null;
	}

	public static function render_page() {
		if ( ! current_user_can( 'manage_options' ) ) {
			return;
		}

		$err = isset( $_GET['mpe_err'] ) ? sanitize_text_field( wp_unslash( rawurldecode( wp_unslash( $_GET['mpe_err'] ) ) ) ) : '';

		$essentials_url = admin_url( 'edit.php?post_type=magicpage&page=magic-page-essentials' );
		?>
		<div class="wrap mpe-import-generator-wrap">
			<h1><?php esc_html_e( 'Magic Page import generator', 'magic-page-essentials' ); ?></h1>
			<p class="description">
				<?php esc_html_e( 'Generates a PHP-serialized spintax file for Magic Page import (same logic as the offline Python script). Your source should still include heading tags (H1, H2) in HTML form. Google’s plain-text export strips those tags—paste from the editor, upload HTML, or download as Web Page and copy the markup.', 'magic-page-essentials' ); ?>
			</p>
			<p>
				<a href="<?php echo esc_url( $essentials_url ); ?>"><?php esc_html_e( '← Magic Page Essentials settings', 'magic-page-essentials' ); ?></a>
			</p>

			<?php if ( $err ) : ?>
				<div class="notice notice-error"><p><?php echo esc_html( $err ); ?></p></div>
			<?php endif; ?>

			<hr />

			<h2><?php esc_html_e( 'Paste text', 'magic-page-essentials' ); ?></h2>
			<form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
				<?php wp_nonce_field( 'mpe_generate_import' ); ?>
				<input type="hidden" name="action" value="mpe_generate_magicpage_import" />
				<input type="hidden" name="mpe_source" value="paste" />
				<p>
					<label for="mpe_raw"><strong><?php esc_html_e( 'Raw content', 'magic-page-essentials' ); ?></strong></label>
				</p>
				<textarea name="mpe_raw" id="mpe_raw" rows="16" class="large-text code" placeholder="&lt;h1&gt;…&lt;/h1&gt;"></textarea>
				<?php submit_button( __( 'Generate & download import file', 'magic-page-essentials' ) ); ?>
			</form>

			<hr />

			<h2><?php esc_html_e( 'Upload .txt file', 'magic-page-essentials' ); ?></h2>
			<form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>" enctype="multipart/form-data">
				<?php wp_nonce_field( 'mpe_generate_import' ); ?>
				<input type="hidden" name="action" value="mpe_generate_magicpage_import" />
				<input type="hidden" name="mpe_source" value="file" />
				<p>
					<input type="file" name="mpe_file" accept=".txt,text/plain" required />
				</p>
				<?php submit_button( __( 'Generate from file', 'magic-page-essentials' ) ); ?>
			</form>

			<hr />

			<h2><?php esc_html_e( 'Google Doc (public link)', 'magic-page-essentials' ); ?></h2>
			<p class="description">
				<?php esc_html_e( 'The document must be shared so anyone with the link can view it. Private docs cannot be fetched by the server.', 'magic-page-essentials' ); ?>
			</p>
			<form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
				<?php wp_nonce_field( 'mpe_generate_import' ); ?>
				<input type="hidden" name="action" value="mpe_generate_magicpage_import" />
				<input type="hidden" name="mpe_source" value="gdoc" />
				<p>
					<label for="mpe_gdoc_url"><strong><?php esc_html_e( 'Google Doc URL', 'magic-page-essentials' ); ?></strong></label><br />
					<input type="url" name="mpe_gdoc_url" id="mpe_gdoc_url" class="large-text" placeholder="https://docs.google.com/document/d/…/edit" />
				</p>
				<?php submit_button( __( 'Fetch & generate', 'magic-page-essentials' ) ); ?>
			</form>
		</div>
		<?php
	}
}
