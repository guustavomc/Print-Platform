import pytest
import trimesh

from core.mesh_utils import MeshValidationError, build_result, export_glb


def make_tray():
    """Bandeja 100x50x30 com parede de 2 mm e fundo de 2 mm."""
    outer = trimesh.creation.box(extents=(100, 50, 30))
    inner = trimesh.creation.box(extents=(96, 46, 30))
    inner.apply_translation((0, 0, 2))  # sobe 2 mm: deixa fundo e vaza no topo
    return outer.difference(inner)


def test_boolean_gera_malha_fechada():
    result = build_result(make_tray())
    assert result.is_watertight
    assert result.dimensions_mm == pytest.approx((100, 50, 30))
    assert result.stl_bytes[:5] != b"solid"  # STL binário, não ASCII


def test_to_dict():
    data = build_result(make_tray()).to_dict()
    assert data["dimensions_mm"]["width"] == 100


def test_glb_exporta():
    assert export_glb(make_tray())[:4] == b"glTF"


def test_rejeita_peca_maior_que_mesa():
    with pytest.raises(MeshValidationError, match="excede a mesa"):
        build_result(trimesh.creation.box(extents=(300, 50, 30)))
