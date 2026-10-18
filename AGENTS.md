# Agents

Magic Page Essentials is a WordPress plugin (PHP >= 7.4). Composer manages dependencies. Production packages are bundled in `vendor/` for site installs. There is no build step.

## Commands

Refresh the bundled production dependencies:

```
composer install --no-dev
```

Install dev dependencies (PHPUnit) before lint or test:

```
composer install
```

Lint (syntax-check this plugin's PHP; skips `vendor/`):

```
composer lint
```

Test:

```
composer test
```

Build: none.

Check `composer.json` (warnings do not fail the command; `composer validate --strict` already fails on the pinned `yahnis-elsts/plugin-update-checker` constraint):

```
composer validate
```

`composer install` changes `vendor/`. Do not commit dev packages. `composer install --no-dev` restores production packages. Leave `vendor/` unstaged unless a production dependency changed.

## Conventions

- Indent PHP, CSS, and JS with tabs. `composer.json` uses 4 spaces. YAML and other JSON use 2 spaces.
- Line endings are LF. `*.ps1`, `*.bat`, and `*.cmd` are CRLF.
- Commits use Conventional Commits (`type: summary`). Branches look like `type/short-description`.
- Plugin version and the `readme.txt` Stable tag move together. A release is a GitHub tag `vX.Y.Z`.
- The committed test suite only proves PHPUnit runs. It does not cover plugin behavior.

## Do not touch

- Plugin behavior in `magic-page-essentials.php`, `includes/`, and `assets/`, unless the task is a product change.
- `vendor/` by hand.
- `SECURITY.md` and `LICENSE.md`, unless the task is those files.
- `.env`, `.env.*`, `CLAUDE.local.md`, and `.claude/settings.local.json`.
- Pushing, tagging, releasing, or deploying, unless the user asks.
