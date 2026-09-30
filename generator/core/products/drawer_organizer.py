
import trimesh
from pydantic import Field, model_validator

from core.base import BaseProductGenerator, BaseProductParams, GenerationResult
from core.mesh_utils import BED_SIZE_MM, build_result

MIN_WALL_MM = 1.2         # parede mínima imprimível (3 linhas de 0.4 mm)
MIN_FLOOR_MM = 0.8        # fundo mínimo (4 camadas de 0.2 mm)
MIN_COMPARTMENT_MM = 10.0  # vão livre mínimo entre paredes/divisórias


class DrawerOrganizerParams(BaseProductParams):
    """Parâmetros do organizador de gaveta. Todas as medidas em mm, externas."""

    width: float = Field(gt=0, le=BED_SIZE_MM[0], description="Largura externa (X)")
    depth: float = Field(gt=0, le=BED_SIZE_MM[1], description="Profundidade externa (Y)")
    height: float = Field(gt=0, le=BED_SIZE_MM[2], description="Altura externa (Z)")
    wall: float = Field(default=1.6, ge=MIN_WALL_MM, le=10, description="Espessura das paredes e divisórias")
    floor: float = Field(default=1.2, ge=MIN_FLOOR_MM, le=10, description="Espessura do fundo")
    
    dividers_x: list[float] = Field(
        default_factory=list,
        description="Posição X (centro, a partir da borda externa esquerda) de cada divisória paralela ao eixo Y",
    )

    dividers_y: list[float] = Field(
        default_factory=list,
        description="Posição Y (centro, a partir da borda externa frontal) de cada divisória paralela ao eixo X",
    )

    @model_validator(mode="after")
    def check_geometry(self) -> "DrawerOrganizerParams":
        if self.floor >= self.height:
            raise ValueError("floor deve ser menor que height")
        _check_compartments("dividers_x", self.dividers_x, self.width, self.wall)
        _check_compartments("dividers_y", self.dividers_y, self.depth, self.wall)
        return self

def _check_compartments(name: str, positions: list[float], length: float, wall: float) -> None:
        """Garante que todo vão entre paredes e divisórias tem pelo menos MIN_COMPARTMENT_MM."""
        centers = sorted(positions)
        starts = [wall] + [c + wall / 2 for c in centers]           # face onde cada vão começa
        ends = [c - wall / 2 for c in centers] + [length - wall]    # face onde cada vão termina
        for start, end in zip(starts, ends):
            if end - start < MIN_COMPARTMENT_MM:
                raise ValueError(
                    f"{name}: vão de {end - start:.1f} mm entre {start:.1f} e {end:.1f} "
                    f"(mínimo {MIN_COMPARTMENT_MM} mm)"
                )

def _box(size: tuple[float, float, float], min_corner: tuple[float, float, float]) -> trimesh.Trimesh:
    """Caixa com o canto mínimo em min_corner (trimesh cria centrado na origem)."""
    box = trimesh.creation.box(extents=size)
    box.apply_translation([m + s / 2 for m, s in zip(min_corner, size)])
    return box


class DrawerOrganizerGenerator(BaseProductGenerator):
    """Bandeja aberta no topo com divisórias internas em X e Y."""

    def generate(self, params: DrawerOrganizerParams) -> GenerationResult:
        w, d, h, t, f = params.width, params.depth, params.height, params.wall, params.floor

        outer = _box((w, d, h), (0, 0, 0))
        # Cavidade começa no fundo e passa do topo, deixando a bandeja aberta
        cavity = _box((w - 2 * t, d - 2 * t, h), (t, t, f))
        tray = outer.difference(cavity)

        # Divisórias ocupam a altura e a profundidade/largura totais: sobrepõem
        # paredes e fundo, então a união funde tudo em um sólido só
        dividers = [_box((t, d, h), (x - t / 2, 0, 0)) for x in params.dividers_x]
        dividers += [_box((w, t, h), (0, y - t / 2, 0)) for y in params.dividers_y]
        if dividers:
            tray = trimesh.boolean.union([tray, *dividers])

        return build_result(tray)