from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import trimesh
from pydantic import BaseModel, ConfigDict


@dataclass
class GenerationResult:
    """Resultado da geração paramétrica de um modelo 3D."""
    mesh: trimesh.Trimesh
    stl_bytes: bytes
    volume_cm3: float
    dimensions_mm: tuple[float, float, float]  # (largura X, profundidade Y, altura Z)
    is_watertight: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "volume_cm3": round(self.volume_cm3, 2),
            "dimensions_mm": {
                "width": round(self.dimensions_mm[0], 2),
                "depth": round(self.dimensions_mm[1], 2),
                "height": round(self.dimensions_mm[2], 2),
            },
            "is_watertight": self.is_watertight,
            "triangle_count": len(self.mesh.faces),
        }


class BaseProductParams(BaseModel):
    """Classe base para parâmetros de produtos paramétricos."""
    model_config = ConfigDict(extra="forbid")


class BaseProductGenerator(ABC):
    """Interface abstrata para geradores de produtos 3D."""

    @abstractmethod
    def generate(self, params: BaseProductParams) -> GenerationResult:
        """Recebe parâmetros validados e gera a malha 3D + STL binário."""
