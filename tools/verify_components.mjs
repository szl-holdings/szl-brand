// SPDX-License-Identifier: Apache-2.0
// Local rendered checks. Requires Node and an installed Playwright browser; never installs them.
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const options = {};
for (let i = 2; i < process.argv.length; i += 2) {
  assert(["--out", "--browser", "--module"].includes(process.argv[i]), "Unknown argument");
  assert(process.argv[i + 1] && !process.argv[i + 1].startsWith("--"), "Missing argument value");
  options[process.argv[i].slice(2)] = process.argv[i + 1];
}
const out = path.resolve(options.out || path.join(root, "dist", "component-check"));
await mkdir(out, { recursive: true });
const { chromium } = await import(options.module || "playwright");
const browser = await chromium.launch({
  headless: true,
  ...(options.browser ? { executablePath: options.browser } : {}),
  args: ["--disable-dev-shm-usage", "--use-gl=angle", "--use-angle=swiftshader"],
});
const results = [];
const observations = [];
const errors = [];
const externalRequests = [];
const specimen = pathToFileURL(path.join(root, "kit/examples/html/components.html")).href;
const record = async (name, run) => {
  try { await run(); results.push({ name, status: "passed" }); }
  catch (error) { results.push({ name, status: "failed", error: error.message }); }
};
const channels = (css) => {
  const numbers = css.match(/[\d.]+/g)?.map(Number);
  assert(numbers && numbers.length >= 3, `Unsupported color: ${css}`);
  const rgb = css.startsWith("color(srgb") ? numbers.slice(0, 3) : numbers.slice(0, 3).map(x => x / 255);
  return [...rgb, numbers[3] ?? 1];
};
const luminance = (rgb) => rgb.map(c => c <= .04045 ? c / 12.92 : ((c + .055) / 1.055) ** 2.4)
  .reduce((sum, c, i) => sum + c * [.2126, .7152, .0722][i], 0);
const contrast = (foreground, background) => {
  const ink = channels(foreground), ground = channels(background);
  assert.equal(ground[3], 1, "Contrast checks need an opaque reading ground");
  const painted = ink.slice(0, 3).map((c, i) => c * ink[3] + ground[i] * (1 - ink[3]));
  const a = luminance(painted), b = luminance(ground.slice(0, 3));
  return (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
};
assert.equal(contrast("rgba(0, 0, 0, 0)", "rgb(255, 255, 255)"), 1);
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
page.on("pageerror", error => errors.push(error.message));
await page.route(/^https?:/, route => {
  externalRequests.push(route.request().url());
  return route.abort();
});
await page.goto(specimen);
await record("Native mark has loaded", async () => {
  assert(await page.locator(".specimen-mark img").evaluate(e => e.complete && e.naturalWidth > 0));
});
for (const theme of ["light", "dark"]) {
  await page.selectOption("#specimen-theme", theme);
  for (const width of [320, 375, 768, 1024, 1440, 2560]) {
    await page.setViewportSize({ width, height: 1000 });
    await record(`${theme}: ${width}px page reflow`, async () => {
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), "Page overflows");
      for (const selector of [".nav", "#primary-action", ".receipt", ".code"]) {
        const boxes = await page.locator(selector).evaluateAll(elements => elements.map(e => {
          const b = e.getBoundingClientRect(); return { left: b.left, right: b.right };
        }));
        assert(boxes.every(b => b.left >= -.5 && b.right <= width + .5), `${selector} is clipped`);
      }
    });
    if ([375, 1440].includes(width)) {
      await page.evaluate(() => scrollTo(0, 0));
      await page.screenshot({ path: path.join(out, `${theme}-${width}.png`) });
    }
  }
  // Reflow equivalent to 1280px at 200% and 400%; native browser-menu zoom is a separate manual check.
  for (const zoom of [2, 4]) {
    await page.setViewportSize({ width: 1280 / zoom, height: 1000 });
    await record(`${theme}: ${zoom * 100}% zoom reflow equivalent`, async () => {
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    });
    await page.setViewportSize({ width: 1280, height: 1000 });
    await page.evaluate(zoom => { document.documentElement.style.fontSize = `${zoom * 100}%`; }, zoom);
    await record(`${theme}: ${zoom * 100}% text enlargement`, async () => {
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    });
    await page.screenshot({ path: path.join(out, `${theme}-text-${zoom * 100}.png`) });
    await page.evaluate(() => { document.documentElement.style.fontSize = ""; });
  }
  await page.setViewportSize({ width: 1440, height: 1000 });
  await record(`${theme}: nested surface inks`, async () => {
    for (const [selector, expected] of [
      ["#dark-in-light", "rgb(241, 244, 248)"], ["#light-in-dark", "rgb(17, 23, 34)"],
      ["#light-in-dark-in-light", "rgb(17, 23, 34)"], ["#dark-in-light-in-dark", "rgb(241, 244, 248)"],
    ]) assert.equal(await page.locator(selector).evaluate(e => getComputedStyle(e).color), expected);
  });
  await page.evaluate(() => {
    const clone = document.createElement("button");
    clone.type = "button"; clone.id = "primary-button-probe"; clone.className = "btn btn-primary";
    clone.textContent = "Native primary state specimen";
    document.querySelector("#actions .cluster").append(clone);
  });
  for (const selector of ["#primary-action", "#primary-button-probe"]) {
    const control = page.locator(selector);
    for (const state of ["rest", "hover", "pressed"]) {
      await control.scrollIntoViewIfNeeded();
      if (state === "rest") await page.mouse.move(0, 0);
      else await control.hover();
      if (state === "pressed") await page.mouse.down();
      await page.waitForTimeout(300);
      await record(`${theme}: ${selector} ${state} contrast`, async () => {
        const style = await control.evaluate(e => {
          const s = getComputedStyle(e); return { ink: s.color, fill: s.backgroundColor, decoration: s.textDecorationLine };
        });
        const ratio = contrast(style.ink, style.fill);
        observations.push({ theme, selector, state, ratio, ...style });
        assert(ratio >= 4.5, `Small label contrast ${ratio}`);
        assert.equal(style.decoration, "none");
      });
      if (state === "pressed") { await page.mouse.move(0, 0); await page.mouse.up(); }
    }
  }
  await page.locator("#primary-button-probe").evaluate(e => e.remove());
  await record(`${theme}: graphite terminal and readable syntax`, async () => {
    const base = await page.locator(".code").evaluate(e => getComputedStyle(e).backgroundColor);
    assert.equal(base, "rgb(5, 7, 12)");
    for (const selector of [".code", ".tok-comment", ".tok-key", ".tok-str"]) {
      const ink = await page.locator(selector).evaluate(e => getComputedStyle(e).color);
      assert(contrast(ink, base) >= 4.5, selector);
    }
  });
  await record(`${theme}: receipt marks have visible contrast`, async () => {
    for (const selector of ["#receipt-unverified", "#receipt-failed"]) {
      const ground = await page.locator(selector).evaluate(e => getComputedStyle(e).backgroundColor);
      const mark = await page.locator(`${selector} .receipt__dot`).evaluate(e => getComputedStyle(e).backgroundColor);
      assert(contrast(mark, ground) >= 3);
    }
  });
}
await record("Keyboard activation keeps local sample boundary", async () => {
  await page.locator("#sample-action").focus(); await page.keyboard.press("Enter");
  assert.match(await page.locator("#sample-action-state").textContent(), /SAMPLE.*local state preview complete/);
});
await record("Unavailable clipboard has useful local fallback", async () => {
  await page.evaluate(() => Object.defineProperty(navigator, "clipboard", { configurable: true,
    value: { writeText: async () => { throw new Error("Unavailable test clipboard"); } } }));
  await page.locator("#copy-command").click();
  assert.match(await page.locator("#copy-state").textContent(), /Copy unavailable.*manually/);
});
await record("Clipboard success copies exact command without execution", async () => {
  await page.evaluate(() => Object.defineProperty(navigator, "clipboard", { configurable: true,
    value: { writeText: async value => { window.sampleCopiedText = value; } } }));
  await page.locator("#copy-command").click();
  assert.equal(await page.evaluate(() => window.sampleCopiedText), "python -m szl_brand kanchay-build --check");
  assert.match(await page.locator("#copy-state").textContent(), /has not been executed/);
});
for (const width of [375, 1440]) {
  await page.setViewportSize({ width, height: 1000 });
  await page.goto(specimen);
  await record(`${width}px: keyboard focus is visible and unobscured`, async () => {
    const count = await page.locator('a[href],button:not([disabled]),input,select,[tabindex="0"]').count();
    for (let i = 0; i < count; i++) {
      await page.keyboard.press("Tab");
      const state = await page.evaluate(() => {
        const e = document.activeElement, s = getComputedStyle(e), r = e.getBoundingClientRect();
        const top = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
        return { name: e.id || e.textContent.trim(), focus: e.matches(":focus-visible"),
          outline: parseFloat(s.outlineWidth), visible: Boolean(top && (e === top || e.contains(top))) };
      });
      assert(state.focus && state.outline >= 2 && state.visible, JSON.stringify(state));
    }
  });
}
await page.evaluate(() => {
  const probe = document.createElement("span"); probe.className = "dot dot--live";
  probe.id = "motion-probe"; probe.setAttribute("aria-hidden", "true"); document.body.append(probe);
});
await page.emulateMedia({ reducedMotion: "reduce", forcedColors: "active" });
await record("Reduced motion stops status pulse", async () => {
  assert.equal(await page.locator("#motion-probe").evaluate(e => getComputedStyle(e).animationName), "none");
});
await record("Forced colors keeps a solid material boundary", async () => {
  const style = await page.locator(".surface-holo").first().evaluate(e => {
    const s = getComputedStyle(e); return { image: s.backgroundImage, border: s.borderTopStyle, width: s.borderTopWidth };
  });
  assert.deepEqual(style, { image: "none", border: "solid", width: "1px" });
});
await record("Forced colors preserves a visible meter track and fill", async () => {
  const style = await page.locator(".meter").evaluate(e => {
    const track = getComputedStyle(e), fill = getComputedStyle(e.querySelector(".meter__fill"));
    return { ground: track.backgroundColor, fill: fill.backgroundColor,
      border: track.borderTopStyle, width: track.borderTopWidth };
  });
  assert.equal(style.border, "solid"); assert.equal(style.width, "1px");
  assert(contrast(style.fill, style.ground) >= 3, JSON.stringify(style));
});
await page.screenshot({ path: path.join(out, "forced-colors.png") });
const touch = await browser.newPage({ viewport: { width: 375, height: 900 }, hasTouch: true, isMobile: true });
await touch.goto(specimen);
await record("Coarse pointer controls reach 44px and fields retain 16px text", async () => {
  assert(await touch.evaluate(() => matchMedia("(pointer:coarse)").matches));
  const targets = await touch.locator(".btn,.nav__link,.nav__brand,.select,.input").evaluateAll(elements => elements.map(e => {
    const b = e.getBoundingClientRect(); return { width: b.width, height: b.height, name: e.id || e.className };
  }));
  assert(targets.every(t => t.width >= 44 && t.height >= 44), JSON.stringify(targets));
  assert.equal(await touch.locator(".input").evaluate(e => getComputedStyle(e).fontSize), "16px");
});
await record("No page script errors or external requests", async () => {
  assert.deepEqual(errors, []); assert.deepEqual(externalRequests, []);
});
const assets = {};
for (const relative of ["kit/tokens/szl-design-system.css", "kit/tokens/szl-console.css", "kit/examples/html/components.html"]) {
  assets[relative] = createHash("sha256").update(await readFile(path.join(root, relative))).digest("hex");
}
const report = { observedAt: new Date().toISOString(), browser: browser.version(),
  sourceRevision: execFileSync("git", ["-C", root, "rev-parse", "HEAD"], { encoding: "utf8" }).trim(),
  sourceDirty: Boolean(execFileSync("git", ["-C", root, "status", "--porcelain"], { encoding: "utf8" }).trim()),
  assets, results, observations, limits: ["Local specimen only; no production or field Core Web Vitals evidence.",
    "Zoom checks use reflow equivalents and text enlargement, not manual browser-menu zoom.",
    "Clipboard success/error use test doubles; native OS clipboard permissions are not certified.",
    "No manual screen-reader, Safari or Firefox review in this Chromium check.",
    "Unsigned local observation metadata, not a product cryptographic receipt."] };
await writeFile(path.join(out, "report.json"), JSON.stringify(report, null, 2) + "\n");
await browser.close();
const failed = results.filter(result => result.status === "failed");
console.log(JSON.stringify({ passed: results.length - failed.length, failed, report: path.join(out, "report.json") }, null, 2));
process.exitCode = failed.length ? 1 : 0;
