<?php
/**
 * Plugin Name: Magic Page Essentials
 * Description: Admin UI enhancements for the Magic Page Plugin. Adds an admin table for Magic Pages, streamlines page management, optional Yoast SEO bridge, and feature toggles.
 * Version: 1.2.4
 * Author: Odell @ Duppins Technology
 * Author URI: https://duppinstech.com
 * Plugin URI: https://duppinstech.com/magicpage-essentials
 * License: GPL2
 * Text Domain: magic-page-essentials
 *
 * @package Magic_Page_Essentials
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'MAGIC_PAGE_ESSENTIALS_VERSION', '1.2.4' );
define( 'MAGIC_PAGE_ESSENTIALS_PATH', plugin_dir_path( __FILE__ ) );
define( 'MAGIC_PAGE_ESSENTIALS_URL', plugin_dir_url( __FILE__ ) );

require_once MAGIC_PAGE_ESSENTIALS_PATH . 'includes/class-essentials-settings.php';
require_once MAGIC_PAGE_ESSENTIALS_PATH . 'includes/performance-scope.php';
require_once MAGIC_PAGE_ESSENTIALS_PATH . 'includes/class-admin-dashboard.php';
require_once MAGIC_PAGE_ESSENTIALS_PATH . 'includes/class-yoast-bridge.php';
require_once MAGIC_PAGE_ESSENTIALS_PATH . 'includes/admin-functions.php';

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
		load_plugin_textdomain( 'magic-page-essentials', false, dirname( plugin_basename( __FILE__ ) ) . '/languages' );

		Magic_Page_Essentials_Settings::init();

		MagicPage_Analytics_Dashboard::maybe_boot();

		if ( Magic_Page_Essentials_Settings::is_feature_enabled( 'yoast_bridge' ) && Magic_Page_Essentials_Settings::yoast_is_installed() ) {
			MPE_Yoast_Bridge::init();
		}
	},
	5
);
