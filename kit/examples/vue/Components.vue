<!-- KANCHAY example components (Vue 3 SFC). Apache-2.0 · ORCID 0009-0001-0110-4173
     Import the token CSS once at app root:
       import "../../tokens/COLOR_TOKENS.css";
       import "../../tokens/COMPONENT_TOKENS.css"; -->
<template>
  <div class="kanchay-demo">
    <div class="stack">
      <button class="btn btn-primary">Verify receipt</button>
      <button class="btn btn-accent">View khipu chain</button>
      <button class="btn btn-danger">Halt (T10)</button>
    </div>

    <div class="card">
      <h3>Receipt verified</h3>
      <p>Chain extends append-only ledger. Signature: <strong>DSSE PLACEHOLDER</strong>.</p>
      <div class="hash">root 3f9a8c2e…b71d</div>
    </div>

    <div class="alerts">
      <div class="alert alert-success" role="alert">Yuyay gate cleared — all 13 axes above floor.</div>
      <div class="alert alert-warning" role="alert">Λ-uniqueness is Conjecture 1 (open), not proven.</div>
      <div class="alert alert-error" role="alert">Action halted: tripwire T01 fired. No receipt written.</div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Stateless presentational components; tokens come from imported CSS custom properties.
</script>

<style scoped>
.kanchay-demo{
  background:var(--color-a11oy-bg); color:var(--color-a11oy-text);
  font-family:"Inter",system-ui,sans-serif; padding:var(--space-12); min-height:100vh;
}
.stack{display:flex; gap:var(--space-3); flex-wrap:wrap; margin-bottom:var(--space-8)}
.btn{font:inherit; font-weight:600; cursor:pointer; border:none;
  padding:var(--space-2) var(--space-5); border-radius:var(--radius-md);
  transition:background var(--duration-fast) var(--ease-standard);}
.btn:focus-visible{outline:none; box-shadow:var(--shadow-focus)}
.btn-primary{background:var(--color-yuyay-600); color:#fff}
.btn-accent{background:var(--color-hatun-400); color:var(--color-gray-950)}
.btn-danger{background:var(--color-yawar-600); color:#fff}
.card{background:var(--color-a11oy-surface); border:1px solid var(--color-a11oy-border);
  border-radius:var(--radius-lg); padding:var(--space-6); max-width:380px;
  box-shadow:var(--shadow-md); margin-bottom:var(--space-8)}
.card h3{margin:0 0 var(--space-2); font-family:"IBM Plex Sans",sans-serif}
.hash{font-family:"JetBrains Mono",monospace; color:var(--color-yuyay-300); font-size:.875rem}
.alerts{display:grid; gap:var(--space-3); max-width:520px}
.alert{padding:var(--space-4); border-radius:var(--radius-md); border:1px solid}
.alert-success{background:color-mix(in srgb,var(--color-success) 12%,transparent);
  border-color:var(--color-success); color:#3fce82}
.alert-warning{background:color-mix(in srgb,var(--color-warning) 12%,transparent);
  border-color:var(--color-warning); color:var(--color-hatun-200)}
.alert-error{background:color-mix(in srgb,var(--color-error) 12%,transparent);
  border-color:var(--color-error); color:var(--color-yawar-200)}
</style>
