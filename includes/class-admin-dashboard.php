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
		add_action( 'admin_footer', array( $this, 'render_page_analytics_modal' ) );
		add_action( 'wp_enqueue_scripts', array( $this, 'enqueue_frontend_analytics_script' ) );

		add_action( 'wp_ajax_nopriv_magicpage_record_visit', array( $this, 'record_magicpage_visit' ) );
		add_action( 'wp_ajax_magicpage_record_visit', array( $this, 'record_magicpage_visit' ) );
		add_action( 'wp_ajax_nopriv_magicpage_record_click', array( $this, 'record_magicpage_click' ) );
		add_action( 'wp_ajax_magicpage_record_click', array( $this, 'record_magicpage_click' ) );
		add_action( 'wp_ajax_nopriv_magicpage_record_404', array( $this, 'record_magicpage_404' ) );
		add_action( 'wp_ajax_magicpage_record_404', array( $this, 'record_magicpage_404' ) );

		add_action( 'wp_ajax_magicpage_analytics_data', array( $this, 'ajax_fetch_analytics_data' ) );
		add_action( 'wp_ajax_magicpage_page_analytics', array( $this, 'ajax_fetch_page_analytics' ) );
		add_action( 'wp_ajax_magicpage_analytics_clear_unassigned', array( $this, 'ajax_clear_unassigned_analytics' ) );
		add_action( 'admin_post_magicpage_analytics_export', array( $this, 'handle_analytics_export' ) );

		add_filter( 'post_row_actions', array( $this, 'add_analytics_row_action' ), 10, 2 );
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

		$static_ids = array();
		if ( ! Magic_Page_Essentials_Settings::is_feature_enabled( 'analytics_include_static_pages' ) ) {
			$merged = $magicpages;
		} else {
			// Export-to-static writes _group_id and _batch_id; _location_id alone may exist from the admin
			// "Location & Group" metabox without an export (see wp-whiterail-seo export-to-static.php meta_input).
			$static_ids = get_posts(
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

			$merged = array_merge( $magicpages, $static_ids );
		}

		$merged = array_values( array_unique( array_map( 'intval', $merged ) ) );

		/**
		 * Extend which post IDs are included in analytics (e.g. LocaleForge `lf_landing`).
		 *
		 * @param int[] $merged     Combined IDs (magicpage ± static export pages).
		 * @param int[] $magicpages Magic Page CPT IDs.
		 * @param int[] $static_ids Static page IDs when static analytics is enabled (else empty).
		 * @since 1.2.4 Filter: `magic_page_essentials_analytics_tracked_post_ids` (formerly `mpe_analytics_tracked_post_ids`).
		 */
		return array_values( array_unique( array_map( 'intval', (array) apply_filters( 'magic_page_essentials_analytics_tracked_post_ids', $merged, $magicpages, $static_ids ) ) ) );
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
		 * @since 1.2.4 Filter: `magic_page_essentials_analytics_track_static_page` (formerly `mpe_analytics_track_static_page`).
		 */
		return (bool) apply_filters( 'magic_page_essentials_analytics_track_static_page', $out, $post_id );
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
		$pt      = get_post_type( $post_id );
		$tracked = false;
		if ( 'magicpage' === $pt ) {
			$tracked = true;
		} elseif ( in_array( $pt, array( 'page', 'post' ), true )
			&& class_exists( 'Magic_Page_Essentials_Settings', false )
			&& Magic_Page_Essentials_Settings::is_feature_enabled( 'analytics_include_static_pages' ) ) {
			$tracked = self::is_static_page_from_magic_export( $post_id );
		}

		/**
		 * Whether this post may record visits/clicks (extend for other CPTs).
		 *
		 * @param bool   $tracked Default from Magic Page / static export rules.
		 * @param int    $post_id Post ID.
		 * @param string $pt      Post type slug.
		 * @since 1.2.4 Filter: `magic_page_essentials_analytics_is_post_tracked` (formerly `mpe_analytics_is_post_tracked`).
		 */
		return (bool) apply_filters( 'magic_page_essentials_analytics_is_post_tracked', $tracked, $post_id, $pt );
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

			// LocaleForge and other stacks may bucket by `lf_place` term ID (`_lf_place_id`).
			if ( taxonomy_exists( 'lf_place' ) ) {
				$term = get_term( $tid, 'lf_place' );
				if ( $term && ! is_wp_error( $term ) ) {
					$region = get_term_meta( $term->term_id, 'lf_region', true );
					if ( '' === $region || false === $region ) {
						$region = '—';
					}
					return array(
						'label'  => $term->name,
						'region' => is_string( $region ) ? $region : '—',
					);
				}
			}
		}

		return array(
			'label'  => (string) $location_key,
			'region' => '—',
		);
	}

	/**
	 * Location bucket for analytics: Magic Page `_location_id`, then LocaleForge `_lf_place_id`.
	 *
	 * @param int $post_id Post ID.
	 * @return string Term ID string or '_unassigned'.
	 */
	private static function get_location_bucket_key_for_post( $post_id ) {
		$post_id = (int) $post_id;
		if ( $post_id <= 0 ) {
			return '_unassigned';
		}
		$location_id = get_post_meta( $post_id, '_location_id', true );
		if ( $location_id !== '' && false !== $location_id && null !== $location_id ) {
			return (string) $location_id;
		}
		$place_id = get_post_meta( $post_id, '_lf_place_id', true );
		if ( $place_id !== '' && false !== $place_id && null !== $place_id ) {
			return (string) $place_id;
		}

		return '_unassigned';
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
		if ( 'edit.php' === $hook ) {
			$this->enqueue_list_modal_assets();
			return;
		}

		$allowed_hooks = array( 'magicpage_page_magicpage-analytics-dashboard' );
		/**
		 * Admin screen hook suffixes where analytics assets load (e.g. LocaleForge mirror page).
		 *
		 * @param string[] $allowed_hooks Hook suffixes from `add_submenu_page`.
		 * @since 1.2.4 Filter: `magic_page_essentials_analytics_dashboard_hook_suffixes` (formerly `mpe_analytics_dashboard_hook_suffixes`).
		 */
		$allowed_hooks = apply_filters( 'magic_page_essentials_analytics_dashboard_hook_suffixes', $allowed_hooks );
		if ( ! in_array( $hook, $allowed_hooks, true ) ) {
			return;
		}

		wp_enqueue_script(
			'chartjs',
			MAGIC_PAGE_ESSENTIALS_URL . 'assets/js/vendor/chart.umd.min.js',
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

		/* translators: 1: current page number, 2: total pages */
		$i18n_page_of = __( 'Page %1$s of %2$s', 'magic-page-essentials' );
		/* translators: %1$s: number of pages cleared */
		$i18n_clear_done = __( 'Cleared stats for %1$s page(s). Reloading…', 'magic-page-essentials' );

		wp_localize_script(
			'magicpage-analytics-js',
			'magicpageAnalytics',
			array(
				'ajax_url'         => admin_url( 'admin-ajax.php' ),
				'nonce'            => wp_create_nonce( 'magicpage_analytics_nonce' ),
				'per_page'         => 25,
				'export_url'       => wp_nonce_url( admin_url( 'admin-post.php?action=magicpage_analytics_export' ), 'magicpage_analytics_export' ),
				'i18n'             => array(
					'page_of'                  => $i18n_page_of,
					'prev'                     => __( '« Previous', 'magic-page-essentials' ),
					'next'                     => __( 'Next »', 'magic-page-essentials' ),
					'clear_unassigned_confirm' => __( 'Clear all visit and click history for tracked pages that have no location assigned? This cannot be undone.', 'magic-page-essentials' ),
					'clear_unassigned_done'    => $i18n_clear_done,
					'loading'                  => __( 'Loading…', 'magic-page-essentials' ),
					'failed'                   => __( 'Failed to load data.', 'magic-page-essentials' ),
					'no_locations'             => __( 'No location data yet. Visits and clicks on tracked pages will show here.', 'magic-page-essentials' ),
					'no_pages'                 => __( 'No page data yet.', 'magic-page-essentials' ),
					'no_data'                  => __( 'No data yet.', 'magic-page-essentials' ),
					'no_visits_range'          => __( 'No visit data for this date range yet.', 'magic-page-essentials' ),
					'no_devices'               => __( 'No device data for this date range yet.', 'magic-page-essentials' ),
					'no_404s'                  => __( 'No 404s recorded for this date range.', 'magic-page-essentials' ),
					'no_404_paths'             => __( 'No 404 paths in this date range.', 'magic-page-essentials' ),
					'range_invalid'            => __( 'Choose a start date and an end date, with the start on or before the end.', 'magic-page-essentials' ),
					'visits'                   => __( 'Visits', 'magic-page-essentials' ),
					'conversions'              => __( 'Conversions', 'magic-page-essentials' ),
					'not_found'                => __( '404s', 'magic-page-essentials' ),
					'clear_failed'             => __( 'Could not clear stats.', 'magic-page-essentials' ),
					'request_failed'           => __( 'Request failed.', 'magic-page-essentials' ),
				),
			)
		);
	}

	/**
	 * Assets for the per-page analytics modal on the Pages and Magic Page lists.
	 *
	 * @return void
	 */
	private function enqueue_list_modal_assets() {
		$screen = function_exists( 'get_current_screen' ) ? get_current_screen() : null;
		if ( ! $screen || 'edit' !== $screen->base || ! in_array( $screen->post_type, array( 'page', $this->post_type ), true ) ) {
			return;
		}

		$version = defined( 'MAGIC_PAGE_ESSENTIALS_VERSION' ) ? MAGIC_PAGE_ESSENTIALS_VERSION : '1.0.0';

		wp_enqueue_style(
			'magicpage-analytics-css',
			MAGIC_PAGE_ESSENTIALS_URL . 'assets/css/magicpage-analytics.css',
			array(),
			$version
		);

		wp_enqueue_script(
			'magicpage-page-analytics',
			MAGIC_PAGE_ESSENTIALS_URL . 'assets/js/magicpage-page-analytics.js',
			array( 'jquery' ),
			$version,
			true
		);

		wp_localize_script(
			'magicpage-page-analytics',
			'magicpagePageAnalytics',
			array(
				'ajax_url' => admin_url( 'admin-ajax.php' ),
				'nonce'    => wp_create_nonce( 'magicpage_page_analytics' ),
				'i18n'     => array(
					'loading'    => __( 'Loading…', 'magic-page-essentials' ),
					'failed'     => __( 'Could not load analytics for this page.', 'magic-page-essentials' ),
					'visits'     => __( 'Visits', 'magic-page-essentials' ),
					'clicks'     => __( 'Clicks', 'magic-page-essentials' ),
					'ctr'        => __( 'CTR', 'magic-page-essentials' ),
					'devices'    => __( 'Devices', 'magic-page-essentials' ),
					'recent'     => __( 'Recent clicks', 'magic-page-essentials' ),
					'no_clicks'  => __( 'No clicks in this date range.', 'magic-page-essentials' ),
					'untracked'  => __( 'Front-end tracking is off for this page, so new visits are not recorded.', 'magic-page-essentials' ),
					'close'      => __( 'Close', 'magic-page-essentials' ),
					'view'       => __( 'View page', 'magic-page-essentials' ),
				),
			)
		);
	}

	/**
	 * @return void
	 */
	public function render_dashboard_page() {
		$export_base = wp_nonce_url( admin_url( 'admin-post.php?action=magicpage_analytics_export' ), 'magicpage_analytics_export' );
		?>
		<div class="wrap magicpage-analytics-dashboard">
			<header class="mpe-dash-header">
				<h1 class="mpe-dash-title"><?php esc_html_e( 'Magic Pages Analytics', 'magic-page-essentials' ); ?></h1>
				<p class="mpe-dash-subtitle"><?php esc_html_e( 'See which locations get traffic and convert — real stats from your magic pages.', 'magic-page-essentials' ); ?></p>
			</header>

			<div class="mpe-range-bar">
				<label for="mpe-range"><?php esc_html_e( 'Date range', 'magic-page-essentials' ); ?></label>
				<select id="mpe-range">
					<option value="7"><?php esc_html_e( 'Last 7 days', 'magic-page-essentials' ); ?></option>
					<option value="30" selected><?php esc_html_e( 'Last 30 days', 'magic-page-essentials' ); ?></option>
					<option value="90"><?php esc_html_e( 'Last 90 days', 'magic-page-essentials' ); ?></option>
					<option value="365"><?php esc_html_e( 'Last 12 months', 'magic-page-essentials' ); ?></option>
					<option value="all"><?php esc_html_e( 'All time', 'magic-page-essentials' ); ?></option>
					<option value="custom"><?php esc_html_e( 'Custom', 'magic-page-essentials' ); ?></option>
				</select>
				<span id="mpe-custom-range" hidden>
					<label class="screen-reader-text" for="mpe-range-start"><?php esc_html_e( 'Start date', 'magic-page-essentials' ); ?></label>
					<input type="date" id="mpe-range-start" />
					<label class="screen-reader-text" for="mpe-range-end"><?php esc_html_e( 'End date', 'magic-page-essentials' ); ?></label>
					<input type="date" id="mpe-range-end" />
				</span>
				<button type="button" class="button button-primary" id="mpe-range-apply"><?php esc_html_e( 'Apply', 'magic-page-essentials' ); ?></button>
				<a class="button" id="mpe-export-csv" data-format="csv" href="<?php echo esc_url( $export_base . '&format=csv&range=30' ); ?>"><?php esc_html_e( 'Export CSV', 'magic-page-essentials' ); ?></a>
				<a class="button" id="mpe-export-json" data-format="json" href="<?php echo esc_url( $export_base . '&format=json&range=30' ); ?>"><?php esc_html_e( 'Export JSON', 'magic-page-essentials' ); ?></a>
				<p class="mpe-range-status" id="mpe-range-status"></p>
			</div>

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
				<div class="mpe-card mpe-card-stat">
					<span class="mpe-stat-value" id="mpe-stat-404">—</span>
					<span class="mpe-stat-label"><?php esc_html_e( '404s', 'magic-page-essentials' ); ?></span>
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

			<section class="mpe-section">
				<h2 class="mpe-section-title"><?php esc_html_e( 'Devices and 404s', 'magic-page-essentials' ); ?></h2>
				<p class="mpe-section-desc"><?php esc_html_e( 'Device type comes from page views. 404s are recorded when a visitor opens a missing URL.', 'magic-page-essentials' ); ?></p>
				<div class="mpe-section-grid">
					<div class="mpe-card mpe-card-chart">
						<h3 class="mpe-card-heading"><?php esc_html_e( 'Device type', 'magic-page-essentials' ); ?></h3>
						<div class="mpe-chart-wrap">
							<canvas id="chart-devices"></canvas>
						</div>
					</div>
					<div class="mpe-card mpe-card-chart">
						<h3 class="mpe-card-heading"><?php esc_html_e( '404s over time', 'magic-page-essentials' ); ?></h3>
						<div class="mpe-chart-wrap">
							<canvas id="chart-404s"></canvas>
						</div>
					</div>
				</div>
				<div class="mpe-card mpe-card-table">
					<h3 class="mpe-card-heading"><?php esc_html_e( 'Top 404 paths', 'magic-page-essentials' ); ?></h3>
					<div class="mpe-table-scroll">
						<table class="mpe-table" id="table-404s">
							<thead>
								<tr>
									<th><?php esc_html_e( 'Path', 'magic-page-essentials' ); ?></th>
									<th><?php esc_html_e( 'Hits', 'magic-page-essentials' ); ?></th>
									<th><?php esc_html_e( 'Last seen', 'magic-page-essentials' ); ?></th>
								</tr>
							</thead>
							<tbody id="not-found-tbody">
								<tr><td colspan="3"><?php esc_html_e( 'Loading…', 'magic-page-essentials' ); ?></td></tr>
							</tbody>
						</table>
					</div>
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
			// phpcs:ignore WordPress.NamingConventions.PrefixAllGlobals.NonPrefixedHooknameFound -- Core WordPress filter.
			$title = apply_filters( 'the_title', $title, $post_id );
		}

		$term = class_exists( 'Magic_Page_Essentials_Yoast_Bridge', false )
			? Magic_Page_Essentials_Yoast_Bridge::get_location_term_for_post( $post_id )
			: null;

		if ( class_exists( 'Magic_Page_Essentials_Yoast_Bridge', false ) ) {
			$title = Magic_Page_Essentials_Yoast_Bridge::replace_mpp_tokens_in_string( $title, $term );
			// Remaining Yoast %%variables%% (sep, title, cf_*, ct_*, etc.); mpp_* already expanded above.
			$title = Magic_Page_Essentials_Yoast_Bridge::replace_yoast_variables_in_string( $title, $post_id );
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
		 * @since 1.2.4 Filter: `magic_page_essentials_analytics_display_title` (formerly `mpe_analytics_display_title`).
		 */
		return apply_filters( 'magic_page_essentials_analytics_display_title', $title, $post_id );
	}

	/**
	 * Build analytics payload for a date range (cached briefly to speed repeat loads).
	 *
	 * @param int[]                $tracked_ids Tracked post IDs.
	 * @param array<string,mixed>  $range       Parsed range from parse_analytics_range().
	 * @return array<string,mixed>
	 */
	private function build_analytics_payload( array $tracked_ids, array $range ) {
		$date_counts   = $this->empty_date_series( $range );
		$locations     = array();
		$total_visits  = 0;
		$total_clicks  = 0;
		$device_totals = array(
			'desktop' => 0,
			'mobile'  => 0,
			'tablet'  => 0,
			'unknown' => 0,
		);
		$top_pages_build = array();

		foreach ( $tracked_ids as $post_id ) {
			$events      = $this->summarize_post_events( $post_id, $range );
			$visit_count = (int) $events['visits'];
			$click_count = (int) $events['clicks'];

			$total_visits += $visit_count;
			$total_clicks += $click_count;

			foreach ( $events['visit_entries'] as $visit ) {
				$day = self::mysql_day( $visit['t'] );
				if ( '' === $day ) {
					continue;
				}
				if ( 'all' === $range['preset'] ) {
					if ( ! isset( $date_counts[ $day ] ) ) {
						$date_counts[ $day ] = 0;
					}
					$date_counts[ $day ]++;
				} elseif ( isset( $date_counts[ $day ] ) ) {
					$date_counts[ $day ]++;
				}
			}

			foreach ( $events['devices'] as $device => $count ) {
				if ( isset( $device_totals[ $device ] ) ) {
					$device_totals[ $device ] += (int) $count;
				}
			}

			$location_key = self::get_location_bucket_key_for_post( $post_id );
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

			$location_label = $locations[ $location_key ]['label'];
			$ctr            = $visit_count > 0 ? round( ( $click_count / $visit_count ) * 100, 1 ) : 0;

			$top_pages_build[] = array(
				'post_id'  => (int) $post_id,
				'title'    => self::get_analytics_display_title( $post_id ),
				'location' => $location_label,
				'count'    => $visit_count,
				'clicks'   => $click_count,
				'ctr'      => $ctr,
			);
		}

		foreach ( array_keys( $locations ) as $lid ) {
			$disp                        = self::resolve_location_display( $lid );
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

		$date_counts = $this->finalize_date_series( $date_counts, $range );
		$not_found   = $this->summarize_404_log( $range, $date_counts );

		$devices = array();
		foreach ( $device_totals as $key => $count ) {
			if ( $count <= 0 ) {
				continue;
			}
			$devices[] = array(
				'key'   => $key,
				'label' => self::device_label( $key ),
				'count' => $count,
			);
		}

		return array(
			'visits_over_time' => $date_counts,
			'locations_all'    => $locations_all,
			'top_pages_all'    => $top_pages_build,
			'devices'          => $devices,
			'not_found'        => $not_found['total'],
			'not_found_over_time' => $not_found['over_time'],
			'not_found_paths'  => $not_found['paths'],
			'range'            => array(
				'preset' => $range['preset'],
				'label'  => $range['label'],
				'start'  => isset( $range['start_day'] ) ? $range['start_day'] : '',
				'end'    => isset( $range['end_day'] ) ? $range['end_day'] : '',
			),
			'summary'          => array(
				'total_pages'     => count( $tracked_ids ),
				'total_locations' => $total_locations,
				'total_visits'    => $total_visits,
				'total_clicks'    => $total_clicks,
				'overall_ctr'     => $overall_ctr,
				'not_found'       => $not_found['total'],
				'range_label'     => $range['label'],
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

			if ( '_unassigned' !== self::get_location_bucket_key_for_post( $post_id ) ) {
				continue;
			}

			/**
			 * Skip clearing analytics for a post (return true to keep its stats).
			 *
			 * @param bool $skip    Default false.
			 * @param int  $post_id Post ID.
			 * @since 1.2.4 Filter: `magic_page_essentials_skip_clear_unassigned_analytics` (formerly `mpe_skip_clear_unassigned_analytics`).
			 */
			if ( apply_filters( 'magic_page_essentials_skip_clear_unassigned_analytics', false, $post_id ) ) {
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

		wp_send_json_success( $this->analytics_for_source( $_POST ) );
	}

	/**
	 * @return void
	 */
	public function enqueue_frontend_analytics_script() {
		$is_404  = is_404();
		$post_id = 0;
		if ( ! $is_404 ) {
			if ( ! is_singular() ) {
				return;
			}
			$post_id = (int) get_queried_object_id();
			if ( ! $post_id || ! self::is_post_tracked_for_analytics( $post_id ) ) {
				return;
			}
		}

		$url = MAGIC_PAGE_ESSENTIALS_URL . 'assets/js/magicpage-frontend-analytics.js';
		wp_enqueue_script(
			'magicpage-frontend-analytics',
			$url,
			array( 'jquery' ),
			defined( 'MAGIC_PAGE_ESSENTIALS_VERSION' ) ? MAGIC_PAGE_ESSENTIALS_VERSION : '1.0',
			true
		);

		$config = array(
			'ajax_url' => admin_url( 'admin-ajax.php' ),
			'is_404'   => $is_404 ? 1 : 0,
		);
		if ( $is_404 ) {
			$config['nonce_404'] = wp_create_nonce( 'magicpage_404_nonce' );
		} else {
			$config['post_id']     = $post_id;
			$config['nonce']       = wp_create_nonce( 'magicpage_visit_nonce' );
			$config['click_nonce'] = wp_create_nonce( 'magicpage_click_nonce' );
		}

		wp_localize_script(
			'magicpage-frontend-analytics',
			'MagicPageAnalyticsFrontend',
			$config
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

		$device = self::sanitize_device( isset( $_POST['device'] ) ? wp_unslash( $_POST['device'] ) : '' );

		$visits = get_post_meta( $post_id, 'magicpage_visits', true );
		if ( ! is_array( $visits ) ) {
			$visits = array();
		}
		$visits[] = array(
			't' => current_time( 'mysql' ),
			'd' => $device,
		);
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
		delete_transient( 'mpe_analytics_cache_token' );
	}

	/**
	 * Token embedded in analytics transients so one delete invalidates every date range.
	 *
	 * @return string
	 */
	private function analytics_cache_token() {
		$token = get_transient( 'mpe_analytics_cache_token' );
		if ( ! is_string( $token ) || '' === $token ) {
			$token = wp_generate_password( 12, false );
			set_transient( 'mpe_analytics_cache_token', $token, DAY_IN_SECONDS );
		}
		return $token;
	}

	/**
	 * Cached analytics payload for the request's date range.
	 *
	 * @param array<string,mixed> $source Request array (POST or GET).
	 * @return array<string,mixed>
	 */
	private function analytics_for_source( $source ) {
		if ( ! is_array( $source ) ) {
			$source = array();
		}
		$range       = $this->parse_analytics_range( $source );
		$tracked_ids = $this->get_tracked_post_ids();
		sort( $tracked_ids, SORT_NUMERIC );
		$cache_key = 'mpe_an4_' . $this->analytics_cache_token() . '_' . md5( implode( ',', $tracked_ids ) . '|' . $range['key'] );

		$cached = get_transient( $cache_key );
		if ( is_array( $cached ) && isset( $cached['summary'], $cached['locations_all'], $cached['top_pages_all'], $cached['visits_over_time'] ) ) {
			return $cached;
		}

		if ( ! empty( $tracked_ids ) ) {
			if ( function_exists( '_prime_post_caches' ) ) {
				_prime_post_caches( $tracked_ids, true, true );
			}
			update_meta_cache( 'post', $tracked_ids );
		}

		$payload = $this->build_analytics_payload( $tracked_ids, $range );
		set_transient( $cache_key, $payload, 90 );

		return $payload;
	}

	/**
	 * @param array<string,mixed> $source Request array.
	 * @return array<string,mixed>
	 */
	private function parse_analytics_range( $source ) {
		$preset = '30';
		if ( isset( $source['range'] ) && is_string( $source['range'] ) ) {
			$preset = sanitize_key( wp_unslash( $source['range'] ) );
		}
		$today  = current_time( 'Y-m-d' );

		if ( 'all' === $preset ) {
			return array(
				'preset' => 'all',
				'start'  => null,
				'end'    => null,
				'key'    => 'all',
				'label'  => __( 'All time', 'magic-page-essentials' ),
			);
		}

		if ( 'custom' === $preset ) {
			$start_day = $this->request_day( $source, 'start' );
			$end_day   = $this->request_day( $source, 'end' );
			if ( '' !== $start_day && '' !== $end_day ) {
				$start_ts = strtotime( $start_day . ' 00:00:00' );
				$end_ts   = strtotime( $end_day . ' 23:59:59' );
				if ( $start_ts && $end_ts && $end_ts >= $start_ts ) {
					if ( ( $end_ts - $start_ts ) > 366 * DAY_IN_SECONDS ) {
						$start_day = gmdate( 'Y-m-d', $end_ts - ( 365 * DAY_IN_SECONDS ) );
						$start_ts  = strtotime( $start_day . ' 00:00:00' );
					}
					$end_day = gmdate( 'Y-m-d', $end_ts );
					return array(
						'preset'    => 'custom',
						'start'     => $start_ts,
						'end'       => $end_ts,
						'start_day' => $start_day,
						'end_day'   => $end_day,
						'key'       => $start_day . '_' . $end_day,
						'label'     => $start_day . ' – ' . $end_day,
					);
				}
			}
			$preset = '30';
		}

		$allowed = array(
			'7'   => 7,
			'30'  => 30,
			'90'  => 90,
			'365' => 365,
		);
		$days = isset( $allowed[ $preset ] ) ? $allowed[ $preset ] : 30;
		$end_ts   = strtotime( $today . ' 23:59:59' );
		$start_day = gmdate( 'Y-m-d', strtotime( $today . ' 00:00:00 -' . ( $days - 1 ) . ' days' ) );
		$start_ts  = strtotime( $start_day . ' 00:00:00' );
		$labels    = array(
			'7'   => __( 'Last 7 days', 'magic-page-essentials' ),
			'30'  => __( 'Last 30 days', 'magic-page-essentials' ),
			'90'  => __( 'Last 90 days', 'magic-page-essentials' ),
			'365' => __( 'Last 12 months', 'magic-page-essentials' ),
		);

		return array(
			'preset'    => (string) $days,
			'start'     => $start_ts,
			'end'       => $end_ts,
			'start_day' => $start_day,
			'end_day'   => $today,
			'days'      => $days,
			'key'       => 'd' . $days,
			'label'     => isset( $labels[ (string) $days ] ) ? $labels[ (string) $days ] : __( 'Last 30 days', 'magic-page-essentials' ),
		);
	}

	/**
	 * @param array<string,mixed> $source Request array.
	 * @param string               $key    Field name.
	 * @return string Y-m-d or empty.
	 */
	private function request_day( $source, $key ) {
		if ( ! isset( $source[ $key ] ) || ! is_string( $source[ $key ] ) ) {
			return '';
		}
		$day = sanitize_text_field( wp_unslash( $source[ $key ] ) );
		return preg_match( '/^\d{4}-\d{2}-\d{2}$/', $day ) ? $day : '';
	}

	/**
	 * Zero-filled day buckets for a bounded range. All-time starts empty and fills from events.
	 *
	 * @param array<string,mixed> $range Parsed range.
	 * @return array<string,int>
	 */
	private function empty_date_series( array $range ) {
		if ( 'all' === $range['preset'] || empty( $range['start_day'] ) || empty( $range['end_day'] ) ) {
			return array();
		}
		$series = array();
		$cursor = strtotime( $range['start_day'] . ' 00:00:00' );
		$end    = strtotime( $range['end_day'] . ' 00:00:00' );
		$guard  = 0;
		while ( $cursor && $end && $cursor <= $end && $guard < 400 ) {
			$series[ gmdate( 'Y-m-d', $cursor ) ] = 0;
			$cursor = strtotime( '+1 day', $cursor );
			++$guard;
		}
		return $series;
	}

	/**
	 * Sort a day series. All-time spans longer than 120 days roll up to months.
	 *
	 * @param array<string,int>   $counts Day => count.
	 * @param array<string,mixed> $range  Parsed range.
	 * @return array<string,int>
	 */
	private function finalize_date_series( array $counts, array $range ) {
		if ( empty( $counts ) ) {
			return $counts;
		}
		ksort( $counts );
		if ( 'all' !== $range['preset'] ) {
			return $counts;
		}
		$keys  = array_keys( $counts );
		$first = strtotime( (string) $keys[0] . ' 00:00:00' );
		$last  = strtotime( (string) $keys[ count( $keys ) - 1 ] . ' 00:00:00' );
		if ( ! $first || ! $last || ( $last - $first ) <= 120 * DAY_IN_SECONDS ) {
			return $counts;
		}
		$monthly = array();
		foreach ( $counts as $day => $count ) {
			$month = substr( (string) $day, 0, 7 );
			if ( ! isset( $monthly[ $month ] ) ) {
				$monthly[ $month ] = 0;
			}
			$monthly[ $month ] += (int) $count;
		}
		ksort( $monthly );
		return $monthly;
	}

	/**
	 * Visits and clicks for one post inside a date range.
	 *
	 * Older visits are plain datetime strings and count as an unknown device.
	 *
	 * @param int                 $post_id Post ID.
	 * @param array<string,mixed> $range   Parsed range.
	 * @return array{visits:int,clicks:int,visit_entries:array<int,array{t:string,d:string}>,click_entries:array<int,array{t:string,u:string,l:string}>,devices:array<string,int>}
	 */
	private function summarize_post_events( $post_id, array $range ) {
		$post_id       = (int) $post_id;
		$visits_raw    = get_post_meta( $post_id, 'magicpage_visits', true );
		$visit_entries = array();
		if ( is_array( $visits_raw ) ) {
			foreach ( $visits_raw as $entry ) {
				$normalized = self::normalize_visit( $entry );
				if ( null === $normalized || ! self::mysql_in_range( $normalized['t'], $range ) ) {
					continue;
				}
				$visit_entries[] = $normalized;
			}
		}

		$visit_count = count( $visit_entries );
		if ( 'all' === $range['preset'] && 0 === $visit_count && ! is_array( $visits_raw ) ) {
			$visit_count = (int) get_post_meta( $post_id, 'magicpage_visit_count', true );
		}

		$clicks_raw    = get_post_meta( $post_id, 'magicpage_clicks', true );
		$click_entries = array();
		if ( is_array( $clicks_raw ) ) {
			foreach ( $clicks_raw as $click ) {
				if ( ! is_array( $click ) || empty( $click['t'] ) || ! is_string( $click['t'] ) ) {
					continue;
				}
				if ( ! self::mysql_in_range( $click['t'], $range ) ) {
					continue;
				}
				$click_entries[] = array(
					't' => $click['t'],
					'u' => isset( $click['u'] ) && is_string( $click['u'] ) ? $click['u'] : '',
					'l' => isset( $click['l'] ) && is_string( $click['l'] ) ? $click['l'] : '',
				);
			}
		}

		$click_count = count( $click_entries );
		if ( 'all' === $range['preset'] && 0 === $click_count && ! is_array( $clicks_raw ) ) {
			$click_count = (int) get_post_meta( $post_id, 'magicpage_click_count', true );
		}

		$devices = array(
			'desktop' => 0,
			'mobile'  => 0,
			'tablet'  => 0,
			'unknown' => 0,
		);
		foreach ( $visit_entries as $visit ) {
			$devices[ $visit['d'] ]++;
		}

		return array(
			'visits'        => $visit_count,
			'clicks'        => $click_count,
			'visit_entries' => $visit_entries,
			'click_entries' => $click_entries,
			'devices'       => $devices,
		);
	}

	/**
	 * @param mixed $entry Stored visit (datetime string or array).
	 * @return array{t:string,d:string}|null
	 */
	private static function normalize_visit( $entry ) {
		if ( is_string( $entry ) && '' !== $entry ) {
			return array(
				't' => $entry,
				'd' => 'unknown',
			);
		}
		if ( is_array( $entry ) && isset( $entry['t'] ) && is_string( $entry['t'] ) && '' !== $entry['t'] ) {
			return array(
				't' => $entry['t'],
				'd' => self::sanitize_device( isset( $entry['d'] ) ? $entry['d'] : '' ),
			);
		}
		return null;
	}

	/**
	 * @param mixed $device Raw device slug.
	 * @return string desktop|mobile|tablet|unknown
	 */
	private static function sanitize_device( $device ) {
		$device  = is_string( $device ) ? sanitize_key( $device ) : '';
		$allowed = array( 'desktop', 'mobile', 'tablet' );
		return in_array( $device, $allowed, true ) ? $device : 'unknown';
	}

	/**
	 * @param string $device Device slug.
	 * @return string
	 */
	private static function device_label( $device ) {
		switch ( $device ) {
			case 'desktop':
				return __( 'Desktop', 'magic-page-essentials' );
			case 'mobile':
				return __( 'Mobile', 'magic-page-essentials' );
			case 'tablet':
				return __( 'Tablet', 'magic-page-essentials' );
			default:
				return __( 'Unknown', 'magic-page-essentials' );
		}
	}

	/**
	 * @param string              $mysql Datetime string.
	 * @param array<string,mixed> $range Parsed range.
	 * @return bool
	 */
	private static function mysql_in_range( $mysql, array $range ) {
		if ( ! is_string( $mysql ) || '' === $mysql ) {
			return false;
		}
		if ( null === $range['start'] ) {
			return true;
		}
		$ts = strtotime( $mysql );
		if ( ! $ts ) {
			return false;
		}
		return $ts >= (int) $range['start'] && $ts <= (int) $range['end'];
	}

	/**
	 * @param string $mysql Datetime string.
	 * @return string Y-m-d or empty.
	 */
	private static function mysql_day( $mysql ) {
		if ( ! is_string( $mysql ) || strlen( $mysql ) < 10 ) {
			return '';
		}
		$day = substr( $mysql, 0, 10 );
		return preg_match( '/^\d{4}-\d{2}-\d{2}$/', $day ) ? $day : '';
	}

	/**
	 * @param string $mysql Datetime string.
	 * @return string
	 */
	private static function format_mysql_datetime( $mysql ) {
		if ( ! is_string( $mysql ) || '' === $mysql ) {
			return '';
		}
		return mysql2date( get_option( 'date_format' ) . ' ' . get_option( 'time_format' ), $mysql );
	}

	/**
	 * 404 totals, daily series, and top paths for a range.
	 *
	 * When the visit series was rolled up to months, 404 days use the same buckets.
	 *
	 * @param array<string,mixed> $range           Parsed range.
	 * @param array<string,int>   $visit_series    Final visit series, used to detect month buckets.
	 * @return array{total:int,over_time:array<string,int>,paths:array<int,array{path:string,count:int,last:string}>}
	 */
	private function summarize_404_log( array $range, array $visit_series ) {
		$month_buckets = false;
		if ( ! empty( $visit_series ) ) {
			$sample = (string) array_key_first( $visit_series );
			if ( 7 === strlen( $sample ) ) {
				$month_buckets = true;
			}
		}

		if ( 'all' === $range['preset'] || $month_buckets ) {
			$over_time = array();
		} else {
			$over_time = $this->empty_date_series( $range );
		}

		$log   = get_option( 'magicpage_404_log', array() );
		$paths = array();
		$total = 0;
		if ( ! is_array( $log ) ) {
			$log = array();
		}

		foreach ( $log as $entry ) {
			if ( ! is_array( $entry ) || empty( $entry['t'] ) || ! is_string( $entry['t'] ) ) {
				continue;
			}
			if ( ! self::mysql_in_range( $entry['t'], $range ) ) {
				continue;
			}
			++$total;
			$path = isset( $entry['p'] ) && is_string( $entry['p'] ) ? $entry['p'] : '/';
			if ( ! isset( $paths[ $path ] ) ) {
				$paths[ $path ] = array(
					'path'  => $path,
					'count' => 0,
					'last'  => $entry['t'],
				);
			}
			$paths[ $path ]['count']++;
			if ( strcmp( $entry['t'], $paths[ $path ]['last'] ) > 0 ) {
				$paths[ $path ]['last'] = $entry['t'];
			}

			$day = self::mysql_day( $entry['t'] );
			if ( '' === $day ) {
				continue;
			}
			$bucket = $month_buckets ? substr( $day, 0, 7 ) : $day;
			if ( 'all' === $range['preset'] || $month_buckets ) {
				if ( ! isset( $over_time[ $bucket ] ) ) {
					$over_time[ $bucket ] = 0;
				}
				$over_time[ $bucket ]++;
			} elseif ( isset( $over_time[ $bucket ] ) ) {
				$over_time[ $bucket ]++;
			}
		}

		ksort( $over_time );
		$path_rows = array_values( $paths );
		usort(
			$path_rows,
			function ( $a, $b ) {
				return $b['count'] - $a['count'];
			}
		);
		$path_rows = array_slice( $path_rows, 0, 25 );
		foreach ( $path_rows as $index => $row ) {
			$path_rows[ $index ]['last_display'] = self::format_mysql_datetime( $row['last'] );
		}

		return array(
			'total'     => $total,
			'over_time' => $over_time,
			'paths'     => $path_rows,
		);
	}

	/**
	 * @param string $path Request path.
	 * @return bool
	 */
	private static function is_ignored_404_path( $path ) {
		$path     = strtolower( $path );
		$prefixes = array( '/wp-admin/', '/wp-content/', '/wp-includes/', '/wp-json/' );
		foreach ( $prefixes as $prefix ) {
			if ( 0 === strpos( $path, $prefix ) ) {
				return true;
			}
		}
		if ( in_array( $path, array( '/wp-admin', '/wp-content', '/wp-includes', '/wp-json', '/xmlrpc.php' ), true ) ) {
			return true;
		}
		if ( 0 === strpos( $path, '/xmlrpc.php/' ) ) {
			return true;
		}
		return (bool) preg_match( '/\.(?:ico|png|jpe?g|gif|webp|svg|css|js|map|woff2?|ttf|eot)$/', $path );
	}

	/**
	 * Record a front-end 404 (path and device only; no IP is stored).
	 *
	 * @return void
	 */
	public function record_magicpage_404() {
		check_ajax_referer( 'magicpage_404_nonce', 'nonce' );

		$url  = isset( $_POST['url'] ) ? esc_url_raw( wp_unslash( $_POST['url'] ) ) : '';
		$host = wp_parse_url( $url, PHP_URL_HOST );
		$path = wp_parse_url( $url, PHP_URL_PATH );
		if ( ! is_string( $host ) || '' === $host || ! is_string( $path ) || '' === $path ) {
			wp_send_json_error( 'Invalid URL.' );
			return;
		}

		$allowed_hosts = array();
		foreach ( array( home_url(), site_url() ) as $candidate ) {
			$candidate_host = wp_parse_url( $candidate, PHP_URL_HOST );
			if ( is_string( $candidate_host ) && '' !== $candidate_host ) {
				$allowed_hosts[] = strtolower( $candidate_host );
			}
		}
		if ( ! in_array( strtolower( $host ), $allowed_hosts, true ) ) {
			wp_send_json_error( 'Invalid URL.' );
			return;
		}

		$path = '/' . ltrim( sanitize_text_field( $path ), '/' );
		$path = mb_substr( $path, 0, 255 );
		if ( self::is_ignored_404_path( $path ) ) {
			wp_send_json_success( array( 'skipped' => true ) );
			return;
		}

		$device = self::sanitize_device( isset( $_POST['device'] ) ? wp_unslash( $_POST['device'] ) : '' );

		/**
		 * Whether to store this 404. Return false to drop it.
		 *
		 * @param bool   $record Default true.
		 * @param string $path   Request path.
		 * @param string $device Device slug.
		 */
		if ( ! apply_filters( 'magic_page_essentials_record_404', true, $path, $device ) ) {
			wp_send_json_success( array( 'skipped' => true ) );
			return;
		}

		$ip         = isset( $_SERVER['REMOTE_ADDR'] ) ? sanitize_text_field( wp_unslash( $_SERVER['REMOTE_ADDR'] ) ) : '';
		$dedupe_key = 'mpe_404_' . md5( $ip . '|' . $path );
		if ( get_transient( $dedupe_key ) ) {
			wp_send_json_success( array( 'deduped' => true ) );
			return;
		}
		set_transient( $dedupe_key, 1, HOUR_IN_SECONDS );

		$stored = get_option( 'magicpage_404_log', null );
		$log    = is_array( $stored ) ? $stored : array();
		$log[]  = array(
			't' => current_time( 'mysql' ),
			'p' => $path,
			'd' => $device,
		);
		if ( count( $log ) > 500 ) {
			$log = array_slice( $log, -500 );
		}

		if ( null === $stored ) {
			add_option( 'magicpage_404_log', $log, '', false );
		} else {
			update_option( 'magicpage_404_log', $log, false );
		}

		$this->bust_analytics_cache();
		wp_send_json_success();
	}

	/**
	 * Analytics row action on Magic Pages and the magicpage list.
	 *
	 * @param array<string,string> $actions Row actions.
	 * @param WP_Post              $post    Post.
	 * @return array<string,string>
	 */
	public function add_analytics_row_action( $actions, $post ) {
		if ( ! $post instanceof WP_Post || ! in_array( $post->post_type, array( 'page', $this->post_type ), true ) ) {
			return $actions;
		}
		if ( ! current_user_can( 'edit_post', $post->ID ) ) {
			return $actions;
		}
		$show = ( $this->post_type === $post->post_type ) || self::post_qualifies_for_page_analytics( $post->ID );
		if ( ! $show ) {
			return $actions;
		}

		$actions['mpe_analytics'] = sprintf(
			'<a href="#mpe-page-analytics" class="mpe-open-page-analytics" data-post-id="%d">%s</a>',
			(int) $post->ID,
			esc_html__( 'Analytics', 'magic-page-essentials' )
		);

		return $actions;
	}

	/**
	 * @param int $post_id Post ID.
	 * @return bool
	 */
	private static function post_qualifies_for_page_analytics( $post_id ) {
		if ( '_unassigned' !== self::get_location_bucket_key_for_post( $post_id ) ) {
			return true;
		}
		return self::is_post_tracked_for_analytics( $post_id );
	}

	/**
	 * Modal markup. The script is enqueued only on the list screens.
	 *
	 * @return void
	 */
	public function render_page_analytics_modal() {
		$screen = function_exists( 'get_current_screen' ) ? get_current_screen() : null;
		if ( ! $screen || 'edit' !== $screen->base || ! in_array( $screen->post_type, array( 'page', $this->post_type ), true ) ) {
			return;
		}
		?>
		<div id="mpe-page-analytics-modal" class="mpe-modal" hidden>
			<div class="mpe-modal-backdrop" data-mpe-close="1"></div>
			<div class="mpe-modal-dialog" role="dialog" aria-modal="true" aria-labelledby="mpe-page-analytics-title">
				<button type="button" class="mpe-modal-close" data-mpe-close="1" aria-label="<?php esc_attr_e( 'Close', 'magic-page-essentials' ); ?>">&times;</button>
				<h2 id="mpe-page-analytics-title"><?php esc_html_e( 'Page analytics', 'magic-page-essentials' ); ?></h2>
				<p class="mpe-modal-meta" id="mpe-page-analytics-meta"></p>
				<div class="mpe-modal-toolbar">
					<label for="mpe-page-range"><?php esc_html_e( 'Date range', 'magic-page-essentials' ); ?></label>
					<select id="mpe-page-range">
						<option value="7"><?php esc_html_e( 'Last 7 days', 'magic-page-essentials' ); ?></option>
						<option value="30" selected><?php esc_html_e( 'Last 30 days', 'magic-page-essentials' ); ?></option>
						<option value="90"><?php esc_html_e( 'Last 90 days', 'magic-page-essentials' ); ?></option>
						<option value="365"><?php esc_html_e( 'Last 12 months', 'magic-page-essentials' ); ?></option>
						<option value="all"><?php esc_html_e( 'All time', 'magic-page-essentials' ); ?></option>
					</select>
				</div>
				<p class="mpe-modal-note" id="mpe-page-analytics-note" hidden></p>
				<div class="mpe-modal-stats" id="mpe-page-analytics-stats"></div>
				<h3 class="mpe-modal-heading"><?php esc_html_e( 'Recent clicks', 'magic-page-essentials' ); ?></h3>
				<ul class="mpe-modal-clicks" id="mpe-page-analytics-clicks"></ul>
			</div>
		</div>
		<?php
	}

	/**
	 * AJAX: one page's visits, clicks, devices, and recent clicks.
	 *
	 * @return void
	 */
	public function ajax_fetch_page_analytics() {
		check_ajax_referer( 'magicpage_page_analytics', 'nonce' );

		$post_id = isset( $_POST['post_id'] ) ? (int) $_POST['post_id'] : 0;
		if ( $post_id <= 0 || ! current_user_can( 'edit_post', $post_id ) ) {
			wp_send_json_error( array( 'message' => __( 'You cannot view analytics for this page.', 'magic-page-essentials' ) ), 403 );
			return;
		}
		if ( ! self::post_qualifies_for_page_analytics( $post_id ) && $this->post_type !== get_post_type( $post_id ) ) {
			wp_send_json_error( array( 'message' => __( 'This page has no Magic Page analytics.', 'magic-page-essentials' ) ), 400 );
			return;
		}

		$range    = $this->parse_analytics_range( $_POST );
		$events   = $this->summarize_post_events( $post_id, $range );
		$visits   = (int) $events['visits'];
		$clicks   = (int) $events['clicks'];
		$ctr      = $visits > 0 ? round( ( $clicks / $visits ) * 100, 1 ) : 0;
		$location = self::resolve_location_display( self::get_location_bucket_key_for_post( $post_id ) );

		$devices = array();
		foreach ( $events['devices'] as $key => $count ) {
			if ( $count <= 0 ) {
				continue;
			}
			$devices[] = array(
				'key'   => $key,
				'label' => self::device_label( $key ),
				'count' => (int) $count,
			);
		}

		$recent = array_slice( $events['click_entries'], -15 );
		$recent = array_reverse( $recent );
		$recent_clicks = array();
		foreach ( $recent as $click ) {
			$href = $click['u'];
			if ( ! preg_match( '#^https?://#i', $href ) ) {
				$href = '';
			}
			$recent_clicks[] = array(
				'display' => self::format_mysql_datetime( $click['t'] ),
				'text'    => $click['l'],
				'href'    => esc_url_raw( $href ),
			);
		}

		wp_send_json_success(
			array(
				'post_id'  => $post_id,
				'title'    => self::get_analytics_display_title( $post_id ),
				'url'      => get_permalink( $post_id ),
				'location' => $location['label'],
				'region'   => $location['region'],
				'tracked'  => self::is_post_tracked_for_analytics( $post_id ),
				'range'    => $range['label'],
				'visits'   => $visits,
				'clicks'   => $clicks,
				'ctr'      => $ctr,
				'devices'  => $devices,
				'clicks_recent' => $recent_clicks,
			)
		);
	}

	/**
	 * Download the current analytics payload as CSV or JSON.
	 *
	 * @return void
	 */
	public function handle_analytics_export() {
		if ( ! current_user_can( 'manage_options' ) ) {
			wp_die( esc_html__( 'You do not have permission to export analytics.', 'magic-page-essentials' ), '', array( 'response' => 403 ) );
		}
		check_admin_referer( 'magicpage_analytics_export' );

		$format  = isset( $_GET['format'] ) ? sanitize_key( wp_unslash( $_GET['format'] ) ) : 'json';
		$payload = $this->analytics_for_source( $_GET );
		if ( 'csv' === $format ) {
			$this->send_csv_export( $payload );
		}
		$this->send_json_export( $payload );
	}

	/**
	 * @param array<string,mixed> $payload Analytics payload.
	 * @return void
	 */
	private function send_json_export( array $payload ) {
		$payload['generated_at'] = current_time( 'mysql' );
		nocache_headers();
		header( 'Content-Type: application/json; charset=utf-8' );
		header( 'Content-Disposition: attachment; filename="magic-page-analytics-' . gmdate( 'Y-m-d' ) . '.json"' );
		echo wp_json_encode( $payload );
		exit;
	}

	/**
	 * @param array<string,mixed> $payload Analytics payload.
	 * @return void
	 */
	private function send_csv_export( array $payload ) {
		nocache_headers();
		header( 'Content-Type: text/csv; charset=utf-8' );
		header( 'Content-Disposition: attachment; filename="magic-page-analytics-' . gmdate( 'Y-m-d' ) . '.csv"' );

		$out = fopen( 'php://output', 'w' );
		if ( false === $out ) {
			exit;
		}
		fwrite( $out, "\xEF\xBB\xBF" );
		$this->put_csv_row( $out, array( 'section', 'name', 'region', 'pages', 'visits', 'clicks', 'ctr', 'date', 'device', 'path', 'count' ) );

		$summary = isset( $payload['summary'] ) && is_array( $payload['summary'] ) ? $payload['summary'] : array();
		$this->put_csv_row(
			$out,
			array(
				'summary',
				isset( $summary['range_label'] ) ? $summary['range_label'] : '',
				'',
				isset( $summary['total_pages'] ) ? $summary['total_pages'] : 0,
				isset( $summary['total_visits'] ) ? $summary['total_visits'] : 0,
				isset( $summary['total_clicks'] ) ? $summary['total_clicks'] : 0,
				isset( $summary['overall_ctr'] ) ? $summary['overall_ctr'] : 0,
				'',
				'',
				'',
				isset( $summary['not_found'] ) ? $summary['not_found'] : 0,
			)
		);

		$pages = isset( $payload['top_pages_all'] ) && is_array( $payload['top_pages_all'] ) ? $payload['top_pages_all'] : array();
		foreach ( $pages as $page ) {
			if ( ! is_array( $page ) ) {
				continue;
			}
			$this->put_csv_row(
				$out,
				array(
					'page',
					isset( $page['title'] ) ? $page['title'] : '',
					isset( $page['location'] ) ? $page['location'] : '',
					1,
					isset( $page['count'] ) ? $page['count'] : 0,
					isset( $page['clicks'] ) ? $page['clicks'] : 0,
					isset( $page['ctr'] ) ? $page['ctr'] : 0,
					'',
					'',
					'',
					'',
				)
			);
		}

		$locations = isset( $payload['locations_all'] ) && is_array( $payload['locations_all'] ) ? $payload['locations_all'] : array();
		foreach ( $locations as $location ) {
			if ( ! is_array( $location ) ) {
				continue;
			}
			$this->put_csv_row(
				$out,
				array(
					'location',
					isset( $location['label'] ) ? $location['label'] : '',
					isset( $location['region'] ) ? $location['region'] : '',
					isset( $location['pages'] ) ? $location['pages'] : 0,
					isset( $location['visits'] ) ? $location['visits'] : 0,
					isset( $location['clicks'] ) ? $location['clicks'] : 0,
					isset( $location['ctr'] ) ? $location['ctr'] : 0,
					'',
					'',
					'',
					'',
				)
			);
		}

		$this->csv_series_rows( $out, 'visit_day', isset( $payload['visits_over_time'] ) ? $payload['visits_over_time'] : array() );
		$this->csv_series_rows( $out, 'not_found_day', isset( $payload['not_found_over_time'] ) ? $payload['not_found_over_time'] : array() );

		$devices = isset( $payload['devices'] ) && is_array( $payload['devices'] ) ? $payload['devices'] : array();
		foreach ( $devices as $device ) {
			if ( ! is_array( $device ) ) {
				continue;
			}
			$this->put_csv_row(
				$out,
				array(
					'device',
					isset( $device['label'] ) ? $device['label'] : '',
					'',
					'',
					'',
					'',
					'',
					'',
					isset( $device['key'] ) ? $device['key'] : '',
					'',
					isset( $device['count'] ) ? $device['count'] : 0,
				)
			);
		}

		$paths = isset( $payload['not_found_paths'] ) && is_array( $payload['not_found_paths'] ) ? $payload['not_found_paths'] : array();
		foreach ( $paths as $path_row ) {
			if ( ! is_array( $path_row ) ) {
				continue;
			}
			$this->put_csv_row(
				$out,
				array(
					'not_found',
					'',
					'',
					'',
					'',
					'',
					'',
					isset( $path_row['last'] ) ? $path_row['last'] : '',
					'',
					isset( $path_row['path'] ) ? $path_row['path'] : '',
					isset( $path_row['count'] ) ? $path_row['count'] : 0,
				)
			);
		}

		fclose( $out );
		exit;
	}

	/**
	 * Prefix spreadsheet formulas so exported titles cannot execute in Excel.
	 *
	 * @param resource         $out CSV handle.
	 * @param array<int,mixed> $row Cells.
	 * @return void
	 */
	private function put_csv_row( $out, array $row ) {
		$safe = array();
		foreach ( $row as $value ) {
			if ( is_string( $value ) && preg_match( '/^[=+\-@\t\r]/', $value ) ) {
				$value = "'" . $value;
			}
			$safe[] = $value;
		}
		fputcsv( $out, $safe );
	}

	/**
	 * @param resource              $out     CSV handle.
	 * @param string                $section Section name.
	 * @param mixed                 $series  Date => count.
	 * @return void
	 */
	private function csv_series_rows( $out, $section, $series ) {
		if ( ! is_array( $series ) ) {
			return;
		}
		foreach ( $series as $date => $count ) {
			$this->put_csv_row(
				$out,
				array(
					$section,
					'',
					'',
					'',
					'',
					'',
					'',
					(string) $date,
					'',
					'',
					(int) $count,
				)
			);
		}
	}
}
