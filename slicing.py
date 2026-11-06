from dataclasses import dataclass

import numpy as np

from shapes import Plane


_AXIS_TOL = 1e-12


@dataclass(frozen=True)
class PlaneFrame:
    plane: Plane
    origin: np.ndarray
    u: np.ndarray
    v: np.ndarray
    normal: np.ndarray
    u_label: str
    v_label: str


@dataclass(frozen=True)
class SliceGrid:
    frame: PlaneFrame
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray
    u: np.ndarray
    v: np.ndarray
    extent: tuple[float, float, float, float]

    @property
    def shape(self):
        return self.x.shape

    @property
    def u_label(self):
        return self.frame.u_label

    @property
    def v_label(self):
        return self.frame.v_label


def plane_frame(plane: Plane) -> PlaneFrame:
    """Build an orthonormal 2D frame embedded in a plane."""
    normal = np.array([plane.a, plane.b, plane.c], dtype=float)
    norm = np.linalg.norm(normal)
    if norm == 0:
        raise ValueError("plane normal must be nonzero")

    normal = normal / norm
    origin = (plane.d / norm) * normal

    nonzero = np.abs(normal) > _AXIS_TOL
    if np.count_nonzero(nonzero) == 1:
        if nonzero[0]:
            u = np.array([0.0, 1.0, 0.0])
            v = np.array([0.0, 0.0, 1.0])
            u_label, v_label = "y", "z"
        elif nonzero[1]:
            u = np.array([1.0, 0.0, 0.0])
            v = np.array([0.0, 0.0, 1.0])
            u_label, v_label = "x", "z"
        else:
            u = np.array([1.0, 0.0, 0.0])
            v = np.array([0.0, 1.0, 0.0])
            u_label, v_label = "x", "y"
    else:
        seed = np.zeros(3)
        seed[np.argmin(np.abs(normal))] = 1.0

        u = np.cross(seed, normal)
        u = u / np.linalg.norm(u)
        v = np.cross(normal, u)
        v = v / np.linalg.norm(v)
        u_label, v_label = "u", "v"

    return PlaneFrame(
        plane=plane,
        origin=origin,
        u=u,
        v=v,
        normal=normal,
        u_label=u_label,
        v_label=v_label,
    )


def make_slice_grid(
    plane: Plane,
    u_range: tuple[float, float],
    v_range: tuple[float, float],
    nx: int,
    ny: int,
) -> SliceGrid:
    """Sample a rectangular grid on the plane in (u, v) coordinates."""
    u_min, u_max = u_range
    v_min, v_max = v_range

    if u_min >= u_max:
        raise ValueError("u_range must satisfy u_min < u_max")
    if v_min >= v_max:
        raise ValueError("v_range must satisfy v_min < v_max")
    if not isinstance(nx, (int, np.integer)) or nx < 2:
        raise ValueError("nx must be an integer >= 2")
    if not isinstance(ny, (int, np.integer)) or ny < 2:
        raise ValueError("ny must be an integer >= 2")

    frame = plane_frame(plane)
    u = np.linspace(u_min, u_max, nx, dtype=float)
    v = np.linspace(v_min, v_max, ny, dtype=float)
    u_grid, v_grid = np.meshgrid(u, v)

    x = frame.origin[0] + u_grid * frame.u[0] + v_grid * frame.v[0]
    y = frame.origin[1] + u_grid * frame.u[1] + v_grid * frame.v[1]
    z = frame.origin[2] + u_grid * frame.u[2] + v_grid * frame.v[2]

    return SliceGrid(
        frame=frame,
        x=x,
        y=y,
        z=z,
        u=u,
        v=v,
        extent=(float(u_min), float(u_max), float(v_min), float(v_max)),
    )
