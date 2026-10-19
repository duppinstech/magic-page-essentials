<?php
/**
 * Remove updater cache when the plugin is deleted.
 *
 * @package Magic_Page_Essentials
 */

if ( ! defined( 'WP_UNINSTALL_PLUGIN' ) ) {
	exit;
}

delete_site_option( 'magic_page_essentials_github_release' );

$magic_page_essentials_old_repos = array(
	'oduppinsjr/wp-magic-page-essentials',
	'oduppinsjr/magic-page-essentials',
	'duppinstech/magic-page-essentials',
);
foreach ( $magic_page_essentials_old_repos as $magic_page_essentials_repo ) {
	delete_site_transient( 'magic_page_essentials_gh_rel_' . md5( $magic_page_essentials_repo ) );
}
