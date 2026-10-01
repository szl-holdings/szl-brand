/* Live, labeled facts for the campaign hub. Anonymous public API calls from the visitor's
 * browser; a source that fails is labeled UNAVAILABLE. No number is typed into the page. */
(function () {
  "use strict";
  var AUTHOR = "SZLHOLDINGS";
  var ORG = "szl-holdings";

  function row(name) {
    return document.querySelector('tr[data-fact="' + name + '"]');
  }
  function setFact(name, value, label) {
    var tr = row(name);
    if (!tr) return;
    tr.children[1].textContent = value;
    var chip = tr.children[2].firstElementChild;
    chip.textContent = label;
    chip.className = "chip " + (label === "MEASURED" ? "chip-live" : "chip-unavailable");
  }
  function unavailable(name) {
    setFact(name, "UNAVAILABLE", "UNAVAILABLE");
  }
  function num(n) {
    return Number(n).toLocaleString("en-US");
  }
  function getJSON(url) {
    return fetch(url, { headers: { Accept: "application/json" } }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    });
  }
  function downloads(x) {
    var d = x && x.downloads;
    return typeof d === "number" && d > 0 ? d : 0;
  }

  getJSON("https://api.github.com/orgs/" + ORG)
    .then(function (org) {
      if (typeof org.public_repos !== "number") throw new Error("shape");
      setFact("gh_repos", num(org.public_repos), "MEASURED");
    })
    .catch(function () { unavailable("gh_repos"); });

  var kinds = ["models", "datasets", "spaces"];
  Promise.all(
    kinds.map(function (kind) {
      return getJSON("https://huggingface.co/api/" + kind + "?author=" + AUTHOR + "&limit=1000")
        .then(function (rows) { return Array.isArray(rows) ? rows : null; })
        .catch(function () { return null; });
    })
  ).then(function (results) {
    var models = results[0], datasets = results[1], spaces = results[2];
    if (models) setFact("hf_models", num(models.length), "MEASURED"); else unavailable("hf_models");
    if (datasets) setFact("hf_datasets", num(datasets.length), "MEASURED"); else unavailable("hf_datasets");
    if (spaces) setFact("hf_spaces", num(spaces.length), "MEASURED"); else unavailable("hf_spaces");
    if (models && datasets) {
      var swept = models.concat(datasets);
      var total = 0, crown = null;
      swept.forEach(function (x) {
        var d = downloads(x);
        total += d;
        if (!crown || d > downloads(crown)) crown = x;
      });
      setFact("downloads", num(total), "MEASURED");
      if (crown) setFact("crown", crown.id + " (" + num(downloads(crown)) + ")", "MEASURED");
      else unavailable("crown");
    } else {
      unavailable("downloads");
      unavailable("crown");
    }
    var at = document.getElementById("measured-at");
    if (at) at.textContent = "Measured: " + new Date().toISOString() + " · anonymous public API pulls from this browser";
  });

  fetch("PUBLICATION_RECEIPT.json")
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (receipt) {
      var el = document.getElementById("source-sha");
      if (el && receipt && receipt.source && receipt.source.sha) {
        el.textContent = "source: szl-brand@" + receipt.source.sha.slice(0, 12) + " · root " + String(receipt.root_sha256 || "").slice(0, 12);
      }
    })
    .catch(function () {});
})();
