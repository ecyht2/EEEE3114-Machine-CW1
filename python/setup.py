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
    femm.mi_readdxf("../cw.dxf")
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

    # Adding Boundary
    femm.mi_addboundprop("Boundary")
    femm.mi_selectarcsegment(62.5, 0)
    femm.mi_selectarcsegment(0, -62.5)
    femm.mi_setarcsegmentprop(5, "Boundary", 0, 0)
    femm.mi_clearselected()
    femm.mi_selectcircle(0, 0, 24.5, 4)
    femm.mi_setgroup(1)

    # Adding Materials
    # Rotor Inner
    add_label(0, 0, STEEL_1018, group=1)
    # Rotor Outer
    add_label(0, 16.25, STEEL_M19, group=1)
    # Air Gap
    add_label(0, 24.5, AIR)
    # Magnets
    magdirs = [45, -45, 180 + 45, 180 - 45]
    for i in range(4):
        x_val = 22 * cosd(i * 90 + 45)
        y_val = 22 * sind(i * 90 + 45)
        add_label(x_val, y_val, N42, magdir=magdirs[i], group=1)
    # Stator Radius
    add_label(0, 46.5, STEEL_M19)
    # Outer Cage Radius
    add_label(0, 56.25, IRON)
    # Windings/Slots
    circuits = ["A", "A", "B", "B", "C", "C"]
    MULTIPLIER = 1
    DIFF = 360 / 24
    for i in range(24):
        x_val = 34 * cosd(i * DIFF + 90)
        y_val = 34 * sind(i * DIFF + 90)
        index = i % 6
        if i % 6 == 0:
            MULTIPLIER = MULTIPLIER * -1
        add_label(x_val, y_val, COPPER, circ=circuits[index], turns=MULTIPLIER * 40)

    # Document saving
    os.makedirs("../dist", exist_ok=True)
    femm.mi_saveas("../dist/cw1.fem")
    femm.closefemm()
