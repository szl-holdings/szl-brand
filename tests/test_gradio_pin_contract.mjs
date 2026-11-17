// SPDX-License-Identifier: Apache-2.0
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { readFileSync } from 'node:fs';
import { pinnedGradioVersion } from '../tools/gradio_pin_contract.mjs';

test('source pins actual Space dependency', () => {
  const src = readFileSync(new URL('../pyproject.toml', import.meta.url), 'utf8');
  assert.equal(pinnedGradioVersion(src), '6.32.0');
});
test('rejects unpinned/missing/double/conflicting declared versions', () => {
  for (const src of [
    '', 'space = []',
    'space = ["gradio>=6.32.0"]',
    'space = ["gradio==6.32.0", "some-other-dep==1.0"]',
    'space = ["gradio==6.32.0"]\nspace = ["gradio==6.33.0"]',
  ]) assert.throws(() => pinnedGradioVersion(src));
});
test('future exact pins require matching installed version', () => {
  assert.equal(pinnedGradioVersion('space = [\n  "gradio==6.33.0",\n]'), '6.33.0');
});
