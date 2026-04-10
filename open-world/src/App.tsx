import React, { useEffect, Suspense, useState } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import * as THREE from 'three';
import type { BuildingData, StreetEdge } from './world';

// ─── Error Boundary ─────────────────────────────────────────────────────────────

class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: string }
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false, error: '' };
  }
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error: error.message + '\n' + (error.stack || '') };
  }
  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('React ErrorBoundary caught:', error, info);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          position: 'absolute', inset: 0,
          background: '#1a0a0a', color: '#ff6060',
          fontFamily: 'monospace', fontSize: 12,
          padding: 20, overflow: 'auto', zIndex: 100,
          whiteSpace: 'pre-wrap',
        }}>
          <strong>🔥 Render Error:</strong>
          {this.state.error}
        </div>
      );
    }
    return this.props.children;
  }
}

// ─── Types ─────────────────────────────────────────────────────────────────────

interface WorldData {
  buildings: BuildingData[];
  edges: StreetEdge[];
  center: { lat: number; lon: number };
}

// ─── Scene Data Loader ─────────────────────────────────────────────────────────

function useWorldData(): WorldData | null {
  const [data, setData] = useState<WorldData | null>(null);

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
  const { camera, scene } = useThree();

  useEffect(() => {
    camera.position.set(0, 20, 0);
    camera.lookAt(0, 0, 10);
    scene.background = new THREE.Color('#1a1a28');
    console.log('SceneContent mounted. Buildings:', data.buildings.length);
  }, [camera, scene, data.buildings.length]);

  return (
    <>
      {/* Simple test with lights */}
      <ambientLight intensity={1} />
      <pointLight position={[0, 10, 10]} intensity={2} color="#ffffff" />

      {/* Bright red box in front of camera */}
      <mesh position={[0, 0, 10]}>
        <boxGeometry args={[4, 4, 4]} />
        <meshStandardMaterial color="#ff3333" />
      </mesh>
    </>
  );
}

// ─── Post-Processing ───────────────────────────────────────────────────────────

function PostFX() {
  return null; // DISABLED — was causing silent failures
  /*
  return (
    <EffectComposer>
      <Bloom intensity={0.5} luminanceThreshold={0.15} luminanceSmoothing={0.9} mipmapBlur />
      <Vignette eskil={false} offset={0.1} darkness={0.4} />
    </EffectComposer>
  );
  */
}

// ─── Camera Controller ─────────────────────────────────────────────────────────

function CameraController() {
  const { camera } = useThree();

  useEffect(() => {
    camera.position.set(0, 120, 80);
    camera.lookAt(0, 0, 0);
  }, [camera]);

  return (
    <OrbitControls
      enableDamping
      dampingFactor={0.05}
      minDistance={5}
      maxDistance={500}
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
  const size = 120;
  const scale = 2200;
  const cx = size / 2;
  const cy = size / 2;
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
      <svg width={size} height={size}>
        {roads.map((edge, i) => {
          const x1 = cx + (edge.u_lon - data.center.lon) * scale;
          const y1 = cy - (edge.u_lat - data.center.lat) * scale;
          const x2 = cx + (edge.v_lon - data.center.lon) * scale;
          const y2 = cy - (edge.v_lat - data.center.lat) * scale;
          return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="#4a5a4a" strokeWidth={0.8} />;
        })}
        <circle cx={cx} cy={cy} r={3} fill="#d4a84b" />
      </svg>
      <div style={{ position: 'absolute', bottom: 4, left: 6, fontSize: 9, color: '#d4a84b80', fontFamily: 'monospace' }}>MINI-MAP</div>
    </div>
  );
}

// ─── App ─────────────────────────────────────────────────────────────────────

export default function App() {
  const data = useWorldData();

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative', background: '#0a0a0f' }}>
      {!data && <LoadingScreen />}

      <ErrorBoundary>
        <Canvas
          gl={{ antialias: false, powerPreference: 'low-power' }}
          camera={{ fov: 75, near: 0.1, far: 1000 }}
          style={{ position: 'absolute', inset: 0 }}
          onCreated={({ gl }) => {
            console.log('Canvas renderer info:', gl.getContext().getParameter(gl.getContext().getExtension('WEBGL_debug_renderer_info')?.UNMASKED_RENDERER_WEBGL || 'unknown'));
          }}
        >
          <Suspense fallback={null}>
            {data && <SceneContent data={data} />}
          </Suspense>
        </Canvas>
      </ErrorBoundary>

      {data && <HUD />}
      {data && <MiniMap data={data} />}
    </div>
  );
}
