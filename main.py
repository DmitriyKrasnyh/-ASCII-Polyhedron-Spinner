"""ASCII Polyhedron spinner."""

import argparse
import os
import time
from typing import Dict, List, Tuple

import numpy as np

POLYHEDRA: Dict[int, Dict[str, object]] = {
    4: {
        "vertices": np.array(
            [
                [1, 1, 1],
                [-1, -1, 1],
                [-1, 1, -1],
                [1, -1, -1],
            ]
        ),
        "edges": [
            (0, 1),
            (1, 2),
            (2, 0),
            (0, 3),
            (1, 3),
            (2, 3),
        ],
    },
    6: {
        "vertices": np.array(
            [
                [1, 0, 0],
                [-1, 0, 0],
                [0, 1, 0],
                [0, -1, 0],
                [0, 0, 1],
                [0, 0, -1],
            ]
        ),
        "edges": [
            (0, 2),
            (0, 3),
            (0, 4),
            (0, 5),
            (1, 2),
            (1, 3),
            (1, 4),
            (1, 5),
            (2, 4),
            (3, 5),
            (2, 5),
            (3, 4),
        ],
    },
    8: {
        "vertices": np.array(
            [
                [-1, -1, -1],
                [1, -1, -1],
                [1, 1, -1],
                [-1, 1, -1],
                [-1, -1, 1],
                [1, -1, 1],
                [1, 1, 1],
                [-1, 1, 1],
            ]
        ),
        "edges": [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 0),
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 4),
            (0, 4),
            (1, 5),
            (2, 6),
            (3, 7),
        ],
    },
    12: {
        "vertices": np.array(
            [
                [-1, (1 + np.sqrt(5)) / 2, 0],
                [1, (1 + np.sqrt(5)) / 2, 0],
                [-1, -(1 + np.sqrt(5)) / 2, 0],
                [1, -(1 + np.sqrt(5)) / 2, 0],
                [0, -1, (1 + np.sqrt(5)) / 2],
                [0, 1, (1 + np.sqrt(5)) / 2],
                [0, -1, -(1 + np.sqrt(5)) / 2],
                [0, 1, -(1 + np.sqrt(5)) / 2],
                [(1 + np.sqrt(5)) / 2, 0, -1],
                [(1 + np.sqrt(5)) / 2, 0, 1],
                [-(1 + np.sqrt(5)) / 2, 0, -1],
                [-(1 + np.sqrt(5)) / 2, 0, 1],
            ]
        ),
        "edges": [
            (0, 11),
            (0, 5),
            (0, 1),
            (0, 7),
            (0, 10),
            (1, 5),
            (1, 9),
            (1, 7),
            (1, 8),
            (2, 3),
            (2, 8),
            (2, 5),
            (2, 9),
            (2, 6),
            (3, 4),
            (3, 9),
            (3, 6),
            (3, 7),
            (4, 11),
            (4, 7),
            (4, 8),
            (4, 10),
            (5, 11),
            (6, 9),
            (6, 8),
            (6, 10),
            (7, 11),
            (8, 10),
            (9, 10),
        ],
    },
}

# Проекции для 2D-отображения
def project_2d(point: np.ndarray, screen_dist: float = 2) -> Tuple[int, int]:
    factor = screen_dist / (screen_dist + point[2])
    x = int(point[0] * factor * 15)  # Увеличиваем масштаб проекции
    y = int(point[1] * factor * 15)
    return x, y

# Поворот в пространстве
def rotate(vertices: np.ndarray, angle_x: float, angle_y: float, angle_z: float) -> np.ndarray:
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(angle_x), -np.sin(angle_x)],
        [0, np.sin(angle_x), np.cos(angle_x)]
    ])
    
    Ry = np.array([
        [np.cos(angle_y), 0, np.sin(angle_y)],
        [0, 1, 0],
        [-np.sin(angle_y), 0, np.cos(angle_y)]
    ])
    
    Rz = np.array([
        [np.cos(angle_z), -np.sin(angle_z), 0],
        [np.sin(angle_z), np.cos(angle_z), 0],
        [0, 0, 1]
    ])
    
    rotation_matrix = np.dot(Rz, np.dot(Ry, Rx))
    return np.dot(vertices, rotation_matrix)

# Функция для рисования многогранника
CANVAS_WIDTH = 60
CANVAS_HEIGHT = 24


def draw_polyhedron(vertices: np.ndarray, edges: List[Tuple[int, int]], offset_x: int = 30, offset_y: int = 12) -> None:
    canvas_width = CANVAS_WIDTH
    canvas_height = CANVAS_HEIGHT
    projected = [project_2d(v) for v in vertices]
    canvas = [[' ' for _ in range(canvas_width)] for _ in range(canvas_height)]
    
    def draw_line(x0, y0, x1, y1):
        for t in np.linspace(0, 1, 100):
            x = int(x0 * (1 - t) + x1 * t) + offset_x
            y = int(y0 * (1 - t) + y1 * t) + offset_y
            if 0 <= x < canvas_width and 0 <= y < canvas_height:
                canvas[y][x] = '#'
    
    for edge in edges:
        draw_line(*projected[edge[0]], *projected[edge[1]])
    
    for line in canvas:
        print("".join(line))

def clear_console() -> None:
    """Clear the terminal window."""
    os.system("cls" if os.name == "nt" else "clear")

# Основной цикл для вращения и отображения
def spinning_polyhedron(n: int, speed: float = 0.05) -> None:
    if n not in POLYHEDRA:
        raise ValueError("Неподдерживаемое количество вершин. Доступны: 4, 6, 8, 12.")

    vertices = POLYHEDRA[n]["vertices"]
    edges = POLYHEDRA[n]["edges"]

    angle_x = angle_y = angle_z = 0.0
    try:
        while True:
            rotated_vertices = rotate(vertices, angle_x, angle_y, angle_z)
            clear_console()
            draw_polyhedron(rotated_vertices, edges, offset_x=30, offset_y=12)
            angle_x += speed
            angle_y += speed
            angle_z += speed
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ASCII 3D polyhedron visualizer")
    parser.add_argument(
        "-v",
        "--vertices",
        type=int,
        choices=sorted(POLYHEDRA.keys()),
        default=8,
        help="Количество вершин (4, 6, 8, 12)",
    )
    parser.add_argument(
        "-s",
        "--speed",
        type=float,
        default=0.05,
        help="Скорость вращения",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    spinning_polyhedron(args.vertices, speed=args.speed)


if __name__ == "__main__":
    main()
