// SPDX-License-Identifier: Apache-2.0
// Actual staged Gradio app, synthetic callbacks, loopback-only qualification.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { execFileSync, spawn } from 'node:child_process';
import { lstat, mkdir, mkdtemp, readFile, writeFile } from 'node:fs/promises';
import { createServer } from 'node:net';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const options = {};
for (let i = 2; i < process.argv.length; i++) {
  const key = process.argv[i];
  assert(['--out', '--python', '--pythonpath', '--module', '--browser', '--allow-dirty'].includes(key));
  if (key === '--allow-dirty') { options.allowDirty = true; continue; }
  assert(process.argv[i + 1] && !process.argv[i + 1].startsWith('--'));
  options[key.slice(2)] = process.argv[++i];
}
const git = (...args) => execFileSync('git', args, { cwd: root, encoding: 'utf8' }).trim();
const source = git('rev-parse', 'HEAD'), tree = git('rev-parse', 'HEAD^{tree}');
const dirty = Boolean(git('status', '--porcelain', '--untracked-files=normal'));
assert(!dirty || options.allowDirty, 'Final qualification requires the exact clean candidate');
if (process.env.SOURCE_SHA) assert.equal(source, process.env.SOURCE_SHA);
const parent = path.resolve(options.out || path.join(root, 'dist', 'marketing-factory-observations'));
await mkdir(parent, { recursive: true });
assert((await lstat(parent)).isDirectory() && !(await lstat(parent)).isSymbolicLink());
const out = await mkdtemp(path.join(parent, 'factory-native-'));
const save = (name, value) => writeFile(path.join(out, name), value, { flag: 'wx', mode: 0o600 });
const listener = createServer();
await new Promise(resolve => listener.listen(0, '127.0.0.1', resolve));
const port = listener.address().port;
await new Promise(resolve => listener.close(resolve));
const origin = `http://127.0.0.1:${port}`;
const env = {
  PATH: process.env.PATH || '/usr/bin:/bin', LANG: 'C.UTF-8', PYTHONUNBUFFERED: '1',
  PYTHONNOUSERSITE: '1', GRADIO_ANALYTICS_ENABLED: 'False', HF_HUB_OFFLINE: '1',
  HF_HUB_DISABLE_IMPLICIT_TOKEN: '1', HF_HUB_DISABLE_TELEMETRY: '1',
  HF_HOME: path.join(out, 'hf-cache'), GRADIO_TEMP_DIR: path.join(out, 'gradio-cache'),
  ...(options.pythonpath ? { PYTHONPATH: path.resolve(options.pythonpath) } : {}),
};
const child = spawn(options.python || 'python', [path.join(root, 'tools/marketing_factory_fixture.py'), '--out', out, '--port', String(port)], { cwd: root, env, stdio: ['ignore', 'pipe', 'pipe'] });
let logs = '', errors = '', ready = null;
child.stdout.on('data', data => { logs += data.toString(); });
child.stderr.on('data', data => { errors += data.toString(); });
const results = [], measurements = [], browserErrors = [], deniedRequests = [], localCallbacks = [], frameworkResets = [], callbackResponses = [], callbackInputs = [];
let browser, formSnapshots = [];
const record = async (name, fn) => {
  try { await fn(); results.push({ name, status: 'passed' }); }
  catch (error) { results.push({ name, status: 'failed', error: error.message }); }
};
const settle = page => page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
const factsCount = () => (logs.match(/FIXTURE_FACTBASE_CALL:/g) || []).length;
let phase = 'navigation';

async function measure(page, name) {
  await settle(page);
  const observed = await page.evaluate(() => {
    const visible = el => {
      if (!(el instanceof HTMLElement) || !el.getClientRects().length) return false;
      if (el.closest('[aria-hidden="true"]')) return false;
      for (let p = el; p; p = p.parentElement) {
        const s = getComputedStyle(p);
        if (s.display === 'none' || s.visibility === 'hidden' || Number(s.opacity) === 0) return false;
      }
      return true;
    };
    const paint = document.createElement('canvas').getContext('2d', { willReadFrequently: true });
    const color = value => {
      assertColor(value);
      paint.clearRect(0, 0, 1, 1); paint.fillStyle = value; paint.fillRect(0, 0, 1, 1);
      const c = paint.getImageData(0, 0, 1, 1).data;
      return [c[0], c[1], c[2], c[3] / 255];
    };
    function assertColor(value) { if (!CSS.supports('color', value)) throw new Error('Unsupported computed color'); }
    const blend = (a, b) => a.slice(0, 3).map((v, i) => v * a[3] + b[i] * (1 - a[3])).concat(1);
    const lum = c => c.slice(0, 3).map(v => (v /= 255) <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4).reduce((a, v, i) => a + v * [.2126, .7152, .0722][i], 0);
    const ratio = (a, b) => (Math.max(lum(a), lum(b)) + .05) / (Math.min(lum(a), lum(b)) + .05);
    const split = value => {
      const out = []; let depth = 0, start = 0;
      for (let i = 0; i < value.length; i++) {
        if (value[i] === '(') depth++;
        if (value[i] === ')') depth--;
        if (value[i] === ',' && !depth) { out.push(value.slice(start, i)); start = i + 1; }
      }
      out.push(value.slice(start)); return out;
    };
    const cache = new Map();
    const backgrounds = el => {
      if (!el) return [[255, 255, 255, 1]];
      if (cache.has(el)) return cache.get(el);
      const s = getComputedStyle(el);
      let colors = backgrounds(el.parentElement).map(bg => blend(color(s.backgroundColor), bg));
      for (const layer of split(s.backgroundImage).reverse()) {
        if (!layer.includes('gradient(')) continue;
        const stops = [...layer.matchAll(/rgba?\([^()]*\)|color\([^()]*\)|#[\da-f]{3,8}\b/gi)].map(m => color(m[0]));
        if (stops.length) colors = colors.flatMap(bg => stops.map(stop => blend(stop, bg)));
        colors = [...new Map(colors.map(c => [c.map(Math.round).join(), c])).values()].slice(0, 64);
      }
      cache.set(el, colors); return colors;
    };
    const badText = [], badTargets = [], unnamed = [];
    let textPairs = 0;
    const inspect = (el, text) => {
      const s = getComputedStyle(el), foreground = color(s.color);
      const minimum = parseFloat(s.fontSize) >= 24 || (parseFloat(s.fontSize) >= 18.66 && Number(s.fontWeight) >= 700) ? 3 : 4.5;
      const actual = Math.min(...backgrounds(el).map(bg => ratio(blend(foreground, bg), bg)));
      textPairs++;
      if (actual + .01 < minimum) badText.push({ text: text.slice(0, 80), ratio: +actual.toFixed(3), minimum, element: el.className });
    };
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) {
      const node = walker.currentNode, el = node.parentElement, text = node.textContent.trim();
      if (text && el && visible(el) && !el.closest("script,style,option,[disabled],[aria-hidden='true']")) inspect(el, text);
    }
    for (const el of document.querySelectorAll('input,textarea')) if (visible(el)) inspect(el, el.value || el.getAttribute('aria-label') || 'Input text');
    for (const el of document.querySelectorAll('button,.mf-nav a,.mf-footer a,.mf-brand')) {
      if (!visible(el)) continue;
      const r = el.getBoundingClientRect();
      const label = (el.getAttribute('aria-label') || el.textContent || '').trim();
      if (r.width < 43.9 || r.height < 43.9) badTargets.push({ label: label.slice(0, 60), width: r.width, height: r.height, element: el.outerHTML.slice(0, 160) });
      if (!label && !el.getAttribute('aria-labelledby')) unnamed.push(el.outerHTML.slice(0, 160));
    }
    return { width: innerWidth, scrollWidth: document.documentElement.scrollWidth, theme: document.documentElement.dataset.surface, textPairs, badText, badTargets, unnamed };
  });
  measurements.push({ name, ...observed });
  await record(`${name}: no page overflow`, () => assert(observed.scrollWidth <= observed.width + 1, JSON.stringify(observed)));
  await record(`${name}: visible text contrast`, () => assert(observed.textPairs > 15 && !observed.badText.length, JSON.stringify(observed.badText)));
  await record(`${name}: named 44px controls`, () => assert(!observed.badTargets.length && !observed.unnamed.length, JSON.stringify({ targets: observed.badTargets, unnamed: observed.unnamed })));
}

try {
  const deadline = Date.now() + 60000;
  while (Date.now() < deadline && child.exitCode === null) {
    const line = logs.split('\n').find(line => line.startsWith('FIXTURE_READY:'));
    if (line) { ready = JSON.parse(line.slice('FIXTURE_READY:'.length)); break; }
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  assert(ready, `Fixture startup failed: ${errors.slice(-5000)}`);
  assert.equal(ready.source, source); assert.equal(ready.gradio, '6.30.0');
  const receipt = JSON.parse(await readFile(path.join(out, 'package/PUBLICATION_RECEIPT.json'), 'utf8'));
  const projection = JSON.parse(await readFile(path.join(out, 'package/native/PROJECTION.json'), 'utf8'));
  for (const [name, expected] of Object.entries(receipt.files)) {
    assert(!path.isAbsolute(name) && !name.split('/').includes('..'));
    assert.equal(createHash('sha256').update(await readFile(path.join(out, 'package', name))).digest('hex'), expected);
  }
  const { chromium } = await import(options.module || 'playwright');
  browser = await chromium.launch({ headless: true, ...(options.browser ? { executablePath: options.browser } : {}), args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, colorScheme: 'light', reducedMotion: 'reduce', serviceWorkers: 'block' });
  await context.route('**/*', async route => {
    const request = route.request(), url = new URL(request.url());
    if (url.origin !== origin) { deniedRequests.push({ method: request.method(), url: url.origin + url.pathname }); await route.abort(); return; }
    if (request.method() === 'GET' || request.method() === 'HEAD') { await route.continue(); return; }
    if (request.method() === 'POST' && url.pathname === '/gradio_api/queue/join' && phase === 'action') {
      const raw = request.postData() || '';
      if (Buffer.byteLength(raw) > 32768) { deniedRequests.push({ method: 'POST', url: url.pathname, reason: 'Oversize fixture input' }); await route.abort(); return; }
      let payload;
      try { payload = JSON.parse(raw); }
      catch { deniedRequests.push({ method: 'POST', url: url.pathname, reason: 'Malformed fixture input' }); await route.abort(); return; }
      callbackInputs.push({ function_index: payload.fn_index, data: payload.data });
      localCallbacks.push(url.pathname); await route.continue(); return;
    }
    if (request.method() === 'POST' && ['/gradio_api/reset', '/gradio_api/reset/'].includes(url.pathname)) {
      frameworkResets.push(url.pathname); await route.continue(); return;
    }
    deniedRequests.push({ method: request.method(), url: url.pathname, phase }); await route.abort();
  });
  const page = await context.newPage();
  await page.addInitScript(() => {
    window.__factoryFixtureInputs = [];
    document.addEventListener('click', event => {
      if (!(event.target instanceof Element) || !event.target.closest('#compose-drafts')) return;
      window.__factoryFixtureInputs.push([...document.querySelectorAll('#factory-panel-drafts .mf-editor input, #factory-panel-drafts .mf-editor textarea')]
        .filter(field => !field.disabled && !field.readOnly).map(field => field.value.slice(0, 4096)));
    }, true);
  });
  page.setDefaultTimeout(7000);
  page.on('pageerror', error => browserErrors.push(error.message));
  page.on('response', async response => {
    if (response.request().method() !== 'POST') return;
    try { callbackResponses.push({ path: new URL(response.url()).pathname, status: response.status(), body: (await response.text()).slice(0, 2000) }); }
    catch { callbackResponses.push({ path: new URL(response.url()).pathname, status: response.status(), body: 'Response closed' }); }
  });
  await page.goto(origin, { waitUntil: 'domcontentloaded' });
  await page.locator('#factory-title').waitFor();
  await page.waitForFunction(() => document.documentElement.dataset.surface === 'light');
  await save('initial-tabs.html', await page.locator('#factory-tabs').evaluate(e => e.outerHTML));
  await page.screenshot({ path: path.join(out, 'factory-initial-desktop.png'), fullPage: true });
  await record('Passive entry makes no factbase request', () => assert.equal(factsCount(), 0));
  await record('Native images are the exact qualified bytes', async () => {
    for (const [selector, sourcePath] of [['.mf-brand img', 'kit/logos/orbit-v2/suite/szl-icon-32.svg'], ['.mf-orbit', 'kit/logos/orbit-v2/suite/szl-orbit-holo.svg']]) {
      const uri = await page.locator(selector).getAttribute('src');
      assert(uri.startsWith('data:image/svg+xml;base64,'));
      assert.deepEqual(Buffer.from(uri.split(',')[1], 'base64'), await readFile(path.join(root, sourcePath)));
    }
    assert.equal(await page.locator('.mf-brand img').evaluate(e => e.getBoundingClientRect().width), 40);
  });
  await record('The document stylesheet preserves exact native tokens and component CSS', async () => {
    const expected = (await readFile(path.join(out, 'package/native/szl-tokens.css'), 'utf8')) + '\n' + (await readFile(path.join(out, 'package/factory.css'), 'utf8'));
    assert.equal(await page.locator('#factory-native-style').textContent(), expected);
  });
  const tabs = ['Public facts', 'Draft studio', 'Copy review', 'Operating plan', 'Source & package'];
  for (const width of [320, 390, 768, 1024, 1440, 2560]) {
    await page.setViewportSize({ width, height: 1000 });
    for (const theme of ['light', 'dark']) {
      if (await page.locator('html').getAttribute('data-surface') !== theme) await page.locator('#factory-theme-toggle').click();
      for (const tab of tabs) {
        await page.getByRole('tab', { name: tab, exact: true }).click();
        await measure(page, `${width}/${theme}/${tab}`);
      }
      if ([320, 1440].includes(width)) {
        await page.getByRole('tab', { name: 'Public facts', exact: true }).click();
        await page.evaluate(() => scrollTo(0, 0));
        await settle(page);
        await page.screenshot({ path: path.join(out, `factory-${width}-${theme}.png`), fullPage: true });
      }
    }
  }
  await record('All tab/theme navigation remains passive', () => assert.equal(factsCount(), 0));
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.getByRole('tab', { name: 'Public facts', exact: true }).click();
  for (const theme of ['light', 'dark']) {
    if (await page.locator('html').getAttribute('data-surface') !== theme) await page.locator('#factory-theme-toggle').click();
    const action = page.locator('#measure-facts');
    await action.scrollIntoViewIfNeeded();
    await page.mouse.move(0, 0);
    await measure(page, `${theme} action normal`);
    await action.hover();
    await measure(page, `${theme} action hover`);
    await page.mouse.down();
    await measure(page, `${theme} action pressed`);
    await page.mouse.move(0, 0); await page.mouse.up();
  }
  await record('Action-state rendering does not execute a callback', () => assert.equal(factsCount(), 0));
  const read = async count => {
    phase = 'action'; await page.locator('#measure-facts').click();
    await page.waitForFunction(() => document.querySelector('.mf-observation-heading'), null, { timeout: 30000 });
    const end = Date.now() + 30000;
    while (factsCount() < count && Date.now() < end) await new Promise(resolve => setTimeout(resolve, 50));
    assert.equal(factsCount(), count);
    await page.locator('#raw-factbase').getByRole('button', { name: 'Inspect the raw factbase JSON' }).click();
    await page.locator('#raw-factbase textarea').waitFor();
  };
  await read(1);
  await record('Measured values and unavailable door remain distinct', async () => {
    await page.waitForFunction(() => document.querySelector('#raw-factbase textarea')?.value.includes('2026-10-11T12:00:00Z'));
    assert.equal(JSON.parse(await page.locator('#raw-factbase textarea').inputValue()).hf.downloads.total, 1200);
    assert(await page.locator('.mf-metric').filter({ hasText: 'a11oy.net' }).innerText().then(t => t.includes('VALUE UNAVAILABLE · SOURCE: MEASURED')));
  });
  await measure(page, 'measured observation');
  await page.locator('#raw-factbase').getByRole('button', { name: 'Inspect the raw factbase JSON' }).click();
  await read(2);
  await record('Partial response clears earlier timestamp and preserves zero', async () => {
    await page.waitForFunction(() => document.querySelector('#raw-factbase textarea')?.value.includes('"repos": 0'));
    assert(await page.locator('.mf-observation-heading').innerText().then(t => t.includes('UNAVAILABLE') && !t.includes('12:00:00')));
    assert.equal(await page.locator('.mf-metric').filter({ has: page.locator('dt', { hasText: /^Repositories$/ }) }).locator('dd').innerText(), '0');
  });
  await page.locator('#raw-factbase').getByRole('button', { name: 'Inspect the raw factbase JSON' }).click();
  await read(3);
  await record('Hostile source text never creates markup or a resource request', async () => {
    await page.waitForFunction(() => document.querySelector('#raw-factbase textarea')?.value.includes('invalid.example'));
    assert.equal(await page.locator('#fact-observation img').count(), 0);
    assert((await page.locator('#fact-observation').innerText()).includes('<img src='));
    assert.equal(await page.evaluate(() => window.injected), undefined);
  });
  await page.locator('#raw-factbase').getByRole('button', { name: 'Inspect the raw factbase JSON' }).click();
  await read(4);
  await record('Malformed callback replaces previous facts with an explicit gap', async () => {
    await page.waitForFunction(() => document.querySelector('#raw-factbase textarea')?.value.includes('fact collection failed'));
    assert.equal(await page.locator('.mf-metric[data-state="measured"]').count(), 0);
  });
  await page.locator('#raw-factbase').getByRole('button', { name: 'Inspect the raw factbase JSON' }).click();
  await read(5);
  await record('A later observation recovers without stale unavailable data', async () => {
    await page.waitForFunction(() => document.querySelector('#raw-factbase textarea')?.value.includes('2026-10-11T12:00:00Z'));
    assert((await page.locator('#fact-observation').innerText()).includes('fixture-data'));
  });
  await page.getByRole('tab', { name: 'Draft studio', exact: true }).click();
  await page.getByLabel('Subject line A', { exact: true }).fill('same');
  await page.getByLabel('Subject line B', { exact: true }).fill('same');
  await page.locator('#compose-drafts').click();
  await record('Invalid subjects do not collect a factbase or retain a draft', async () => {
    await page.waitForFunction(() => document.querySelector('#compose-verdict textarea')?.value.includes('two distinct'));
    assert.deepEqual(callbackInputs.at(-1)?.data, ['same', 'same', '']);
    assert.equal(factsCount(), 5); assert.equal(await page.locator('#substack-draft textarea').inputValue(), '');
  });
  await page.getByLabel('Subject line A', { exact: true }).fill('Source observations');
  await page.getByLabel('Subject line B', { exact: true }).fill('');
  await page.getByLabel('Subject line B', { exact: true }).pressSequentially('The next draft');
  await page.getByRole('textbox', { name: /^Essay body/ }).fill('<img src="https://invalid.example/draft" onerror="window.injected=1">');
  await page.getByRole('tab', { name: 'Operating plan', exact: true }).click();
  await page.getByRole('tab', { name: 'Draft studio', exact: true }).click();
  await record('Unsubmitted edits survive workspace navigation without a fact read', async () => {
    assert.equal(await page.getByLabel('Subject line A', { exact: true }).inputValue(), 'Source observations');
    assert.equal(await page.getByLabel('Subject line B', { exact: true }).inputValue(), 'The next draft');
    assert.equal(await page.getByRole('textbox', { name: /^Essay body/ }).inputValue(), '<img src="https://invalid.example/draft" onerror="window.injected=1">');
    assert.equal(factsCount(), 5);
  });
  await page.locator('#compose-drafts').click();
  await record('Draft output retains literal source without rendering author markup', async () => {
    await page.waitForFunction(() => document.querySelector('#substack-draft textarea')?.value.includes('invalid.example/draft'));
    assert.deepEqual(callbackInputs.at(-1)?.data, ['Source observations', 'The next draft', '<img src="https://invalid.example/draft" onerror="window.injected=1">']);
    assert.equal(factsCount(), 6); assert.equal(await page.locator('#substack-draft img').count(), 0);
    assert((await page.locator('#compose-verdict textarea').inputValue()).includes('house linter only'));
  });
  await measure(page, 'draft source and verdict');
  await page.evaluate(() => scrollTo(0, 0));
  await page.screenshot({ path: path.join(out, 'factory-drafts-1440.png'), fullPage: true });
  await page.setViewportSize({ width: 320, height: 1000 });
  await measure(page, 'mobile draft source and verdict');
  await page.evaluate(() => scrollTo(0, 0));
  await page.screenshot({ path: path.join(out, 'factory-drafts-320.png'), fullPage: true });
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.getByRole('tab', { name: 'Copy review', exact: true }).click();
  await page.getByLabel('Draft to review', { exact: true }).fill('We guarantee it.');
  await page.locator('#review-copy').click();
  await record('House-rule violations are visible without a provider read', async () => {
    await page.waitForFunction(() => document.querySelector('#lint-findings textarea')?.value.startsWith('BLOCKED'));
    assert.equal(factsCount(), 6);
  });
  await page.getByLabel('Draft to review', { exact: true }).fill('The source remains visible.');
  await page.locator('#review-copy').click();
  await record('Clean house-rule result retains its publication limit', async () => {
    await page.waitForFunction(() => document.querySelector('#lint-findings textarea')?.value.startsWith('CLEAN'));
    assert((await page.locator('#lint-findings textarea').inputValue()).includes('not publication approval'));
    assert.equal(factsCount(), 6);
  });
  formSnapshots = await page.evaluate(() => window.__factoryFixtureInputs);
  phase = 'navigation';
  await page.getByRole('tab', { name: 'Source & package', exact: true }).click();
  await record('Declared source and package-stage statement bind this staged candidate', async () => {
    assert((await page.locator('#factory-provenance').innerText()).includes(receipt.root_sha256));
    assert.equal(await page.getByRole('link', { name: 'Inspect the declared source commit' }).getAttribute('href'), `https://github.com/szl-holdings/szl-brand/commit/${source}`);
    assert((await page.locator('#factory-provenance').innerText()).includes('PACKAGE_BUILT_NOT_PUBLISHED'));
  });
  await record('Theme is keyboard operable and persists on reload', async () => {
    const prior = await page.locator('html').getAttribute('data-surface');
    await page.locator('#factory-theme-toggle').focus(); await page.keyboard.press('Enter');
    const next = await page.locator('html').getAttribute('data-surface'); assert.notEqual(next, prior);
    await page.reload({ waitUntil: 'domcontentloaded' }); await page.locator('#factory-title').waitFor();
    await page.waitForFunction(theme => document.documentElement.dataset.surface === theme, next);
    assert.equal(factsCount(), 6);
  });
  await record('Keyboard tab navigation activates the corresponding named panel', async () => {
    await page.getByRole('tab', { name: 'Public facts', exact: true }).focus();
    await page.keyboard.press('ArrowRight');
    assert.equal(await page.getByRole('tab', { name: 'Draft studio', exact: true }).getAttribute('aria-selected'), 'true');
    assert.equal(await page.getByRole('tab', { name: 'Draft studio', exact: true }).getAttribute('aria-controls'), 'factory-panel-drafts');
    await page.keyboard.press('End');
    assert.equal(await page.getByRole('tab', { name: 'Source & package', exact: true }).getAttribute('aria-selected'), 'true');
    await page.keyboard.press('Home');
    assert.equal(await page.getByRole('tab', { name: 'Public facts', exact: true }).getAttribute('aria-selected'), 'true');
    assert.equal(factsCount(), 6);
  });
  await record('Skip link places keyboard focus in the workspace', async () => {
    await page.locator('.mf-skip').focus(); await page.keyboard.press('Enter');
    assert.equal(await page.evaluate(() => document.activeElement.id), 'factory-workspace');
  });
  await record('Reduced-motion preference removes smooth scrolling', async () => assert.equal(await page.evaluate(() => getComputedStyle(document.documentElement).scrollBehavior), 'auto'));
  await page.emulateMedia({ forcedColors: 'active' });
  await measure(page, 'forced colors');
  await record('Forced colors retain a native control focus ring', async () => {
    await page.locator('#factory-theme-toggle').focus();
    assert(parseFloat(await page.locator('#factory-theme-toggle').evaluate(e => getComputedStyle(e).outlineWidth)) >= 3);
  });
  await context.close();
  await record('Browser context makes no remote or unapproved request', () => assert.deepEqual(deniedRequests, []));
  await record('No browser page error', () => assert.deepEqual(browserErrors, []));
  await record('Python fixture attempts no remote DNS or socket connect', () => assert(!logs.includes('FIXTURE_REMOTE_DENIED')));
  await record('Exact package and projection are recorded as local observations', () => { assert.equal(ready.file_count, 20); assert.equal(projection.classification, 'UNSIGNED_LOCAL_PROJECTION_METADATA'); });
} catch (error) {
  results.push({ name: 'Fixture execution', status: 'failed', error: error.stack || error.message });
} finally {
  if (browser) await browser.close();
  child.kill('SIGTERM');
  await Promise.race([new Promise(resolve => child.once('exit', resolve)), new Promise(resolve => setTimeout(resolve, 3000))]);
  if (child.exitCode === null && child.signalCode === null) child.kill('SIGKILL');
  await save('fixture.log', logs + '\n--- stderr ---\n' + errors);
  const failed = results.filter(row => row.status === 'failed');
  const report = {
    schema: 'szl.marketing-factory-rendered-fixture/v1', classification: 'UNSIGNED_LOCAL_RENDERED_FIXTURE',
    source, tree, dirty, package: ready, results, measurements, browserErrors, deniedRequests, callbackResponses,
    synthetic_callback_inputs: callbackInputs, synthetic_form_snapshots: formSnapshots,
    local_synthetic_callback_posts: localCallbacks.length, gradio_session_cleanup_posts: frameworkResets.length,
    factbase_fixture_calls: factsCount(),
    scope: 'Actual staged Gradio application, six widths and two themes, synthetic facts and explicit local callbacks. Browser counters cover the browser context; Python DNS/connect calls are separately denied. No provider fact collection or publication is exercised. These are local observations, not signed or provider readiness receipts.',
  };
  await save('results.json', JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({ out, passed: results.length - failed.length, failed: failed.length, measurements: measurements.length, facts: factsCount(), failures: failed.slice(0, 20) }, null, 2));
  process.exitCode = failed.length ? 1 : 0;
}
