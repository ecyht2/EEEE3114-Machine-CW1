#!/usr/bin/env python3
"""Script for showing task 4 measurment spots."""
import femm  # type: ignore
import numpy as np

from lib import MIDDLE, SLOT, TEETH, femm_handler


@femm_handler("../dist/cw1_sliding.fem")
def task_4_measurement():
    """Function to get data for Task 4 measurement.

    :returns: The flux at important points.
    """
    femm.smartmesh(1)

    a = 20 * np.sin(np.radians(0))
    b = 20 * np.sin(np.radians(120))
    c = 20 * np.sin(np.radians(-120))

    femm.mi_modifycircprop("A", 1, a)
    femm.mi_modifycircprop("B", 1, b)
    femm.mi_modifycircprop("C", 1, c)
    femm.mi_modifyboundprop("Sliding Boundary", 10, 60)

    teeth_angle = np.radians((SLOT + TEETH) * 5)
    # Yoke
    femm.mi_addnode(46.5 * np.cos(teeth_angle), 46.5 * np.sin(teeth_angle))
    # Teeth
    femm.mi_addnode(36 * np.cos(teeth_angle), 36 * np.sin(teeth_angle))
    # Magnet
    femm.mi_addnode(22 * np.cos(np.radians(MIDDLE)), 22 * np.sin(np.radians(MIDDLE)))

    femm.mi_savebitmap("../dist/task_4_measurement.bpm")


if __name__ == "__main__":
    task_4_measurement()
