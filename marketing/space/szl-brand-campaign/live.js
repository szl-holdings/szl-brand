/* Public catalog observations only. No credential, provider write or inferred runtime state. */
(function () {
  "use strict";

  const HF = "https://huggingface.co";
  const OWNER = "SZLHOLDINGS";
  const GH_SOURCE = "https://api.github.com/orgs/szl-holdings";
  const MAX_PAGES = 25;
  const TIMEOUT_MS = 20000;
  const CATALOGS = [
    { key: "models", url: HF + "/api/models?author=" + OWNER + "&limit=1000" },
    { key: "datasets", url: HF + "/api/datasets?author=" + OWNER + "&limit=1000" },
    { key: "spaces", url: HF + "/api/spaces?author=" + OWNER + "&limit=1000" },
    { key: "kernels", url: HF + "/api/kernels?author=" + OWNER + "&limit=1000" },
    { key: "collections", url: HF + "/api/collections?owner=" + OWNER + "&limit=100" },
    // The Hub's list_buckets SDK uses this namespace endpoint with Link pagination;
    // it has no caller-supplied page limit. Do not invent one for its terminal rule.
    { key: "buckets", url: HF + "/api/buckets/" + OWNER },
  ];
  const facts = document.getElementById("facts");
  const refresh = document.getElementById("refresh-facts");
  const status = document.getElementById("snapshot-status");
  const number = new Intl.NumberFormat("en-US");
  let busy = false;

  function setFact(name, value, label, note, source) {
    const item = document.querySelector('[data-fact="' + name + '"]');
    if (!item) return;
    const shown = item.querySelector(".fact-value");
    shown.textContent = value;
    shown.dataset.unavailable = String(label === "UNAVAILABLE");
    const chip = item.querySelector(".chip");
    chip.textContent = label;
    chip.className = "chip " + (label === "MEASURED" ? "chip-measured" : label === "PARTIAL" ? "chip-partial" : "chip-unavailable");
    const detail = item.querySelector(".fact-note");
    detail.replaceChildren(document.createTextNode(note));
    if (source) {
      const link = document.createElement("a");
      link.href = source;
      link.textContent = "Inspect source";
      detail.append(document.createElement("br"), link);
    }
  }

  function reason(error) {
    if (error && error.name === "AbortError") return "The observation timed out. Refresh to try again.";
    if (error && error.name === "SyntaxError") return "The source returned unreadable JSON.";
    if (error && error.name === "TypeError") return "The source could not be reached or read. Refresh to try again.";
    return error && error.message ? error.message : "The source could not be read.";
  }

  async function request(url, signal) {
    const response = await fetch(url, {
      signal, credentials: "omit", redirect: "error", headers: { Accept: "application/json" },
    });
    if (!response.ok) throw new Error("The source returned HTTP " + response.status + ".");
    return response;
  }

  function nextPage(header, current, first) {
    if (!header) return null;
    const next = header.split(/,(?=\s*<)/).filter(part => {
      const relation = part.match(/;\s*rel\s*=\s*(?:"([^"]+)"|([^;\s,]+))/i);
      return relation && (relation[1] || relation[2]).split(/\s+/).includes("next");
    });
    if (!next.length) return null;
    if (next.length !== 1) throw new Error("The source returned ambiguous pagination.");
    const match = next[0].match(/<([^>]+)>/);
    if (!match) throw new Error("The source returned invalid pagination.");
    const url = new URL(match[1], current);
    const base = new URL(first);
    if (url.origin !== HF || url.pathname !== base.pathname || url.username || url.password || url.hash) {
      throw new Error("The next page left the expected catalog.");
    }
    for (const filter of ["author", "owner"]) {
      if (url.searchParams.getAll(filter).join("\n") !== base.searchParams.getAll(filter).join("\n")) {
        throw new Error("The next page changed the organization filter.");
      }
    }
    return url.href;
  }

  function identity(item, kind) {
    const id = item && (kind === "collections" ? item.slug : item.id);
    if (typeof id !== "string" || !/^[A-Za-z0-9][A-Za-z0-9._-]*\/[A-Za-z0-9][A-Za-z0-9._-]*$/.test(id)) {
      throw new Error("A listing did not include a valid artifact identity.");
    }
    if (id.split("/")[0].toUpperCase() !== OWNER || item.private === true) {
      throw new Error("A listing left the expected public organization scope.");
    }
    if (kind === "collections" && (!item.owner || typeof item.owner.name !== "string" || item.owner.name.toUpperCase() !== OWNER)) {
      throw new Error("A collection did not match the expected owner.");
    }
    return id;
  }

  async function catalog(spec, signal) {
    const items = [];
    const ids = new Set();
    const pages = new Set();
    let url = spec.url;
    try {
      while (url) {
        if (pages.size >= MAX_PAGES) throw new Error("The bounded page limit was reached.");
        if (pages.has(url)) throw new Error("The source repeated a pagination page.");
        const limits = new URL(url).searchParams.getAll("limit");
        const limit = spec.key === "buckets" ? null : Number(limits[0]);
        if (limit !== null && (limits.length !== 1 || !Number.isSafeInteger(limit) || limit < 1 || limit > 1000)) {
          throw new Error("The source changed the bounded catalog page size.");
        }
        pages.add(url);
        const response = await request(url, signal);
        const rows = await response.json();
        if (!Array.isArray(rows)) throw new Error("The source returned an unexpected catalog shape.");
        const pageIds = rows.map(item => identity(item, spec.key));
        if (new Set(pageIds).size !== pageIds.length || pageIds.some(id => ids.has(id))) {
          throw new Error("The source repeated a listing; a complete total is unavailable.");
        }
        rows.forEach((item, index) => { items.push(item); ids.add(pageIds[index]); });
        const next = nextPage(response.headers.get("Link"), url, spec.url);
        if (!next && limit !== null && rows.length >= limit) {
          throw new Error("A full page had no readable continuation metadata. Complete coverage could not be established.");
        }
        url = next;
      }
      return { items, complete: true, source: spec.url };
    } catch (error) {
      return { items, complete: false, source: spec.url, reason: reason(error) };
    }
  }

  async function github(signal) {
    try {
      const response = await request(GH_SOURCE, signal);
      const org = await response.json();
      if (!org || !Number.isSafeInteger(org.public_repos) || org.public_repos < 0) {
        throw new Error("The source did not return a valid public repository count.");
      }
      return { count: org.public_repos, complete: true };
    } catch (error) {
      return { complete: false, reason: reason(error) };
    }
  }

  function renderCatalog(key, result) {
    if (result.complete) {
      setFact("hf_" + key, number.format(result.items.length), "MEASURED", "Complete anonymous catalog observation.", result.source);
    } else if (result.items.length) {
      setFact("hf_" + key, "≥ " + number.format(result.items.length), "PARTIAL", result.reason, result.source);
    } else {
      setFact("hf_" + key, "UNAVAILABLE", "UNAVAILABLE", result.reason, result.source);
    }
  }

  function renderDownloads(models, datasets) {
    const records = [
      ...models.items.map(item => ({ item, kind: "model" })),
      ...datasets.items.map(item => ({ item, kind: "dataset" })),
    ];
    const fieldsValid = records.every(({ item }) => Number.isSafeInteger(item.downloads) && item.downloads >= 0);
    const total = fieldsValid ? records.reduce((sum, { item }) => sum + item.downloads, 0) : NaN;
    if (!models.complete || !datasets.complete || !fieldsValid || !Number.isSafeInteger(total)) {
      const note = "A complete model and dataset catalog with valid download fields is required. Missing values are not treated as zero.";
      setFact("downloads", "UNAVAILABLE", "UNAVAILABLE", note, HF + "/" + OWNER);
      setFact("crown", "UNAVAILABLE", "UNAVAILABLE", note, HF + "/" + OWNER);
      return;
    }
    setFact("downloads", number.format(total), "MEASURED", "Sum of the model and dataset download fields returned by the APIs; their reporting windows apply.", HF + "/" + OWNER);
    const ranked = records.sort((a, b) => b.item.downloads - a.item.downloads || a.item.id.localeCompare(b.item.id) || a.kind.localeCompare(b.kind));
    if (!ranked.length) {
      setFact("crown", "No listed artifact", "MEASURED", "Both complete catalogs were empty.", HF + "/" + OWNER);
      return;
    }
    const winner = ranked[0];
    const prefix = winner.kind === "dataset" ? "/datasets/" : "/";
    const source = HF + prefix + winner.item.id.split("/").map(encodeURIComponent).join("/");
    setFact("crown", winner.item.id, "MEASURED", number.format(winner.item.downloads) + " reported downloads · " + winner.kind + ". Ties use artifact identity.", source);
  }

  async function observe() {
    if (busy) return;
    busy = true;
    refresh.disabled = true;
    facts.setAttribute("aria-busy", "true");
    status.textContent = "Reading the public catalogs. Existing values keep their previous observation time while the refresh runs.";
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
    try {
      const [org, catalogs] = await Promise.all([
        github(controller.signal),
        Promise.all(CATALOGS.map(spec => catalog(spec, controller.signal))),
      ]);
      if (org.complete) {
        setFact("gh_repos", number.format(org.count), "MEASURED", "Public repository count returned by GitHub.", GH_SOURCE);
      } else {
        setFact("gh_repos", "UNAVAILABLE", "UNAVAILABLE", org.reason, GH_SOURCE);
      }
      catalogs.forEach((result, index) => renderCatalog(CATALOGS[index].key, result));
      renderDownloads(catalogs[0], catalogs[1]);
      const at = new Date().toISOString();
      const time = document.createElement("time");
      time.dateTime = at;
      time.textContent = at;
      document.getElementById("measured-at").replaceChildren(document.createTextNode("Observed: "), time, document.createTextNode(" · anonymous public catalog requests"));
      const incomplete = !org.complete || catalogs.some(result => !result.complete);
      const unavailable = [...facts.querySelectorAll(".chip")].some(chip => chip.textContent === "UNAVAILABLE");
      status.textContent = incomplete || unavailable
        ? "Some observations are partial or unavailable. Each metric records its own coverage and source."
        : "Observation complete. Each metric links to its source; public listings do not establish runtime readiness.";
    } finally {
      clearTimeout(timer);
      busy = false;
      refresh.disabled = false;
      facts.setAttribute("aria-busy", "false");
    }
  }

  async function publication() {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
    try {
      const response = await request("PUBLICATION_RECEIPT.json", controller.signal);
      const receipt = await response.json();
      const sha = receipt && receipt.source && receipt.source.sha;
      const root = receipt && receipt.root_sha256;
      if (!receipt || receipt.schema !== "szl.marketing-space-publication/v1"
        || receipt.state !== "PACKAGE_BUILT_NOT_PUBLISHED"
        || !receipt.source
        || receipt.source.repository !== "szl-holdings/szl-brand"
        || receipt.source.directory !== "marketing/space/szl-brand-campaign"
        || !receipt.target || receipt.target.repository !== "SZLHOLDINGS/szl-brand-campaign"
        || receipt.target.repo_type !== "space"
        || !/^[0-9a-f]{40}$/.test(sha || "") || !/^[0-9a-f]{64}$/.test(root || "")) {
        throw new Error("Invalid publication record.");
      }
      const link = document.createElement("a");
      link.href = "https://github.com/szl-holdings/szl-brand/tree/" + sha;
      link.textContent = "szl-brand@" + sha.slice(0, 12);
      document.getElementById("source-sha").replaceChildren(link, document.createTextNode(" · package " + root.slice(0, 12)));
    } catch (_error) {
      document.getElementById("source-sha").textContent = "Publication record UNAVAILABLE. Source: szl-holdings/szl-brand.";
    } finally {
      clearTimeout(timer);
    }
  }

  refresh.addEventListener("click", observe);
  observe();
  publication();
})();
