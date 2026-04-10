import * as THREE from 'three';

// ─── Coordinate Projection ─────────────────────────────────────────────────────
// Convert lat/lon to local scene coordinates (meters from center)
// Using Web Mercator approximation

export interface LatLon { lat: number; lon: number }

export function projectToScene(lat: number, lon: number, center: LatLon): { x: number; z: number } {
  const R = 6378137; // Earth radius in meters
  const latCircumference = 2 * Math.PI * R;
  const lonCircumference = Math.cos(center.lat * Math.PI / 180) * latCircumference;
  
  const x = (lon - center.lon) / 360 * lonCircumference;
  const z = (lat - center.lat) / 360 * latCircumference;
  
  return { x, z };
}

// ─── Building Colors ──────────────────────────────────────────────────────────

const BUILDING_COLORS: Record<string, string> = {
  'yes': '#8B7355',           // generic brown/tan
  'house': '#9B8B7A',         // rowhouse tan
  'semidetached_house': '#A89080',
  'residential': '#9B8B7A',
  'apartments': '#7A8B9B',    // slightly blue-gray
  'retail': '#6B8B7A',        // greenish commercial
  'commercial': '#6B8B7A',
  'office': '#5B7B8B',
  'terrace': '#8B7B65',
  'transportation': '#4B5B6B',
  'industrial': '#5B5B5B',
  'warehouse': '#5B5B5B',
  'school': '#8B7B9B',
  'religious': '#9B8B9B',
  'hospital': '#9B6B6B',
  'hotel': '#7B8B9B',
  'civic': '#8B9B8B',
};

// ─── Road Colors ───────────────────────────────────────────────────────────────

const ROAD_COLOR = '#1a1a1a';       // dark asphalt
const ROAD_LINE_COLOR = '#d4a84b';   // yellow center lines
const SIDEWALK_COLOR = '#c4b89a';    // concrete sidewalk

// ─── Building Geometry ────────────────────────────────────────────────────────

export interface BuildingData {
  height: number;
  type: string;
  name: string;
  polygon: [number, number][];  // [lat, lon][]
}

export function createBuildingMesh(
  data: BuildingData,
  center: LatLon,
  groundY = 0
): THREE.Mesh {
  const points = data.polygon.map(([lat, lon]) => {
    const { x, z } = projectToScene(lat, lon, center);
    return new THREE.Vector2(x, z);
  });

  const shape = new THREE.Shape(points);
  const geometry = new THREE.ExtrudeGeometry(shape, {
    depth: data.height,
    bevelEnabled: false,
  });

  geometry.rotateX(-Math.PI / 2);  // extrude upward
  geometry.translate(0, groundY, 0);

  const color = BUILDING_COLORS[data.type.toLowerCase()] || BUILDING_COLORS['yes'];
  const material = new THREE.MeshStandardMaterial({
    color,
    roughness: 0.85,
    metalness: 0.05,
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  mesh.name = data.name;

  return mesh;
}

// ─── Road Geometry ────────────────────────────────────────────────────────────

export interface StreetEdge {
  u_lat: number; u_lon: number;
  v_lat: number; v_lon: number;
  highway: string;
  lanes: number;
}

export function createRoadMesh(
  edges: StreetEdge[],
  center: LatLon,
  groundY = 0
): THREE.Group {
  const group = new THREE.Group();

  const isDriveable = (h: string) =>
    !['footway', 'path', 'cycleway', 'steps'].includes(h.toLowerCase());

  const driveable = edges.filter(e => isDriveable(e.highway));
  const pedestrian = edges.filter(e => !isDriveable(e.highway));

  const roadMat = new THREE.MeshStandardMaterial({ color: ROAD_COLOR, roughness: 0.95 });
  const sidewalkMat = new THREE.MeshStandardMaterial({ color: SIDEWALK_COLOR, roughness: 0.9 });

  // Roads
  for (const edge of driveable) {
    const u = projectToScene(edge.u_lat, edge.u_lon, center);
    const v = projectToScene(edge.v_lat, edge.v_lon, center);

    const width = edge.lanes ? Math.max(4, Number(edge.lanes) * 2) : 6;

    const dx = v.x - u.x;
    const dz = v.z - u.z;
    const length = Math.sqrt(dx * dx + dz * dz);
    if (length < 0.1) continue;

    const geometry = new THREE.PlaneGeometry(length, width);
    geometry.rotateX(-Math.PI / 2);
    geometry.translate((u.x + v.x) / 2, groundY + 0.01, (u.z + v.z) / 2);

    // Rotate to align with road direction
    const angle = Math.atan2(dx, dz);
    geometry.rotateY(-angle);

    const mesh = new THREE.Mesh(geometry, roadMat);
    mesh.receiveShadow = true;
    group.add(mesh);

    // Center yellow line
    const lineGeom = new THREE.PlaneGeometry(length, 0.15);
    lineGeom.rotateX(-Math.PI / 2);
    lineGeom.translate((u.x + v.x) / 2, groundY + 0.02, (u.z + v.z) / 2);
    lineGeom.rotateY(-angle);
    const lineMat = new THREE.MeshStandardMaterial({ color: ROAD_LINE_COLOR, roughness: 0.5, emissive: ROAD_LINE_COLOR, emissiveIntensity: 0.1 });
    const line = new THREE.Mesh(lineGeom, lineMat);
    group.add(line);
  }

  // Footways / sidewalks
  for (const edge of pedestrian) {
    const u = projectToScene(edge.u_lat, edge.u_lon, center);
    const v = projectToScene(edge.v_lat, edge.v_lon, center);

    const dx = v.x - u.x;
    const dz = v.z - u.z;
    const length = Math.sqrt(dx * dx + dz * dz);
    if (length < 0.1) continue;

    const geometry = new THREE.PlaneGeometry(length, 2);
    geometry.rotateX(-Math.PI / 2);
    geometry.translate((u.x + v.x) / 2, groundY + 0.005, (u.z + v.z) / 2);

    const angle = Math.atan2(dx, dz);
    geometry.rotateY(-angle);

    const mesh = new THREE.Mesh(geometry, sidewalkMat);
    mesh.receiveShadow = true;
    group.add(mesh);
  }

  return group;
}

// ─── Ground Plane ────────────────────────────────────────────────────────────

export function createGroundPlane(center: LatLon, radius = 800): THREE.Mesh {
  const geometry = new THREE.PlaneGeometry(radius * 2, radius * 2);
  geometry.rotateX(-Math.PI / 2);
  const material = new THREE.MeshStandardMaterial({
    color: '#1a1a18',  // dark asphalt ground
    roughness: 1.0,
  });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.set(0, -0.02, 0);
  mesh.receiveShadow = true;
  return mesh;
}

// ─── Grid Helper (subtle) ─────────────────────────────────────────────────────

export function createGrid(center: LatLon): THREE.GridHelper {
  const size = 800;
  const divisions = 40;
  const grid = new THREE.GridHelper(size, divisions, '#2a2a2a', '#1e1e1e');
  grid.position.y = 0.01;
  return grid;
}
