<?php
/**
 * Plugin Name: Magic Page Essentials
 * Plugin URI: https://github.com/duppinstech/magic-page-essentials
 * Description: Add-on for the third-party Magic Page plugin: filtered Pages list, feature toggles, optional Yoast SEO bridge, and analytics.
 * Version: 1.3.0
 * Requires at least: 5.8
 * Requires PHP: 7.4
 * Author: Duppins Technology
 * Author URI: https://duppinstech.com
 * License: GPL-2.0-or-later
 * License URI: https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain: magic-page-essentials
 * Update URI: https://github.com/duppinstech/magic-page-essentials
 *
 * @package Magic_Page_Essentials
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'MAGIC_PAGE_ESSENTIALS_VERSION', '1.3.0' );
define( 'MAGIC_PAGE_ESSENTIALS_FILE', __FILE__ );
define( 'MAGIC_PAGE_ESSENTIALS_PATH', plugin_dir_path( __FILE__ ) );
define( 'MAGIC_PAGE_ESSENTIALS_URL', plugin_dir_url( __FILE__ ) );

require_once MAGIC_PAGE_ESSENTIALS_PATH . 'includes/class-magic-page-essentials-github-updater.php';
require_once MAGIC_PAGE_ESSENTIALS_PATH . 'includes/class-magic-page-essentials-plugin-info.php';
require_once MAGIC_PAGE_ESSENTIALS_PATH . 'includes/class-essentials-settings.php';
require_once MAGIC_PAGE_ESSENTIALS_PATH . 'includes/performance-scope.php';
require_once MAGIC_PAGE_ESSENTIALS_PATH . 'includes/class-admin-dashboard.php';
require_once MAGIC_PAGE_ESSENTIALS_PATH . 'includes/class-yoast-bridge.php';
require_once MAGIC_PAGE_ESSENTIALS_PATH . 'includes/admin-functions.php';

// Updates from GitHub Releases. Booted at load so WP-Cron and background auto-updates see releases.
// Disable with define( 'MAGIC_PAGE_ESSENTIALS_DISABLE_GITHUB_UPDATER', true ).
Magic_Page_Essentials_GitHub_Updater::boot(
	array(
		'file'    => MAGIC_PAGE_ESSENTIALS_FILE,
		'version' => MAGIC_PAGE_ESSENTIALS_VERSION,
		'owner'   => 'duppinstech',
		'repo'    => 'magic-page-essentials',
		'prefix'  => 'magic_page_essentials',
	)
);

// Plugins screen links and the View details modal. No public help guide is published.
Magic_Page_Essentials_Plugin_Info::boot(
	array(
		'file'         => MAGIC_PAGE_ESSENTIALS_FILE,
		'settings_url' => 'edit.php?post_type=magicpage&page=magic-page-essentials',
		'help_url'     => '',
		'support_url'  => 'mailto:support@duppinstech.com',
	)
);

register_activation_hook(
	__FILE__,
	function () {
		if ( get_option( Magic_Page_Essentials_Settings::OPTION_NAME, null ) === null ) {
			update_option( Magic_Page_Essentials_Settings::OPTION_NAME, Magic_Page_Essentials_Settings::get_defaults() );
		}
	}
);

add_action(
	'plugins_loaded',
	function () {
		// Hosted outside WordPress.org: load /languages from the plugin directory.
		// phpcs:ignore PluginCheck.CodeAnalysis.DiscouragedFunctions.load_plugin_textdomainFound -- Non–WordPress.org distribution.
		load_plugin_textdomain( 'magic-page-essentials', false, dirname( plugin_basename( __FILE__ ) ) . '/languages' );

		Magic_Page_Essentials_Settings::init();

		MagicPage_Analytics_Dashboard::maybe_boot();

		if ( Magic_Page_Essentials_Settings::is_feature_enabled( 'yoast_bridge' ) && Magic_Page_Essentials_Settings::yoast_is_installed() ) {
			Magic_Page_Essentials_Yoast_Bridge::init();
		}
	},
	5
);
