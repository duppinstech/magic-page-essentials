<?php
/**
 * Essentials admin settings (Magic Page → Essentials).
 *
 * @package Magic_Page_Essentials
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class Magic_Page_Essentials_Settings {

	const OPTION_NAME = 'magic_page_essentials_settings';

	/**
	 * @var array|null
	 */
	private static $settings = null;

	public static function init() {
		add_action( 'admin_menu', [ __CLASS__, 'register_menu' ], 20 );
		add_action( 'admin_init', [ __CLASS__, 'register_settings' ] );
	}

	public static function register_menu() {
		add_submenu_page(
			'edit.php?post_type=magicpage',
			__( 'Magic Page Essentials', 'magic-page-essentials' ),
			__( 'Essentials', 'magic-page-essentials' ),
			'manage_options',
			'magic-page-essentials',
			[ __CLASS__, 'render_page' ]
		);
	}

	public static function register_settings() {
		register_setting(
			'mpe_essentials_group',
			self::OPTION_NAME,
			[
				'type'              => 'array',
				'sanitize_callback' => [ __CLASS__, 'sanitize' ],
				'default'           => self::get_defaults(),
			]
		);
	}

	/**
	 * @return array
	 */
	public static function get_defaults() {
		return [
			'yoast_bridge'                   => self::yoast_is_installed(),
			'analytics_dashboard'            => true,
			'performance_scope'              => true,
			'analytics_include_static_pages' => true,
		];
	}

	/**
	 * @return array
	 */
	public static function get_settings() {
		if ( is_array( self::$settings ) ) {
			return self::$settings;
		}
		$stored = get_option( self::OPTION_NAME, [] );
		if ( ! is_array( $stored ) ) {
			$stored = [];
		}
		self::$settings = array_merge( self::get_defaults(), $stored );
		return self::$settings;
	}

	/**
	 * @param string $key Feature key.
	 * @return bool
	 */
	public static function is_feature_enabled( $key ) {
		$settings = self::get_settings();
		return ! empty( $settings[ $key ] );
	}

	/**
	 * @param array|null $input Raw POST.
	 * @return array
	 */
	public static function sanitize( $input ) {
		$defaults = self::get_defaults();
		$out      = $defaults;

		if ( ! is_array( $input ) ) {
			return $out;
		}

		$out['yoast_bridge'] = ! empty( $input['yoast_bridge'] );

		// Only allow enabling Yoast bridge if Yoast is present.
		if ( $out['yoast_bridge'] && ! self::yoast_is_installed() ) {
			$out['yoast_bridge'] = false;
		}

		$out['analytics_dashboard'] = ! empty( $input['analytics_dashboard'] );

		$out['performance_scope'] = ! empty( $input['performance_scope'] );

		$out['analytics_include_static_pages'] = ! empty( $input['analytics_include_static_pages'] );

		self::$settings = $out;
		return $out;
	}

	/**
	 * @return bool
	 */
	public static function yoast_is_installed() {
		return defined( 'WPSEO_VERSION' )
			|| defined( 'YOAST_ENVIRONMENT' )
			|| class_exists( '\Yoast\WP\SEO\Main', false );
	}

	public static function render_page() {
		if ( ! current_user_can( 'manage_options' ) ) {
			return;
		}

		$settings = self::get_settings();
		$yoast_ok = self::yoast_is_installed();

		?>
		<div class="wrap mpe-essentials-wrap">
			<h1><?php esc_html_e( 'Magic Page Essentials', 'magic-page-essentials' ); ?></h1>
			<p class="description">
				<?php esc_html_e( 'Toggle fixes and integrations layered on top of the Magic Page plugin.', 'magic-page-essentials' ); ?>
			</p>

			<form method="post" action="options.php">
				<?php
				settings_fields( 'mpe_essentials_group' );
				?>
				<table class="form-table" role="presentation">
					<tbody>
						<tr>
							<th scope="row"><?php esc_html_e( 'Yoast SEO integration', 'magic-page-essentials' ); ?></th>
							<td>
								<label>
									<input type="checkbox" name="<?php echo esc_attr( self::OPTION_NAME ); ?>[yoast_bridge]" value="1" <?php checked( ! empty( $settings['yoast_bridge'] ) ); ?> <?php disabled( ! $yoast_ok ); ?> />
									<?php esc_html_e( 'Register %%mpp_*%% replacement variables for titles and meta (recommended when using Yoast with Magic Page).', 'magic-page-essentials' ); ?>
								</label>
								<?php if ( ! $yoast_ok ) : ?>
									<p class="description"><?php esc_html_e( 'Yoast SEO is not active. Install and activate Yoast SEO to use this option.', 'magic-page-essentials' ); ?></p>
								<?php endif; ?>
							</td>
						</tr>
						<tr>
							<th scope="row"><?php esc_html_e( 'Analytics dashboard', 'magic-page-essentials' ); ?></th>
							<td>
								<label>
									<input type="checkbox" name="<?php echo esc_attr( self::OPTION_NAME ); ?>[analytics_dashboard]" value="1" <?php checked( ! empty( $settings['analytics_dashboard'] ) ); ?> />
									<?php esc_html_e( 'Show the Analytics submenu and collect visit/click stats.', 'magic-page-essentials' ); ?>
								</label>
							</td>
						</tr>
						<tr>
							<th scope="row"><?php esc_html_e( 'Analytics: static pages', 'magic-page-essentials' ); ?></th>
							<td>
								<label>
									<input type="checkbox" name="<?php echo esc_attr( self::OPTION_NAME ); ?>[analytics_include_static_pages]" value="1" <?php checked( ! empty( $settings['analytics_include_static_pages'] ) ); ?> />
									<?php esc_html_e( 'Include published Pages and Posts that were created by Magic Page export (they have non-empty _group_id or _batch_id meta). Location-only meta from the admin metabox is ignored so normal pages are not mixed with exported static pages.', 'magic-page-essentials' ); ?>
								</label>
							</td>
						</tr>
						<tr>
							<th scope="row"><?php esc_html_e( 'Performance scope', 'magic-page-essentials' ); ?></th>
							<td>
								<label>
									<input type="checkbox" name="<?php echo esc_attr( self::OPTION_NAME ); ?>[performance_scope]" value="1" <?php checked( ! empty( $settings['performance_scope'] ) ); ?> />
									<?php esc_html_e( 'On normal pages that are not Magic Page templates or location-backed content, remove Magic Page front-end hooks to reduce database load and timeouts.', 'magic-page-essentials' ); ?>
								</label>
								<p class="description">
									<?php esc_html_e( 'Requires the Magic Page plugin. Does not modify vendor files. If something breaks after a Magic Page update, disable this toggle and check debug.log for Essentials notices.', 'magic-page-essentials' ); ?>
								</p>
							</td>
						</tr>
						<tr>
							<th scope="row"><?php esc_html_e( 'Hosting / database (manual)', 'magic-page-essentials' ); ?></th>
							<td>
								<p class="description">
									<?php esc_html_e( 'Heavy Magic Page SQL and transients can still stress MySQL. Recommended: persistent object cache (Redis) so query transients skip the database on hits; enable the MySQL slow query log and review indexes on large sites; optional full-page cache for anonymous traffic. Raising PHP workers or Cloudflare origin timeouts alone does not fix slow queries.', 'magic-page-essentials' ); ?>
								</p>
							</td>
						</tr>
					</tbody>
				</table>
				<?php submit_button(); ?>
			</form>
		</div>
		<?php
	}
}
