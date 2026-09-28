import numpy as np
import trimesh
from typing import List, Tuple

def triangles_to_trimesh(triangles: List[Tuple[np.ndarray, np.ndarray, np.ndarray]]) -> trimesh.Trimesh:
    """Converte uma lista de triângulos [(v0, v1, v2), ...] em uma malha Trimesh indexada."""
    """Funde vértices compartilhados para garantir conectividade manifold."""

    if not triangles:
        raise ValueError("A lista de triângulos não pode estar vazia.")

    # Converte para array (N, 3, 3) -> N triângulos com 3 vértices (X, Y, Z)
    tri_array = np.array(triangles, dtype=np.float64)
    num_triangles = len(tri_array)

    vertices = tri_array.reshape(-1, 3)
    faces = np.arange(num_triangles * 3).reshape(-1, 3)

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    
    # Funde vértices adjacentes para fechar a casca da malha
    mesh.merge_vertices()
    
    # Corrige orientação de normais
    mesh.fix_normals()
    return mesh