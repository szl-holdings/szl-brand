// KANCHAY example components (React + TSX). Apache-2.0 · ORCID 0009-0001-0110-4173
// Consumes canonical tokens via CSS custom properties (import the token CSS once at app root):
//   import "../../tokens/COLOR_TOKENS.css";
//   import "../../tokens/COMPONENT_TOKENS.css";
import React from "react";

type Variant = "primary" | "accent" | "danger";
const BTN_BG: Record<Variant, string> = {
  primary: "var(--color-yuyay-600)",
  accent: "var(--color-hatun-400)",
  danger: "var(--color-yawar-600)",
};
const BTN_FG: Record<Variant, string> = {
  primary: "#fff",
  accent: "var(--color-gray-950)",
  danger: "#fff",
};

export function Button({
  variant = "primary",
  children,
  ...rest
}: { variant?: Variant } & React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      {...rest}
      style={{
        font: "inherit",
        fontWeight: 600,
        cursor: "pointer",
        border: "none",
        padding: "var(--space-2) var(--space-5)",
        borderRadius: "var(--radius-md)",
        background: BTN_BG[variant],
        color: BTN_FG[variant],
        transition: "background var(--duration-fast) var(--ease-standard)",
      }}
    >
      {children}
    </button>
  );
}

export function Card({ title, hash, children }: { title: string; hash?: string; children: React.ReactNode }) {
  return (
    <div
      style={{
        background: "var(--color-a11oy-surface)",
        border: "1px solid var(--color-a11oy-border)",
        borderRadius: "var(--radius-lg)",
        padding: "var(--space-6)",
        maxWidth: 380,
        boxShadow: "var(--shadow-md)",
        color: "var(--color-a11oy-text)",
        fontFamily: '"Inter", system-ui, sans-serif',
      }}
    >
      <h3 style={{ margin: "0 0 var(--space-2)", fontFamily: '"IBM Plex Sans", sans-serif' }}>{title}</h3>
      <div>{children}</div>
      {hash && (
        <div style={{ fontFamily: '"JetBrains Mono", monospace', color: "var(--color-yuyay-300)", fontSize: ".875rem" }}>
          {hash}
        </div>
      )}
    </div>
  );
}

type AlertKind = "success" | "warning" | "error";
const ALERT_BORDER: Record<AlertKind, string> = {
  success: "var(--color-success)",
  warning: "var(--color-warning)",
  error: "var(--color-error)",
};
const ALERT_FG: Record<AlertKind, string> = {
  success: "#3fce82",
  warning: "var(--color-hatun-200)",
  error: "var(--color-yawar-200)",
};

export function Alert({ kind, children }: { kind: AlertKind; children: React.ReactNode }) {
  return (
    <div
      role="alert"
      style={{
        display: "flex",
        gap: "var(--space-3)",
        padding: "var(--space-4)",
        borderRadius: "var(--radius-md)",
        border: `1px solid ${ALERT_BORDER[kind]}`,
        background: `color-mix(in srgb, ${ALERT_BORDER[kind]} 12%, transparent)`,
        color: ALERT_FG[kind],
      }}
    >
      {children}
    </div>
  );
}

// Demo
export default function Demo() {
  return (
    <div style={{ background: "var(--color-a11oy-bg)", padding: "var(--space-12)", minHeight: "100vh" }}>
      <Button variant="primary">Verify receipt</Button>{" "}
      <Button variant="accent">View khipu chain</Button>{" "}
      <Button variant="danger">Halt (T10)</Button>
      <div style={{ marginTop: "var(--space-8)" }}>
        <Card title="Receipt verified" hash="root 3f9a8c2e…b71d">
          Chain extends append-only ledger. Signature: <strong>DSSE PLACEHOLDER</strong>.
        </Card>
      </div>
      <div style={{ marginTop: "var(--space-8)", display: "grid", gap: "var(--space-3)", maxWidth: 520 }}>
        <Alert kind="success">Yuyay gate cleared — all 13 axes above floor.</Alert>
        <Alert kind="warning">Λ-uniqueness is Conjecture 1 (open), not proven.</Alert>
        <Alert kind="error">Action halted: tripwire T01 fired. No receipt written.</Alert>
      </div>
    </div>
  );
}
