<?php
/**
 * Offer one-click updates from GitHub releases (tag = version, e.g. v1.2.5).
 *
 * Preferred: attach a release asset whose name ends in .zip (WordPress plugin layout:
 * magic-page-essentials/magic-page-essentials.php inside the zip). If no asset exists,
 * the source archive URL is used and {@see Magic_Page_Essentials_GitHub_Updater::fix_github_zip_root()}
 * renames the extracted folder to magic-page-essentials.
 *
 * @package Magic_Page_Essentials
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * GitHub Releases API integration for plugin updates.
 */
class Magic_Page_Essentials_GitHub_Updater {

	/**
	 * GitHub owner/repo (no leading or trailing slashes).
	 *
	 * @var string
	 */
	private static $repo = 'oduppinsjr/wp-magic-page-essentials';

	/**
	 * @return void
	 */
	public static function init() {
		add_filter( 'pre_set_site_transient_update_plugins', array( __CLASS__, 'inject_update' ) );
		add_filter( 'plugins_api', array( __CLASS__, 'plugins_api' ), 10, 3 );
		add_filter( 'upgrader_source_selection', array( __CLASS__, 'fix_github_zip_root' ), 10, 4 );
		add_action( 'upgrader_process_complete', array( __CLASS__, 'clear_release_cache' ), 10, 2 );
	}

	/**
	 * @return string Plugin basename relative to WP_PLUGIN_DIR.
	 */
	private static function plugin_basename() {
		return plugin_basename( MAGIC_PAGE_ESSENTIALS_FILE );
	}

	/**
	 * @return string owner/repo parsed from plugin header Update URI when possible.
	 */
	private static function get_repo() {
		if ( ! function_exists( 'get_file_data' ) || ! defined( 'MAGIC_PAGE_ESSENTIALS_FILE' ) ) {
			return self::$repo;
		}
		$data = get_file_data(
			MAGIC_PAGE_ESSENTIALS_FILE,
			array( 'UpdateURI' => 'Update URI' )
		);
		if ( ! empty( $data['UpdateURI'] ) && is_string( $data['UpdateURI'] ) ) {
			$uri = trim( $data['UpdateURI'] );
			if ( preg_match( '#github\.com/([^/]+/[^/#?]+)#i', $uri, $m ) ) {
				return trim( $m[1], '/' );
			}
		}
		return self::$repo;
	}

	/**
	 * @return string
	 */
	private static function cache_key() {
		return 'magic_page_essentials_gh_rel_' . md5( self::get_repo() );
	}

	/**
	 * @return array<string,mixed>|null Release payload or null on failure / no release.
	 */
	private static function fetch_latest_release() {
		$key = self::cache_key();
		$cached = get_site_transient( $key );
		if ( is_array( $cached ) && isset( $cached['fetched'] ) ) {
			return $cached['data'];
		}

		$repo = self::get_repo();
		$url  = 'https://api.github.com/repos/' . $repo . '/releases/latest';

		$response = wp_remote_get(
			$url,
			array(
				'timeout' => 12,
				'headers' => array(
					'Accept'     => 'application/vnd.github+json',
					'User-Agent' => 'WordPress/' . get_bloginfo( 'version' ) . '; ' . esc_url( home_url( '/' ) ),
				),
			)
		);

		$data = null;
		if ( ! is_wp_error( $response ) && 200 === (int) wp_remote_retrieve_response_code( $response ) ) {
			$json = json_decode( wp_remote_retrieve_body( $response ), true );
			if ( is_array( $json ) && ! empty( $json['tag_name'] ) ) {
				$tag     = (string) $json['tag_name'];
				$version = ltrim( $tag, 'vV' );

				$package = '';
				if ( ! empty( $json['assets'] ) && is_array( $json['assets'] ) ) {
					foreach ( $json['assets'] as $asset ) {
						if ( empty( $asset['browser_download_url'] ) || empty( $asset['name'] ) ) {
							continue;
						}
						if ( preg_match( '/\.zip$/i', (string) $asset['name'] ) ) {
							$package = (string) $asset['browser_download_url'];
							break;
						}
					}
				}

				if ( '' === $package ) {
					$encoded = rawurlencode( $tag );
					$package = 'https://github.com/' . $repo . '/archive/refs/tags/' . $encoded . '.zip';
				}

				$data = array(
					'version'      => $version,
					'package'      => $package,
					'body'         => isset( $json['body'] ) ? (string) $json['body'] : '',
					'published_at' => isset( $json['published_at'] ) ? (string) $json['published_at'] : '',
					'html_url'     => isset( $json['html_url'] ) ? (string) $json['html_url'] : '',
				);
			}
		}

		set_site_transient( $key, array( 'fetched' => true, 'data' => $data ), 12 * HOUR_IN_SECONDS );

		return $data;
	}

	/**
	 * @param object $transient Value from site transient.
	 * @return object
	 */
	public static function inject_update( $transient ) {
		if ( empty( $transient->checked ) || ! is_array( $transient->checked ) ) {
			return $transient;
		}

		$file = self::plugin_basename();
		if ( empty( $transient->checked[ $file ] ) ) {
			return $transient;
		}

		$remote = self::fetch_latest_release();
		if ( ! is_array( $remote ) || empty( $remote['version'] ) ) {
			return $transient;
		}

		if ( ! defined( 'MAGIC_PAGE_ESSENTIALS_VERSION' ) ) {
			return $transient;
		}

		if ( version_compare( MAGIC_PAGE_ESSENTIALS_VERSION, $remote['version'], '>=' ) ) {
			return $transient;
		}

		if ( ! isset( $transient->response ) ) {
			$transient->response = array();
		}

		$repo = self::get_repo();

		$transient->response[ $file ] = (object) array(
			'id'            => $file,
			'slug'          => 'magic-page-essentials',
			'plugin'        => $file,
			'new_version'   => $remote['version'],
			'url'           => 'https://github.com/' . $repo,
			'package'       => $remote['package'],
			'icons'         => array(),
			'banners'       => array(),
			'banners_rtl'   => array(),
			'tested'        => '',
			'requires_php'  => '',
			'requires'      => '',
			'compatibility' => new stdClass(),
		);

		return $transient;
	}

	/**
	 * @param mixed  $result Result.
	 * @param string $action Action.
	 * @param object $args   Arguments.
	 * @return mixed
	 */
	public static function plugins_api( $result, $action, $args ) {
		if ( 'plugin_information' !== $action || empty( $args->slug ) || 'magic-page-essentials' !== $args->slug ) {
			return $result;
		}

		$remote = self::fetch_latest_release();
		if ( ! is_array( $remote ) || empty( $remote['version'] ) ) {
			return $result;
		}

		return (object) array(
			'name'          => 'Magic Page Essentials',
			'slug'          => 'magic-page-essentials',
			'version'       => $remote['version'],
			'author'        => '<a href="https://duppinstech.com">Duppins Technology</a>',
			'homepage'      => ! empty( $remote['html_url'] ) ? $remote['html_url'] : 'https://github.com/' . self::get_repo(),
			'download_link' => $remote['package'],
			'sections'      => array(
				'description' => ! empty( $remote['body'] ) ? wp_kses_post( wpautop( $remote['body'] ) ) : '',
				'changelog'   => '',
			),
			'banners'       => array(),
			'icons'         => array(),
		);
	}

	/**
	 * Rename GitHub archive folder (owner-repo-hash) to magic-page-essentials.
	 *
	 * @param string      $source        Path to extracted directory.
	 * @param string      $remote_source Parent tmp path.
	 * @param WP_Upgrader $upgrader      Upgrader instance.
	 * @param array       $hook_extra    Extra args.
	 * @return string|\WP_Error
	 */
	public static function fix_github_zip_root( $source, $remote_source, $upgrader, $hook_extra = null ) {
		global $wp_filesystem;

		$file = self::plugin_basename();
		if ( empty( $hook_extra['plugin'] ) || $hook_extra['plugin'] !== $file ) {
			return $source;
		}
		if ( is_wp_error( $source ) || ! is_string( $source ) ) {
			return $source;
		}

		$desired = trailingslashit( $remote_source ) . 'magic-page-essentials/';
		if ( $wp_filesystem->exists( $desired ) ) {
			return $source;
		}
		if ( ! $wp_filesystem->exists( $source ) ) {
			return $source;
		}

		if ( $wp_filesystem->move( $source, $desired ) ) {
			return $desired;
		}

		return $source;
	}

	/**
	 * @param WP_Upgrader $upgrader WP_Upgrader instance.
	 * @param array       $options  Hook extra.
	 * @return void
	 */
	public static function clear_release_cache( $upgrader, $options ) {
		if ( empty( $options['action'] ) || 'update' !== $options['action'] ) {
			return;
		}
		if ( empty( $options['type'] ) || 'plugin' !== $options['type'] ) {
			return;
		}
		if ( empty( $options['plugins'] ) || ! is_array( $options['plugins'] ) ) {
			return;
		}
		$file = self::plugin_basename();
		if ( ! in_array( $file, $options['plugins'], true ) ) {
			return;
		}
		delete_site_transient( self::cache_key() );
	}
}
