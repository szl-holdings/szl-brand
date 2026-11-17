// SPDX-License-Identifier: Apache-2.0
// Fail-closed single-source contract for the exact pinned Gradio Space extra.
import assert from 'node:assert/strict';

export function pinnedGradioVersion(pyprojectText) {
  assert.equal(typeof pyprojectText, 'string', 'project manifest must be text');
  // This exact-source grammar refuses extra/unpinned dependencies. A changed
  // manifest shape requires an explicit reviewed implementation update.
  const matches = [...pyprojectText.matchAll(/^space\s*=\s*\[\s*"gradio==(\d+\.\d+\.\d+)"\s*,?\s*\]/gm)];
  assert.equal(matches.length, 1, 'Space must declare exactly one exact Gradio pin');
  return matches[0][1];
}
