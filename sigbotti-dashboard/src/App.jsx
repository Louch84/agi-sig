import React, { useEffect, useState, useRef, Suspense, useCallback } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import * as THREE from 'three'

// ─── Palette ──────────────────────────────────────────────────────────────────
const C = {
  bg: '#0a0f1a',
  panel: '#0a0a12',
  panelDark: '#07070f',
  border: '#1a1a2e',
  accent: '#00f5d4',
  accent2: '#f72585',
  accent3: '#9b5de5',
  text: '#c8c8e0',
  dim: '#4a4a6a',
  success: '#00f5a0',
  warning: '#f5a623',
  danger: '#f5365c',
}

// ─── API ───────────────────────────────────────────────────────────────────────
const API = ''

async function apiAction(action) {
  const r = await fetch(`${API}/api/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action }),
  })
  return r.json()
}

async function apiStatus() {
  try {
    const r = await fetch(`${API}/api/status`)
    return r.json()
  } catch {
    return null
  }
}

// ─── Fox Character (Procedural 3D) ────────────────────────────────────────────
function Fox({ position = [0, 0, 0] }) {
  const groupRef = useRef()
  const bodyRef = useRef()
  const tailRef = useRef()
  const earLRRef = useRef()
  const earRRRef = useRef()
  const eyeLRef = useRef()
  const eyeRRef = useRef()
  const blinkRef = useRef(0)
  const timeRef = useRef(0)

  useFrame((state) => {
    timeRef.current += 0.016
    const t = timeRef.current

    if (groupRef.current) {
      // Gentle idle sway
      groupRef.current.rotation.y = Math.sin(t * 0.3) * 0.15
    }
    if (bodyRef.current) {
      // Breathing
      const b = 1 + Math.sin(t * 1.8) * 0.025
      bodyRef.current.scale.set(b, 1, b)
      // Subtle bounce
      bodyRef.current.position.y = position[1] + Math.sin(t * 1.8) * 0.05
    }
    if (tailRef.current) {
      tailRef.current.rotation.z = Math.sin(t * 2.5) * 0.3 + 0.5
      tailRef.current.rotation.x = Math.sin(t * 1.5) * 0.15
    }
    if (earLRRef.current) {
      earLRRef.current.rotation.z = Math.sin(t * 3.0 + 1) * 0.08
    }
    if (earRRRef.current) {
      earRRRef.current.rotation.z = -(Math.sin(t * 3.0 + 1) * 0.08)
    }
    // Blink
    blinkRef.current += 0.01
    if (blinkRef.current > 4.2) {
      blinkRef.current = 0
    }
    const blinkAmount = (blinkRef.current > 4.0 && blinkRef.current < 4.2) ? 0.1 : 1
    if (eyeLRef.current) eyeLRef.current.scale.y = blinkAmount
    if (eyeRRef.current) eyeRRef.current.scale.y = blinkAmount
  })

  const orange = '#e87a25'
  const darkOrange = '#c45e10'
  const white = '#f5e6d0'
  const black = '#111111'

  return (
    <group ref={groupRef} position={position}>
      {/* Body */}
      <mesh ref={bodyRef} position={[0, 0.55, 0]}>
        <boxGeometry args={[0.7, 0.5, 0.5]} />
        <meshStandardMaterial color={orange} roughness={0.7} emissive={orange} emissiveIntensity={0.08} />
      </mesh>
      {/* Chest */}
      <mesh position={[0, 0.52, 0.22]}>
        <boxGeometry args={[0.35, 0.3, 0.08]} />
        <meshStandardMaterial color={white} roughness={0.8} emissive={white} emissiveIntensity={0.05} />
      </mesh>
      {/* Head */}
      <mesh position={[0, 1.0, 0.2]}>
        <boxGeometry args={[0.55, 0.45, 0.45]} />
        <meshStandardMaterial color={orange} roughness={0.7} emissive={orange} emissiveIntensity={0.08} />
      </mesh>
      {/* Snout */}
      <mesh position={[0, 0.92, 0.46]}>
        <boxGeometry args={[0.22, 0.18, 0.22]} />
        <meshStandardMaterial color={white} roughness={0.8} />
      </mesh>
      {/* Nose */}
      <mesh position={[0, 0.95, 0.58]}>
        <sphereGeometry args={[0.045, 8, 8]} />
        <meshStandardMaterial color={black} roughness={0.3} emissive={black} emissiveIntensity={0.2} />
      </mesh>
      {/* Eyes */}
      <mesh ref={eyeLRef} position={[0.14, 1.06, 0.44]}>
        <sphereGeometry args={[0.055, 8, 8]} />
        <meshStandardMaterial color="#222222" roughness={0.1} metalness={0.3} emissive="#111111" emissiveIntensity={0.3} />
      </mesh>
      <mesh position={[0.14, 1.08, 0.47]}>
        <sphereGeometry args={[0.022, 6, 6]} />
        <meshStandardMaterial color={white} emissive={white} emissiveIntensity={2} />
      </mesh>
      <mesh ref={eyeRRef} position={[-0.14, 1.06, 0.44]}>
        <sphereGeometry args={[0.055, 8, 8]} />
        <meshStandardMaterial color="#222222" roughness={0.1} metalness={0.3} emissive="#111111" emissiveIntensity={0.3} />
      </mesh>
      <mesh position={[-0.14, 1.08, 0.47]}>
        <sphereGeometry args={[0.022, 6, 6]} />
        <meshStandardMaterial color={white} emissive={white} emissiveIntensity={2} />
      </mesh>
      {/* Left Ear */}
      <group ref={earLRRef} position={[0.2, 1.32, 0.05]}>
        <mesh rotation={[0, 0, 0.2]}>
          <coneGeometry args={[0.1, 0.28, 4]} />
          <meshStandardMaterial color={orange} roughness={0.7} />
        </mesh>
        <mesh position={[0, 0.02, 0.03]} rotation={[0, 0, 0.2]}>
          <coneGeometry args={[0.055, 0.16, 4]} />
          <meshStandardMaterial color={white} roughness={0.8} />
        </mesh>
      </group>
      {/* Right Ear */}
      <group ref={earRRRef} position={[-0.2, 1.32, 0.05]}>
        <mesh rotation={[0, 0, -0.2]}>
          <coneGeometry args={[0.1, 0.28, 4]} />
          <meshStandardMaterial color={orange} roughness={0.7} />
        </mesh>
        <mesh position={[0, 0.02, 0.03]} rotation={[0, 0, -0.2]}>
          <coneGeometry args={[0.055, 0.16, 4]} />
          <meshStandardMaterial color={white} roughness={0.8} />
        </mesh>
      </group>
      {/* Tail */}
      <group ref={tailRef} position={[0, 0.65, -0.32]}>
        <mesh rotation={[-0.8, 0, 0]}>
          <coneGeometry args={[0.18, 0.7, 8]} />
          <meshStandardMaterial color={orange} roughness={0.7} />
        </mesh>
        <mesh position={[0, -0.28, -0.25]} rotation={[-0.8, 0, 0]}>
          <coneGeometry args={[0.16, 0.35, 8]} />
          <meshStandardMaterial color={white} roughness={0.8} />
        </mesh>
      </group>
      {/* Front Legs */}
      <mesh position={[0.22, 0.2, 0.2]}>
        <cylinderGeometry args={[0.07, 0.07, 0.4, 8]} />
        <meshStandardMaterial color={orange} roughness={0.7} />
      </mesh>
      <mesh position={[-0.22, 0.2, 0.2]}>
        <cylinderGeometry args={[0.07, 0.07, 0.4, 8]} />
        <meshStandardMaterial color={orange} roughness={0.7} />
      </mesh>
      {/* Back Legs */}
      <mesh position={[0.22, 0.2, -0.15]}>
        <cylinderGeometry args={[0.07, 0.07, 0.4, 8]} />
        <meshStandardMaterial color={darkOrange} roughness={0.7} />
      </mesh>
      <mesh position={[-0.22, 0.2, -0.15]}>
        <cylinderGeometry args={[0.07, 0.07, 0.4, 8]} />
        <meshStandardMaterial color={darkOrange} roughness={0.7} />
      </mesh>
      {/* Paws */}
      <mesh position={[0.22, 0.0, 0.2]}>
        <boxGeometry args={[0.12, 0.06, 0.14]} />
        <meshStandardMaterial color={white} roughness={0.8} />
      </mesh>
      <mesh position={[-0.22, 0.0, 0.2]}>
        <boxGeometry args={[0.12, 0.06, 0.14]} />
        <meshStandardMaterial color={white} roughness={0.8} />
      </mesh>
      <mesh position={[0.22, 0.0, -0.15]}>
        <boxGeometry args={[0.12, 0.06, 0.14]} />
        <meshStandardMaterial color={white} roughness={0.8} />
      </mesh>
      <mesh position={[-0.22, 0.0, -0.15]}>
        <boxGeometry args={[0.12, 0.06, 0.14]} />
        <meshStandardMaterial color={white} roughness={0.8} />
      </mesh>
    </group>
  )
}

// ─── Trees ─────────────────────────────────────────────────────────────────────
function PineTree({ position, scale = 1, rotation = 0 }) {
  return (
    <group position={position} scale={scale} rotation={[0, rotation, 0]}>
      {/* Trunk */}
      <mesh position={[0, 0.5, 0]}>
        <cylinderGeometry args={[0.12, 0.18, 1.0, 6]} />
        <meshStandardMaterial color="#3d2510" roughness={1} />
      </mesh>
      {/* Bottom foliage */}
      <mesh position={[0, 1.5, 0]}>
        <coneGeometry args={[1.1, 1.6, 6]} />
        <meshStandardMaterial color="#2d5a2d" roughness={0.9} />
      </mesh>
      {/* Middle foliage */}
      <mesh position={[0, 2.4, 0]}>
        <coneGeometry args={[0.8, 1.4, 6]} />
        <meshStandardMaterial color="#366636" roughness={0.9} />
      </mesh>
      {/* Top foliage */}
      <mesh position={[0, 3.15, 0]}>
        <coneGeometry args={[0.5, 1.2, 6]} />
        <meshStandardMaterial color="#407040" roughness={0.9} />
      </mesh>
    </group>
  )
}

function DeciduousTree({ position, scale = 1, rotation = 0 }) {
  return (
    <group position={position} scale={scale} rotation={[0, rotation, 0]}>
      {/* Trunk */}
      <mesh position={[0, 0.8, 0]}>
        <cylinderGeometry args={[0.15, 0.22, 1.6, 6]} />
        <meshStandardMaterial color="#4a3020" roughness={1} />
      </mesh>
      {/* Canopy */}
      <mesh position={[0, 2.5, 0]}>
        <sphereGeometry args={[1.2, 8, 8]} />
        <meshStandardMaterial color="#2d5a2d" roughness={0.9} />
      </mesh>
      <mesh position={[0, 2.5, 0]}>
        <sphereGeometry args={[0.9, 8, 8]} />
        <meshStandardMaterial color="#3a6e3a" roughness={0.9} />
      </mesh>
    </group>
  )
}

// ─── Campfire ─────────────────────────────────────────────────────────────────
function Campfire({ position }) {
  const flame1Ref = useRef()
  const flame2Ref = useRef()
  const glowRef = useRef()
  const lightRef = useRef()

  useFrame((state) => {
    const t = state.clock.elapsedTime
    if (flame1Ref.current) {
      flame1Ref.current.scale.x = 1 + Math.sin(t * 8) * 0.15
      flame1Ref.current.scale.z = 1 + Math.cos(t * 6) * 0.12
      flame1Ref.current.scale.y = 1 + Math.sin(t * 10) * 0.2
    }
    if (flame2Ref.current) {
      flame2Ref.current.scale.x = 1 + Math.sin(t * 7 + 1) * 0.12
      flame2Ref.current.scale.z = 1 + Math.cos(t * 9 + 2) * 0.15
      flame2Ref.current.scale.y = 1 + Math.sin(t * 12) * 0.18
    }
    if (glowRef.current) {
      const s = 1 + Math.sin(t * 4) * 0.1
      glowRef.current.scale.set(s, s, s)
    }
    if (lightRef.current) {
      lightRef.current.intensity = 1.2 + Math.sin(t * 6) * 0.3
    }
  })

  return (
    <group position={position}>
      {/* Stone ring */}
      {[0, 1, 2, 3, 4, 5].map((i) => (
        <mesh key={i} position={[Math.cos(i * Math.PI / 3) * 0.4, 0.05, Math.sin(i * Math.PI / 3) * 0.4]}>
          <sphereGeometry args={[0.1, 5, 5]} />
          <meshStandardMaterial color="#555555" roughness={1} />
        </mesh>
      ))}
      {/* Logs */}
      <mesh position={[0.15, 0.05, 0]} rotation={[0, 0.3, Math.PI / 2]}>
        <cylinderGeometry args={[0.05, 0.05, 0.5, 6]} />
        <meshStandardMaterial color="#3d2010" roughness={1} />
      </mesh>
      <mesh position={[-0.15, 0.05, 0]} rotation={[0, -0.3, Math.PI / 2]}>
        <cylinderGeometry args={[0.05, 0.05, 0.5, 6]} />
        <meshStandardMaterial color="#3d2010" roughness={1} />
      </mesh>
      {/* Flames */}
      <mesh ref={flame1Ref} position={[0, 0.35, 0]}>
        <coneGeometry args={[0.18, 0.6, 6]} />
        <meshStandardMaterial color="#ff4400" emissive="#ff2200" emissiveIntensity={2} transparent opacity={0.85} />
      </mesh>
      <mesh ref={flame2Ref} position={[0.05, 0.45, 0.05]}>
        <coneGeometry args={[0.12, 0.45, 6]} />
        <meshStandardMaterial color="#ff8800" emissive="#ff6600" emissiveIntensity={2} transparent opacity={0.8} />
      </mesh>
      <mesh ref={glowRef} position={[0, 0.5, 0]}>
        <sphereGeometry args={[0.25, 8, 8]} />
        <meshStandardMaterial color="#ffaa00" emissive="#ff8800" emissiveIntensity={1.5} transparent opacity={0.3} />
      </mesh>
      <pointLight ref={lightRef} color="#ff6600" intensity={3.0} distance={12} position={[0, 1, 0]} castShadow shadow-mapSize-width={512} shadow-mapSize-height={512} />
    </group>
  )
}

// ─── Fireflies ────────────────────────────────────────────────────────────────
function Fireflies({ count = 40 }) {
  const groupRef = useRef()
  const positionsRef = useRef([])

  const positions = useRef(
    Array.from({ length: count }, () => ({
      x: (Math.random() - 0.5) * 16,
      y: Math.random() * 3 + 0.5,
      z: (Math.random() - 0.5) * 16,
      speed: Math.random() * 0.5 + 0.3,
      offset: Math.random() * Math.PI * 2,
    }))
  )

  useFrame((state) => {
    const t = state.clock.elapsedTime
    if (!groupRef.current) return
    const children = groupRef.current.children
    for (let i = 0; i < children.length; i++) {
      const p = positions.current[i]
      children[i].position.x = p.x + Math.sin(t * p.speed + p.offset) * 0.8
      children[i].position.y = p.y + Math.sin(t * p.speed * 1.3 + p.offset) * 0.5
      children[i].position.z = p.z + Math.cos(t * p.speed * 0.8 + p.offset) * 0.8
      const glow = 0.3 + Math.sin(t * 3 + p.offset) * 0.3
      children[i].material.opacity = glow
    }
  })

  return (
    <group ref={groupRef}>
      {positions.current.map((p, i) => (
        <mesh key={i} position={[p.x, p.y, p.z]}>
          <sphereGeometry args={[0.04, 6, 6]} />
          <meshStandardMaterial color="#aaffaa" emissive="#88ff88" emissiveIntensity={2} transparent opacity={0.5} />
        </mesh>
      ))}
    </group>
  )
}

// ─── Rocks ────────────────────────────────────────────────────────────────────
function Rock({ position, scale = 1, rotation = 0 }) {
  return (
    <group position={position} scale={scale} rotation={[0, rotation, 0]}>
      <mesh>
        <dodecahedronGeometry args={[0.3, 0]} />
        <meshStandardMaterial color="#444444" roughness={1} />
      </mesh>
    </group>
  )
}

// ─── Tent ─────────────────────────────────────────────────────────────────────
function Tent({ position }) {
  return (
    <group position={position}>
      {/* Tent body */}
      <mesh position={[0, 0.5, 0]} rotation={[0, 0.5, 0]}>
        <coneGeometry args={[1.0, 1.2, 4]} />
        <meshStandardMaterial color="#c45e5e" roughness={0.8} />
      </mesh>
      {/* Tent opening (darker) */}
      <mesh position={[0.2, 0.35, 0.15]} rotation={[0, 0.5, 0]}>
        <coneGeometry args={[0.3, 0.6, 4]} />
        <meshStandardMaterial color="#1a1a1a" roughness={1} />
      </mesh>
    </group>
  )
}

// ─── Camping Chair ────────────────────────────────────────────────────────────
function CampingChair({ position, rotation = 0 }) {
  return (
    <group position={position} rotation={[0, rotation, 0]}>
      {/* Seat */}
      <mesh position={[0, 0.3, 0]}>
        <boxGeometry args={[0.5, 0.05, 0.5]} />
        <meshStandardMaterial color="#2255aa" roughness={0.8} />
      </mesh>
      {/* Back */}
      <mesh position={[0, 0.55, -0.22]} rotation={[0.3, 0, 0]}>
        <boxGeometry args={[0.5, 0.5, 0.05]} />
        <meshStandardMaterial color="#2255aa" roughness={0.8} />
      </mesh>
      {/* Frame */}
      {[[-0.2, -0.2], [0.2, -0.2], [-0.2, 0.2], [0.2, 0.2]].map(([x, z], i) => (
        <mesh key={i} position={[x, 0.15, z]}>
          <cylinderGeometry args={[0.02, 0.02, 0.3, 4]} />
          <meshStandardMaterial color="#888888" metalness={0.8} roughness={0.3} />
        </mesh>
      ))}
    </group>
  )
}

// ─── Grass Tufts ─────────────────────────────────────────────────────────────
function GrassTuft({ position }) {
  return (
    <group position={position}>
      {[0, 1, 2].map((i) => (
        <mesh key={i} position={[i * 0.08 - 0.08, 0.1, 0]} rotation={[0, i * 0.8, 0]}>
          <coneGeometry args={[0.03, 0.25, 3]} />
          <meshStandardMaterial color="#2d6a2d" roughness={0.9} />
        </mesh>
      ))}
    </group>
  )
}

// ─── Forest Floor ────────────────────────────────────────────────────────────
function ForestFloor() {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.02, 0]} receiveShadow>
      <planeGeometry args={[50, 50, 8, 8]} />
      <meshStandardMaterial color="#1a2e1a" roughness={1} />
    </mesh>
  )
}

// ─── Skybox ───────────────────────────────────────────────────────────────────
const STAR_POSITIONS = Array.from({ length: 400 }, () => ({
  x: (Math.random() - 0.5) * 250,
  y: Math.random() * 90 + 8,
  z: (Math.random() - 0.5) * 250,
  s: Math.random() * 0.06 + 0.02,
}))

function Stars() {
  return (
    <>
      {STAR_POSITIONS.map((star, i) => (
        <mesh key={i} position={[star.x, star.y, star.z]}>
          <sphereGeometry args={[star.s, 4, 4]} />
          <meshBasicMaterial color="#ffffff" transparent opacity={0.85} />
        </mesh>
      ))}
    </>
  )
}

function Moon() {
  const glowRef = useRef()
  useFrame((state) => {
    if (glowRef.current) {
      const s = 1 + Math.sin(state.clock.elapsedTime * 0.5) * 0.02
      glowRef.current.scale.set(s, s, s)
    }
  })
  return (
    <group position={[30, 45, -60]}>
      <mesh>
        <sphereGeometry args={[4, 32, 32]} />
        <meshStandardMaterial color="#e8e4d8" roughness={0.9} metalness={0} />
      </mesh>
      <mesh ref={glowRef}>
        <sphereGeometry args={[5.5, 32, 32]} />
        <meshBasicMaterial color="#c8d8ff" transparent opacity={0.12} />
      </mesh>
      <mesh position={[1, 1, 3.5]}>
        <sphereGeometry args={[0.6, 16, 16]} />
        <meshStandardMaterial color="#ccc8b8" roughness={1} />
      </mesh>
      <mesh position={[-1.5, -0.5, 3.2]}>
        <sphereGeometry args={[0.4, 16, 16]} />
        <meshStandardMaterial color="#ccc8b8" roughness={1} />
      </mesh>
      <mesh position={[0.5, 2, 3.0]}>
        <sphereGeometry args={[0.35, 16, 16]} />
        <meshStandardMaterial color="#ccc8b8" roughness={1} />
      </mesh>
    </group>
  )
}

function NightSky() {
  return (
    <>
      <color attach="background" args={['#060c18']} />
      <fog attach="fog" args={['#060c18', 20, 60]} />
      <Stars />
      <Moon />
    </>
  )
}

// ─── Forest Camp (Full Scene) ────────────────────────────────────────────────
function ForestCamp() {
  return (
    <>
      <NightSky />
      {/* Moonlight — main outdoor light source */}
      <directionalLight position={[30, 50, -60]} intensity={1.4} color="#c8d8f0" castShadow shadow-mapSize-width={2048} shadow-mapSize-height={2048} shadow-camera-far={100} shadow-camera-left={-20} shadow-camera-right={20} shadow-camera-top={20} shadow-camera-bottom={-20} />
      <ambientLight intensity={0.2} color="#223355" />
      <pointLight position={[0, 8, 0]} intensity={0.4} color="#6688aa" distance={35} />
      <pointLight position={[-8, 4, -8]} intensity={0.3} color="#334422" distance={25} />
      <pointLight position={[8, 4, 8]} intensity={0.3} color="#334422" distance={25} />

      {/* Forest Floor */}
      <ForestFloor />

      {/* ── Pine Trees ── */}
      <PineTree position={[-7, 0, -7]} scale={1.6} rotation={0.3} />
      <PineTree position={[-9, 0, -3]} scale={1.2} rotation={1.1} />
      <PineTree position={[-6, 0, -10]} scale={1.8} rotation={2.5} />
      <PineTree position={[7, 0, -8]} scale={1.4} rotation={0.7} />
      <PineTree position={[9, 0, -3]} scale={1.3} rotation={3.2} />
      <PineTree position={[6, 0, -11]} scale={1.7} rotation={1.8} />
      <PineTree position={[-8, 0, 6]} scale={1.5} rotation={2.1} />
      <PineTree position={[8, 0, 7]} scale={1.2} rotation={0.4} />
      <PineTree position={[0, 0, -13]} scale={2.0} rotation={1.5} />
      <PineTree position={[-11, 0, -9]} scale={1.0} rotation={2.8} />
      <PineTree position={[11, 0, -9]} scale={1.1} rotation={3.7} />
      <PineTree position={[-5, 0, -13]} scale={1.3} rotation={1.2} />
      <PineTree position={[5, 0, -13]} scale={1.4} rotation={0.9} />
      <PineTree position={[-12, 0, 2]} scale={0.9} rotation={2.3} />
      <PineTree position={[12, 0, 2]} scale={1.0} rotation={1.6} />

      {/* ── Deciduous Trees ── */}
      <DeciduousTree position={[-10, 0, 0]} scale={1.3} rotation={0.5} />
      <DeciduousTree position={[10, 0, 0]} scale={1.2} rotation={2.1} />
      <DeciduousTree position={[-4, 0, -8]} scale={1.0} rotation={1.3} />
      <DeciduousTree position={[4, 0, -9]} scale={1.1} rotation={3.0} />

      {/* ── Rocks ── */}
      <Rock position={[-3, 0, -4]} scale={1.2} rotation={0.5} />
      <Rock position={[4, 0, -3]} scale={0.8} rotation={1.2} />
      <Rock position={[-5, 0, 3]} scale={1.0} rotation={2.1} />
      <Rock position={[3, 0, 4]} scale={0.7} rotation={0.8} />
      <Rock position={[0, 0, -6]} scale={0.5} rotation={1.7} />

      {/* ── Grass Tufts ── */}
      {[[-2, 0, -3], [3, 0, -2], [-4, 0, 2], [2, 0, 3], [-1, 0, -5], [5, 0, -5]].map(([x, y, z], i) => (
        <GrassTuft key={i} position={[x, y, z]} />
      ))}

      {/* ── Campfire ── */}
      <Campfire position={[0, 0, 0]} />

      {/* ── Tent ── */}
      <Tent position={[-2.5, 0, -1.5]} />

      {/* ── Camping Chair ── */}
      <CampingChair position={[1.5, 0, 1.2]} rotation={-0.5} />

      {/* ── Sig Fox ── */}
      <Fox position={[0, 0, 1.8]} />

      {/* Campfire warm glow on fox */}
      <pointLight position={[0, 0.5, 0]} color="#ff5500" intensity={0.8} distance={5} />

      {/* ── Fireflies ── */}
      <Fireflies count={45} />
    </>
  )
}

// ─── System Block (kept from original) ────────────────────────────────────────
function SystemBlock({ position, color, label, speed = 1, size = 0.6, pulseRef }) {
  const ref = useRef()

  useFrame((state) => {
    if (ref.current) {
      ref.current.rotation.x += 0.005 * speed
      ref.current.rotation.y += 0.008 * speed
      ref.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * speed + position[0]) * 0.3
    }
    if (pulseRef?.current) {
      pulseRef.current.rotation.y += 0.02 * speed
    }
  })

  return (
    <group position={position}>
      <mesh ref={ref}>
        <boxGeometry args={[size, size, size]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.3} roughness={0.3} metalness={0.6} />
      </mesh>
      {pulseRef && (
        <mesh ref={pulseRef} position={[0, 0, 0]}>
          <sphereGeometry args={[size * 0.6, 8, 8]} />
          <meshBasicMaterial color={color} transparent opacity={0.15} />
        </mesh>
      )}
    </group>
  )
}

// ─── World (with floating blocks + forest) ───────────────────────────────────
function World({ activeBlock }) {
  const { camera } = useThree()
  const blockRefs = {
    HEART: useRef(), MEMORY: useRef(), SCANNER: useRef(), GIT: useRef(), CRON: useRef(),
  }

  useEffect(() => {
    camera.position.set(0, 6, 14)
    camera.lookAt(0, 1, 0)
  }, [camera])

  useFrame((state) => {
    const key = activeBlock
    if (key && blockRefs[key]?.current) {
      const s = 1 + Math.sin(state.clock.elapsedTime * 4) * 0.15
      blockRefs[key].current.scale.set(s, s, s)
    }
  })

  return (
    <>
      <ForestCamp />

      {/* Floating system blocks — orbit around the forest */}
      <SystemBlock ref={blockRefs.HEART} position={[7, 3, 0]} color={C.accent} label="HEART" speed={1.2} size={0.7} />
      <SystemBlock ref={blockRefs.MEMORY} position={[-7, 4, 1]} color={C.accent2} label="MEM" speed={0.8} size={0.6} />
      <SystemBlock ref={blockRefs.SCANNER} position={[0, 5, -7]} color={C.accent3} label="SCAN" speed={1.5} size={0.5} />
      <SystemBlock ref={blockRefs.GIT} position={[-6, 2.5, -6]} color={C.warning} label="GIT" speed={0.6} size={0.55} />
      <SystemBlock ref={blockRefs.CRON} position={[6, 2, 5]} color={C.success} label="CRON" speed={1.0} size={0.65} />

      <OrbitControls enablePan={false} minDistance={5} maxDistance={35} maxPolarAngle={Math.PI / 2.1} autoRotate autoRotateSpeed={0.3} />
    </>
  )
}

// ─── Panel primitives ──────────────────────────────────────────────────────────
function Panel({ title, children, accent = C.accent, style }) {
  return (
    <div style={{
      background: C.panel,
      border: `1px solid ${C.border}`,
      borderTop: `2px solid ${accent}`,
      borderRadius: 4,
      padding: '10px 12px',
      display: 'flex',
      flexDirection: 'column',
      gap: 7,
      minWidth: 0,
      ...style,
    }}>
      <div style={{ color: accent, fontSize: 9, letterSpacing: 2, textTransform: 'uppercase', marginBottom: 2 }}>
        {title}
      </div>
      {children}
    </div>
  )
}

function StatRow({ label, value, color = C.text, small }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: small ? 10 : 11, minWidth: 0 }}>
      <span style={{ color: C.dim, flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis' }}>{label}</span>
      <span style={{ color, fontWeight: 'bold', marginLeft: 8, flexShrink: 0 }}>{value}</span>
    </div>
  )
}

function StatusDot({ color = C.success, large }) {
  return (
    <span style={{
      display: 'inline-block',
      width: large ? 8 : 6,
      height: large ? 8 : 6,
      borderRadius: '50%',
      background: color,
      boxShadow: `0 0 6px ${color}`,
      marginRight: 6,
      verticalAlign: 'middle',
      flexShrink: 0,
    }} />
  )
}

function PulseBar({ value = 1, color = C.accent }) {
  return (
    <div style={{ background: C.border, borderRadius: 2, height: 3, overflow: 'hidden' }}>
      <div style={{
        width: `${Math.min(100, value * 100)}%`,
        height: '100%',
        background: color,
        boxShadow: `0 0 6px ${color}`,
        transition: 'width 0.5s ease',
      }} />
    </div>
  )
}

// ─── Action Buttons ────────────────────────────────────────────────────────────
function ActionBtn({ label, onClick, loading, accent = C.accent, icon }) {
  const [hover, setHover] = useState(false)
  const [pressed, setPressed] = useState(false)

  return (
    <button
      onClick={onClick}
      disabled={loading}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => { setHover(false); setPressed(false) }}
      onMouseDown={() => setPressed(true)}
      onMouseUp={() => setPressed(false)}
      style={{
        background: loading ? `${accent}15` : pressed ? `${accent}30` : hover ? `${accent}22` : 'transparent',
        border: `1px solid ${loading ? accent + '40' : hover ? accent : C.border}`,
        color: loading ? accent + 'aa' : hover ? accent : C.text,
        padding: '5px 8px',
        borderRadius: 3,
        fontSize: 10,
        fontFamily: 'inherit',
        cursor: loading ? 'not-allowed' : 'pointer',
        textAlign: 'left',
        transition: 'all 0.12s',
        marginBottom: 3,
        display: 'flex',
        alignItems: 'center',
        gap: 6,
        opacity: pressed ? 0.8 : 1,
      }}
    >
      {loading ? '⏳' : icon || '▶'} {label}
    </button>
  )
}

// ─── Output Log ────────────────────────────────────────────────────────────────
function OutputLog({ entries }) {
    const bottomRef = useRef(null)
    useEffect(() => {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [entries])

    return (
      <div style={{
        borderTop: `1px solid ${C.border}`,
        background: `${C.panelDark}f0`,
        flex: 1,
        overflowY: 'auto',
        padding: '8px 12px',
        display: 'flex',
        flexDirection: 'column',
        gap: 4,
        minHeight: 0,
      }}>
        {entries.length === 0 && (
          <div style={{ color: C.dim, fontSize: 10, fontStyle: 'italic' }}>
            Action output will appear here...
          </div>
        )}
        {entries.map((e, i) => (
          <div key={i} style={{ fontSize: 10, lineHeight: 1.5 }}>
            <span style={{ color: C.dim, marginRight: 8 }}>{e.time}</span>
            <span style={{
              color: e.type === 'ok' ? C.success : e.type === 'err' ? C.danger : e.type === 'info' ? C.accent : C.text,
              fontWeight: 'bold',
              marginRight: 8,
            }}>[{e.type.toUpperCase()}]</span>
            <span style={{ color: C.text }}>{e.msg}</span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    )
}

// ─── Main App ─────────────────────────────────────────────────────────────────
export default function App() {
  const [tick, setTick] = useState(0)
  const [status, setStatus] = useState(null)
  const [activeBlock, setActiveBlock] = useState(null)
  const [loading, setLoading] = useState({})
  const [logEntries, setLogEntries] = useState([])
  const time = new Date().toLocaleTimeString('en-US', { timeZone: 'America/New_York' })
  const date = new Date().toLocaleDateString('en-US', { timeZone: 'America/New_York', weekday: 'short', month: 'short', day: 'numeric' })

  const addLog = useCallback((msg, type = 'info') => {
    const t = new Date().toLocaleTimeString('en-US', { timeZone: 'America/New_York', hour12: false })
    setLogEntries(prev => [...prev.slice(-50), { time: t, msg, type }])
  }, [])

  const doAction = useCallback(async (actionKey, label, blockKey) => {
    if (loading[actionKey]) return
    setLoading(prev => ({ ...prev, [actionKey]: true }))
    setActiveBlock(blockKey)
    addLog(`Starting: ${label}`, 'info')

    try {
      const result = await apiAction(actionKey)
      if (result.ok) {
        addLog(`✓ ${result.summary || label}`, 'ok')
        if (result.details) {
          const d = result.details
          if (d.branch) addLog(`  branch: ${d.branch}`, 'text')
          if (d.status) addLog(`  ${d.status || '(clean)'}`, 'text')
          if (d.log) addLog(`  ${d.log.split('\n').join('\n  ')}`, 'text')
          if (d.newArticles !== undefined) addLog(`  ${d.newArticles} new articles`, 'text')
          if (d.crons) {
            d.crons.split('\n').filter(l => l.trim()).forEach(l => addLog(`  ${l.trim()}`, 'text'))
          }
          if (d.output) addLog(`  ${d.output}`, 'text')
          if (d.scan) {
            const newCount = (d.scan.match(/New: \d+/g) || []).join(', ')
            if (newCount) addLog(`  ${newCount}`, 'text')
          }
        }
      } else {
        addLog(`✗ ${result.error || 'Failed'}`, 'err')
      }
    } catch (e) {
      addLog(`✗ ${e.message}`, 'err')
    } finally {
      setLoading(prev => ({ ...prev, [actionKey]: false }))
      setActiveBlock(null)
      setTick(t => t + 1)
    }
  }, [loading, addLog])

  useEffect(() => {
    const id = setInterval(async () => {
      const s = await apiStatus()
      if (s) setStatus(s)
    }, 15000)
    return () => clearInterval(id)
  }, [])

  useEffect(() => {
    apiStatus().then(s => { if (s) setStatus(s) })
  }, [])

  useEffect(() => {
    const id = setInterval(() => setTick(t => t + 1), 1000)
    return () => clearInterval(id)
  }, [])

  const actions = [
    { key: 'refresh', label: 'Refresh heartbeat', icon: '🔄', block: 'HEART' },
    { key: 'scan-rss', label: 'Scan RSS feeds', icon: '🔍', block: 'SCANNER' },
    { key: 'git-status', label: 'Git status', icon: '📁', block: 'GIT' },
    { key: 'run-scanner', label: 'Run scanner now', icon: '📊', block: 'SCANNER' },
    { key: 'sync-memory', label: 'Sync memory', icon: '🧠', block: 'MEMORY' },
    { key: 'list-crons', label: 'List crons', icon: '⏱', block: 'CRON' },
    { key: 'openclaw-status', label: 'OpenClaw status', icon: '⚙', block: 'HEART' },
  ]

  return (
    <div style={{
      width: '100vw', height: '100vh',
      background: C.bg,
      display: 'flex',
      flexDirection: 'column',
      color: C.text,
      overflow: 'hidden',
    }}>
      {/* ── Header ─────────────────────────────────────────────── */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '8px 16px',
        borderBottom: `1px solid ${C.border}`,
        background: `${C.panel}ee`,
        flexShrink: 0,
        zIndex: 10,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div style={{ fontSize: 20 }}>🐾</div>
          <div>
            <div style={{ fontSize: 14, fontWeight: 'bold', color: C.accent, letterSpacing: 2 }}>SIGBOTTI OS</div>
            <div style={{ fontSize: 9, color: C.dim, letterSpacing: 1 }}>AUTONOMOUS AGI CORE</div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
          {[
            { label: 'OC', ok: true },
            { label: 'GW', ok: true },
            { label: 'OLL', ok: true },
            { label: 'BLOG', ok: true },
          ].map(({ label, ok }) => (
            <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 9 }}>
              <StatusDot color={ok ? C.success : C.danger} />
              <span style={{ color: C.dim }}>{label}</span>
            </div>
          ))}
        </div>

        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: 11, color: C.text }}>{date}</div>
          <div style={{ fontSize: 11, color: C.accent, fontVariantNumeric: 'tabular-nums' }}>{time}</div>
        </div>
      </div>

      {/* ── Main ──────────────────────────────────────────────── */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>

        {/* ── Left panels ─────────────────────────────────────── */}
        <div style={{
          width: 220,
          display: 'flex',
          flexDirection: 'column',
          gap: 8,
          padding: 10,
          overflowY: 'auto',
          borderRight: `1px solid ${C.border}`,
          flexShrink: 0,
        }}>
          <Panel title="❤️ Heartbeat" accent={C.accent}>
            <StatRow label="Status" value="ACTIVE" color={C.success} />
            <StatRow label="Interval" value="30 min" />
            <PulseBar value={0.82} color={C.accent} />
            <StatRow label="RSS feeds" value="5" />
            <StatRow label="New articles" value="2 unread" color={C.warning} />
            <StatRow label="Last scan" value={time} small />
          </Panel>

          <Panel title="🧠 Memory" accent={C.accent2}>
            <StatRow label="Long-term" value="MEMORY.md" />
            <StatRow label="Hot RAM" value="SESSION" />
            <StatRow label="Daily logs" value="14 days" />
            <StatRow label="Vector store" value="active" color={C.success} />
            <StatRow label="Learnings" value="~20" />
          </Panel>

          <Panel title="🔍 Scanner" accent={C.accent3}>
            <StatRow label="Universe" value="43 stocks" />
            <StatRow label="Last run" value="midnight" color={C.dim} />
            <StatRow label="Next run" value="midnight ET" color={C.accent} />
            <StatRow label="Last signals" value="21 found" color={C.success} />
          </Panel>

          <Panel title="⏱ Crons" accent={C.warning}>
            <StatRow label="Self-review" value="9:00 AM ET" />
            <StatRow label="Scanner" value="midnight ET" />
            <StatRow label="Backup" value="hourly" />
            <StatRow label="Self-eval" value="~21d" color={C.dim} />
          </Panel>

          <Panel title="🦊 Agent" accent={C.accent}>
            <StatRow label="Model" value="MiniMax-M2" />
            <StatRow label="Benchmark" value="3.1 / 5" color={C.warning} />
            <StatRow label="Skills" value="~30" />
            <StatRow label="Session" value="main" />
          </Panel>
        </div>

        {/* ── World viewport ──────────────────────────────────── */}
        <div style={{ flex: 1, position: 'relative', minWidth: 0 }}>
          <Canvas
            gl={{ antialias: true, powerPreference: 'high-performance', toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.2 }}
            shadows
            style={{ position: 'absolute', inset: 0 }}
          >
            <Suspense fallback={null}>
              <World activeBlock={activeBlock} />
            </Suspense>
          </Canvas>

          <div style={{
            position: 'absolute', top: 10, right: 10,
            background: `${C.panel}cc`,
            border: `1px solid ${C.border}`,
            borderRadius: 4,
            padding: '8px 10px',
            display: 'flex',
            flexDirection: 'column',
            gap: 5,
          }}>
            {[
              { label: 'HEART', color: C.accent },
              { label: 'MEMORY', color: C.accent2 },
              { label: 'SCANNER', color: C.accent3 },
              { label: 'CRON', color: C.success },
              { label: 'GIT', color: C.warning },
            ].map(({ label, color }) => (
              <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 9, letterSpacing: 1 }}>
                <StatusDot color={activeBlock === label ? color : color + '80'} large />
                <span style={{ color: activeBlock === label ? color : C.dim }}>{label}</span>
              </div>
            ))}
          </div>

          <div style={{
            position: 'absolute', bottom: 10, left: 12,
            fontSize: 9, color: C.dim, letterSpacing: 1,
          }}>
            DRAG TO ORBIT · SCROLL TO ZOOM
          </div>

          {activeBlock && (
            <div style={{
              position: 'absolute', top: 10, left: 12,
              fontSize: 10, color: C.accent,
              letterSpacing: 1,
              animation: 'pulse 1s ease-in-out infinite',
              background: `${C.panel}88`,
              padding: '4px 8px',
              borderRadius: 3,
              border: `1px solid ${C.accent}40`,
            }}>
              ⚡ {activeBlock} ACTIVE
            </div>
          )}
        </div>

        {/* ── Right panels ────────────────────────────────────── */}
        <div style={{
          width: 220,
          display: 'flex',
          flexDirection: 'column',
          gap: 8,
          padding: 10,
          overflowY: 'auto',
          borderLeft: `1px solid ${C.border}`,
          flexShrink: 0,
        }}>
          <Panel title="⚡ Actions" accent={C.warning}>
            {actions.map(a => (
              <ActionBtn
                key={a.key}
                label={a.label}
                icon={a.icon}
                loading={!!loading[a.key]}
                accent={C.warning}
                onClick={() => doAction(a.key, a.label, a.block)}
              />
            ))}
          </Panel>

          <Panel title="⚙ Systems" accent={C.dim}>
            <StatRow label="OpenClaw" value="running" color={C.success} />
            <StatRow label="Gateway" value="online" color={C.success} />
            <StatRow label="Ollama" value="connected" color={C.success} />
            <StatRow label="Blogwatcher" value="active" color={C.success} />
            <StatRow label="PerfectPlace" value="ok" color={C.success} />
          </Panel>

          <Panel title="📋 Output Log" accent={C.accent3} style={{ flex: 1, minHeight: 120 }}>
            <OutputLog entries={logEntries} />
          </Panel>
        </div>
      </div>

      {/* ── Footer ─────────────────────────────────────────────── */}
      <div style={{
        padding: '5px 16px',
        borderTop: `1px solid ${C.border}`,
        background: `${C.panel}cc`,
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: 9,
        color: C.dim,
        flexShrink: 0,
        letterSpacing: 1,
      }}>
        <span>🐾 SIGBOTTI OS — Autonomous AGI Control Interface</span>
        <span>TICK #{tick}</span>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: ${C.border}; border-radius: 2px; }
      `}</style>
    </div>
  )
}
