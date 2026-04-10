import React, { useEffect, useRef, Suspense } from 'react';
import { Canvas, useThree, useFrame } from '@react-three/fiber';
import { OrbitControls, Sky, useTexture } from '@react-three/drei';
import { EffectComposer, Bloom, Vignette, ColorAverage } from '@react-three/postprocessing';
import * as THREE from 'three';
import { createBuildingMesh, createRoadMesh, createGroundPlane, createGrid, type BuildingData, type StreetEdge } from './world';

// ─── Types ─────────────────────────────────────────────────────────────────────

interface WorldData {
  buildings: BuildingData[];
  edges: StreetEdge[];
  center: { lat: number; lon: number };
}

// ─── Scene Data Loader (async) ─────────────────────────────────────────────────

function useWorldData(): WorldData | null {
  const [data, setData] = React.useState<WorldData | null>(null);

  useEffect(() => {
    Promise.all([
      fetch('/buildings.json').then(r => r.json()),
      fetch('/streets.json').then(r => r.json()),
    ]).then(([buildings, streets]) => {
      setData({ buildings, edges: streets.edges || [], center: streets.center });
    }).catch(console.error);
  }, []);

  return data;
}

// ─── Scene Content ─────────────────────────────────────────────────────────────

function SceneContent({ data }: { data: WorldData }) {
  const { camera } = useThree();

  useEffect(() => {
    // Place camera above the scene, looking down
    camera.position.set(0, 120, 80);
    camera.lookAt(0, 0, 0);
  }, [camera]);

  useFrame(({ clock }) => {
    // Subtle time-based animation if needed
  });

  const ground = createGroundPlane(data.center);
  const roadMesh = createRoadMesh(data.edges, data.center);

  // Building meshes
  const buildingMeshes = data.buildings.map((b, i) => {
    const mesh = createBuildingMesh(b, data.center);
    // Slight color variation per building for texture
    const mat = (mesh.material as THREE.MeshStandardMaterial);
    const variation = (Math.random() - 0.5) * 0.08;
    const hsl = new THREE.Color(mat.color).getHSL({});
    mat.color.setHSL(hsl.h, hsl.s, Math.max(0.1, hsl.l + variation));
    mesh.position.y = i * 0.001; // tiny offset to prevent z-fighting
    return mesh;
  });

  return (
    <>
      {/* Lighting */}
      <ambientLight intensity={0.25} color="#b0c0d0" />
      <directionalLight
        position={[100, 200, 80]}
        intensity={1.8}
        color="#fff5e0"
        castShadow
        shadow-mapSize={[2048, 2048]}
        shadow-camera-far={600}
        shadow-camera-left={-300}
        shadow-camera-right={300}
        shadow-camera-top={300}
        shadow-camera-bottom={-300}
      />
      {/* Warm fill light from opposite side */}
      <directionalLight position={[-80, 60, -60]} intensity={0.3} color="#ffd090" />
      {/* Street-level ambient */}
      <pointLight position={[0, 5, 0]} intensity={0.3} color="#ff9940" distance={50} />

      {/* Sky */}
      <Sky
        distance={450000}
        sunPosition={[100, 20, -100]}
        inclination={0.5}
        azimuth={0.25}
        turbidity={8}
        rayleigh={0.5}
      />

      {/* Ground */}
      <primitive object={ground} />

      {/* Roads */}
      <primitive object={roadMesh} />

      {/* Buildings */}
      {buildingMeshes.map((mesh, i) => (
        <primitive key={i} object={mesh} />
      ))}

      {/* Grid */}
      <primitive object={createGrid(data.center)} />
    </>
  );
}

// ─── Post-Processing ───────────────────────────────────────────────────────────

function PostFX() {
  return (
    <EffectComposer>
      {/* Bloom — street lights, windows glow */}
      <Bloom
        intensity={0.6}
        luminanceThreshold={0.4}
        luminanceSmoothing={0.9}
        mipmapBlur
      />
      {/* Subtle vignette for GTA feel */}
      <Vignette eskil={false} offset={0.15} darkness={0.7} />
      {/* Warm color grade */}
      <ColorAverage />
    </EffectComposer>
  );
}

// ─── Camera Controller ─────────────────────────────────────────────────────────

function CameraController() {
  const controlsRef = useRef<any>(null);
  const { camera } = useThree();

  useEffect(() => {
    camera.position.set(0, 150, 100);
    camera.lookAt(0, 0, 0);
  }, [camera]);

  return (
    <OrbitControls
      ref={controlsRef}
      enableDamping
      dampingFactor={0.05}
      minDistance={10}
      maxDistance={600}
      maxPolarAngle={Math.PI / 2.1}
      target={[0, 0, 0]}
    />
  );
}

// ─── Loading Screen ─────────────────────────────────────────────────────────────

function LoadingScreen() {
  return (
    <div style={{
      position: 'absolute', inset: 0,
      background: '#0a0a0f',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      color: '#d4a84b',
      fontFamily: "'Courier New', monospace",
      fontSize: 14,
      letterSpacing: 3,
      zIndex: 10,
    }}>
      <div style={{ fontSize: 28, marginBottom: 20 }}>🗺️</div>
      <div style={{ textTransform: 'uppercase' }}>Loading 60th &amp; Market...</div>
      <div style={{ marginTop: 10, opacity: 0.5 }}>West Philadelphia</div>
    </div>
  );
}

// ─── HUD ───────────────────────────────────────────────────────────────────────

function HUD() {
  return (
    <div style={{
      position: 'absolute', top: 16, left: 16,
      color: '#d4a84b',
      fontFamily: "'Courier New', monospace",
      fontSize: 12,
      pointerEvents: 'none',
      textShadow: '0 0 8px #d4a84b80',
      lineHeight: 1.8,
    }}>
      <div style={{ fontSize: 16, fontWeight: 'bold', marginBottom: 4 }}>WEST PHILADELPHIA</div>
      <div>📍 60th &amp; Market</div>
      <div>🎮 Orbit: Left Mouse</div>
      <div>🔍 Zoom: Scroll</div>
      <div>📋 Pan: Right Mouse</div>
      <div style={{ marginTop: 8, color: '#888', fontSize: 10 }}>
        249 buildings • 1146 road segments
      </div>
    </div>
  );
}

// ─── Mini Map ─────────────────────────────────────────────────────────────────

function MiniMap({ data }: { data: WorldData }) {
  if (!data) return null;

  const size = 120;
  const scale = 2000; // meters per pixel roughly
  const cx = size / 2;
  const cy = size / 2;

  // Road type filter
  const isRoad = (h: string) => !['footway', 'path', 'cycleway', 'steps'].includes(h.toLowerCase());
  const roads = data.edges.filter(e => isRoad(e.highway));

  return (
    <div style={{
      position: 'absolute', bottom: 16, right: 16,
      width: size, height: size,
      background: 'rgba(10,10,10,0.85)',
      border: '1px solid #d4a84b40',
      borderRadius: 4,
      overflow: 'hidden',
    }}>
      <div style={{
        position: 'absolute', inset: 0,
        background: '#0d1a0d',
      }}>
        {/* Road lines */}
        <svg width={size} height={size} style={{ position: 'absolute', inset: 0 }}>
          {roads.map((edge, i) => {
            const x1 = cx + (edge.u_lon - data.center.lon) * scale;
            const y1 = cy - (edge.u_lat - data.center.lat) * scale;
            const x2 = cx + (edge.v_lon - data.center.lon) * scale;
            const y2 = cy - (edge.v_lat - data.center.lat) * scale;
            return (
              <line key={i} x1={x1} y1={y1} x2={x2} y2={y2}
                stroke="#4a5a4a" strokeWidth={0.8} />
            );
          })}
          {/* Center dot */}
          <circle cx={cx} cy={cy} r={3} fill="#d4a84b" />
        </svg>
      </div>
      <div style={{
        position: 'absolute', bottom: 4, left: 6,
        fontSize: 9, color: '#d4a84b80',
        fontFamily: 'monospace',
      }}>MINI-MAP</div>
    </div>
  );
}

// ─── App ───────────────────────────────────────────────────────────────────────

export default function App() {
  const data = useWorldData();

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative', background: '#0a0a0f' }}>
      {!data && <LoadingScreen />}

      <Canvas
        shadows
        gl={{
          antialias: true,
          toneMapping: THREE.ACESFilmicToneMapping,
          toneMappingExposure: 1.1,
          outputColorSpace: THREE.SRGBColorSpace,
        }}
        camera={{ fov: 55, near: 0.5, far: 3000 }}
        style={{ position: 'absolute', inset: 0 }}
      >
        <Suspense fallback={null}>
          {data && <SceneContent data={data} />}
          <CameraController />
          <PostFX />
        </Suspense>
      </Canvas>

      {data && <HUD />}
      {data && <MiniMap data={data} />}
    </div>
  );
}
