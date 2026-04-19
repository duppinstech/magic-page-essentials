<?php
/**
 * Multisite helpers: network admin vs site context.
 *
 * @package Magic_Page_Essentials
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Whether to skip features that belong to a single site (Pages list, Magic Page menus).
 * True when viewing Network Admin on a multisite installation.
 *
 * @return bool
 */
function mpe_skip_network_admin_ui() {
	return is_multisite() && is_admin() && is_network_admin();
}

/**
 * Register activation hook behavior for single-site vs network activation.
 *
 * @param bool $network_wide Whether the plugin was network-activated.
 */
function mpe_plugin_activate( $network_wide ) {
	if ( ! $network_wide || ! is_multisite() ) {
		return;
	}
	// No global tables or per-site setup required; each site uses its own posts/options when the plugin runs.
}
