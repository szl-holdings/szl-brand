/*
 * szl-hololattice — SZL Holdings signature 3D holographic substrate
 * ----------------------------------------------------------------
 * One reusable module dropped into every SZL Space. The hologram is
 * NOT decoration: its geometry is bound to REAL measured counts
 * (locked formulas, tests, Lean decls, measured joules). Lambda is
 * ADVISORY — green when within bounds, amber when advisory-flagged.
 * Honest BLOCKED renders as a literal broken lattice. Never faked green.
 *
 * Doctrine: no fabricated number. MEASURED-only. Lambda = Conjecture 1 (advisory).
 *
 * Tech: frontier WebGPU + TSL GPGPU khipu compute-particle field with
 * automatic, silent fallback to the original WebGL2 ShaderMaterial path.
 * ---------------------------------------------------------------------------
 * IMPORTMAP (Three.js r0.183.0): map three, three/webgpu, three/tsl, three/addons/
 * ---------------------------------------------------------------------------
 */

import * as THREE from 'three';

const ACCENTS = {
  green:    { core: 0x36e6d0, rim: 0x6cf2ff, glow: 0x0a2a2e },
  advisory: { core: 0xf4b13e, rim: 0xffd27a, glow: 0x2e220a },
  blocked:  { core: 0xff4d5e, rim: 0xff8a96, glow: 0x2e0a0e },
};

function scatterFor(state) {
  return state === 'blocked' ? 1.0 : (state === 'advisory' ? 0.35 : 0.0);
}

function clampNodes(nodes) {
  return Math.max(64, Math.min(nodes | 0, 60000));
}

function cordsFor(n) {
  return Math.max(3, Math.round(Math.sqrt(n) / 2));
}

function buildKhipuArrays(n) {
  const cords = cordsFor(n);
  const pos = new Float32Array(n * 3);
  const seed = new Float32Array(n);
  const cord = new Float32Array(n);
  const rowCount = Math.ceil(n / cords);
  for (let i = 0; i < n; i++) {
    const c = i % cords;
    const along = Math.floor(i / cords) / rowCount;
    const ang = (c / cords) * Math.PI * 2.0;
    const radius = 2.2 + Math.sin(along * Math.PI) * 0.6;
    pos[i * 3 + 0] = Math.cos(ang) * radius;
    pos[i * 3 + 1] = (along - 0.5) * 5.0;
    pos[i * 3 + 2] = Math.sin(ang) * radius;
    seed[i] = Math.random();
    cord[i] = c;
  }
  return { pos, seed, cord, cords };
}

const VERT = `
  uniform float uTime;
  uniform float uScatter;
  uniform float uPixelRatio;
  attribute float aSeed;
  attribute float aCord;
  varying float vSeed;
  varying float vDepth;
  void main() {
    vSeed = aSeed;
    vec3 p = position;
    float ph = uTime * 0.25 + aCord * 1.7;
    p.x += sin(ph + aSeed * 6.2831) * (0.08 + uScatter * 0.9);
    p.y += cos(ph * 0.8 + aSeed * 3.14) * (0.06 + uScatter * 0.7);
    p.z += sin(ph * 0.5 + aCord) * (0.05 + uScatter * 0.8);
    vec4 mv = modelViewMatrix * vec4(p, 1.0);
    vDepth = -mv.z;
    gl_Position = projectionMatrix * mv;
    gl_PointSize = (2.2 + aSeed * 3.0) * uPixelRatio * (8.0 / max(vDepth, 0.5));
  }
`;

const FRAG = `
  precision highp float;
  uniform vec3 uCore;
  uniform vec3 uRim;
  uniform float uTime;
  varying float vSeed;
  varying float vDepth;
  void main() {
    vec2 uv = gl_PointCoord - 0.5;
    float d = length(uv);
    if (d > 0.5) discard;
    float fres = smoothstep(0.5, 0.18, d);
    float core = smoothstep(0.32, 0.0, d);
    float scan = 0.82 + 0.18 * sin(vDepth * 30.0 + uTime * 4.0 + vSeed * 20.0);
    vec3 col = mix(uRim, uCore, core) * scan;
    float alpha = (fres * 0.55 + core) * (0.85 - vDepth * 0.015);
    gl_FragColor = vec4(col, clamp(alpha, 0.0, 1.0));
  }
`;

function buildPointsGeometryWebGL(nodes, scatter) {
  const n = clampNodes(nodes);
  const { pos, seed, cord } = buildKhipuArrays(n);
  for (let i = 0; i < n; i++) {
    pos[i * 3 + 0] += (Math.random() - 0.5) * scatter;
    pos[i * 3 + 1] += (Math.random() - 0.5) * scatter;
    pos[i * 3 + 2] += (Math.random() - 0.5) * scatter;
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('aSeed', new THREE.BufferAttribute(seed, 1));
  geo.setAttribute('aCord', new THREE.BufferAttribute(cord, 1));
  return geo;
}

function mountWebGL(container, cfg) {
  const palette = ACCENTS[cfg.state] || ACCENTS.green;
  const coreCol = new THREE.Color(cfg.accent != null ? cfg.accent : palette.core);
  const rimCol = new THREE.Color(palette.rim);
  let scatter = scatterFor(cfg.state);
  const w = container.clientWidth || window.innerWidth;
  const h = container.clientHeight || window.innerHeight;
  const pr = Math.min(window.devicePixelRatio || 1, 2);
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(pr);
  renderer.setSize(w, h);
  renderer.setClearColor(0x000000, 0);
  container.appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(palette.glow, 0.06);
  const camera = new THREE.PerspectiveCamera(50, w / h, 0.1, 100);
  camera.position.set(0, 0, 9);
  const haloMat = new THREE.SpriteMaterial({
    color: new THREE.Color(palette.glow).multiplyScalar(3.0),
    transparent: true, opacity: 0.5, blending: THREE.AdditiveBlending, depthWrite: false,
  });
  const halo = new THREE.Sprite(haloMat);
  halo.scale.set(14, 14, 1);
  scene.add(halo);
  let geo = buildPointsGeometryWebGL(cfg.nodes, scatter);
  const uniforms = {
    uTime: { value: 0 }, uScatter: { value: scatter }, uPixelRatio: { value: pr },
    uCore: { value: coreCol }, uRim: { value: rimCol },
  };
  const mat = new THREE.ShaderMaterial({
    uniforms, vertexShader: VERT, fragmentShader: FRAG,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  });
  const points = new THREE.Points(geo, mat);
  scene.add(points);
  let mx = 0, my = 0;
  function onMove(e) {
    const r = container.getBoundingClientRect();
    mx = ((e.clientX - r.left) / r.width - 0.5) * 2;
    my = ((e.clientY - r.top) / r.height - 0.5) * 2;
  }
  container.addEventListener('pointermove', onMove);
  const clock = new THREE.Clock();
  let raf = 0, running = true;
  const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function tick() {
    if (!running) return;
    raf = requestAnimationFrame(tick);
    const t = clock.getElapsedTime();
    uniforms.uTime.value = t;
    if (!prefersReduced) {
      points.rotation.y = t * 0.06 + mx * 0.25;
      points.rotation.x = my * 0.18;
      camera.position.x += (mx * 0.8 - camera.position.x) * 0.03;
      camera.position.y += (-my * 0.6 - camera.position.y) * 0.03;
      camera.lookAt(0, 0, 0);
    }
    renderer.render(scene, camera);
  }
  tick();
  function onResize() {
    const nw = container.clientWidth || window.innerWidth;
    const nh = container.clientHeight || window.innerHeight;
    camera.aspect = nw / nh; camera.updateProjectionMatrix();
    renderer.setSize(nw, nh);
  }
  window.addEventListener('resize', onResize);
  const io = new IntersectionObserver((entries) => {
    for (const en of entries) {
      if (en.isIntersecting && !running) { running = true; tick(); }
      else if (!en.isIntersecting) { running = false; cancelAnimationFrame(raf); }
    }
  }, { threshold: 0.01 });
  io.observe(container);
  return {
    backend: 'webgl2',
    setState(state) {
      const p = ACCENTS[state] || ACCENTS.green;
      uniforms.uCore.value.set(cfg.accent != null && state === 'green' ? cfg.accent : p.core);
      uniforms.uRim.value.set(p.rim);
      scatter = scatterFor(state);
      uniforms.uScatter.value = scatter;
      scene.fog.color.set(p.glow);
      const fresh = buildPointsGeometryWebGL(cfg.nodes, scatter);
      points.geometry = fresh; geo.dispose(); geo = fresh;
    },
    destroy() {
      running = false; cancelAnimationFrame(raf);
      window.removeEventListener('resize', onResize);
      container.removeEventListener('pointermove', onMove);
      io.disconnect();
      geo.dispose(); mat.dispose(); haloMat.dispose(); renderer.dispose();
      if (renderer.domElement.parentNode) renderer.domElement.parentNode.removeChild(renderer.domElement);
    },
  };
}

async function mountWebGPU(container, cfg, GPU, TSL) {
  const {
    Fn, instancedArray, instanceIndex, uniform, float, vec3, vec4, uv,
    sin, cos, length, mix, smoothstep, max, clamp, shapeCircle, color,
  } = TSL;
  const n = clampNodes(cfg.nodes);
  const cords = cordsFor(n);
  const rowCount = Math.ceil(n / cords);
  const { pos, seed, cord } = buildKhipuArrays(n);
  const palette = ACCENTS[cfg.state] || ACCENTS.green;
  const coreHex = cfg.accent != null ? cfg.accent : palette.core;
  const w = container.clientWidth || window.innerWidth;
  const h = container.clientHeight || window.innerHeight;
  const pr = Math.min(window.devicePixelRatio || 1, 2);
  const renderer = new GPU.WebGPURenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(pr);
  renderer.setSize(w, h);
  renderer.setClearColor(0x000000, 0);
  container.appendChild(renderer.domElement);
  const scene = new GPU.Scene();
  scene.fog = new THREE.FogExp2(palette.glow, 0.06);
  const camera = new THREE.PerspectiveCamera(50, w / h, 0.1, 100);
  camera.position.set(0, 0, 9);
  const haloMat = new THREE.SpriteMaterial({
    color: new THREE.Color(palette.glow).multiplyScalar(3.0),
    transparent: true, opacity: 0.5, blending: THREE.AdditiveBlending, depthWrite: false,
  });
  const halo = new THREE.Sprite(haloMat);
  halo.scale.set(14, 14, 1);
  scene.add(halo);
  const basePos = instancedArray(n, 'vec3');
  const livePos = instancedArray(n, 'vec3');
  const seeds   = instancedArray(n, 'vec3');
  const uTime = uniform(0.0);
  const uScatter = uniform(scatterFor(cfg.state));
  const uCore = uniform(color(coreHex));
  const uRim = uniform(color(palette.rim));
  const baseArr = basePos.value.array;
  const seedArr = seeds.value.array;
  const stride = baseArr.length / n;
  for (let i = 0; i < n; i++) {
    const o = i * stride;
    baseArr[o + 0] = pos[i * 3 + 0];
    baseArr[o + 1] = pos[i * 3 + 1];
    baseArr[o + 2] = pos[i * 3 + 2];
    seedArr[o + 0] = seed[i];
    seedArr[o + 1] = cord[i];
    seedArr[o + 2] = 0;
  }
  basePos.value.needsUpdate = true;
  seeds.value.needsUpdate = true;
  const computeInit = Fn(() => {
    const b = basePos.element(instanceIndex);
    livePos.element(instanceIndex).assign(b);
  })().compute(n);
  const computeUpdate = Fn(() => {
    const b = basePos.element(instanceIndex).toVar();
    const s = seeds.element(instanceIndex);
    const sd = s.x;
    const cd = s.y;
    const ph = uTime.mul(0.25).add(cd.mul(1.7));
    const amp = uScatter;
    const dx = sin(ph.add(sd.mul(6.2831))).mul(amp.mul(0.9).add(0.08));
    const dy = cos(ph.mul(0.8).add(sd.mul(3.14))).mul(amp.mul(0.7).add(0.06));
    const dz = sin(ph.mul(0.5).add(cd)).mul(amp.mul(0.8).add(0.05));
    const out = vec3(b.x.add(dx), b.y.add(dy), b.z.add(dz));
    livePos.element(instanceIndex).assign(out);
  })().compute(n);
  const material = new GPU.SpriteNodeMaterial();
  material.positionNode = livePos.toAttribute();
  const c = uv().sub(0.5);
  const d = length(c);
  const fres = smoothstep(0.5, 0.18, d);
  const coreM = smoothstep(0.32, 0.0, d);
  const colNode = mix(uRim, uCore, coreM);
  material.colorNode = colNode;
  material.opacityNode = clamp(fres.mul(0.55).add(coreM), 0.0, 1.0).mul(shapeCircle());
  material.scaleNode = float(0.12);
  material.transparent = true;
  material.depthWrite = false;
  material.blending = THREE.AdditiveBlending;
  material.alphaToCoverage = true;
  const particles = new GPU.Sprite(material);
  particles.count = n;
  particles.frustumCulled = false;
  scene.add(particles);
  let mx = 0, my = 0;
  function onMove(e) {
    const r = container.getBoundingClientRect();
    mx = ((e.clientX - r.left) / r.width - 0.5) * 2;
    my = ((e.clientY - r.top) / r.height - 0.5) * 2;
  }
  container.addEventListener('pointermove', onMove);
  const clock = new THREE.Clock();
  let raf = 0, running = true, ready = false;
  const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  await renderer.init();
  renderer.compute(computeInit);
  ready = true;
  function tick() {
    if (!running || !ready) return;
    raf = requestAnimationFrame(tick);
    const t = clock.getElapsedTime();
    uTime.value = t;
    renderer.compute(computeUpdate);
    if (!prefersReduced) {
      particles.rotation.y = t * 0.06 + mx * 0.25;
      particles.rotation.x = my * 0.18;
      camera.position.x += (mx * 0.8 - camera.position.x) * 0.03;
      camera.position.y += (-my * 0.6 - camera.position.y) * 0.03;
      camera.lookAt(0, 0, 0);
    }
    renderer.render(scene, camera);
  }
  tick();
  function onResize() {
    const nw = container.clientWidth || window.innerWidth;
    const nh = container.clientHeight || window.innerHeight;
    camera.aspect = nw / nh; camera.updateProjectionMatrix();
    renderer.setSize(nw, nh);
  }
  window.addEventListener('resize', onResize);
  const io = new IntersectionObserver((entries) => {
    for (const en of entries) {
      if (en.isIntersecting && !running) { running = true; tick(); }
      else if (!en.isIntersecting) { running = false; cancelAnimationFrame(raf); }
    }
  }, { threshold: 0.01 });
  io.observe(container);
  return {
    backend: 'webgpu',
    setState(state) {
      const p = ACCENTS[state] || ACCENTS.green;
      uCore.value.set(cfg.accent != null && state === 'green' ? cfg.accent : p.core);
      uRim.value.set(p.rim);
      uScatter.value = scatterFor(state);
      scene.fog.color.set(p.glow);
    },
    destroy() {
      running = false; cancelAnimationFrame(raf);
      window.removeEventListener('resize', onResize);
      container.removeEventListener('pointermove', onMove);
      io.disconnect();
      haloMat.dispose();
      if (material.dispose) material.dispose();
      if (renderer.dispose) renderer.dispose();
      if (renderer.domElement.parentNode) renderer.domElement.parentNode.removeChild(renderer.domElement);
    },
  };
}

function hasWebGPU() {
  return typeof navigator !== 'undefined' && !!navigator.gpu;
}

export function mountHololattice(container, opts = {}) {
  const cfg = { nodes: 749, accent: null, state: 'green', label: '', ...opts };
  if (!hasWebGPU()) {
    return mountWebGL(container, cfg);
  }
  let impl = null;
  let pendingState = null;
  let destroyed = false;
  (async () => {
    try {
      const [GPU, TSL] = await Promise.all([
        import('three/webgpu'),
        import('three/tsl'),
      ]);
      if (destroyed) return;
      if (navigator.gpu.requestAdapter) {
        const adapter = await navigator.gpu.requestAdapter();
        if (!adapter) throw new Error('no-webgpu-adapter');
      }
      if (destroyed) return;
      impl = await mountWebGPU(container, cfg, GPU, TSL);
    } catch (err) {
      if (destroyed) return;
      impl = mountWebGL(container, cfg);
    }
    if (destroyed && impl) { impl.destroy(); impl = null; return; }
    if (pendingState != null && impl) impl.setState(pendingState);
  })();
  return {
    get backend() { return impl ? impl.backend : 'webgpu-pending'; },
    setState(state) {
      if (impl) impl.setState(state);
      else pendingState = state;
    },
    destroy() {
      destroyed = true;
      if (impl) { impl.destroy(); impl = null; }
    },
  };
}
