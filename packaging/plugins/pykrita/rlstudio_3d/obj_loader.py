"""
RL Studio - Fast Wavefront OBJ 3D Model Parser & Normalizer
Reads .obj geometry, calculates bounding box, centers and normalizes scale.
"""

import math

class ModelMesh:
    def __init__(self, name="Mesh"):
        self.name = name
        self.vertices = []      # Flat list: [x0, y0, z0, x1, y1, z1, ...]
        self.normals = []       # Flat list: [nx0, ny0, nz0, ...]
        self.wire_indices = []  # Flat line indices: [i0, i1, i1, i2, ...]
        self.triangle_count = 0
        self.vertex_count = 0

class OBJLoader:
    @staticmethod
    def load(filepath):
        raw_v = []
        raw_vn = []
        faces = []

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = line.split()
                    if not parts:
                        continue
                    prefix = parts[0]

                    if prefix == 'v':
                        raw_v.append([float(parts[1]), float(parts[2]), float(parts[3])])
                    elif prefix == 'vn':
                        raw_vn.append([float(parts[1]), float(parts[2]), float(parts[3])])
                    elif prefix == 'f':
                        face_v = []
                        face_vn = []
                        for token in parts[1:]:
                            sub = token.split('/')
                            v_idx = int(sub[0]) - 1 if int(sub[0]) > 0 else len(raw_v) + int(sub[0])
                            face_v.append(v_idx)
                            if len(sub) >= 3 and sub[2]:
                                vn_idx = int(sub[2]) - 1 if int(sub[2]) > 0 else len(raw_vn) + int(sub[2])
                                face_vn.append(vn_idx)
                            else:
                                face_vn.append(None)
                        faces.append((face_v, face_vn))
        except Exception as e:
            print(f"[OBJLoader] Error loading {filepath}: {e}")
            return None

        if not raw_v or not faces:
            return None

        # Calculate bounding box
        min_x = min(v[0] for v in raw_v)
        max_x = max(v[0] for v in raw_v)
        min_y = min(v[1] for v in raw_v)
        max_y = max(v[1] for v in raw_v)
        min_z = min(v[2] for v in raw_v)
        max_z = max(v[2] for v in raw_v)

        cx = (min_x + max_x) / 2.0
        cy = (min_y + max_y) / 2.0
        cz = (min_z + max_z) / 2.0

        max_span = max(max_x - min_x, max_y - min_y, max_z - min_z)
        scale = 2.0 / max_span if max_span > 1e-6 else 1.0

        # Normalize vertices
        norm_v = []
        for x, y, z in raw_v:
            norm_v.append([(x - cx) * scale, (y - cy) * scale, (z - cz) * scale])

        mesh = ModelMesh()
        mesh_v = []
        mesh_vn = []

        # Triangulate polygons and construct vertex/normal buffers
        for f_v, f_vn in faces:
            if len(f_v) < 3:
                continue

            for i in range(1, len(f_v) - 1):
                idx0, idx1, idx2 = f_v[0], f_v[i], f_v[i + 1]
                v0, v1, v2 = norm_v[idx0], norm_v[idx1], norm_v[idx2]

                # Compute face normal if vertex normals aren't supplied
                vn0_idx, vn1_idx, vn2_idx = f_vn[0], f_vn[i], f_vn[i + 1]
                if vn0_idx is not None and vn0_idx < len(raw_vn):
                    n0 = raw_vn[vn0_idx]
                else:
                    n0 = None

                if vn1_idx is not None and vn1_idx < len(raw_vn):
                    n1 = raw_vn[vn1_idx]
                else:
                    n1 = None

                if vn2_idx is not None and vn2_idx < len(raw_vn):
                    n2 = raw_vn[vn2_idx]
                else:
                    n2 = None

                if n0 is None or n1 is None or n2 is None:
                    # Calculate cross product normal
                    ax, ay, az = v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2]
                    bx, by, bz = v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2]
                    nx = ay * bz - az * by
                    ny = az * bx - ax * bz
                    nz = ax * by - ay * bx
                    l = math.sqrt(nx * nx + ny * ny + nz * nz)
                    if l > 1e-6:
                        nx, ny, nz = nx / l, ny / l, nz / l
                    else:
                        nx, ny, nz = 0.0, 1.0, 0.0
                    n0 = n1 = n2 = [nx, ny, nz]

                mesh_v.extend(v0)
                mesh_vn.extend(n0)
                mesh_v.extend(v1)
                mesh_vn.extend(n1)
                mesh_v.extend(v2)
                mesh_vn.extend(n2)

                # Wireframe indices (edges of triangle)
                base_idx = mesh.vertex_count
                mesh.wire_indices.extend([base_idx, base_idx + 1, base_idx + 1, base_idx + 2, base_idx + 2, base_idx])
                mesh.vertex_count += 3
                mesh.triangle_count += 1

        mesh.vertices = mesh_v
        mesh.normals = mesh_vn
        return mesh
