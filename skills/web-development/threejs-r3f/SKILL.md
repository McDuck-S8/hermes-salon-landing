---
name: threejs-r3f
description: "3D web experiences with Three.js and React Three Fiber (R3F) — Canvas setup, lighting, environment maps, controls, Suspense asset loading, Drei helpers, useFrame animation. Load when ANY 3D/interactive web element is needed."
version: 1.0.0
tags: [threejs, r3f, 3d, webgl, react, fiber, drei]
---

# Three.js & React Three Fiber (R3F)

## Install

```bash
npm install three @react-three/fiber @react-three/drei
# Optional
npm install @react-three/postprocessing @react-spring/three
```

## CDN (static HTML)
```html
<script src="https://cdn.jsdelivr.net/npm/three@0.166.1/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.166.1/examples/js/controls/OrbitControls.min.js"></script>
```

---

## React Three Fiber — Basic Scene

```jsx
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment, useGLTF } from '@react-three/drei';

function Box() {
  return (
    <mesh>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="orange" />
    </mesh>
  );
}

function Scene() {
  return (
    <Canvas camera={{ position: [0, 0, 5] }}>
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={1} />
      <Box />
      <OrbitControls />
    </Canvas>
  );
}
```

### Suspense loading
```jsx
import { Suspense } from 'react';

function Scene() {
  return (
    <Canvas>
      <Suspense fallback={null}>
        <Environment preset="apartment" />
        <Model url="/model.glb" />
      </Suspense>
      <OrbitControls />
    </Canvas>
  );
}
```

### Model loader
```jsx
import { useGLTF, useAnimations } from '@react-three/drei';

function Model({ url, animate = false }) {
  const { nodes, materials, animations } = useGLTF(url);
  const { actions } = useAnimations(animations, group);

  return (
    <group ref={group}>
      <skinnedMesh geometry={nodes.character.geometry} material={materials.skin} />
      {animate && actions?.idle?.play()}
    </group>
  );
}
```

---

## Raw Three.js (Vanilla)

```javascript
// Scene setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Geometry
const geometry = new THREE.BoxGeometry();
const material = new THREE.MeshStandardMaterial({ color: 0xff6b35 });
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

// Lighting
const ambient = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambient);
const directional = new THREE.DirectionalLight(0xffffff, 1);
directional.position.set(10, 10, 5);
scene.add(directional);

// Animation loop
function animate() {
  requestAnimationFrame(animate);
  cube.rotation.x += 0.01;
  cube.rotation.y += 0.01;
  renderer.render(scene, camera);
}
animate();

// Orbit controls
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

// Handle resize
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

---

## Drei Helpers (R3F)

```jsx
import { OrbitControls, Environment, ContactShadows, Html, Text, useGLTF } from '@react-three/drei';

// Environment lighting
<Environment preset="warehouse" />

// Contact shadows (ground shadow)
<ContactShadows position={[0, -0.5, 0]} opacity={0.5} scale={10} />

// HTML overlay
<Html position={[0, 1.5, 0]}>
  <div className="label">Hello 3D</div>
</Html>

// 3D Text
<Text font="/fonts/Inter-Bold.woff" position={[0, 0, 0]}>
  Hello
</Text>

// Preload all assets
useGLTF.preload('/model.glb');
```

### Environment presets
- `apartment`, `city`, `dawn`, `evening`, `goldenGate`, `home`, `lobby`, `night`, `park`, `studio`, `sunset`, `warehouse`

---

## Animation (useFrame)

```jsx
import { useFrame } from '@react-three/fiber';
import { useRef } from 'react';

function RotatingBox() {
  const ref = useRef();

  useFrame((state, delta) => {
    ref.current.rotation.x += delta;
    ref.current.rotation.y += delta;
  });

  return (
    <mesh ref={ref}>
      <boxGeometry />
      <meshStandardMaterial color="hotpink" />
    </mesh>
  );
}
```

### React Spring (R3F)
```jsx
import { useSpring } from '@react-spring/three';

function AnimatedBox({ active }) {
  const { scale, rotation } = useSpring({
    scale: active ? [1.5, 1.5, 1.5] : [1, 1, 1],
    rotation: active ? [0, Math.PI, 0] : [0, 0, 0],
  });

  return (
    <mesh scale={scale} rotation={rotation}>
      <boxGeometry />
      <meshStandardMaterial color="orange" />
    </mesh>
  );
}
```

---

## Performance

### LOD (Level of Detail)
```jsx
import { LOD } from '@react-three/drei';

<LOD>
  <mesh scale={1} position={[0, 0, 0]}>
    <detailedGeometry args={highDetail} />
  </mesh>
  <mesh scale={0.5} position={[0, 0, 0]}>
    <detailedGeometry args={lowDetail} />
  </mesh>
</LOD>
```

### InstancedMesh (many objects)
```jsx
import { Instances, Instance } from '@react-three/drei';

function Balls() {
  const positions = Array.from({ length: 100 }, () => [
    Math.random() * 10 - 5,
    Math.random() * 10 - 5,
    Math.random() * 10 - 5
  ]);

  return (
    <Instances>
      <sphereGeometry args={[0.1, 8, 8]} />
      <meshStandardMaterial color="orange" />
      {positions.map((pos, i) => <Instance key={i} position={pos} />)}
    </Instances>
  );
}
```

### Performance checklist
- [ ] Use `useMemo` for geometries that don't change
- [ ] Use `InstancedMesh` for repeated objects (>10)
- [ ] Use `LOD` for complex models
- [ ] Compress glTF models (`.glb` with Draco compression)
- [ ] Limit lights (max 2-3 per scene)
- [ ] Use `dpr={[1, 2]}` for pixel ratio control
- [ ] Dispose geometries: `geometry.dispose()` on unmount
- [ ] Use `frustumCulled={false}` for transparent objects

---

## Common Patterns

### 3D Hero Section
```jsx
function Hero3D() {
  return (
    <div className="hero">
      <Canvas camera={{ position: [0, 0, 3] }}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[5, 5, 5]} intensity={1} />
        <Model url="/hero.glb" />
        <OrbitControls enableZoom={false} autoRotate />
      </Canvas>
      <div className="hero-content">
        <h1>Заголовок</h1>
      </div>
    </div>
  );
}
```

### Interactive 3D Card
```jsx
function Card3D() {
  const [hovered, setHovered] = useState(false);
  const { scale } = useSpring({ scale: hovered ? 1.1 : 1 });

  return (
    <mesh onPointerOver={() => setHovered(true)} onPointerOut={() => setHovered(false)} scale={scale}>
      <planeGeometry args={[3, 2]} />
      <meshStandardMaterial color={hovered ? 'hotpink' : 'white'} side={THREE.DoubleSide} />
    </mesh>
  );
}
```

### Loading screen
```jsx
function Loading() {
  const { progress } = useProgress();
  return <Html center>{Math.round(progress)}% loaded</Html>;
}

<Suspense fallback={<Loading />}>
  <Model />
</Suspense>
```

---

## Pitfalls
- **Large GLB files** — compress with Draco (`gltf-pipeline`), keep under 500KB for web
- **Mobile performance** — reduce poly count, use fewer lights, disable shadows on mobile
- **OrbitControls conflict** — don't use with Lenis smooth scroll (use `enableDamping` instead)
- **FOUC** — Canvas takes 100-200ms to initialize — show fallback
- **Memory leaks** — dispose geometries and materials on unmount
- **SSR issues** — `window` undefined in Next.js SSR — use `dynamic(() => import(...), { ssr: false })`
- **WebGL context lost** — add error boundary and recovery
- **Touch events** — OrbitControls works on touch but test on real devices
