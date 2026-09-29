/* @ds-bundle: {"format":4,"namespace":"Kanchay","components":[{"name":"Button"},{"name":"Input"},{"name":"Select"},{"name":"Badge"},{"name":"SeverityChip"},{"name":"GovernanceDot"},{"name":"StatusDot"},{"name":"FabricStat"},{"name":"MicroBar"},{"name":"Sparkline"},{"name":"HeatCell"},{"name":"OutputPanel"},{"name":"FabricHeader"},{"name":"FabricCard"},{"name":"Card"},{"name":"FabricToolbar"},{"name":"FabricDrawer"},{"name":"Skeleton"},{"name":"SidebarNav"},{"name":"SiteHeader"},{"name":"Eyebrow"},{"name":"SzlMark"}]} */
/* SZL Kanchay components. Hand-written from a11oy/organs/amaru/web/src and a11oy/landing/style.css;
   styled only by components/bundle.css on KANCHAY tokens. Reads window.React; assigns window.Kanchay. */
(function () {
  "use strict";
  var React = window.React;
  var h = React.createElement;

  function cx() {
    var out = [];
    for (var i = 0; i < arguments.length; i++) if (arguments[i]) out.push(arguments[i]);
    return out.join(" ");
  }

  var TONE_TEXT = {
    neutral: null,
    gold: "var(--color-a11oy-gold)",
    good: "var(--color-success)",
    warn: "var(--color-ink-caution)",
    bad: "var(--color-ink-danger)"
  };
  var TONE_MARK = {
    gold: "var(--color-a11oy-gold)",
    good: "var(--color-success)",
    warn: "var(--color-ink-caution)",
    bad: "var(--color-error)"
  };
  function toneStyle(map, tone, style) {
    var v = map[tone];
    return v ? Object.assign({ "--kc-tone": v }, style) : style;
  }

  /* ---------- Actions ---------- */
  var Button = React.forwardRef(function Button(props, ref) {
    var variant = props.variant || "default";
    var size = props.size || "default";
    var isLoading = !!props.isLoading;
    var rest = Object.assign({}, props);
    delete rest.variant; delete rest.size; delete rest.isLoading; delete rest.className; delete rest.children;
    var className = cx("kc-btn", "kc-btn--" + variant, size !== "default" && "kc-btn--" + size, props.className);
    var spinner = isLoading ? h("span", { className: "kc-spinner", "aria-hidden": "true" }) : null;
    if (props.href) {
      delete rest.disabled;
      return h("a", Object.assign(rest, { ref: ref, className: className, "aria-disabled": props.disabled || isLoading || undefined }), spinner, props.children);
    }
    return h("button", Object.assign({ type: "button" }, rest, {
      ref: ref, className: className, disabled: props.disabled || isLoading, "aria-busy": isLoading || undefined
    }), spinner, props.children);
  });
  Button.displayName = "Button";

  /* ---------- Forms ---------- */
  var Input = React.forwardRef(function Input(props, ref) {
    return h("input", Object.assign({}, props, { ref: ref, className: cx("kc-input", props.className) }));
  });
  Input.displayName = "Input";

  var Select = React.forwardRef(function Select(props, ref) {
    return h("select", Object.assign({}, props, { ref: ref, className: cx("kc-select", props.className) }));
  });
  Select.displayName = "Select";

  /* ---------- Status ---------- */
  function Badge(props) {
    var variant = props.variant || "default";
    var rest = Object.assign({}, props);
    delete rest.variant; delete rest.className; delete rest.children;
    return h("span", Object.assign(rest, { className: cx("kc-badge", "kc-badge--" + variant, props.className) }),
      h("span", { className: "kc-badge-dot", "aria-hidden": "true" }), props.children);
  }

  var SEVERITY_LABEL = { critical: "CRITICAL", high: "HIGH", medium: "MED", low: "LOW", info: "INFO" };
  function SeverityChip(props) {
    var level = props.level || "info";
    return h("span", { className: cx("kc-sev", "kc-sev--" + level, props.className) }, props.children || SEVERITY_LABEL[level]);
  }

  function GovernanceDot(props) {
    var state = props.state || "green";
    var label = props.label || state;
    return h("span", { className: cx("kc-gdot", "kc-gdot--" + state, props.className), role: "img", "aria-label": label, title: label });
  }

  function StatusDot(props) {
    var status = props.status || "idle";
    var label = props.label || status;
    return h("span", {
      className: cx("kc-sdot", "kc-sdot--" + status, props.pulse && "kc-sdot--pulse", props.className),
      role: "img", "aria-label": label, title: label
    });
  }

  /* ---------- Data ---------- */
  function FabricStat(props) {
    var tone = props.tone || "neutral";
    return h("div", { className: cx("kc-stat", props.className) },
      h("div", { className: "kc-label" }, props.label),
      h("div", { className: "kc-stat-value", style: toneStyle(TONE_TEXT, tone) }, props.value),
      props.sub ? h("div", { className: "kc-stat-sub" }, props.sub) : null);
  }

  function MicroBar(props) {
    var max = Math.max(1, props.max == null ? 100 : props.max);
    var value = props.value || 0;
    var pct = Math.max(0, Math.min(100, (value / max) * 100));
    return h("div", {
      className: cx("kc-microbar", props.className), role: "meter",
      "aria-valuemin": 0, "aria-valuemax": max, "aria-valuenow": value, "aria-label": props.label
    }, h("div", { className: "kc-microbar-fill", style: toneStyle(TONE_MARK, props.tone || "gold", { width: pct + "%" }) }));
  }

  function Sparkline(props) {
    var values = props.values || [];
    var width = props.width || 120;
    var height = props.height || 28;
    var style = toneStyle(TONE_MARK, props.tone || "gold");
    if (!values.length) return h("svg", { className: "kc-spark", width: width, height: height, style: style, "aria-hidden": "true" });
    var min = Math.min.apply(null, values);
    var max = Math.max.apply(null, values);
    var range = max - min || 1;
    var stepX = width / Math.max(1, values.length - 1);
    var d = values.map(function (v, i) {
      var x = i * stepX;
      var y = height - ((v - min) / range) * height;
      return (i === 0 ? "M" : "L") + x.toFixed(1) + "," + y.toFixed(1);
    }).join(" ");
    return h("svg", {
      className: cx("kc-spark", props.className), width: width, height: height, viewBox: "0 0 " + width + " " + height,
      style: style, role: props.label ? "img" : undefined, "aria-label": props.label, "aria-hidden": props.label ? undefined : "true"
    }, h("path", { d: d }));
  }

  function HeatCell(props) {
    var value = props.value || 0;
    var intensity = Math.max(0, Math.min(1, value / Math.max(1, props.max == null ? 1 : props.max)));
    var pct = Math.round((0.08 + intensity * 0.5) * 100);
    return h("div", {
      className: cx("kc-heat", props.className), title: String(value),
      style: { background: "color-mix(in srgb, var(--color-error) " + pct + "%, transparent)" }
    }, value > 0 ? value : "");
  }

  function OutputPanel(props) {
    var status = props.status || "idle";
    return h("div", { className: cx("kc-output", props.className) },
      h("div", { className: "kc-output-label" },
        h("span", null, props.label || "Output"),
        h("span", { className: "kc-output-status" },
          h(StatusDot, { status: status, label: props.statusLabel || status }),
          props.statusLabel || status)),
      h("pre", { className: "kc-output-pre", tabIndex: 0 }, props.children));
  }

  /* ---------- Layout ---------- */
  function FabricHeader(props) {
    return h("div", { className: cx("kc-fheader", props.className) },
      h("div", null,
        props.eyebrow ? h("div", { className: "kc-fheader-eyebrow" }, props.eyebrow) : null,
        h("h1", { className: "kc-fheader-title" }, props.title),
        props.blurb ? h("p", { className: "kc-fheader-blurb" }, props.blurb) : null),
      props.trailing || null);
  }

  function FabricCard(props) {
    var hasHead = props.title || props.trailing;
    return h("div", { className: cx("kc-fcard", props.className) },
      hasHead ? h("div", { className: "kc-fcard-head" },
        props.title ? h("div", { className: "kc-label" }, props.title) : h("span"),
        props.trailing || null) : null,
      props.children);
  }

  function part(tag, cls) {
    return function (props) {
      return h(tag, Object.assign({}, props, { className: cx(cls, props.className) }));
    };
  }
  var Card = part("div", "kc-card");
  var CardHeader = part("div", "kc-card-header");
  var CardTitle = part("h3", "kc-card-title");
  var CardContent = part("div", "kc-card-content");

  function FabricToolbar(props) {
    return h("div", { className: cx("kc-toolbar", props.className), role: "toolbar", "aria-label": props.label }, props.children);
  }

  function FabricDrawer(props) {
    var closeRef = React.useRef(null);
    var onCloseRef = React.useRef(props.onClose);
    onCloseRef.current = props.onClose;
    var onClose = function () { if (onCloseRef.current) onCloseRef.current(); };
    React.useEffect(function () {
      if (!props.open) return undefined;
      if (closeRef.current) closeRef.current.focus();
      function onKey(e) { if (e.key === "Escape") onClose(); }
      document.addEventListener("keydown", onKey);
      return function () { document.removeEventListener("keydown", onKey); };
    }, [props.open]);
    if (!props.open) return null;
    return h("div", { className: "kc-drawer", role: "dialog", "aria-modal": "true", "aria-label": props.title },
      h("button", { className: "kc-drawer-scrim", onClick: onClose, "aria-label": "Close", tabIndex: -1 }),
      h("aside", { className: cx("kc-drawer-panel", props.className) },
        h("div", { className: "kc-drawer-head" },
          h("div", null,
            h("div", { className: "kc-label" }, props.kicker || "Detail"),
            h("h3", { className: "kc-drawer-title" }, props.title),
            props.subtitle ? h("div", { className: "kc-drawer-sub" }, props.subtitle) : null),
          h("button", { ref: closeRef, className: "kc-drawer-close", onClick: onClose, "aria-label": "Close" }, "✕")),
        h("div", { className: "kc-drawer-body" }, props.children)));
  }

  function Skeleton(props) {
    var style = Object.assign({}, props.style);
    if (props.width != null) style.width = props.width;
    if (props.height != null) style.height = props.height;
    return h("div", { className: cx("kc-skeleton", props.className), style: style, "aria-hidden": "true" });
  }

  /* ---------- Navigation ---------- */
  function MenuGlyph() {
    return h("svg", { width: 16, height: 16, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 2, strokeLinecap: "round", strokeLinejoin: "round", "aria-hidden": "true" },
      h("line", { x1: 4, x2: 20, y1: 12, y2: 12 }), h("line", { x1: 4, x2: 20, y1: 6, y2: 6 }), h("line", { x1: 4, x2: 20, y1: 18, y2: 18 }));
  }

  function SidebarNav(props) {
    var controlled = typeof props.collapsed === "boolean";
    var st = React.useState(!!props.defaultCollapsed);
    var collapsed = controlled ? props.collapsed : st[0];
    function toggle() {
      if (!controlled) st[1](!collapsed);
      if (props.onToggle) props.onToggle(!collapsed);
    }
    var brand = props.brand || { name: "Amaru", letter: "A", href: "/" };
    var sections = props.sections || [];
    var nav = [];
    sections.forEach(function (section, si) {
      if (si > 0) nav.push(h("div", { key: "d" + si, className: "kc-nav-divider", role: "presentation" }));
      if (!collapsed && section.label) nav.push(h("p", { key: "l" + si, className: "kc-nav-section" }, section.label));
      (section.items || []).forEach(function (item, ii) {
        var ext = item.external ? { target: "_blank", rel: "noopener noreferrer" } : {};
        nav.push(h("a", Object.assign({
          key: si + "-" + ii, href: item.href || "#", className: "kc-nav-link",
          "aria-current": item.active ? "page" : undefined,
          "aria-label": collapsed ? item.name : undefined,
          title: collapsed ? item.name : undefined
        }, ext),
          item.icon ? h("span", { className: "kc-nav-icon", "aria-hidden": "true" }, item.icon) : null,
          collapsed ? null : h("span", null, item.name)));
      });
    });
    return h("aside", { className: cx("kc-sidebar", collapsed && "kc-sidebar--collapsed", props.className) },
      h("div", { className: "kc-sidebar-head" },
        collapsed ? null : h("a", { href: brand.href || "/", className: "kc-sidebar-brand" },
          h("span", { className: "kc-sidebar-tile", "aria-hidden": "true" }, brand.letter || (brand.name || "?").charAt(0)),
          h("span", null, brand.name)),
        h("button", {
          type: "button", className: "kc-nav-toggle", onClick: toggle,
          "aria-label": collapsed ? "Expand sidebar" : "Collapse sidebar", "aria-expanded": !collapsed
        }, h(MenuGlyph))),
      h("nav", { className: "kc-nav", "aria-label": props.label || "Main navigation" }, nav));
  }

  function SzlMark(props) {
    var size = props.size || 32;
    var title = props.title == null ? "SZL Holdings" : props.title;
    return h("svg", {
      className: cx("kc-mark", props.className), width: size, height: size, viewBox: "0 0 32 32", fill: "none",
      role: title ? "img" : undefined, "aria-label": title || undefined, "aria-hidden": title ? undefined : "true", style: props.style
    },
      h("rect", { x: 1, y: 1, width: 30, height: 30, rx: 7, fill: "none", stroke: "currentColor", strokeWidth: 1.6 }),
      h("path", { d: "M9 9 L23 9 L9 23 L23 23", stroke: "currentColor", strokeWidth: 2.2, strokeLinejoin: "round", strokeLinecap: "round", fill: "none" }),
      h("circle", { cx: 9, cy: 9, r: 2.1, fill: "currentColor" }),
      h("circle", { cx: 23, cy: 23, r: 2.1, fill: "currentColor" }));
  }

  function SiteHeader(props) {
    var cta = props.cta;
    return h("header", { className: cx("kc-site-header", props.className) },
      h("div", { className: "kc-site-inner" },
        h("a", { href: props.href || "/", className: "kc-site-brand" },
          props.mark === false ? null : (props.mark || h(SzlMark, { size: 20, title: "" })),
          h("span", { className: "kc-site-name" }, props.name || "SZL Holdings"),
          props.tag ? h("span", { className: "kc-site-tag" }, props.tag) : null),
        cta ? h("a", { href: cta.href || "#", className: "kc-cta" }, cta.label, h("span", { "aria-hidden": "true" }, "→")) : null));
  }

  function Eyebrow(props) {
    return h("span", { className: cx("kc-eyebrow", props.className) },
      props.dot === false ? null : h("span", { className: "kc-eyebrow-dot", "aria-hidden": "true" }),
      h("span", { className: "kc-eyebrow-text" }, props.children));
  }

  window.Kanchay = {
    Button: Button, Input: Input, Select: Select,
    Badge: Badge, SeverityChip: SeverityChip, GovernanceDot: GovernanceDot, StatusDot: StatusDot,
    FabricStat: FabricStat, MicroBar: MicroBar, Sparkline: Sparkline, HeatCell: HeatCell, OutputPanel: OutputPanel,
    FabricHeader: FabricHeader, FabricCard: FabricCard,
    Card: Card, CardHeader: CardHeader, CardTitle: CardTitle, CardContent: CardContent,
    FabricToolbar: FabricToolbar, FabricDrawer: FabricDrawer, Skeleton: Skeleton,
    SidebarNav: SidebarNav, SiteHeader: SiteHeader, Eyebrow: Eyebrow, SzlMark: SzlMark
  };
})();
