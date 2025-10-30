import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { PointerLockControls } from 'three/examples/jsm/controls/PointerLockControls.js';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { OutlinePass } from 'three/examples/jsm/postprocessing/OutlinePass.js';

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
  const [hitFlash, setHitFlash] = useState(false);
  const activeZombiesRef = useRef(0);
  const spawnTimerRef = useRef(0);
  const spawnIntervalRef = useRef(3.0);
  const spawnBatchRef = useRef(1);
  const elapsedRef = useRef(0);
  const spawnEnemyRef = useRef(null);

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
    camera.position.set(0, 2, 5);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(sizes.width, sizes.height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    mountEl.appendChild(renderer.domElement);
    rendererRef.current = renderer;
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
      ctx.fillStyle = '#8b5a2b';
      ctx.fillRect(0, 0, s, s);
      // bark vertical streaks
      ctx.strokeStyle = '#6e451f';
      ctx.lineWidth = 2;
      for (let i = 0; i < 8; i++) {
        const x = Math.floor((i + 0.5 + Math.random() * 0.3) * (s / 8));
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, s);
        ctx.stroke();
      }
      // subtle highlights
      ctx.strokeStyle = '#a8713a';
      ctx.lineWidth = 1;
      for (let i = 0; i < 10; i++) {
        const x = Math.floor(Math.random() * s);
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, s);
        ctx.stroke();
      }
    });
    const trunkTopTex = makeCanvasTexture((ctx, s) => {
      // growth rings
      ctx.fillStyle = '#9c6b3b';
      ctx.fillRect(0, 0, s, s);
      ctx.strokeStyle = '#7a512d';
      for (let r = s * 0.45; r > 6; r -= 6) {
        ctx.beginPath();
        ctx.arc(s / 2, s / 2, r + (Math.random() * 1.5 - 0.75), 0, Math.PI * 2);
        ctx.stroke();
      }
      // center darker knot
      ctx.fillStyle = '#6e451f';
      ctx.beginPath();
      ctx.arc(s / 2, s / 2, 4, 0, Math.PI * 2);
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
    const zombieTex = makeCanvasTexture((ctx, s) => {
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
    const zombieMat = new THREE.MeshStandardMaterial({ map: zombieTex });
    const trunkMesh = makeInstanced(trunkMaterials, trunkPositions);
    const leavesMesh = makeInstanced(leavesMat, leavesPositions);
    scene.add(grassMesh);
    scene.add(rockMesh);
    scene.add(waterMesh);
    scene.add(trunkMesh);
    scene.add(leavesMesh);
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
    // Enemies (zombies) instanced with capacity and timed spawns
    const maxZombies = 200;
    const initialZombies = 10;
    const zombieMesh = new THREE.InstancedMesh(cubeGeo, zombieMat, maxZombies);
    for (let i = 0; i < maxZombies; i++) {
      zombieMesh.setColorAt(i, new THREE.Color(0xffffff));
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
    for (let i = 0; i < maxZombies; i++) {
      const e = { x: 0, y: -9999, z: 0, hp: 0, alive: false, cooldown: 0, hitTint: 0, bouncePhase: Math.random() * Math.PI * 2 };
      enemies.push(e);
      zMat.makeTranslation(e.x, e.y, e.z);
      zombieMesh.setMatrixAt(i, zMat);
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
          zombieMesh.setMatrixAt(i, zMat);
          zombieMesh.setColorAt(i, new THREE.Color(0xffffff));
          zombieMesh.instanceMatrix.needsUpdate = true;
          zombieMesh.instanceColor.needsUpdate = true;
          activeZombiesRef.current++;
          return true;
        }
      }
      return false;
    }
    spawnEnemyRef.current = spawnEnemy;
    for (let i = 0; i < initialZombies; i++) spawnEnemy();
    scene.add(zombieMesh);
    enemiesRef.current = { list: enemies, mesh: zombieMesh };
    // Configure outline pass to highlight world meshes
    try {
      outlinePass.selectedObjects = [grassMesh, rockMesh, trunkMesh, leavesMesh, zombieMesh];
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

    // Click to lock pointer
    const requestPointerLock = () => {
      if (!controls.isLocked) controls.lock();
    };
    const onMouseDown = (e) => {
      // Left click swings sword
      if (e.button === 0 && controls.isLocked && !gameOverRef.current) {
        if (swingCooldownRef.current <= 0) {
          swingCooldownRef.current = 0.25;
          swordSwingTRef.current = 0;
          swordSwingActiveRef.current = true;
        }
        // Perform hit detection once per click
        const enemies = enemiesRef.current.list;
        const forward = new THREE.Vector3();
        camera.getWorldDirection(forward);
        forward.y = 0; forward.normalize();
        const camPos = controls.getObject().position;
        const cosArc = Math.cos(Math.PI / 3); // 60deg swing arc
        const range = 5.0; // larger reach
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
              en.y = -9999; // hide
              scoreRef.current += 10;
              setScore(scoreRef.current);
            }
          }
        });
        if (hitAny) {
          enemiesRef.current.mesh.instanceMatrix.needsUpdate = true;
          enemiesRef.current.mesh.instanceColor.needsUpdate = true;
        }
      }
    };
    renderer.domElement.style.cursor = 'crosshair';
    renderer.domElement.addEventListener('click', requestPointerLock);
    renderer.domElement.addEventListener('mousedown', onMouseDown);

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

      if (controls.isLocked) {
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

        // Sword swing animation
        if (swingCooldownRef.current > 0) swingCooldownRef.current -= dt;
        if (swordSwingActiveRef.current && swordRef.current) {
          const dur = 0.22; // slower, heavier swing
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
        const harmRange = 1.6;
        const enemySpeed = 2.2;
        const nowSec = now / 1000;
        // Spawn more zombies over time
        spawnTimerRef.current += dt;
        elapsedRef.current += dt;
        if (spawnTimerRef.current >= spawnIntervalRef.current) {
          spawnTimerRef.current = 0;
          let batch = spawnBatchRef.current;
          for (let b = 0; b < batch; b++) spawnEnemy();
          if (spawnIntervalRef.current > 0.7) spawnIntervalRef.current *= 0.96;
          if (elapsedRef.current > 25) spawnBatchRef.current = 2;
          if (elapsedRef.current > 60) spawnBatchRef.current = 3;
        }
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
          // hit flash tint
          if (en.hitTint > 0) {
            en.hitTint -= dt;
            const c = new THREE.Color(1, Math.max(0, 1 - 4 * en.hitTint), Math.max(0, 1 - 4 * en.hitTint));
            zMesh.setColorAt(i, c);
            zMesh.instanceColor.needsUpdate = true;
          } else {
            zMesh.setColorAt(i, new THREE.Color(0xffffff));
          }

          // attack
          if (!gameOverRef.current && dist < harmRange) {
            if (now - lastHitRef.current > 800) { // 0.8s i-frames
              lastHitRef.current = now;
              healthRef.current = Math.max(0, healthRef.current - 1);
              setHealth(healthRef.current);
              if (healthRef.current <= 0) {
                gameOverRef.current = true;
                setGameOver(true);
                try { controls.unlock(); } catch (e) {}
              }
            }
          }
          zMat.makeTranslation(en.x, en.y, en.z);
          zMesh.setMatrixAt(i, zMat);
        }
        zMesh.instanceMatrix.needsUpdate = true;
      }

      try { composer.render(); } catch (e) { renderer.render(scene, camera); }
      animId = requestAnimationFrame(tick);
    };
    let animId = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', onResize);
      document.removeEventListener('keydown', onKeyDown);
      document.removeEventListener('keyup', onKeyUp);
      renderer.domElement.removeEventListener('click', requestPointerLock);
      try { renderer.domElement.removeEventListener('mousedown', onMouseDown); } catch (e) {}
      mountEl.removeChild(renderer.domElement);
      renderer.dispose();
      try { composer.dispose?.(); } catch (e) {}
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
      zombieMat.dispose();
      zombieTex.dispose();
      trunkSideTex.dispose();
      trunkTopTex.dispose();
      leavesTex.dispose();
      // sword cleanup
      try {
        bladeGeo.dispose(); hiltGeo.dispose(); guardGeo.dispose();
        bladeMat.dispose(); hiltMat.dispose(); guardMat.dispose();
      } catch (e) {}
    };
  }, []);

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
      {hitFlash && (
        <div style={{ position: 'absolute', inset: 0, background: 'rgba(255,0,0,0.22)', zIndex: 2, pointerEvents: 'none' }} />
      )}
      {gameOver && (
        <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.6)', color: '#fff', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', zIndex: 3 }}>
          <h2 style={{ marginBottom: 12 }}>Game Over</h2>
          <div style={{ marginBottom: 12 }}>Final Score: {score}</div>
          <button
            onClick={() => {
              healthRef.current = 5; setHealth(5);
              gameOverRef.current = false; setGameOver(false);
              lastHitRef.current = 0;
              scoreRef.current = 0; setScore(0);
              // reset enemies
              const { list, mesh } = enemiesRef.current;
              const m = new THREE.Matrix4();
              for (let i = 0; i < list.length; i++) {
                const en = list[i];
                en.alive = false; en.hp = 0; en.x = 0; en.y = -9999; en.z = 0; en.hitTint = 0;
                m.makeTranslation(en.x, en.y, en.z);
                mesh.setMatrixAt(i, m);
                mesh.setColorAt(i, new THREE.Color(0xffffff));
              }
              mesh.instanceMatrix.needsUpdate = true; mesh.instanceColor.needsUpdate = true;
              // reset spawn pacing
              spawnTimerRef.current = 0; elapsedRef.current = 0; spawnBatchRef.current = 1; spawnIntervalRef.current = 3.0;
              // spawn initial
              if (spawnEnemyRef.current) {
                for (let i = 0; i < 10; i++) spawnEnemyRef.current();
              }
            }}
            style={{ padding: '8px 14px', borderRadius: 6, background: '#39d353', color: '#000', border: 'none', cursor: 'pointer' }}
          >Restart</button>
        </div>
      )}
      <MobileControls moveRef={moveRef} jumpRef={jumpRef} sprintRef={sprintRef} />
    </div>
  );
}

function MobileControls({ moveRef, jumpRef, sprintRef }) {
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
      {/* Jump and Sprint */}
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
      </div>
    </>
  );
}



