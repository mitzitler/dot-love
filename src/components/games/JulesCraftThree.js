import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { PointerLockControls } from 'three/examples/jsm/controls/PointerLockControls.js';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { OutlinePass } from 'three/examples/jsm/postprocessing/OutlinePass.js';

// Format seconds to M:SS
function formatTime(sec) {
  const s = Math.max(0, Math.floor(sec || 0));
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${m}:${String(r).padStart(2, '0')}`;
}

// Simple seeded PRNG (Mulberry32)
function mulberry32(seed) {
  let t = seed >>> 0;
  return function () {
    t += 0x6D2B79F5;
    let r = Math.imul(t ^ (t >>> 15), 1 | t);
    r ^= r + Math.imul(r ^ (r >>> 7), 61 | r);
    return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
  };
}

// Lightweight 2D Perlin noise
function createPerlin2D(seed = 12345) {
  const rand = mulberry32(seed);
  const p = new Uint8Array(512);
  const perm = new Uint8Array(256);
  for (let i = 0; i < 256; i++) perm[i] = i;
  // Fisher-Yates
  for (let i = 255; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    const tmp = perm[i];
    perm[i] = perm[j];
    perm[j] = tmp;
  }
  for (let i = 0; i < 512; i++) p[i] = perm[i & 255];

  const grad2 = (hash, x, y) => {
    // 8 directions
    switch (hash & 7) {
      case 0: return x + y;
      case 1: return -x + y;
      case 2: return x - y;
      case 3: return -x - y;
      case 4: return x;
      case 5: return -x;
      case 6: return y;
      case 7: return -y;
      default: return 0;
    }
  };
  const fade = (t) => t * t * t * (t * (t * 6 - 15) + 10);
  const lerp = (a, b, t) => a + t * (b - a);

  function noise(x, y) {
    const X = Math.floor(x) & 255;
    const Y = Math.floor(y) & 255;

    const xf = x - Math.floor(x);
    const yf = y - Math.floor(y);

    const u = fade(xf);
    const v = fade(yf);

    const aa = p[p[X] + Y];
    const ab = p[p[X] + Y + 1];
    const ba = p[p[X + 1] + Y];
    const bb = p[p[X + 1] + Y + 1];

    const x1 = lerp(grad2(aa, xf, yf), grad2(ba, xf - 1, yf), u);
    const x2 = lerp(grad2(ab, xf, yf - 1), grad2(bb, xf - 1, yf - 1), u);
    return lerp(x1, x2, v); // range approx [-1,1]
  }

  function fbm(x, y, octaves = 4, lacunarity = 2.0, gain = 0.5) {
    let amp = 0.5;
    let freq = 1.0;
    let sum = 0.0;
    for (let i = 0; i < octaves; i++) {
      sum += amp * noise(x * freq, y * freq);
      freq *= lacunarity;
      amp *= gain;
    }
    // remap from roughly [-1,1] to [0,1]
    return sum * 0.5 + 0.5;
  }

  return { noise, fbm };
}

export default function JulesCraftThree() {
  const mountRef = useRef(null);
  const rendererRef = useRef(null);
  const moveRef = useRef({ forward: false, backward: false, left: false, right: false });
  const jumpRef = useRef(false);
  const sprintRef = useRef(false);
  const [health, setHealth] = useState(5);
  const [gameOver, setGameOver] = useState(false);
  const healthRef = useRef(5);
  const gameOverRef = useRef(false);
  const enemiesRef = useRef({ list: [], mesh: null });
  const lastHitRef = useRef(0); // player i-frames
  const swingCooldownRef = useRef(0);
  const swordRef = useRef(null);
  const swordSwingTRef = useRef(1);
  const swordSwingActiveRef = useRef(false);
  const [score, setScore] = useState(0);
  const scoreRef = useRef(0);
  const [timeSurvived, setTimeSurvived] = useState(0);
  const timeSecRef = useRef(0);
  const [hitFlash, setHitFlash] = useState(false);
  const hitFlashTimeoutRef = useRef(null);
  const [resetKey, setResetKey] = useState(0);
  const activeSlimesRef = useRef(0);
  const spawnTimerRef = useRef(0);
  const spawnIntervalRef = useRef(3.0);
  const spawnBatchRef = useRef(1);
  const elapsedRef = useRef(0);
  const spawnEnemyRef = useRef(null);
  const performAttackRef = useRef(null);

  useEffect(() => {
    const mountEl = mountRef.current;
    if (!mountEl) return;

    const sizes = {
      width: mountEl.clientWidth || 800,
      height: mountEl.clientHeight || 500,
    };

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87ceeb); // sky blue

    const camera = new THREE.PerspectiveCamera(75, sizes.width / sizes.height, 0.1, 1000);
    camera.rotation.order = 'YXZ';
    camera.position.set(0, 2, 5);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(sizes.width, sizes.height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    mountEl.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Audio: sword swoosh
    const listener = new THREE.AudioListener();
    camera.add(listener);
    const audioLoader = new THREE.AudioLoader();
    const swingSfx = new THREE.Audio(listener);
    audioLoader.load('/audio/jules/sword-swoosh.wav', (buffer) => {
      swingSfx.setBuffer(buffer);
      swingSfx.setVolume(0.65);
    });
    // Audio: slime pop (voice pool for overlap)
    const popVoices = [];
    audioLoader.load('/audio/jules/pop.wav', (buffer) => {
      for (let i = 0; i < 4; i++) {
        const v = new THREE.Audio(listener);
        v.setBuffer(buffer);
        v.setVolume(0.6);
        popVoices.push(v);
      }
    });
    // Postprocessing composer with OutlinePass (keeps colors, adds edges)
    const composer = new EffectComposer(renderer);
    const renderPass = new RenderPass(scene, camera);
    composer.addPass(renderPass);
    let outlinePass = new OutlinePass(new THREE.Vector2(sizes.width, sizes.height), scene, camera);
    outlinePass.edgeStrength = 2.5;
    outlinePass.edgeGlow = 0.0;
    outlinePass.edgeThickness = 1.0;
    outlinePass.pulsePeriod = 0;
    outlinePass.visibleEdgeColor.set('#000000');
    outlinePass.hiddenEdgeColor.set('#000000');
    composer.addPass(outlinePass);

    // Lights
    const ambient = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambient);
    const dir = new THREE.DirectionalLight(0xffffff, 1.1);
    dir.position.set(8, 15, 6);
    scene.add(dir);
    if (renderer.outputColorSpace !== undefined) {
      renderer.outputColorSpace = THREE.SRGBColorSpace;
    }

    // Voxel terrain (blocky, cube-based)
    const { fbm } = createPerlin2D(1337);
    const cellSize = 2; // cube size
    const enemySize = cellSize; // same as cube
    const enemyRadius = enemySize * 0.5; // use circle on XZ for collision
    const playerRadius = cellSize * 0.55; // player collision radius
    const gridCount = 64; // per axis (64x64 blocks)
    const worldSize = gridCount * cellSize;
    const half = worldSize / 2;

    // Noise & elevation parameters
    const noiseScale = 0.035; // smoother features
    const maxHeightBlocks = 10; // lower vertical variation
    const waterLevel = 0.25; // less water
    const rockLevel = 0.80; // more grass overall
    const waterBlocks = Math.floor(waterLevel * maxHeightBlocks);

    // Simple procedural textures (canvas-based)
    function makeCanvasTexture(drawFn, size = 64) {
      const canvas = document.createElement('canvas');
      canvas.width = size; canvas.height = size;
      const ctx = canvas.getContext('2d');
      drawFn(ctx, size);
      const tex = new THREE.CanvasTexture(canvas);
      tex.magFilter = THREE.NearestFilter;
      tex.minFilter = THREE.NearestFilter;
      tex.anisotropy = 1;
      tex.needsUpdate = true;
      return tex;
    }

    const grassTopTex = makeCanvasTexture((ctx, s) => {
      ctx.fillStyle = '#3dbf2f';
      ctx.fillRect(0, 0, s, s);
      // light speckles
      ctx.fillStyle = '#46d63a';
      for (let i = 0; i < 200; i++) {
        const x = Math.random() * s, y = Math.random() * s;
        ctx.fillRect(x, y, 1, 1);
      }
    });
    const dirtTex = makeCanvasTexture((ctx, s) => {
      ctx.fillStyle = '#8e5c2a';
      ctx.fillRect(0, 0, s, s);
      ctx.fillStyle = '#7a4f25';
      for (let i = 0; i < 150; i++) {
        const x = Math.random() * s, y = Math.random() * s;
        ctx.fillRect(x, y, 1, 1);
      }
    });
    const grassSideTex = makeCanvasTexture((ctx, s) => {
      // dirt base
      ctx.fillStyle = '#8e5c2a';
      ctx.fillRect(0, 0, s, s);
      ctx.fillStyle = '#7a4f25';
      for (let i = 0; i < 120; i++) {
        const x = Math.random() * s, y = Math.random() * s;
        ctx.fillRect(x, y, 1, 1);
      }
      // grass fringe at top 20%
      const h = Math.floor(s * 0.22);
      ctx.fillStyle = '#3dbf2f';
      ctx.fillRect(0, 0, s, h);
      ctx.fillStyle = '#46d63a';
      for (let x = 0; x < s; x++) {
        const hh = h - Math.floor(Math.random() * 3);
        ctx.fillRect(x, Math.max(0, hh - 1), 1, 2);
      }
    });
    const rockTex = makeCanvasTexture((ctx, s) => {
      ctx.fillStyle = '#9e9e9e';
      ctx.fillRect(0, 0, s, s);
      ctx.fillStyle = '#bdbdbd';
      for (let i = 0; i < 200; i++) {
        const x = Math.random() * s, y = Math.random() * s;
        ctx.globalAlpha = 0.5;
        ctx.fillRect(x, y, 1, 1);
      }
      ctx.globalAlpha = 1;
    });

    // Tree textures
    const trunkSideTex = makeCanvasTexture((ctx, s) => {
      // base bark color with vertical gradient
      const grd = ctx.createLinearGradient(0, 0, s, 0);
      grd.addColorStop(0, '#6f4a23');
      grd.addColorStop(0.5, '#8b5a2b');
      grd.addColorStop(1, '#5e3d1c');
      ctx.fillStyle = grd;
      ctx.fillRect(0, 0, s, s);

      // darker vertical ridges of varying thickness
      ctx.strokeStyle = '#4e351a';
      for (let i = 0; i < 14; i++) {
        const x = Math.floor((i + Math.random() * 0.5) * (s / 14));
        ctx.lineWidth = 1 + Math.random() * 2.0;
        ctx.globalAlpha = 0.55 + Math.random() * 0.2;
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, s);
        ctx.stroke();
      }
      ctx.globalAlpha = 1;

      // subtle lighter highlights to suggest sheen
      ctx.strokeStyle = '#a8713a';
      ctx.lineWidth = 1;
      ctx.globalAlpha = 0.35;
      for (let i = 0; i < 10; i++) {
        const x = Math.floor(Math.random() * s);
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, s);
        ctx.stroke();
      }
      ctx.globalAlpha = 1;

      // scattered knots
      const knots = 3 + Math.floor(Math.random() * 3);
      for (let k = 0; k < knots; k++) {
        const x = Math.random() * s;
        const y = Math.random() * s;
        ctx.fillStyle = '#4a2f16';
        ctx.beginPath();
        ctx.ellipse(x, y, 2 + Math.random() * 2, 1 + Math.random() * 1.5, Math.random() * Math.PI, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#2f1e0f';
        ctx.lineWidth = 1;
        ctx.globalAlpha = 0.5;
        ctx.beginPath();
        ctx.ellipse(x, y, 3 + Math.random() * 2, 2 + Math.random() * 2, Math.random() * Math.PI, 0, Math.PI * 2);
        ctx.stroke();
        ctx.globalAlpha = 1;
      }
    });
    const trunkTopTex = makeCanvasTexture((ctx, s) => {
      // wood end with growth rings and subtle radial shading
      ctx.fillStyle = '#9c6b3b';
      ctx.fillRect(0, 0, s, s);
      const cx = s / 2, cy = s / 2;
      ctx.strokeStyle = '#7a512d';
      ctx.globalAlpha = 0.9;
      for (let r = s * 0.45; r > 4; r -= 4 + Math.random() * 2) {
        ctx.beginPath();
        ctx.arc(cx, cy, r + (Math.random() * 1.2 - 0.6), 0, Math.PI * 2);
        ctx.stroke();
      }
      ctx.globalAlpha = 1;
      // darker core
      ctx.fillStyle = '#6e451f';
      ctx.beginPath();
      ctx.arc(cx, cy, 4 + Math.random() * 2, 0, Math.PI * 2);
      ctx.fill();
    });
    const leavesTex = makeCanvasTexture((ctx, s) => {
      ctx.fillStyle = '#2ecc71';
      ctx.fillRect(0, 0, s, s);
      // leaf speckles
      ctx.fillStyle = '#27ae60';
      for (let i = 0; i < 220; i++) {
        const x = Math.random() * s, y = Math.random() * s;
        ctx.fillRect(x, y, 1, 1);
      }
      // brighter highlights
      ctx.fillStyle = '#3eea85';
      for (let i = 0; i < 120; i++) {
        const x = Math.random() * s, y = Math.random() * s;
        ctx.globalAlpha = 0.7;
        ctx.fillRect(x, y, 1, 1);
      }
      ctx.globalAlpha = 1;
    });
    const slimeTex = makeCanvasTexture((ctx, s) => {
      // green skin base
      ctx.fillStyle = '#8dcf5f';
      ctx.fillRect(0, 0, s, s);
      // noise
      ctx.fillStyle = '#79b84f';
      for (let i = 0; i < 140; i++) {
        const x = Math.random() * s, y = Math.random() * s;
        ctx.fillRect(x, y, 1, 1);
      }
      // simple face on top half
      ctx.fillStyle = '#2b2b2b';
      const eyeY = Math.floor(s * 0.3);
      const eyeX1 = Math.floor(s * 0.3);
      const eyeX2 = Math.floor(s * 0.7);
      ctx.fillRect(eyeX1, eyeY, 4, 4);
      ctx.fillRect(eyeX2 - 4, eyeY, 4, 4);
      ctx.fillRect(Math.floor(s * 0.5) - 3, Math.floor(s * 0.5), 6, 2);
    });

    // Materials from textures
    const grassMatTop = new THREE.MeshStandardMaterial({ map: grassTopTex });
    const grassMatSide = new THREE.MeshStandardMaterial({ map: grassSideTex });
    const grassMatBottom = new THREE.MeshStandardMaterial({ map: dirtTex });
    const grassMaterials = [
      grassMatSide, // +x
      grassMatSide, // -x
      grassMatTop,  // +y (top)
      grassMatBottom, // -y (bottom)
      grassMatSide, // +z
      grassMatSide  // -z
    ];
    const rockMat = new THREE.MeshStandardMaterial({ map: rockTex });
    const waterMat = new THREE.MeshStandardMaterial({ color: 0x1e90ff, transparent: true, opacity: 0.7 });

    // Geometry shared by instanced meshes
    const cubeGeo = new THREE.BoxGeometry(cellSize, cellSize, cellSize);

    // Precompute positions for instancing
    const grassPositions = [];
    const grassColors = [];
    const rockPositions = [];
    const rockColors = [];
    const waterPositions = [];
    const topYArr = new Float32Array(gridCount * gridCount);
    const isGrassArr = new Uint8Array(gridCount * gridCount);
    const noiseValArr = new Float32Array(gridCount * gridCount);

    for (let gx = 0; gx < gridCount; gx++) {
      for (let gz = 0; gz < gridCount; gz++) {
        const x = -half + gx * cellSize + cellSize / 2;
        const z = -half + gz * cellSize + cellSize / 2;
        const nx = (x + half) * noiseScale;
        const nz = (z + half) * noiseScale;
        let n = fbm(nx, nz, 4, 2.0, 0.5);
        n = Math.pow(n, 1.1);
        const hBlocks = Math.max(0, Math.floor(n * maxHeightBlocks));
        // Build solid column: rock for inner blocks, grass or rock on top depending on elevation
        const pushColor = (arr, hex, factor=0) => {
          const c = new THREE.Color(hex);
          // lighten by factor to indicate height
          const hsl = { h: 0, s: 0, l: 0 };
          c.getHSL(hsl);
          hsl.l = Math.min(1, hsl.l + factor);
          c.setHSL(hsl.h, hsl.s, hsl.l);
          arr.push(c.r, c.g, c.b);
        };

        const topIndex = Math.max(0, hBlocks);
        // Fill inner from 0..topIndex-1 as rock
        for (let yi = 0; yi < topIndex; yi++) {
          const py = (yi + 0.5) * cellSize;
          rockPositions.push(x, py, z);
          // darker at lower heights, lighter higher
          const factor = yi / maxHeightBlocks * 0.25;
          pushColor(rockColors, 0x9e9e9e, factor);
        }
        // Top block material by elevation
        const topY = (topIndex + 0.5) * cellSize;
        if (n > rockLevel) {
          rockPositions.push(x, topY, z);
          const factor = (topIndex) / maxHeightBlocks * 0.3;
          pushColor(rockColors, 0x9e9e9e, factor);
        } else {
          grassPositions.push(x, topY, z);
          const factor = (topIndex) / maxHeightBlocks * 0.35;
          pushColor(grassColors, 0x39d353, factor);
        }

        // Fill water up to waterBlocks above ground
        if (n < waterLevel) {
          for (let wi = topIndex + 1; wi <= waterBlocks; wi++) {
            const wy = (wi + 0.5) * cellSize;
            waterPositions.push(x, wy, z);
          }
        }
        const idx = gz + gx * gridCount;
        topYArr[idx] = topY;
        isGrassArr[idx] = n <= rockLevel ? 1 : 0;
        noiseValArr[idx] = n;
      }
    }

    // Simple trees on grassy tiles
    const trunkPositions = [];
    const leavesPositions = [];
    const rand = mulberry32(9001);
    for (let gx = 0; gx < gridCount; gx++) {
      for (let gz = 0; gz < gridCount; gz++) {
        const idx = gz + gx * gridCount;
        if (!isGrassArr[idx]) continue;
        const n = noiseValArr[idx];
        if (n > 0.35 && n < 0.75 && rand() < 0.04) {
          const x = -half + gx * cellSize + cellSize / 2;
          const z = -half + gz * cellSize + cellSize / 2;
          const baseY = topYArr[idx];
          const trunkH = 3 + Math.floor(rand() * 2); // 3-4 blocks
          for (let t = 1; t <= trunkH; t++) {
            trunkPositions.push(x, baseY + t * cellSize, z);
          }
          const leafY0 = baseY + trunkH * cellSize + cellSize;
          for (let lx = -1; lx <= 1; lx++) {
            for (let lz = -1; lz <= 1; lz++) {
              for (let ly = 0; ly <= 1; ly++) {
                if (Math.abs(lx) === 1 && Math.abs(lz) === 1 && ly === 1) continue;
                leavesPositions.push(
                  x + lx * cellSize,
                  leafY0 + ly * cellSize,
                  z + lz * cellSize
                );
              }
            }
          }
        }
      }
    }

    function makeInstanced(mat, positions, colors) {
      const count = positions.length / 3;
      const mesh = new THREE.InstancedMesh(cubeGeo, mat, count);
      const m = new THREE.Matrix4();
      const col = new THREE.Color();
      for (let i = 0; i < count; i++) {
        const px = positions[i * 3 + 0];
        const py = positions[i * 3 + 1];
        const pz = positions[i * 3 + 2];
        m.makeTranslation(px, py, pz);
        mesh.setMatrixAt(i, m);
        if (colors) {
          col.setRGB(colors[i * 3 + 0], colors[i * 3 + 1], colors[i * 3 + 2]);
          mesh.setColorAt(i, col);
        }
      }
      mesh.instanceMatrix.needsUpdate = true;
      if (colors) mesh.instanceColor.needsUpdate = true;
      return mesh;
    }

    const grassMesh = makeInstanced(grassMaterials, grassPositions);
    const rockMesh = makeInstanced(rockMat, rockPositions);
    const waterMesh = makeInstanced(waterMat, waterPositions);
    const trunkMatSide = new THREE.MeshStandardMaterial({ map: trunkSideTex });
    const trunkMatTop = new THREE.MeshStandardMaterial({ map: trunkTopTex });
    const trunkMatBottom = trunkMatTop;
    const trunkMaterials = [
      trunkMatSide, // +x
      trunkMatSide, // -x
      trunkMatTop,  // +y
      trunkMatBottom, // -y
      trunkMatSide, // +z
      trunkMatSide  // -z
    ];
    const leavesMat = new THREE.MeshStandardMaterial({ map: leavesTex });
    const slimeMat = new THREE.MeshStandardMaterial({ map: slimeTex });
    const trunkMesh = makeInstanced(trunkMaterials, trunkPositions);
    const leavesMesh = makeInstanced(leavesMat, leavesPositions);
    scene.add(grassMesh);
    scene.add(rockMesh);
    scene.add(waterMesh);
    scene.add(trunkMesh);
    scene.add(leavesMesh);

    // Build a spatial set of trunk columns for simple collision checks (XZ plane)
    const trunkCellSet = new Set();
    const cellIndex = (v) => Math.floor((v + half) / cellSize);
    const trunkKeyStr = (ix, iz) => `${ix},${iz}`;
    for (let i = 0; i < trunkPositions.length; i += 3) {
      const tx = trunkPositions[i + 0];
      const tz = trunkPositions[i + 2];
      const ix = cellIndex(tx);
      const iz = cellIndex(tz);
      trunkCellSet.add(trunkKeyStr(ix, iz));
    }
    // Sword (first-person view model)
    const swordGroup = new THREE.Group();
    const bladeGeo = new THREE.BoxGeometry(0.08, 0.9, 0.06);
    const hiltGeo = new THREE.BoxGeometry(0.12, 0.25, 0.12);
    const guardGeo = new THREE.BoxGeometry(0.35, 0.05, 0.08);
    const bladeMat = new THREE.MeshStandardMaterial({ color: 0xcfd8dc, metalness: 0.7, roughness: 0.3 });
    const hiltMat = new THREE.MeshStandardMaterial({ color: 0x8b5a2b, roughness: 0.9 });
    const guardMat = new THREE.MeshStandardMaterial({ color: 0x9e9e9e, metalness: 0.5, roughness: 0.4 });
    const blade = new THREE.Mesh(bladeGeo, bladeMat);
    blade.position.set(0, 0.45, 0);
    const hilt = new THREE.Mesh(hiltGeo, hiltMat);
    hilt.position.set(0, 0.05, 0);
    const guard = new THREE.Mesh(guardGeo, guardMat);
    guard.position.set(0, 0.15, 0);
    swordGroup.add(blade);
    swordGroup.add(hilt);
    swordGroup.add(guard);
    swordGroup.position.set(0.6, -0.6, -1.2);
    swordGroup.rotation.set(-0.2, 0.8, 0.1);
    camera.add(swordGroup);
    scene.add(camera);
    swordRef.current = { group: swordGroup, basePos: swordGroup.position.clone(), baseRot: swordGroup.rotation.clone() };
    // Enemies (slimes) instanced with capacity and timed spawns
    const maxSlimes = 200;
    const initialSlimes = 10;
    const slimeMesh = new THREE.InstancedMesh(cubeGeo, slimeMat, maxSlimes);
    for (let i = 0; i < maxSlimes; i++) {
      slimeMesh.setColorAt(i, new THREE.Color(0xffffff));
    }
    const zMat = new THREE.Matrix4();
    const enemies = [];
    function randomGrassTop() {
      if (grassPositions.length === 0) return null;
      const tries = 50;
      for (let t = 0; t < tries; t++) {
        const idx = Math.floor(Math.random() * (grassPositions.length / 3));
        const gx = grassPositions[idx * 3 + 0];
        const gy = grassPositions[idx * 3 + 1];
        const gz = grassPositions[idx * 3 + 2];
        // Avoid spawning too close to player start
        if (Math.hypot(gx - 0, gz - 5) < 12) continue;
        return { x: gx, y: gy + cellSize, z: gz };
      }
      return null;
    }
    // Initialize pool as inactive
    for (let i = 0; i < maxSlimes; i++) {
      const e = { x: 0, y: -9999, z: 0, hp: 0, alive: false, cooldown: 0, hitTint: 0, bouncePhase: Math.random() * Math.PI * 2 };
      enemies.push(e);
      zMat.makeTranslation(e.x, e.y, e.z);
      slimeMesh.setMatrixAt(i, zMat);
    }
    function spawnEnemy() {
      const pos = randomGrassTop();
      if (!pos) return false;
      for (let i = 0; i < enemies.length; i++) {
        const en = enemies[i];
        if (!en.alive) {
          en.x = pos.x; en.y = pos.y; en.z = pos.z;
          en.hp = 3; en.alive = true; en.hitTint = 0; en.cooldown = 0; en.bouncePhase = Math.random() * Math.PI * 2;
          zMat.makeTranslation(en.x, en.y, en.z);
          slimeMesh.setMatrixAt(i, zMat);
          slimeMesh.setColorAt(i, new THREE.Color(0xffffff));
          slimeMesh.instanceMatrix.needsUpdate = true;
          slimeMesh.instanceColor.needsUpdate = true;
          activeSlimesRef.current++;
          return true;
        }
      }
      return false;
    }
    spawnEnemyRef.current = spawnEnemy;
    for (let i = 0; i < initialSlimes; i++) spawnEnemy();
    scene.add(slimeMesh);
    enemiesRef.current = { list: enemies, mesh: slimeMesh };

    // Particle system (encapsulated): small red cubes that burst on slime death
    const particlesSys = (() => {
      const maxParticles = 1000;
      const geo = new THREE.BoxGeometry(0.3, 0.3, 0.3);
      const mat = new THREE.MeshBasicMaterial({ color: 0xff5555, transparent: true, opacity: 0.95, depthWrite: false });
      const mesh = new THREE.InstancedMesh(geo, mat, maxParticles);
      const mtx = new THREE.Matrix4();
      const store = new Array(maxParticles).fill(null).map(() => ({ active: false, x: 0, y: -9999, z: 0, vx: 0, vy: 0, vz: 0, life: 0, ttl: 0 }));
      for (let i = 0; i < maxParticles; i++) { mtx.makeTranslation(0, -9999, 0); mesh.setMatrixAt(i, mtx); }
      mesh.instanceMatrix.needsUpdate = true;
      mesh.frustumCulled = false;
      scene.add(mesh);

      function spawn(x, y, z, count = 18) {
        for (let c = 0; c < count; c++) {
          const idx = store.findIndex(p => !p.active);
          if (idx === -1) break;
          const p = store[idx];
          p.active = true;
          p.x = x; p.y = y; p.z = z;
          const speed = 3 + Math.random() * 2.5;
          const theta = Math.random() * Math.PI * 2;
          const up = 2 + Math.random() * 3;
          p.vx = Math.cos(theta) * speed;
          p.vz = Math.sin(theta) * speed;
          p.vy = up;
          p.ttl = 0.8 + Math.random() * 0.6;
          p.life = p.ttl;
          const tmpPos = new THREE.Vector3(p.x, p.y, p.z);
          const tmpQuat = new THREE.Quaternion();
          const tmpScale = new THREE.Vector3(1, 1, 1);
          mtx.compose(tmpPos, tmpQuat, tmpScale);
          mesh.setMatrixAt(idx, mtx);
          mesh.instanceMatrix.needsUpdate = true;
        }
      }

      function update(dt) {
        let changed = false;
        for (let i = 0; i < store.length; i++) {
          const p = store[i];
          if (!p.active) continue;
          p.life -= dt;
          if (p.life <= 0) {
            p.active = false;
            mtx.makeTranslation(0, -9999, 0);
            mesh.setMatrixAt(i, mtx);
            changed = true;
            continue;
          }
          p.vy -= 9.8 * dt;
          p.x += p.vx * dt;
          p.y += p.vy * dt;
          p.z += p.vz * dt;
          const s = Math.max(0.05, p.life / p.ttl);
          const tmpPos2 = new THREE.Vector3(p.x, p.y, p.z);
          const tmpQuat2 = new THREE.Quaternion();
          const tmpScale2 = new THREE.Vector3(s, s, s);
          mtx.compose(tmpPos2, tmpQuat2, tmpScale2);
          mesh.setMatrixAt(i, mtx);
          changed = true;
        }
        if (changed) mesh.instanceMatrix.needsUpdate = true;
      }

      function dispose() {
        try { mesh.dispose(); geo.dispose(); mat.dispose(); } catch (e) {}
      }
      return { spawn, update, dispose };
    })();
    // Configure outline pass to highlight world meshes
    try {
      outlinePass.selectedObjects = [grassMesh, rockMesh, trunkMesh, leavesMesh, slimeMesh];
    } catch (e) {}

    // Grid helper for orientation
    const grid = new THREE.GridHelper(worldSize, gridCount, 0x444444, 0x222222);
    scene.add(grid);

    // Controls (first-person)
    const controls = new PointerLockControls(camera, renderer.domElement);
    scene.add(controls.getObject());

    // Simple movement state (shared with mobile buttons)
    const move = moveRef.current;
    const baseSpeed = 6; // units per second
    const sprintMultiplier = 1.8;

    // Key handlers and listeners are defined once below (with jump support)
    // Reusable helpers (reduce allocations)
    const tmpColor = new THREE.Color();

    // Click to lock pointer
    const el = renderer.domElement;
    const canPointerLock = !!(el.requestPointerLock || el.webkitRequestPointerLock || el.mozRequestPointerLock || el.msRequestPointerLock);
    const requestPointerLock = () => {
      if (!canPointerLock) return; // mobile or unsupported – no-op
      if (!controls.isLocked) controls.lock();
    };
    // Shared attack routine for mouse and touch buttons
    const performAttack = ({ ignoreLock = false } = {}) => {
      try { listener?.context?.resume?.(); } catch (e) {}
      if ((!ignoreLock && !controls.isLocked) || gameOverRef.current) return;
      // Gate attacks strictly by cooldown so damage cannot be spammed
      if (swingCooldownRef.current > 0) return;
      swingCooldownRef.current = 0.10; // 100ms between attacks
      swordSwingTRef.current = 0;
      swordSwingActiveRef.current = true;
      const enemies = enemiesRef.current.list;
      const forward = new THREE.Vector3();
      camera.getWorldDirection(forward);
      forward.y = 0; forward.normalize();
      const camPos = controls.getObject().position;
      const cosArc = Math.cos(Math.PI / 3);
      const range = 5.0;
      let hitAny = false;
      enemies.forEach((en) => {
        if (!en.alive) return;
        const dx = en.x - camPos.x;
        const dz = en.z - camPos.z;
        const dist = Math.hypot(dx, dz);
        if (dist > range) return;
        const dir = new THREE.Vector3(dx, 0, dz).normalize();
        if (dir.dot(forward) >= cosArc) {
          en.hp -= 1;
          en.hitTint = 0.15;
          hitAny = true;
          if (en.hp <= 0) {
            en.alive = false;
            particlesSys.spawn(en.x, en.y, en.z, 20);
            en.y = -9999;
            scoreRef.current += 10;
            setScore(scoreRef.current);
            // Play slime pop with slight random pitch; use an available voice
            if (popVoices && popVoices.length) {
              const voice = popVoices.find((a) => !a.isPlaying) || popVoices[0];
              if (voice && voice.buffer) {
                try { if (voice.isPlaying) voice.stop(); } catch (e) {}
                const rate = 0.9 + Math.random() * 0.25; // 0.90–1.15
                voice.setPlaybackRate(rate);
                try { voice.play(); } catch (e) {}
              }
            }
          }
        }
      });
      if (hitAny) {
        enemiesRef.current.mesh.instanceMatrix.needsUpdate = true;
        enemiesRef.current.mesh.instanceColor.needsUpdate = true;
      }
      // Play sword swoosh with slight random pitch
      if (swingSfx && swingSfx.buffer) {
        try { if (swingSfx.isPlaying) swingSfx.stop(); } catch (e) {}
        const rate = 0.92 + Math.random() * 0.18; // 0.92–1.10
        swingSfx.setPlaybackRate(rate);
        try { swingSfx.play(); } catch (e) {}
      }
    };
    performAttackRef.current = (ignoreLock = false) => performAttack({ ignoreLock });

    const onMouseDown = (e) => {
      // Left click swings sword
      if (e.button === 0) {
        performAttack({ ignoreLock: false });
      }
    };
    el.style.cursor = canPointerLock ? 'crosshair' : 'default';
    if (canPointerLock) el.addEventListener('click', requestPointerLock);
    el.addEventListener('mousedown', onMouseDown);

    // Touch-look support for mobile (drag to rotate view; no translation)
    const touchState = { active: false, id: -1, x: 0, y: 0 };
    const lookSensitivity = 0.007; // radians per pixel (faster turning)
    const clampPitch = (v) => Math.max(-Math.PI / 2 + 0.01, Math.min(Math.PI / 2 - 0.01, v));
    function onTouchStart(e) {
      if (e.changedTouches && e.changedTouches.length > 0) {
        const t = e.changedTouches[0];
        touchState.active = true;
        touchState.id = t.identifier;
        touchState.x = t.clientX;
        touchState.y = t.clientY;
        try { listener?.context?.resume?.(); } catch (err) {}
        e.preventDefault();
      }
    }
    function onTouchMove(e) {
      if (!touchState.active) return;
      for (let i = 0; i < e.changedTouches.length; i++) {
        const t = e.changedTouches[i];
        if (t.identifier !== touchState.id) continue;
        const dx = t.clientX - touchState.x;
        const dy = t.clientY - touchState.y;
        touchState.x = t.clientX;
        touchState.y = t.clientY;
        // Rotate view: yaw (world Y) and pitch (camera X), same as desktop pointer lock
        controls.getObject().rotation.y -= dx * lookSensitivity;
        camera.rotation.x = clampPitch(camera.rotation.x - dy * lookSensitivity);
        e.preventDefault();
        break;
      }
    }
    function onTouchEnd(e) {
      for (let i = 0; i < e.changedTouches.length; i++) {
        if (e.changedTouches[i].identifier === touchState.id) {
          touchState.active = false;
          touchState.id = -1;
          break;
        }
      }
    }
    // Register touch listeners (non-passive to allow preventDefault)
    el.addEventListener('touchstart', onTouchStart, { passive: false });
    el.addEventListener('touchmove', onTouchMove, { passive: false });
    el.addEventListener('touchend', onTouchEnd, { passive: false });
    el.addEventListener('touchcancel', onTouchEnd, { passive: false });

    // Handle resize
    const onResize = () => {
      const w = mountEl.clientWidth || window.innerWidth;
      const h = mountEl.clientHeight || window.innerHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
      try { composer.setSize(w, h); outlinePass.setSize(w, h); } catch (e) {}
    };
    window.addEventListener('resize', onResize);

    // Animation loop
    let prevT = performance.now();
    const up = new THREE.Vector3(0, 1, 0);
    const tmpDir = new THREE.Vector3();
    const tmpRight = new THREE.Vector3();
    const velocity = new THREE.Vector3();
    let yVel = 0;
    let onGround = false;
    const eyeHeight = 1.6 + cellSize; // one block taller
    const boundsHalf = half - cellSize; // keep within

    // Height sampling from noise (matches generation)
    function surfaceYAt(x, z) {
      const nx = (x + half) * noiseScale;
      const nz = (z + half) * noiseScale;
      let n = fbm(nx, nz, 4, 2.0, 0.5);
      n = Math.pow(n, 1.1);
      const hBlocks = Math.max(0, Math.floor(n * maxHeightBlocks));
      const groundTop = (hBlocks + 1) * cellSize; // top face of cube
      const waterTop = (waterBlocks + 1) * cellSize;
      return n < waterLevel ? Math.max(groundTop, waterTop) : groundTop;
    }

    // Place camera on terrain to start
    controls.getObject().position.set(0, surfaceYAt(0, 0) + eyeHeight, 5);

    const onKeyDown = (e) => {
      switch (e.code) {
        case 'ArrowUp':
        case 'KeyW':
          move.forward = true; break;
        case 'ArrowLeft':
        case 'KeyA':
          move.left = true; break;
        case 'ArrowDown':
        case 'KeyS':
          move.backward = true; break;
        case 'ArrowRight':
        case 'KeyD':
          move.right = true; break;
        case 'Space':
          e.preventDefault();
          jumpRef.current = true; break;
        case 'ShiftLeft':
        case 'ShiftRight':
          sprintRef.current = true; break;
        default:
          break;
      }
    };

    const onKeyUp = (e) => {
      switch (e.code) {
        case 'ArrowUp':
        case 'KeyW':
          move.forward = false; break;
        case 'ArrowLeft':
        case 'KeyA':
          move.left = false; break;
        case 'ArrowDown':
        case 'KeyS':
          move.backward = false; break;
        case 'ArrowRight':
        case 'KeyD':
          move.right = false; break;
        case 'Space':
          e.preventDefault();
          break;
        case 'ShiftLeft':
        case 'ShiftRight':
          sprintRef.current = false; break;
        default:
          break;
      }
    };

    document.addEventListener('keydown', onKeyDown);
    document.addEventListener('keyup', onKeyUp);
    const tick = () => {
      const now = performance.now();
      const dt = Math.min(0.05, (now - prevT) / 1000); // clamp to avoid jumps
      prevT = now;

      // On mobile where pointer lock is unavailable, always run gameplay updates
      if (controls.isLocked || !canPointerLock) {
        // Camera basis vectors
        camera.getWorldDirection(tmpDir);
        tmpDir.y = 0;
        tmpDir.normalize();
        // Right vector: forward x up (right-handed)
        tmpRight.crossVectors(tmpDir, up).normalize();

        velocity.set(0, 0, 0);
        if (move.forward) velocity.add(tmpDir);
        if (move.backward) velocity.sub(tmpDir);
        if (move.left) velocity.sub(tmpRight);
        if (move.right) velocity.add(tmpRight);

        if (velocity.lengthSq() > 0) {
          const moveSpeed = baseSpeed * (sprintRef.current ? sprintMultiplier : 1);
          velocity.normalize().multiplyScalar(moveSpeed * dt);
          controls.getObject().position.add(velocity);
        }

        // Clamp to terrain bounds
        const posObj = controls.getObject().position;
        posObj.x = Math.max(-boundsHalf, Math.min(boundsHalf, posObj.x));
        posObj.z = Math.max(-boundsHalf, Math.min(boundsHalf, posObj.z));

        // Resolve collisions against trunk AABBs (XZ only, cylinder vs square)
        const halfBox = cellSize * 0.5;
        const cix = cellIndex(posObj.x);
        const ciz = cellIndex(posObj.z);
        for (let oz = -1; oz <= 1; oz++) {
          for (let ox = -1; ox <= 1; ox++) {
            const ix = cix + ox;
            const iz = ciz + oz;
            if (!trunkCellSet.has(trunkKeyStr(ix, iz))) continue;
            const centerX = -half + ix * cellSize + cellSize * 0.5;
            const centerZ = -half + iz * cellSize + cellSize * 0.5;
            const dx = posObj.x - centerX;
            const dz = posObj.z - centerZ;
            const clampedX = Math.max(-halfBox, Math.min(halfBox, dx));
            const clampedZ = Math.max(-halfBox, Math.min(halfBox, dz));
            const nearestX = centerX + clampedX;
            const nearestZ = centerZ + clampedZ;
            const ddx = posObj.x - nearestX;
            const ddz = posObj.z - nearestZ;
            const distSq = ddx * ddx + ddz * ddz;
            const r = playerRadius;
            if (distSq < r * r - 1e-6) {
              const dist = Math.max(1e-6, Math.sqrt(distSq));
              const nx = ddx / dist;
              const nz = ddz / dist;
              const push = r - dist;
              posObj.x += nx * push;
              posObj.z += nz * push;
            }
          }
        }

        // Sword swing animation
        if (swingCooldownRef.current > 0) swingCooldownRef.current -= dt;
        if (swordSwingActiveRef.current && swordRef.current) {
          const dur = 0.35; // slower, heavier swing to match cooldown
          swordSwingTRef.current += dt / dur;
          let t = swordSwingTRef.current;
          if (t >= 1) { t = 1; swordSwingActiveRef.current = false; }
          const swing = t < 0.5 ? (t / 0.5) : (1 - (t - 0.5) / 0.5);
          const s = swordRef.current;
          // Add lateral sweep to the left across the screen
          const xOffset = -0.40 * swing; // move left as swing progresses
          const zOffset = -0.28 * swing; // move slightly forward
          s.group.position.set(s.basePos.x + xOffset, s.basePos.y, s.basePos.z + zOffset);
          // Start yaw to the right, sweep left by reducing yaw over swing
          const yawStart = s.baseRot.y + 1.2;
          const yawEnd = s.baseRot.y - 0.8;
          const yaw = yawStart + (yawEnd - yawStart) * swing;
          s.group.rotation.set(s.baseRot.x - 1.6 * swing, yaw, s.baseRot.z + 0.45 * swing);
        }

        // Gravity & jumping
        const g = 20;
        const surface = surfaceYAt(posObj.x, posObj.z) + eyeHeight;
        if (jumpRef.current && onGround) {
          yVel = 8; // jump impulse
          onGround = false;
          jumpRef.current = false;
        }
        yVel -= g * dt;
        posObj.y += yVel * dt;
        if (posObj.y <= surface) {
          posObj.y = surface;
          yVel = 0;
          onGround = true;
        } else {
          onGround = false;
        }

        // Update enemies (seek + damage)
        const enemies = enemiesRef.current.list;
        const zMesh = enemiesRef.current.mesh;
        const playerPos = controls.getObject().position;
        const harmRange = playerRadius + enemyRadius + 0.15; // damage trigger when touching
        const enemySpeed = 2.2;
        const nowSec = now / 1000;
        // Spawn more slimes over time
        spawnTimerRef.current += dt;
        elapsedRef.current += dt;
        // update UI timer (only when whole seconds change)
        const whole = Math.floor(elapsedRef.current);
        if (whole !== timeSecRef.current) {
          timeSecRef.current = whole;
          setTimeSurvived(whole);
        }
        if (spawnTimerRef.current >= spawnIntervalRef.current) {
          spawnTimerRef.current = 0;
          let batch = spawnBatchRef.current;
          for (let b = 0; b < batch; b++) spawnEnemy();
          if (spawnIntervalRef.current > 0.7) spawnIntervalRef.current *= 0.96;
          if (elapsedRef.current > 25) spawnBatchRef.current = 2;
          if (elapsedRef.current > 60) spawnBatchRef.current = 3;
        }
        // First pass: steer toward player and update bounce
        for (let i = 0; i < enemies.length; i++) {
          const en = enemies[i];
          if (!en.alive) {
            zMat.makeTranslation(en.x, en.y, en.z);
            zMesh.setMatrixAt(i, zMat);
            continue;
          }
          // seek
          const dx = playerPos.x - en.x;
          const dz = playerPos.z - en.z;
          const dist = Math.hypot(dx, dz);
          if (dist > 0.001) {
            const step = Math.min(enemySpeed * dt, dist);
            en.x += (dx / dist) * step;
            en.z += (dz / dist) * step;
            // snap to ground and add bounce
            const groundY = surfaceYAt(en.x, en.z);
            const bounceAmp = 0.35 * cellSize;
            const bounceSpeed = 6.0;
            const phase = en.bouncePhase || 0;
            const bounce = Math.abs(Math.sin(nowSec * bounceSpeed + phase)) * bounceAmp;
            en.y = groundY + cellSize + bounce; // center of cube + bounce
          }
          // hit flash tint (only write color when changed)
          if (en.hitTint > 0) {
            en.hitTint -= dt;
            tmpColor.setRGB(1, Math.max(0, 1 - 4 * en.hitTint), Math.max(0, 1 - 4 * en.hitTint));
            zMesh.setColorAt(i, tmpColor);
            zMesh.instanceColor.needsUpdate = true;
            en._tinted = true;
          } else if (en._tinted) {
            // reset to white only once after tint fades
            tmpColor.set(0xffffff);
            zMesh.setColorAt(i, tmpColor);
            zMesh.instanceColor.needsUpdate = true;
            en._tinted = false;
          }

          // attack
          if (!gameOverRef.current && dist < harmRange) {
            if (now - lastHitRef.current > 800) { // 0.8s i-frames
              lastHitRef.current = now;
              healthRef.current = Math.max(0, healthRef.current - 1);
              setHealth(healthRef.current);
              // quick red flash on hit
              try { if (hitFlashTimeoutRef.current) clearTimeout(hitFlashTimeoutRef.current); } catch (e) {}
              setHitFlash(true);
              hitFlashTimeoutRef.current = setTimeout(() => setHitFlash(false), 150);
              if (healthRef.current <= 0) {
                gameOverRef.current = true;
                setGameOver(true);
                try { controls.unlock(); } catch (e) {}
              }
            }
          }
        }
        // Second pass: resolve collisions against player (push slimes out)
        for (let i = 0; i < enemies.length; i++) {
          const en = enemies[i];
          if (!en.alive) continue;
          const dxp = en.x - playerPos.x;
          const dzp = en.z - playerPos.z;
          const d = Math.hypot(dxp, dzp);
          const minD = playerRadius + enemyRadius;
          if (d > 0 && d < minD) {
            const overlap = minD - d;
            en.x += (dxp / d) * overlap;
            en.z += (dzp / d) * overlap;
          }
        }
        // Third pass: resolve slime–tree collisions (XZ circle vs trunk AABB)
        for (let i = 0; i < enemies.length; i++) {
          const en = enemies[i];
          if (!en.alive) continue;
          const ecix = cellIndex(en.x);
          const eciz = cellIndex(en.z);
          for (let oz = -1; oz <= 1; oz++) {
            for (let ox = -1; ox <= 1; ox++) {
              const ix = ecix + ox;
              const iz = eciz + oz;
              if (!trunkCellSet.has(trunkKeyStr(ix, iz))) continue;
              const centerX = -half + ix * cellSize + cellSize * 0.5;
              const centerZ = -half + iz * cellSize + cellSize * 0.5;
              const halfBox = cellSize * 0.5;
              const dx = en.x - centerX;
              const dz = en.z - centerZ;
              const clampedX = Math.max(-halfBox, Math.min(halfBox, dx));
              const clampedZ = Math.max(-halfBox, Math.min(halfBox, dz));
              const nearestX = centerX + clampedX;
              const nearestZ = centerZ + clampedZ;
              const ddx = en.x - nearestX;
              const ddz = en.z - nearestZ;
              const distSq = ddx * ddx + ddz * ddz;
              const r = enemyRadius;
              if (distSq < r * r - 1e-6) {
                const dist = Math.max(1e-6, Math.sqrt(distSq));
                const nx = ddx / dist;
                const nz = ddz / dist;
                const push = r - dist;
                en.x += nx * push;
                en.z += nz * push;
              }
            }
          }
        }

        // Fourth pass: resolve slime–slime collisions using a spatial grid
        const cell = enemyRadius * 2 + 0.25;
        const grid = new Map();
        function gridKey(ix, iz) { return (ix << 16) ^ iz; }
        for (let i = 0; i < enemies.length; i++) {
          const e = enemies[i];
          if (!e.alive) continue;
          const ix = Math.floor(e.x / cell);
          const iz = Math.floor(e.z / cell);
          const k = gridKey(ix, iz);
          if (!grid.has(k)) grid.set(k, []);
          grid.get(k).push(i);
        }
        const offsets = [
          [-1,-1], [0,-1], [1,-1],
          [-1, 0], [0, 0], [1, 0],
          [-1, 1], [0, 1], [1, 1],
        ];
        const minD = enemyRadius * 2;
        for (const [k, idxs] of grid) {
          const ix0 = k >> 16; const iz0 = k & 0xffff;
          for (let oi = 0; oi < offsets.length; oi++) {
            const nx = ix0 + offsets[oi][0];
            const nz = iz0 + offsets[oi][1];
            const nk = gridKey(nx, nz);
            const other = grid.get(nk);
            if (!other) continue;
            for (let aIdx = 0; aIdx < idxs.length; aIdx++) {
              const i = idxs[aIdx];
              const a = enemies[i]; if (!a.alive) continue;
              const start = (nk === k) ? aIdx + 1 : 0;
              for (let bIdx = start; bIdx < other.length; bIdx++) {
                const j = other[bIdx]; if (j === i) continue;
                const b = enemies[j]; if (!b.alive) continue;
                const dx = b.x - a.x; const dz = b.z - a.z;
                const d = Math.hypot(dx, dz);
                if (d > 0 && d < minD) {
                  const overlap = (minD - d) * 0.5;
                  const nxv = dx / d; const nzv = dz / d;
                  a.x -= nxv * overlap; a.z -= nzv * overlap;
                  b.x += nxv * overlap; b.z += nzv * overlap;
                }
              }
            }
          }
        }
        // After separation, update y and instance matrices
        for (let i = 0; i < enemies.length; i++) {
          const en = enemies[i];
          if (!en.alive) continue;
          const groundY = surfaceYAt(en.x, en.z);
          const bounceAmp = 0.35 * cellSize;
          const bounceSpeed = 6.0;
          const phase = en.bouncePhase || 0;
          const bounce = Math.abs(Math.sin(nowSec * bounceSpeed + phase)) * bounceAmp;
          en.y = groundY + cellSize + bounce;
          zMat.makeTranslation(en.x, en.y, en.z);
          zMesh.setMatrixAt(i, zMat);
        }
        zMesh.instanceMatrix.needsUpdate = true;
      }

      // Update particles
      particlesSys.update(dt);

      try { composer.render(); } catch (e) { renderer.render(scene, camera); }
      animId = requestAnimationFrame(tick);
    };
    let animId = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', onResize);
      document.removeEventListener('keydown', onKeyDown);
      document.removeEventListener('keyup', onKeyUp);
      if (canPointerLock) renderer.domElement.removeEventListener('click', requestPointerLock);
      try { renderer.domElement.removeEventListener('mousedown', onMouseDown); } catch (e) {}
      try {
        el.removeEventListener('touchstart', onTouchStart);
        el.removeEventListener('touchmove', onTouchMove);
        el.removeEventListener('touchend', onTouchEnd);
        el.removeEventListener('touchcancel', onTouchEnd);
      } catch (e) {}
      mountEl.removeChild(renderer.domElement);
      renderer.dispose();
      try { composer.dispose?.(); } catch (e) {}
      try { swingSfx?.stop(); } catch (e) {}
      try { popVoices?.forEach(v => { try { v.stop(); } catch (e) {} }); } catch (e) {}
      try { particlesSys.dispose(); } catch (e) {}
      cubeGeo.dispose();
      grassMatTop.dispose();
      grassMatSide.dispose();
      grassMatBottom.dispose();
      rockMat.dispose();
      waterMat.dispose();
      grassTopTex.dispose();
      grassSideTex.dispose();
      dirtTex.dispose();
      rockTex.dispose();
      trunkMatSide.dispose();
      trunkMatTop.dispose();
      // trunkMatBottom is same as top
      leavesMat.dispose();
      slimeMat.dispose();
      slimeTex.dispose();
      trunkSideTex.dispose();
      trunkTopTex.dispose();
      leavesTex.dispose();
      // sword cleanup
      try {
        bladeGeo.dispose(); hiltGeo.dispose(); guardGeo.dispose();
        bladeMat.dispose(); hiltMat.dispose(); guardMat.dispose();
      } catch (e) {}
    };
  }, [resetKey]);

  return (
    <div
      ref={mountRef}
      style={{ position: 'relative', width: '100%', height: '60vh', maxWidth: 900, margin: '0 auto', borderRadius: 8, overflow: 'hidden', background: '#000', touchAction: 'none' }}
    >
      {/* Canvas mounts here */}
      {/* HUD */}
      <div style={{ position: 'absolute', top: 8, left: 10, display: 'flex', gap: 6, zIndex: 2 }}>
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} style={{ width: 18, height: 18, borderRadius: 3, border: '1px solid #fff', background: i < health ? '#ff3b3b' : 'transparent' }} />
        ))}
      </div>
      <div style={{ position: 'absolute', top: 8, right: 12, color: '#fff', fontWeight: 600, zIndex: 2 }}>
        Score: {score}
      </div>
      <div style={{ position: 'absolute', top: 8, left: '50%', transform: 'translateX(-50%)', color: '#fff', fontWeight: 600, zIndex: 2 }}>
        Time: {formatTime(timeSurvived)}
      </div>
      {hitFlash && (
        <div style={{ position: 'absolute', inset: 0, background: 'rgba(255,0,0,0.22)', zIndex: 2, pointerEvents: 'none' }} />
      )}
      {gameOver && (
        <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.6)', color: '#fff', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', zIndex: 3 }}>
          <h2 style={{ marginBottom: 12 }}>Game Over</h2>
          <div style={{ marginBottom: 12 }}>Final Score: {score}</div>
          <div style={{ marginBottom: 16 }}>Time Survived: {formatTime(timeSurvived)}</div>
          <button
            onClick={() => {
              // Reset React UI state
              setHealth(5); healthRef.current = 5;
              setScore(0); scoreRef.current = 0;
              setTimeSurvived(0); timeSecRef.current = 0; elapsedRef.current = 0;
              setGameOver(false); gameOverRef.current = false;
              lastHitRef.current = 0;
              // Trigger full teardown + re-init of three.js scene
              setResetKey((k) => k + 1);
            }}
            style={{ padding: '8px 14px', borderRadius: 6, background: '#39d353', color: '#000', border: 'none', cursor: 'pointer' }}
          >Restart</button>
        </div>
      )}
      <MobileControls
        moveRef={moveRef}
        jumpRef={jumpRef}
        sprintRef={sprintRef}
        onAttack={() => performAttackRef.current?.(true)}
      />
    </div>
  );
}

function MobileControls({ moveRef, jumpRef, sprintRef, onAttack }) {
  const press = (dir, e) => {
    if (e && e.preventDefault) e.preventDefault();
    const m = moveRef.current;
    switch (dir) {
      case 'up':
        m.forward = true; break;
      case 'down':
        m.backward = true; break;
      case 'left':
        m.left = true; break;
      case 'right':
        m.right = true; break;
      case 'jump':
        jumpRef.current = true; break;
      case 'sprint':
        sprintRef.current = true; break;
      default:
        break;
    }
  };
  const release = (dir, e) => {
    if (e && e.preventDefault) e.preventDefault();
    const m = moveRef.current;
    switch (dir) {
      case 'up':
        m.forward = false; break;
      case 'down':
        m.backward = false; break;
      case 'left':
        m.left = false; break;
      case 'right':
        m.right = false; break;
      case 'sprint':
        sprintRef.current = false; break;
      // jump doesn't need to hold
      default:
        break;
    }
  };

  const commonHandlers = (dir) => ({
    onTouchStart: (e) => press(dir, e),
    onTouchEnd: (e) => release(dir, e),
    onMouseDown: (e) => press(dir, e),
    onMouseUp: (e) => release(dir, e),
  });

  const btnStyle = {
    width: 56,
    height: 56,
    borderRadius: 12,
    background: 'rgba(255,255,255,0.2)',
    border: '1px solid rgba(255,255,255,0.35)',
    color: '#fff',
    fontSize: 18,
    backdropFilter: 'blur(6px)',
    touchAction: 'none',
  };

  return (
    <>
      {/* D-pad */}
      <div style={{ position: 'absolute', left: 12, bottom: 12, width: 180, height: 180 }}>
        <div style={{ position: 'absolute', left: 62, top: 0 }}>
          <button aria-label="Up" style={btnStyle} {...commonHandlers('up')}>↑</button>
        </div>
        <div style={{ position: 'absolute', left: 0, top: 62 }}>
          <button aria-label="Left" style={btnStyle} {...commonHandlers('left')}>←</button>
        </div>
        <div style={{ position: 'absolute', right: 0, top: 62 }}>
          <button aria-label="Right" style={btnStyle} {...commonHandlers('right')}>→</button>
        </div>
        <div style={{ position: 'absolute', left: 62, bottom: 0 }}>
          <button aria-label="Down" style={btnStyle} {...commonHandlers('down')}>↓</button>
        </div>
      </div>
      {/* Jump, Sprint, Attack */}
      <div style={{ position: 'absolute', right: 16, bottom: 24, display: 'flex', gap: 12 }}>
        <button aria-label="Jump" style={{ ...btnStyle, width: 70, height: 70, fontSize: 16 }}
          onTouchStart={(e) => press('jump', e)}
          onMouseDown={(e) => press('jump', e)}
        >Jump</button>
        <button aria-label="Sprint" style={{ ...btnStyle, width: 70, height: 70, fontSize: 16 }}
          onTouchStart={(e) => press('sprint', e)}
          onTouchEnd={(e) => release('sprint', e)}
          onMouseDown={(e) => press('sprint', e)}
          onMouseUp={(e) => release('sprint', e)}
        >Sprint</button>
        {/* Attack button above Sprint */
        }
        <button aria-label="Attack"
          style={{ ...btnStyle, position: 'absolute', right: 0, bottom: 70 + 12, width: 70, height: 70, fontSize: 16 }}
          onTouchStart={(e) => { e.preventDefault(); onAttack?.(); }}
          onMouseDown={(e) => { e.preventDefault(); onAttack?.(); }}
        >Attack</button>
        {/* Look buttons removed; touch-drag handles yaw/pitch */}
      </div>
    </>
  );
}


