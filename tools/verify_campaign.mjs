// SPDX-License-Identifier: Apache-2.0
// Deterministic browser checks; public APIs are test doubles, never live completeness evidence.
// Uses existing Node/Playwright/Chromium, installs nothing and never publishes a Space.
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { createServer } from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const options = {};
for (let i = 2; i < process.argv.length; i += 2) {
  assert(["--out", "--browser", "--module", "--package"].includes(process.argv[i]), "Unknown argument");
  assert(process.argv[i + 1] && !process.argv[i + 1].startsWith("--"), "Missing argument value");
  options[process.argv[i].slice(2)] = process.argv[i + 1];
}
const out = path.resolve(options.out || path.join(root, "dist", "campaign-check"));
await mkdir(out, { recursive: true });
const campaign = path.join(root, "marketing/space/szl-brand-campaign");
const assets = {
  "index.html": path.join(campaign, "index.html"),
  "style.css": path.join(campaign, "style.css"),
  "live.js": path.join(campaign, "live.js"),
  "szl-design-system.css": path.join(root, "kanchay/szl-design-system.css"),
  "szl-orbit-holo.svg": path.join(root, "kit/logos/orbit-v2/suite/szl-orbit-holo.svg"),
};
const fixtureReceipt = {
  schema: "szl.marketing-space-publication/v1", state: "PACKAGE_BUILT_NOT_PUBLISHED",
  target: { repository: "SZLHOLDINGS/szl-brand-campaign", repo_type: "space" },
  source: { repository: "szl-holdings/szl-brand", directory: "marketing/space/szl-brand-campaign", sha: "0".repeat(40) },
  root_sha256: "0".repeat(64), test_fixture: true,
};
if (options.package) {
  for (const name of Object.keys(assets)) assets[name] = path.join(path.resolve(options.package), name);
  assets["PUBLICATION_RECEIPT.json"] = path.join(path.resolve(options.package), "PUBLICATION_RECEIPT.json");
}
const bytes = {};
for (const [name, location] of Object.entries(assets)) bytes[name] = await readFile(location);
bytes["PUBLICATION_RECEIPT.json"] ??= Buffer.from(JSON.stringify(fixtureReceipt));
const receipt = JSON.parse(bytes["PUBLICATION_RECEIPT.json"]);
const hashes = Object.fromEntries(Object.entries(bytes).map(([name, body]) => [name, createHash("sha256").update(body).digest("hex")]));
assert.equal(hashes["szl-orbit-holo.svg"], "66bbf937cb3cd257ec4ab5e7b016e4c09b5d6ea97f735453833a04c534a63b37", "Approved native asset changed");
if (options.package) {
  assert.equal(receipt.source.sha, execFileSync("git", ["-C", root, "rev-parse", "HEAD"], { encoding: "utf8" }).trim());
  for (const [name, hash] of Object.entries(hashes)) if (name !== "PUBLICATION_RECEIPT.json") assert.equal(hash, receipt.files[name]);
}
const mime = { ".html": "text/html", ".css": "text/css", ".js": "text/javascript", ".svg": "image/svg+xml", ".json": "application/json" };
const server = createServer((request, response) => {
  const url = new URL(request.url, "http://localhost");
  const name = url.pathname === "/" ? "index.html" : url.pathname.slice(1);
  if (!Object.hasOwn(bytes, name)) { response.writeHead(404); response.end(); return; }
  response.writeHead(200, { "Content-Type": mime[path.extname(name)], "Cache-Control": "no-store" });
  response.end(bytes[name]);
});
await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
const base = `http://127.0.0.1:${server.address().port}/`;
const { chromium } = await import(options.module || "playwright");
const browser = await chromium.launch({ headless: true,
  ...(options.browser ? { executablePath: options.browser } : {}),
  args: ["--no-sandbox", "--disable-dev-shm-usage", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
});
const results = [], observations = [], errors = [], unexpected = [], networkDiagnostics = [];
const record = async (name, run) => {
  try { await run(); results.push({ name, status: "passed" }); }
  catch (error) { results.push({ name, status: "failed", error: error.message }); }
};
const fixture = {
  models: [{ id: "SZLHOLDINGS/model-a", downloads: 12 }, { id: "SZLHOLDINGS/model-b", downloads: 7 }],
  datasets: [{ id: "SZLHOLDINGS/data-a", downloads: 30 }],
  spaces: [{ id: "SZLHOLDINGS/space-a" }],
  kernels: [{ id: "SZLHOLDINGS/kernel-a" }, { id: "SZLHOLDINGS/kernel-b" }],
  collections: [{ slug: "SZLHOLDINGS/collection-0123456789abcdef", owner: { name: "SZLHOLDINGS" } }],
  buckets: [{ id: "SZLHOLDINGS/bucket-a", author: "SZLHOLDINGS" }],
};
const next = "https://huggingface.co/api/models?author=SZLHOLDINGS&limit=1000&cursor=next";
async function openScenario(mode = "success", contextOptions = {}) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, ...contextOptions });
  const requests = [];
  page.on("pageerror", error => errors.push({ mode, error: error.message }));
  page.on("requestfailed", request => networkDiagnostics.push({ mode, url: request.url(), reason: request.failure()?.errorText }));
  await page.route(/^https:\/\//, async route => {
    const url = new URL(route.request().url());
    requests.push(url.href);
    const headers = { "Access-Control-Allow-Origin": "*", "Access-Control-Expose-Headers": "Link" };
    let body, status = 200;
    if (url.href === "https://api.github.com/orgs/szl-holdings") {
      body = mode === "malformed" ? null : { public_repos: mode === "empty" ? 0 : 128 };
    } else if (url.origin === "https://huggingface.co" && /^\/api\/(models|datasets|spaces|kernels|collections|buckets)(\/SZLHOLDINGS)?$/.test(url.pathname)) {
      const kind = url.pathname.split("/")[2];
      body = structuredClone(fixture[kind]);
      if (mode === "empty") body = [];
      else if (kind === "models") {
        if (mode === "timeout") return;
        if (url.searchParams.has("cursor")) {
          body = [{ id: "SZLHOLDINGS/model-c", downloads: 1 }];
          if (mode === "partial") status = 502;
          if (mode === "duplicate") body = [structuredClone(fixture.models[0])];
        } else {
          const target = mode === "scope" ? "https://outside.invalid/next" : mode === "owner" ? next.replace("author=SZLHOLDINGS", "author=OTHER") : next;
          headers.Link = `<${target}>; rel="next"`;
        }
      }
      if (mode === "missing-download" && kind === "datasets") delete body[0].downloads;
      if (mode === "malformed" && kind === "collections") body[0].owner.name = 42;
      if (mode === "invalid-json" && kind === "buckets") {
        await route.fulfill({ status, headers, contentType: "application/json", body: "{invalid" }); return;
      }
    } else {
      unexpected.push({ mode, url: url.href }); await route.abort(); return;
    }
    await route.fulfill({ status, headers, contentType: "application/json", body: JSON.stringify(body) });
  });
  if (mode === "bad-publication") {
    await page.route("**/PUBLICATION_RECEIPT.json", route => route.fulfill({ contentType: "application/json",
      body: JSON.stringify({ ...fixtureReceipt, source: { ...fixtureReceipt.source, repository: "OTHER/brand" } }) }));
  }
  await page.goto(base);
  return { page, requests };
}
const settle = page => page.waitForFunction(() => document.querySelector("#facts").getAttribute("aria-busy") === "false", null, { timeout: 25000 });
const fact = (page, key) => page.locator(`[data-fact="${key}"]`);
const value = (page, key) => fact(page, key).locator(".fact-value").textContent();
const chip = (page, key) => fact(page, key).locator(".chip").textContent();
const rgba = css => {
  const values = css.match(/[\d.]+/g)?.map(Number);
  assert(values?.length >= 3, `Unsupported color ${css}`);
  return [...(css.startsWith("color(srgb") ? values.slice(0, 3) : values.slice(0, 3).map(c => c / 255)), values[3] ?? 1];
};
const blend = (fg, bg) => [...fg.slice(0, 3).map((c, i) => c * fg[3] + bg[i] * (1 - fg[3])), 1];
const luminance = rgb => rgb.slice(0, 3).map(c => c <= .04045 ? c / 12.92 : ((c + .055) / 1.055) ** 2.4)
  .reduce((sum, c, i) => sum + c * [.2126, .7152, .0722][i], 0);
const ratio = (a, b) => (Math.max(luminance(a), luminance(b)) + .05) / (Math.min(luminance(a), luminance(b)) + .05);
const style = element => {
  const css = getComputedStyle(element), grounds = [];
  for (let e = element; e; e = e.parentElement) grounds.push(getComputedStyle(e).backgroundColor);
  return { ink: css.color, grounds, text: element.textContent.trim().slice(0, 70) };
};
const contrast = probe => {
  const ground = probe.grounds.map(rgba).reverse().reduce((bg, fg) => blend(fg, bg), [1, 1, 1, 1]);
  return ratio(blend(rgba(probe.ink), ground), ground);
};

const { page, requests } = await openScenario();
await settle(page);
await record("Terminal pagination preserves exact public counts and download ranking", async () => {
  for (const [key, expected] of Object.entries({ gh_repos: "128", hf_models: "3", hf_datasets: "1", hf_spaces: "1", hf_kernels: "2", hf_collections: "1", hf_buckets: "1", downloads: "50", crown: "SZLHOLDINGS/data-a" })) {
    assert.equal(await value(page, key), expected, key); assert.equal(await chip(page, key), "MEASURED", key);
  }
  assert(requests.includes(next), "Next page was not fetched");
  assert.equal(await fact(page, "crown").locator("a").getAttribute("href"), "https://huggingface.co/datasets/SZLHOLDINGS/data-a");
  assert.match(await page.locator("#source-sha").textContent(), new RegExp(receipt.source.sha.slice(0, 12)));
  assert.match(await page.locator("#measured-at time").getAttribute("datetime"), /^\d{4}-\d{2}-\d{2}T/);
});
await record("Approved holographic vector is loaded without remote art", async () => {
  assert(await page.locator(".identity-panel img").evaluate(e => e.complete && e.naturalWidth > 0));
  assert.equal(await page.locator("img").count(), 1);
  assert.equal(await page.locator(".identity-panel").evaluate(e => getComputedStyle(e).backgroundColor), "rgb(17, 23, 34)");
});
await record("Refresh works by keyboard and returns to an available state", async () => {
  const before = requests.filter(url => url.includes("api.github.com")).length;
  await page.locator("#refresh-facts").focus(); await page.keyboard.press("Enter");
  await page.waitForFunction(() => document.querySelector("#refresh-facts").disabled === false);
  assert.equal(requests.filter(url => url.includes("api.github.com")).length, before + 1);
  assert.equal(await value(page, "downloads"), "50");
});
for (const width of [320, 375, 768, 1024, 1440]) {
  await page.setViewportSize({ width, height: 1000 });
  await record(`${width}px: page and content remain within the viewport`, async () => {
    const overflow = await page.evaluate(() => [...document.querySelectorAll(".campaign-nav,.campaign-hero,.hero-copy,.identity-panel,.estate-panel,.fact,.door,.campaign-footer")]
      .map(e => ({ name: e.className, rect: e.getBoundingClientRect().toJSON(), scroll: e.scrollWidth, client: e.clientWidth }))
      .filter(e => e.rect.left < -.5 || e.rect.right > innerWidth + .5 || e.scroll > e.client + 1));
    assert.deepEqual(overflow, []);
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  });
  if ([375, 1440].includes(width)) {
    await page.evaluate(() => scrollTo(0, 0));
    await page.screenshot({ path: path.join(out, `campaign-${width}.png`), fullPage: true });
  }
}
for (const zoom of [2, 4]) {
  await page.setViewportSize({ width: 1280, height: 1000 });
  await page.evaluate(z => { document.documentElement.style.fontSize = `${z * 100}%`; }, zoom);
  await record(`${zoom * 100}% enlarged text reflows without clipped metrics or controls`, async () => {
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    const overflow = await page.locator(".fact,.door,.identity-panel,.section-heading").evaluateAll(elements => elements.filter(e => e.scrollWidth > e.clientWidth + 1).map(e => e.className));
    assert.deepEqual(overflow, []);
  });
  await page.screenshot({ path: path.join(out, `campaign-text-${zoom * 100}.png`) });
  await page.evaluate(() => { document.documentElement.style.fontSize = ""; });
}
await page.setViewportSize({ width: 1440, height: 1000 });
await record("Editorial and nested graphite text retain at least 4.5:1 contrast", async () => {
  const probes = await page.locator(".hero-copy h1,.hero-copy p,.identity-caption span,.estate-panel p,.estate-panel h2,.fact dt,.fact-value,.chip,.fact-note,.principles h2,.principles h3,.principles p,.door-kicker,.door strong,.door-address,.campaign-footer p").evaluateAll(elements => elements.map(element => {
    const css = getComputedStyle(element), grounds = [];
    for (let e = element; e; e = e.parentElement) grounds.push(getComputedStyle(e).backgroundColor);
    return { ink: css.color, grounds, text: element.textContent.trim().slice(0, 70) };
  }));
  for (const probe of probes) {
    const actual = contrast(probe); observations.push({ ...probe, contrast: actual });
    assert(actual >= 4.5, `${probe.text}: ${actual}`);
  }
});
for (const state of ["rest", "hover", "pressed"]) {
  const control = page.locator(".hero-actions .btn-primary");
  await control.scrollIntoViewIfNeeded();
  if (state === "rest") await page.mouse.move(0, 0); else await control.hover();
  if (state === "pressed") await page.mouse.down();
  await page.waitForTimeout(300);
  await record(`Primary action ${state} keeps readable text`, async () => {
    const probe = await control.evaluate(style); assert(contrast(probe) >= 4.5);
  });
  if (state === "pressed") { await page.mouse.move(0, 0); await page.mouse.up(); }
}
for (const width of [375, 1440]) {
  await page.setViewportSize({ width, height: 1000 }); await page.goto(base); await settle(page);
  await record(`${width}px: keyboard focus remains visible and unobscured`, async () => {
    const count = await page.locator("a[href],button:not([disabled])").count();
    for (let i = 0; i < count; i++) {
      await page.keyboard.press("Tab");
      const state = await page.evaluate(() => {
        const e = document.activeElement, s = getComputedStyle(e);
        const visible = [...e.getClientRects()].some(b => {
          const hit = document.elementFromPoint(b.left + b.width / 2, b.top + b.height / 2);
          return hit && (hit === e || e.contains(hit));
        });
        return { name: e.textContent.trim(), focus: e.matches(":focus-visible"), outline: parseFloat(s.outlineWidth),
          visible };
      });
      assert(state.focus && state.outline >= 2 && state.visible, JSON.stringify(state));
    }
  });
}
await page.emulateMedia({ reducedMotion: "reduce", forcedColors: "active" });
await record("Reduced motion and forced colors preserve the material boundary", async () => {
  const probe = await page.locator(".identity-panel").evaluate(e => { const s = getComputedStyle(e); return { image: s.backgroundImage, border: s.borderTopStyle }; });
  assert.deepEqual(probe, { image: "none", border: "solid" });
  assert.equal(await page.locator(".door").first().evaluate(e => getComputedStyle(e).transitionDuration), "1e-05s");
});
await page.screenshot({ path: path.join(out, "campaign-forced-colors.png") });
await page.close();

for (const mode of ["empty", "partial", "missing-download", "duplicate", "scope", "owner", "malformed", "invalid-json", "bad-publication", "timeout"]) {
  const { page: scenario, requests: seen } = await openScenario(mode);
  await record(`${mode}: coverage, unavailable values and recovery are explicit`, async () => {
    await settle(scenario);
    assert.equal(await scenario.locator("#refresh-facts").isEnabled(), true);
    assert.equal(await scenario.locator(".chip").filter({ hasText: "PENDING" }).count(), 0);
    if (mode === "empty") {
      assert.equal(await value(scenario, "hf_models"), "0"); assert.equal(await value(scenario, "downloads"), "0");
      assert.equal(await chip(scenario, "downloads"), "MEASURED"); assert.equal(await value(scenario, "crown"), "No listed artifact");
    } else if (["partial", "duplicate", "scope", "owner"].includes(mode)) {
      assert.equal(await value(scenario, "hf_models"), "≥ 2"); assert.equal(await chip(scenario, "hf_models"), "PARTIAL");
      assert.equal(await value(scenario, "downloads"), "UNAVAILABLE"); assert.equal(await value(scenario, "crown"), "UNAVAILABLE");
      if (["scope", "owner"].includes(mode)) assert(!seen.some(url => url.includes("outside.invalid") || url.includes("author=OTHER")));
    } else if (mode === "missing-download") {
      assert.equal(await value(scenario, "hf_datasets"), "1"); assert.equal(await chip(scenario, "hf_datasets"), "MEASURED");
      assert.equal(await value(scenario, "downloads"), "UNAVAILABLE");
    } else if (mode === "malformed") {
      assert.equal(await value(scenario, "gh_repos"), "UNAVAILABLE"); assert.equal(await value(scenario, "hf_collections"), "UNAVAILABLE");
      assert.match(await fact(scenario, "hf_collections").textContent(), /expected owner/);
    } else if (mode === "invalid-json") {
      assert.equal(await value(scenario, "hf_buckets"), "UNAVAILABLE"); assert.match(await fact(scenario, "hf_buckets").textContent(), /unreadable JSON/);
    } else if (mode === "bad-publication") {
      await scenario.waitForFunction(() => document.querySelector("#source-sha").textContent.includes("UNAVAILABLE"));
    } else if (mode === "timeout") {
      assert.equal(await value(scenario, "hf_models"), "UNAVAILABLE"); assert.match(await fact(scenario, "hf_models").textContent(), /timed out/);
      assert.equal(await value(scenario, "hf_spaces"), "1");
    }
  });
  if (mode === "partial") await scenario.screenshot({ path: path.join(out, "campaign-partial.png"), fullPage: true });
  await scenario.close();
}
const { page: touch } = await openScenario("success", { viewport: { width: 375, height: 900 }, hasTouch: true, isMobile: true });
await settle(touch);
await record("Coarse-pointer principal controls and source links reach 44px", async () => {
  assert(await touch.evaluate(() => matchMedia("(pointer:coarse)").matches));
  const targets = await touch.locator(".btn,.campaign-brand,.campaign-nav nav a,.fact-note a,.door").evaluateAll(elements => elements.map(e => {
    const b = e.getBoundingClientRect(); return { name: e.textContent.trim(), width: b.width, height: b.height };
  }));
  assert(targets.every(t => t.width >= 44 && t.height >= 44), JSON.stringify(targets));
});
await touch.close();
const noScript = await browser.newPage({ javaScriptEnabled: false });
await noScript.goto(base);
await record("Without JavaScript the page and direct source routes remain available", async () => {
  assert(await noScript.locator("h1").isVisible()); assert(await noScript.locator("noscript .static-notice").isVisible());
  assert.equal(await noScript.locator(".door").count(), 4);
});
await noScript.close();
await record("No uncaught script errors or out-of-scope external requests", async () => {
  assert.deepEqual(errors, []); assert.deepEqual(unexpected, []);
});
const report = { observedAt: new Date().toISOString(), browser: browser.version(),
  sourceRevision: execFileSync("git", ["-C", root, "rev-parse", "HEAD"], { encoding: "utf8" }).trim(),
  sourceDirty: Boolean(execFileSync("git", ["-C", root, "status", "--porcelain"], { encoding: "utf8" }).trim()),
  surface: options.package ? "Qualified local package" : "Working source with explicitly synthetic package record",
  assets: hashes, results, observations, networkDiagnostics, limits: [
    "All public API responses are local test doubles. These are behavior checks, not current estate counts or live deployment evidence.",
    "Text enlargement and 320px reflow are exercised; manual browser-menu zoom and assistive-technology review remain separate.",
    "Text contrast uses computed opaque/composited CSS grounds. Native artwork and atmospheric gradients also require visual inspection.",
    "Chromium only; no field Core Web Vitals, Safari or Firefox certification.",
    "Unsigned local observation metadata, not a product cryptographic receipt.",
  ] };
await writeFile(path.join(out, "report.json"), JSON.stringify(report, null, 2) + "\n");
await browser.close();
await new Promise(resolve => server.close(resolve));
const failed = results.filter(item => item.status === "failed");
console.log(JSON.stringify({ passed: results.length - failed.length, failed, report: path.join(out, "report.json") }, null, 2));
process.exitCode = failed.length ? 1 : 0;
