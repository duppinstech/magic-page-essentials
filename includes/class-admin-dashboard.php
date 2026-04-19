<?php
/**
 * Analytics dashboard and visit/click tracking.
 *
 * @package Magic_Page_Essentials
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Magic Page analytics (admin charts + lightweight front-end tracking).
 */
class MagicPage_Analytics_Dashboard {

	/**
	 * @var MagicPage_Analytics_Dashboard|null
	 */
	private static $instance = null;

	/**
	 * Magic Page CPT slug (vendor default).
	 *
	 * @var string
	 */
	private $post_type = 'magicpage';

	/**
	 * Boot analytics submenu and hooks when enabled.
	 *
	 * @return void
	 */
	public static function maybe_boot() {
		if ( ! class_exists( 'Magic_Page_Essentials_Settings', false ) ) {
			return;
		}
		if ( ! Magic_Page_Essentials_Settings::is_feature_enabled( 'analytics_dashboard' ) ) {
			return;
		}
		self::get_instance();
	}

	/**
	 * @return MagicPage_Analytics_Dashboard
	 */
	public static function get_instance() {
		if ( null === self::$instance ) {
			self::$instance = new self();
		}
		return self::$instance;
	}

	private function __construct() {
		add_action( 'admin_menu', array( $this, 'add_dashboard_menu' ) );
		add_action( 'admin_enqueue_scripts', array( $this, 'enqueue_assets' ) );
		add_action( 'wp_enqueue_scripts', array( $this, 'enqueue_frontend_analytics_script' ) );

		add_action( 'wp_ajax_nopriv_magicpage_record_visit', array( $this, 'record_magicpage_visit' ) );
		add_action( 'wp_ajax_magicpage_record_visit', array( $this, 'record_magicpage_visit' ) );
		add_action( 'wp_ajax_nopriv_magicpage_record_click', array( $this, 'record_magicpage_click' ) );
		add_action( 'wp_ajax_magicpage_record_click', array( $this, 'record_magicpage_click' ) );

		add_action( 'wp_ajax_magicpage_analytics_data', array( $this, 'ajax_fetch_analytics_data' ) );
		add_action( 'wp_ajax_magicpage_analytics_clear_unassigned', array( $this, 'ajax_clear_unassigned_analytics' ) );
	}

	/**
	 * Post IDs that contribute to analytics (magicpage CPT and optionally static pages from Magic Page export).
	 *
	 * @return int[]
	 */
	private function get_tracked_post_ids() {
		$magicpages = get_posts(
			array(
				'post_type'              => $this->post_type,
				'posts_per_page'         => -1,
				'post_status'            => 'publish',
				'fields'                 => 'ids',
				'no_found_rows'          => true,
				'update_post_meta_cache' => false,
				'update_post_term_cache' => false,
			)
		);

		if ( ! Magic_Page_Essentials_Settings::is_feature_enabled( 'analytics_include_static_pages' ) ) {
			return $magicpages;
		}

		// Export-to-static writes _group_id and _batch_id; _location_id alone may exist from the admin
		// "Location & Group" metabox without an export (see wp-whiterail-seo export-to-static.php meta_input).
		$static = get_posts(
			array(
				'post_type'              => array( 'page', 'post' ),
				'posts_per_page'         => -1,
				'post_status'            => 'publish',
				'fields'                 => 'ids',
				'no_found_rows'          => true,
				'update_post_meta_cache' => false,
				'update_post_term_cache' => false,
				'meta_query'             => array(
					'relation' => 'OR',
					array(
						'key'     => '_group_id',
						'value'   => '',
						'compare' => '!=',
						'type'    => 'CHAR',
					),
					array(
						'key'     => '_batch_id',
						'value'   => '',
						'compare' => '!=',
						'type'    => 'CHAR',
					),
				),
			)
		);

		return array_values( array_unique( array_merge( $magicpages, $static ) ) );
	}

	/**
	 * Whether a Page/Post looks like a static page created by Magic Page export (not merely a manual location in metabox).
	 *
	 * @param int $post_id Post ID.
	 * @return bool
	 */
	public static function is_static_page_from_magic_export( $post_id ) {
		$post_id = (int) $post_id;
		if ( $post_id <= 0 ) {
			return false;
		}
		$batch = get_post_meta( $post_id, '_batch_id', true );
		$group = get_post_meta( $post_id, '_group_id', true );
		$out   = ( $batch !== '' && $batch !== false && $batch !== null )
			|| ( $group !== '' && $group !== false && $group !== null );

		/**
		 * Override whether a static Page/Post is included in Magic Page analytics.
		 *
		 * @param bool $out     Default decision from export meta (_group_id / _batch_id).
		 * @param int  $post_id Post ID.
		 */
		return (bool) apply_filters( 'mpe_analytics_track_static_page', $out, $post_id );
	}

	/**
	 * Whether this post may record visits/clicks.
	 *
	 * @param int $post_id Post ID.
	 * @return bool
	 */
	public static function is_post_tracked_for_analytics( $post_id ) {
		$post_id = (int) $post_id;
		if ( $post_id <= 0 ) {
			return false;
		}
		$pt = get_post_type( $post_id );
		if ( 'magicpage' === $pt ) {
			return true;
		}
		if ( ! in_array( $pt, array( 'page', 'post' ), true ) ) {
			return false;
		}
		if ( ! class_exists( 'Magic_Page_Essentials_Settings', false ) || ! Magic_Page_Essentials_Settings::is_feature_enabled( 'analytics_include_static_pages' ) ) {
			return false;
		}

		return self::is_static_page_from_magic_export( $post_id );
	}

	/**
	 * Resolve location bucket key to label and region (termmeta `region` on `location` taxonomy).
	 *
	 * @param string $location_key Raw meta value or '_unassigned'.
	 * @return array{label:string,region:string}
	 */
	private static function resolve_location_display( $location_key ) {
		if ( '_unassigned' === $location_key || '' === $location_key ) {
			return array(
				'label'  => __( 'Unassigned', 'magic-page-essentials' ),
				'region' => '—',
			);
		}

		$tid = absint( $location_key );
		if ( $tid > 0 ) {
			$term = get_term( $tid, 'location' );
			if ( $term && ! is_wp_error( $term ) ) {
				$region = get_term_meta( $term->term_id, 'region', true );
				if ( '' === $region || false === $region ) {
					$region = '—';
				}
				return array(
					'label'  => $term->name,
					'region' => is_string( $region ) ? $region : '—',
				);
			}
		}

		return array(
			'label'  => (string) $location_key,
			'region' => '—',
		);
	}

	/**
	 * @return void
	 */
	public function add_dashboard_menu() {
		add_submenu_page(
			'edit.php?post_type=' . $this->post_type,
			__( 'Magic Pages Analytics', 'magic-page-essentials' ),
			__( 'Analytics', 'magic-page-essentials' ),
			'manage_options',
			'magicpage-analytics-dashboard',
			array( $this, 'render_dashboard_page' )
		);
	}

	/**
	 * @param string $hook Current admin page hook.
	 * @return void
	 */
	public function enqueue_assets( $hook ) {
		if ( 'magicpage_page_magicpage-analytics-dashboard' !== $hook ) {
			return;
		}

		wp_enqueue_script(
			'chartjs',
			'https://cdn.jsdelivr.net/npm/chart.js',
			array(),
			'4.4.0',
			true
		);

		$assets_url = MAGIC_PAGE_ESSENTIALS_URL;

		wp_enqueue_script(
			'magicpage-analytics-js',
			$assets_url . 'assets/js/magicpage-analytics.js',
			array( 'chartjs', 'jquery' ),
			defined( 'MAGIC_PAGE_ESSENTIALS_VERSION' ) ? MAGIC_PAGE_ESSENTIALS_VERSION : '1.0.0',
			true
		);

		wp_enqueue_style(
			'magicpage-analytics-css',
			$assets_url . 'assets/css/magicpage-analytics.css',
			array(),
			defined( 'MAGIC_PAGE_ESSENTIALS_VERSION' ) ? MAGIC_PAGE_ESSENTIALS_VERSION : '1.0.0'
		);

		wp_localize_script(
			'magicpage-analytics-js',
			'magicpageAnalytics',
			array(
				'ajax_url'         => admin_url( 'admin-ajax.php' ),
				'nonce'            => wp_create_nonce( 'magicpage_analytics_nonce' ),
				'per_page'         => 25,
				'i18n'             => array(
					'page_of' => __( 'Page %1$s of %2$s', 'magic-page-essentials' ),
					'prev'    => __( '« Previous', 'magic-page-essentials' ),
					'next'    => __( 'Next »', 'magic-page-essentials' ),
					'clear_unassigned_confirm' => __( 'Clear all visit and click history for tracked pages that have no location assigned? This cannot be undone.', 'magic-page-essentials' ),
					'clear_unassigned_done'    => __( 'Cleared stats for %1$s page(s). Reloading…', 'magic-page-essentials' ),
				),
			)
		);
	}

	/**
	 * @return void
	 */
	public function render_dashboard_page() {
		?>
		<div class="wrap magicpage-analytics-dashboard">
			<header class="mpe-dash-header">
				<h1 class="mpe-dash-title"><?php esc_html_e( 'Magic Pages Analytics', 'magic-page-essentials' ); ?></h1>
				<p class="mpe-dash-subtitle"><?php esc_html_e( 'See which locations get traffic and convert — real stats from your magic pages.', 'magic-page-essentials' ); ?></p>
			</header>

			<div id="mpe-summary-cards" class="mpe-summary-cards">
				<div class="mpe-card mpe-card-stat">
					<span class="mpe-stat-value" id="mpe-stat-locations">—</span>
					<span class="mpe-stat-label"><?php esc_html_e( 'Locations', 'magic-page-essentials' ); ?></span>
				</div>
				<div class="mpe-card mpe-card-stat">
					<span class="mpe-stat-value" id="mpe-stat-visits">—</span>
					<span class="mpe-stat-label"><?php esc_html_e( 'Total visits', 'magic-page-essentials' ); ?></span>
				</div>
				<div class="mpe-card mpe-card-stat">
					<span class="mpe-stat-value" id="mpe-stat-clicks">—</span>
					<span class="mpe-stat-label"><?php esc_html_e( 'Conversions (clicks)', 'magic-page-essentials' ); ?></span>
				</div>
				<div class="mpe-card mpe-card-stat">
					<span class="mpe-stat-value" id="mpe-stat-ctr">—</span>
					<span class="mpe-stat-label"><?php esc_html_e( 'Overall CTR', 'magic-page-essentials' ); ?></span>
				</div>
			</div>

			<section class="mpe-section">
				<h2 class="mpe-section-title"><?php esc_html_e( 'Location performance', 'magic-page-essentials' ); ?></h2>
				<p class="mpe-section-desc"><?php esc_html_e( 'Which locations get the most hits and convert best. Value = traffic + engagement.', 'magic-page-essentials' ); ?></p>
				<p class="mpe-tools mpe-clear-unassigned-wrap">
					<button type="button" class="button" id="mpe-clear-unassigned-stats">
						<?php esc_html_e( 'Clear “Unassigned” visit &amp; click history', 'magic-page-essentials' ); ?>
					</button>
					<span class="description"><?php esc_html_e( 'Removes stored analytics for tracked pages with no _location_id (e.g. old template traffic or pages dropped from export).', 'magic-page-essentials' ); ?></span>
				</p>
				<div class="mpe-section-grid">
					<div class="mpe-card mpe-card-chart">
						<h3 class="mpe-card-heading"><?php esc_html_e( 'Top locations by visits', 'magic-page-essentials' ); ?></h3>
						<div class="mpe-chart-wrap">
							<canvas id="chart-locations-visits"></canvas>
						</div>
					</div>
					<div class="mpe-card mpe-card-chart">
						<h3 class="mpe-card-heading"><?php esc_html_e( 'Top locations by conversions', 'magic-page-essentials' ); ?></h3>
						<div class="mpe-chart-wrap">
							<canvas id="chart-locations-clicks"></canvas>
						</div>
					</div>
				</div>
				<div class="mpe-card mpe-card-table">
					<h3 class="mpe-card-heading"><?php esc_html_e( 'Locations at a glance', 'magic-page-essentials' ); ?></h3>
					<div class="mpe-table-scroll">
						<table class="mpe-table" id="table-locations">
							<thead>
								<tr>
									<th><?php esc_html_e( 'Location', 'magic-page-essentials' ); ?></th>
									<th><?php esc_html_e( 'Region', 'magic-page-essentials' ); ?></th>
									<th><?php esc_html_e( 'Pages', 'magic-page-essentials' ); ?></th>
									<th><?php esc_html_e( 'Visits', 'magic-page-essentials' ); ?></th>
									<th><?php esc_html_e( 'Clicks', 'magic-page-essentials' ); ?></th>
									<th><?php esc_html_e( 'CTR %', 'magic-page-essentials' ); ?></th>
								</tr>
							</thead>
							<tbody id="locations-tbody">
								<tr><td colspan="6"><?php esc_html_e( 'Loading…', 'magic-page-essentials' ); ?></td></tr>
							</tbody>
						</table>
					</div>
					<div class="mpe-pager" id="mpe-locations-pager" hidden></div>
				</div>
			</section>

			<section class="mpe-section">
				<h2 class="mpe-section-title"><?php esc_html_e( 'Visits over time', 'magic-page-essentials' ); ?></h2>
				<div class="mpe-card mpe-card-chart mpe-chart-wide">
					<div class="mpe-chart-wrap">
						<canvas id="chart-page-visits-over-time"></canvas>
					</div>
				</div>
			</section>

			<section class="mpe-section">
				<h2 class="mpe-section-title"><?php esc_html_e( 'Top magic pages', 'magic-page-essentials' ); ?></h2>
				<div class="mpe-card mpe-card-table">
					<div class="mpe-table-scroll">
						<table class="mpe-table" id="table-top-pages">
							<thead>
								<tr>
									<th><?php esc_html_e( 'Page', 'magic-page-essentials' ); ?></th>
									<th><?php esc_html_e( 'Visits', 'magic-page-essentials' ); ?></th>
									<th><?php esc_html_e( 'Clicks', 'magic-page-essentials' ); ?></th>
									<th><?php esc_html_e( 'CTR %', 'magic-page-essentials' ); ?></th>
								</tr>
							</thead>
							<tbody id="top-pages-tbody">
								<tr><td colspan="4"><?php esc_html_e( 'Loading…', 'magic-page-essentials' ); ?></td></tr>
							</tbody>
						</table>
					</div>
					<div class="mpe-pager" id="mpe-top-pages-pager" hidden></div>
				</div>
			</section>
		</div>
		<?php
	}

	/**
	 * Page title for analytics tables: match front-end Magic Page + Yoast %%mpp_*%% behavior, then strip tags.
	 *
	 * @param int $post_id Post ID.
	 * @return string
	 */
	private static function get_analytics_display_title( $post_id ) {
		$post_id = (int) $post_id;
		$pt      = get_post_type( $post_id );
		$raw     = get_post_field( 'post_title', $post_id );
		$raw     = is_string( $raw ) ? $raw : '';

		// Prefer stored SEO title when present (same as get_magic_page_title in Magic Page).
		$source = $raw;
		$meta_title = get_post_meta( $post_id, '_magic_page_meta_title', true );
		if ( is_string( $meta_title ) && $meta_title !== '' ) {
			$source = $meta_title;
		}

		global $post;
		$previous_post = $post instanceof WP_Post ? $post : null;
		$post_object   = get_post( $post_id );
		$post          = ( $post_object instanceof WP_Post ) ? $post_object : null;

		$title = $source;
		if ( $post ) {
			// Runs Magic Page the_title processing for [location], [meta_*], spintax, etc. when brackets/spintax present.
			$title = apply_filters( 'the_title', $title, $post_id );
		}

		$term = class_exists( 'MPE_Yoast_Bridge', false )
			? MPE_Yoast_Bridge::get_location_term_for_post( $post_id )
			: null;

		if ( class_exists( 'MPE_Yoast_Bridge', false ) ) {
			$title = MPE_Yoast_Bridge::replace_mpp_tokens_in_string( $title, $term );
			// Remaining Yoast %%variables%% (sep, title, cf_*, ct_*, etc.); mpp_* already expanded above.
			$title = MPE_Yoast_Bridge::replace_yoast_variables_in_string( $title, $post_id );
		}

		$post = $previous_post;

		$title = wp_strip_all_tags( do_shortcode( is_string( $title ) ? $title : '' ) );

		if ( $title === '' && $post_object instanceof WP_Post && is_string( $post_object->post_title ) ) {
			$title = $post_object->post_title;
		}

		if ( 'page' === $pt ) {
			/* translators: %s: page title */
			$title = sprintf( __( '%s (Page)', 'magic-page-essentials' ), $title );
		} elseif ( 'post' === $pt ) {
			/* translators: %s: post title */
			$title = sprintf( __( '%s (Post)', 'magic-page-essentials' ), $title );
		}
		/**
		 * Filter the label used for a post in Magic Page analytics JSON (after shortcodes / suffix).
		 *
		 * @param string $title   Display title.
		 * @param int    $post_id Post ID.
		 */
		return apply_filters( 'mpe_analytics_display_title', $title, $post_id );
	}

	/**
	 * Build analytics payload (cached briefly to speed repeat loads).
	 *
	 * @param int[] $tracked_ids Tracked post IDs.
	 * @return array<string,mixed>
	 */
	private function build_analytics_payload( array $tracked_ids ) {
		$days = 30;
		$date_counts = array_fill_keys(
			array_map(
				function ( $i ) {
					return gmdate( 'Y-m-d', strtotime( '-' . $i . ' days' ) );
				},
				range( $days - 1, 0 )
			),
			0
		);

		$locations     = array();
		$total_visits    = 0;
		$total_clicks    = 0;
		$top_pages_build = array();

		foreach ( $tracked_ids as $post_id ) {
			$visits = get_post_meta( $post_id, 'magicpage_visits', true );
			if ( ! is_array( $visits ) ) {
				$visits = array();
			}
			$visit_count = count( $visits );
			$click_count = (int) get_post_meta( $post_id, 'magicpage_click_count', true );

			$total_visits += $visit_count;
			$total_clicks += $click_count;

			foreach ( $visits as $visit_date ) {
				if ( ! is_string( $visit_date ) ) {
					continue;
				}
				$key = gmdate( 'Y-m-d', strtotime( $visit_date ) );
				if ( isset( $date_counts[ $key ] ) ) {
					$date_counts[ $key ]++;
				}
			}

			$location_id = get_post_meta( $post_id, '_location_id', true );
			if ( $location_id === '' || false === $location_id || null === $location_id ) {
				$location_key = '_unassigned';
			} else {
				$location_key = (string) $location_id;
			}

			if ( ! isset( $locations[ $location_key ] ) ) {
				$disp                       = self::resolve_location_display( $location_key );
				$locations[ $location_key ] = array(
					'label'  => $disp['label'],
					'region' => $disp['region'],
					'visits' => 0,
					'clicks' => 0,
					'pages'  => 0,
				);
			}

			$locations[ $location_key ]['visits'] += $visit_count;
			$locations[ $location_key ]['clicks'] += $click_count;
			$locations[ $location_key ]['pages']++;

			$ctr = $visit_count > 0 ? round( ( $click_count / $visit_count ) * 100, 1 ) : 0;

			$top_pages_build[] = array(
				'title'  => self::get_analytics_display_title( $post_id ),
				'count'  => $visit_count,
				'clicks' => $click_count,
				'ctr'    => $ctr,
			);
		}

		foreach ( array_keys( $locations ) as $lid ) {
			$disp = self::resolve_location_display( $lid );
			$locations[ $lid ]['label']  = $disp['label'];
			$locations[ $lid ]['region'] = $disp['region'];
			$v                           = $locations[ $lid ]['visits'];
			$locations[ $lid ]['ctr']    = $v > 0 ? round( ( $locations[ $lid ]['clicks'] / $v ) * 100, 1 ) : 0;
		}

		usort(
			$locations,
			function ( $a, $b ) {
				return $b['visits'] - $a['visits'];
			}
		);
		$locations_all   = array_values( $locations );
		$total_locations = count( $locations_all );
		$overall_ctr     = $total_visits > 0 ? round( ( $total_clicks / $total_visits ) * 100, 1 ) : 0;

		usort(
			$top_pages_build,
			function ( $a, $b ) {
				return $b['count'] - $a['count'];
			}
		);

		return array(
			'visits_over_time' => $date_counts,
			'locations_all'    => $locations_all,
			'top_pages_all'    => $top_pages_build,
			'summary'          => array(
				'total_pages'     => count( $tracked_ids ),
				'total_locations' => $total_locations,
				'total_visits'    => $total_visits,
				'total_clicks'    => $total_clicks,
				'overall_ctr'     => $overall_ctr,
			),
		);
	}

	/**
	 * AJAX: delete visit/click meta for tracked posts with no _location_id (the “Unassigned” bucket).
	 *
	 * @return void
	 */
	public function ajax_clear_unassigned_analytics() {
		check_ajax_referer( 'magicpage_analytics_nonce', 'nonce' );
		if ( ! current_user_can( 'manage_options' ) ) {
			wp_send_json_error( array( 'message' => 'Unauthorized' ), 403 );
			return;
		}

		$tracked = $this->get_tracked_post_ids();
		$cleared_posts  = 0;
		$cleared_visits = 0;
		$cleared_clicks = 0;

		foreach ( $tracked as $post_id ) {
			$post_id = (int) $post_id;
			if ( $post_id <= 0 ) {
				continue;
			}

			$location_id = get_post_meta( $post_id, '_location_id', true );
			if ( $location_id !== '' && false !== $location_id && null !== $location_id ) {
				continue;
			}

			/**
			 * Skip clearing analytics for a post (return true to keep its stats).
			 *
			 * @param bool $skip    Default false.
			 * @param int  $post_id Post ID.
			 */
			if ( apply_filters( 'mpe_skip_clear_unassigned_analytics', false, $post_id ) ) {
				continue;
			}

			$visits = get_post_meta( $post_id, 'magicpage_visits', true );
			if ( is_array( $visits ) ) {
				$cleared_visits += count( $visits );
			}
			$cleared_clicks += (int) get_post_meta( $post_id, 'magicpage_click_count', true );

			delete_post_meta( $post_id, 'magicpage_visits' );
			delete_post_meta( $post_id, 'magicpage_visit_count' );
			delete_post_meta( $post_id, 'magicpage_clicks' );
			delete_post_meta( $post_id, 'magicpage_click_count' );
			++$cleared_posts;
		}

		$this->bust_analytics_cache();

		wp_send_json_success(
			array(
				'cleared_posts'  => $cleared_posts,
				'cleared_visits' => $cleared_visits,
				'cleared_clicks' => $cleared_clicks,
			)
		);
	}

	/**
	 * AJAX: aggregated analytics JSON for the dashboard.
	 *
	 * @return void
	 */
	public function ajax_fetch_analytics_data() {
		check_ajax_referer( 'magicpage_analytics_nonce', 'nonce' );
		if ( ! current_user_can( 'manage_options' ) ) {
			wp_send_json_error( array( 'message' => 'Unauthorized' ) );
			return;
		}

		$tracked_ids = $this->get_tracked_post_ids();
		sort( $tracked_ids, SORT_NUMERIC );
		$cache_key = 'mpe_analytics_v3_' . md5( implode( ',', $tracked_ids ) );

		$cached = get_transient( $cache_key );
		if ( is_array( $cached ) && isset( $cached['summary'], $cached['locations_all'], $cached['top_pages_all'], $cached['visits_over_time'] ) ) {
			wp_send_json_success( $cached );
			return;
		}

		if ( ! empty( $tracked_ids ) ) {
			if ( function_exists( '_prime_post_caches' ) ) {
				_prime_post_caches( $tracked_ids, true, true );
			}
			update_meta_cache( 'post', $tracked_ids );
		}

		$payload = $this->build_analytics_payload( $tracked_ids );

		set_transient( $cache_key, $payload, 90 );

		wp_send_json_success( $payload );
	}

	/**
	 * @return void
	 */
	public function enqueue_frontend_analytics_script() {
		if ( ! is_singular() ) {
			return;
		}
		$post_id = get_queried_object_id();
		if ( ! $post_id || ! self::is_post_tracked_for_analytics( $post_id ) ) {
			return;
		}

		$url = MAGIC_PAGE_ESSENTIALS_URL . 'assets/js/magicpage-frontend-analytics.js';
		wp_enqueue_script(
			'magicpage-frontend-analytics',
			$url,
			array( 'jquery' ),
			defined( 'MAGIC_PAGE_ESSENTIALS_VERSION' ) ? MAGIC_PAGE_ESSENTIALS_VERSION : '1.0',
			true
		);

		wp_localize_script(
			'magicpage-frontend-analytics',
			'MagicPageAnalyticsFrontend',
			array(
				'ajax_url'    => admin_url( 'admin-ajax.php' ),
				'post_id'     => $post_id,
				'nonce'       => wp_create_nonce( 'magicpage_visit_nonce' ),
				'click_nonce' => wp_create_nonce( 'magicpage_click_nonce' ),
			)
		);
	}

	/**
	 * @return void
	 */
	public function record_magicpage_visit() {
		check_ajax_referer( 'magicpage_visit_nonce', 'nonce' );

		$post_id = isset( $_POST['post_id'] ) ? intval( $_POST['post_id'] ) : 0;
		if ( ! $post_id || ! self::is_post_tracked_for_analytics( $post_id ) ) {
			wp_send_json_error( 'Invalid post.' );
			return;
		}

		$count = (int) get_post_meta( $post_id, 'magicpage_visit_count', true );
		update_post_meta( $post_id, 'magicpage_visit_count', $count + 1 );

		$visits = get_post_meta( $post_id, 'magicpage_visits', true );
		if ( ! is_array( $visits ) ) {
			$visits = array();
		}
		$visits[] = current_time( 'mysql' );
		update_post_meta( $post_id, 'magicpage_visits', $visits );

		$this->bust_analytics_cache();

		wp_send_json_success();
	}

	/**
	 * Record a link click on a magic page (for conversion/CTR analytics).
	 *
	 * @return void
	 */
	public function record_magicpage_click() {
		check_ajax_referer( 'magicpage_click_nonce', 'click_nonce' );

		$post_id = isset( $_POST['post_id'] ) ? intval( $_POST['post_id'] ) : 0;
		if ( ! $post_id || ! self::is_post_tracked_for_analytics( $post_id ) ) {
			wp_send_json_error( 'Invalid post.' );
			return;
		}

		$href = isset( $_POST['href'] ) ? esc_url_raw( wp_unslash( $_POST['href'] ) ) : '';
		$text = isset( $_POST['text'] ) ? sanitize_text_field( wp_unslash( $_POST['text'] ) ) : '';
		$entry = array(
			't' => current_time( 'mysql' ),
			'u' => $href,
			'l' => mb_substr( $text, 0, 255 ),
		);

		$clicks = get_post_meta( $post_id, 'magicpage_clicks', true );
		if ( ! is_array( $clicks ) ) {
			$clicks = array();
		}
		$clicks[] = $entry;
		update_post_meta( $post_id, 'magicpage_clicks', $clicks );

		$total = (int) get_post_meta( $post_id, 'magicpage_click_count', true );
		update_post_meta( $post_id, 'magicpage_click_count', $total + 1 );

		$this->bust_analytics_cache();

		wp_send_json_success();
	}

	/**
	 * Drop cached analytics JSON so the dashboard reflects new visits/clicks quickly.
	 *
	 * @return void
	 */
	private function bust_analytics_cache() {
		$tracked_ids = $this->get_tracked_post_ids();
		sort( $tracked_ids, SORT_NUMERIC );
		delete_transient( 'mpe_analytics_v3_' . md5( implode( ',', $tracked_ids ) ) );
	}
}
