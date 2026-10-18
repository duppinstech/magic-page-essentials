<?php
/**
 * Syntax-check this plugin's PHP files. Skips vendor and VCS metadata.
 */

$root = dirname(__DIR__);
$directory = new RecursiveDirectoryIterator($root, FilesystemIterator::SKIP_DOTS);
$filtered = new RecursiveCallbackFilterIterator(
	$directory,
	static function ($current, $key, $iterator) {
		if ($current->isDir()) {
			return !in_array($current->getFilename(), array('vendor', '.git', 'node_modules'), true);
		}

		return true;
	}
);

$failed = 0;
foreach (new RecursiveIteratorIterator($filtered) as $file) {
	if (!$file->isFile()) {
		continue;
	}

	$path = $file->getPathname();
	if (substr($path, -4) !== '.php') {
		continue;
	}

	$output = array();
	$code = 0;
	exec(escapeshellarg(PHP_BINARY) . ' -l ' . escapeshellarg($path), $output, $code);
	if ($code !== 0) {
		fwrite(STDERR, implode(PHP_EOL, $output) . PHP_EOL);
		$failed = $code;
	}
}

if ($failed !== 0) {
	exit($failed);
}

fwrite(STDOUT, "lint ok\n");
