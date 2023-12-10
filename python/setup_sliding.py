#!/usr/bin/env python3
"""Document creation and setup"""
import math
import os

import femm  # type: ignore


def add_label(
    x: float,
    y: float,
    mat: str,
    circ: str = "",
    magdir: float = 0,
    group: int = 0,
    turns: int = 0,
):
    """Adds a new label to the problem."""
    # pylint: disable=too-many-arguments
    femm.mi_addblocklabel(x, y)
    femm.mi_selectlabel(x, y)
    femm.mi_setblockprop(mat, 1, 0, circ, magdir, group, turns)
    femm.mi_clearselected()


def add_boundary(coords: list[float], name: str):
    """Adds new boundaries."""
    for index, coord in enumerate(coords):
        boundary_name = name.format(index)
        femm.mi_addboundprop(boundary_name, *[None for _ in range(8)], 5)
        femm.mi_selectsegment(coord, 0)
        femm.mi_selectsegment(0, coord)
        femm.mi_setsegmentprop(boundary_name, None, None, None, None)
        femm.mi_clearselected()


def cosd(value: float) -> float:
    """Calculate the cosine using degrees."""
    return math.cos(math.radians(value))


def sind(value: float) -> float:
    """Calculate the sine using degrees."""
    return math.sin(math.radians(value))


if __name__ == "__main__":
    femm.openfemm(
        winepath="/usr/bin/wine",
        femmpath="/home/user/.local/share/wineprefixes/default/drive_c/femm42/bin/",
    )
    femm.newdocument(0)
    femm.mi_probdef(None, "millimeters", "planar", None, 100)
    femm.smartmesh(0)

    # Importing
    femm.mi_readdxf("../cw_sliding.dxf")
    femm.mi_zoomnatural()

    # Importing Materials
    AIR = "Air"
    IRON = "Pure Iron"
    N42 = "N42"
    STEEL_1018 = "1018 Steel"
    STEEL_M19 = "M-19 Steel"
    COPPER = "10 AWG"
    femm.mi_getmaterial(AIR)
    femm.mi_getmaterial(IRON)
    femm.mi_getmaterial(N42)
    femm.mi_getmaterial(STEEL_1018)
    femm.mi_getmaterial(STEEL_M19)
    femm.mi_getmaterial(COPPER)

    # Adding Circuits
    femm.mi_addcircprop("A", 0, 1)
    femm.mi_addcircprop("B", 0, 1)
    femm.mi_addcircprop("C", 0, 1)

    # Adding Static Boundary
    femm.mi_addboundprop("Boundary")
    femm.mi_selectarcsegment(62.5, 0)
    femm.mi_setarcsegmentprop(5, "Boundary", None, None)
    femm.mi_clearselected()
    # Sliding Boundary
    femm.mi_addboundprop("Sliding Boundary", *[None for _ in range(8)], 7)
    femm.mi_selectarcsegment(24.7, 0)
    femm.mi_selectarcsegment(24.3, 0)
    femm.mi_setarcsegmentprop(5, "Sliding Boundary", None, None)
    femm.mi_clearselected()
    # Moving Boundary
    # Rotor
    add_boundary([6.25, 16.25], "Rotor Boundary {}")
    # Air Gap 1
    add_boundary([22, 25], "Air Gap {}")
    # Air Gap 2
    # Stator Boundary
    add_boundary([46.5, 56.25], "Stator Boundary {}")
    # Setting Rotor Group
    femm.mi_selectcircle(0, 0, 24.5, 4)
    femm.mi_setgroup(1)

    # Adding Materials
    # Rotor Inner
    add_label(6.25 * cosd(45), 6.25 * sind(45), STEEL_1018, group=1)
    # Rotor Outer
    add_label(16.25 * cosd(45), 16.25 * sind(45), STEEL_M19, group=1)
    # Air Gap
    add_label(24.8 * cosd(45), 24.8 * sind(45), AIR)
    add_label(24.15 * cosd(15), 24.15 * sind(15), AIR)
    # Magnets
    x_val = 22 * cosd(52.5)
    y_val = 22 * sind(52.5)
    add_label(x_val, y_val, N42, magdir=45, group=1)
    # Stator Radius
    add_label(46.5 * cosd(45), 46.5 * sind(45), STEEL_M19)
    # Outer Cage Radius
    add_label(56.25 * cosd(45), 56.25 * sind(45), IRON)
    # Windings/Slots
    # Middle Full
    circuits = [("B", 1), ("B", 1), ("C", -1), ("C", -1), ("A", 1), ("A", 1)]
    DIFF = 360 / 24
    for i, circuit in enumerate(circuits):
        x_val = 36 * cosd(i * DIFF + DIFF / 2)
        y_val = 36 * sind(i * DIFF + DIFF / 2)
        add_label(x_val, y_val, COPPER, circ=circuit[0], turns=40 * circuit[1])

    # Document saving
    os.makedirs("../dist", exist_ok=True)
    femm.mi_saveas("../dist/cw1_sliding.fem")
    femm.closefemm()
