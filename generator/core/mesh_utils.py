import trimesh

from core.base import GenerationResult

# Volume máximo de impressão (X, Y, Z) em mm; ajuste para a sua impressora
BED_SIZE_MM = (256.0, 256.0, 256.0)


class MeshValidationError(ValueError):
    """Malha gerada não é imprimível."""


def validate(mesh: trimesh.Trimesh, bed_size: tuple[float, float, float] = BED_SIZE_MM) -> None:
    """Garante que a malha é fechada, tem volume positivo e cabe na mesa."""
    errors = []
    if not mesh.is_watertight:
        errors.append("malha não é fechada (watertight)")
    if not mesh.is_winding_consistent:
        errors.append("normais inconsistentes")
    if mesh.volume <= 0:
        errors.append(f"volume inválido: {mesh.volume:.2f} mm³")
    for axis, size, limit in zip("XYZ", mesh.extents, bed_size):
        if size > limit:
            errors.append(f"eixo {axis} excede a mesa: {size:.1f} > {limit:.1f} mm")
    if errors:
        raise MeshValidationError("; ".join(errors))


def export_stl(mesh: trimesh.Trimesh) -> bytes:
    """STL binário para o fatiador."""
    return mesh.export(file_type="stl")


def export_glb(mesh: trimesh.Trimesh) -> bytes:
    """GLB para o preview 3D na web."""
    return mesh.export(file_type="glb")


def build_result(mesh: trimesh.Trimesh) -> GenerationResult:
    """Valida a malha e monta o GenerationResult padrão."""
    validate(mesh)
    x, y, z = (float(v) for v in mesh.extents)
    return GenerationResult(
        mesh=mesh,
        stl_bytes=export_stl(mesh),
        volume_cm3=mesh.volume / 1000.0,
        dimensions_mm=(x, y, z),
        is_watertight=mesh.is_watertight,
    )
