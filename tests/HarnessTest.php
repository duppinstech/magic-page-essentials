<?php

use PHPUnit\Framework\TestCase;

/**
 * Proves the PHPUnit command runs. This does not exercise plugin behavior.
 */
final class HarnessTest extends TestCase
{
    public function testHarnessRuns(): void
    {
        $this->assertTrue(true);
    }
}
