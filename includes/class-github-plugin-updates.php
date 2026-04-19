<?php
/**
 * GitHub-hosted updates via Yahnis Elsts Plugin Update Checker (Composer: yahnis-elsts/plugin-update-checker).
 *
 * Overrides WordPress.org; updates are loaded from the GitHub repository (tags / branch).
 *
 * @package Magic_Page_Essentials
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Registers the update checker against MAGIC_PAGE_ESSENTIALS_GITHUB_REPO.
 */
class MPE_Github_Plugin_Updates {

	/**
	 * How often to contact GitHub (hours).
	 */
	const CHECK_PERIOD_HOURS = 12;

	public static function boot() {
		$autoload = MAGIC_PAGE_ESSENTIALS_PATH . 'vendor/autoload.php';
		if ( ! is_readable( $autoload ) ) {
			return;
		}

		require_once $autoload;

		$repo = apply_filters(
			'magic_page_essentials_github_update_repo',
			defined( 'MAGIC_PAGE_ESSENTIALS_GITHUB_REPO' ) ? MAGIC_PAGE_ESSENTIALS_GITHUB_REPO : ''
		);

		if ( ! is_string( $repo ) || '' === $repo ) {
			return;
		}

		try {
			$checker = \YahnisElsts\PluginUpdateChecker\v5\PucFactory::buildUpdateChecker(
				$repo,
				MAGIC_PAGE_ESSENTIALS_FILE,
				'magic-page-essentials',
				self::CHECK_PERIOD_HOURS
			);
		} catch ( \Throwable $e ) {
			return;
		}

		$branch = apply_filters( 'magic_page_essentials_github_update_branch', 'main' );
		if ( is_string( $branch ) && '' !== $branch ) {
			$checker->setBranch( $branch );
		}

		$token = apply_filters( 'magic_page_essentials_github_update_token', '' );
		if ( is_string( $token ) && '' !== $token ) {
			$checker->setAuthentication( $token );
		}
	}
}
