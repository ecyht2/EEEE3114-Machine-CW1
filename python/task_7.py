#!/usr/bin/env python3
"""Script for task 7."""
import logging
import multiprocessing
import os
from dataclasses import dataclass

import femm  # type: ignore
import numpy as np

from lib import femm_handler, I_PEAK


@dataclass
class TaskData:
    """The output data format for the collected data."""

    r_s: float
    l_l: float
    l_m: float


@femm_handler("../dist/cw1_sliding.fem")
def task_7() -> TaskData:
    """Function to get data for Task 7."""
    thread_logger = multiprocessing.get_logger()
    thread_logger.info("Setting Up Simulation")
    # Setup
    femm.smartmesh(1)
    # Setting Current
    femm.mi_modifycircprop("A", 1, I_PEAK * np.sin(np.radians(90)))
    femm.mi_modifycircprop("B", 1, I_PEAK * np.sin(np.radians(90 + 120)))
    femm.mi_modifycircprop("C", 1, I_PEAK * np.sin(np.radians(90 - 120)))
    # Setting Rotor Angle
    femm.mi_modifyboundprop("Sliding Boundary", 10, 0)

    # Total Inductance Ls
    thread_logger.info("Getting Ls")
    # Anlyzing
    femm.mi_analyze(1)
    femm.mi_loadsolution()
    # Gathering Data
    circprops_a = femm.mo_getcircuitproperties("A")
    circprops_b = femm.mo_getcircuitproperties("B")
    circprops_c = femm.mo_getcircuitproperties("C")
    if circprops_a[0] == 0:
        circprops_a[0] = 1
    l_s = 4 * circprops_a[2] / circprops_a[0]
    r_s = 4 * circprops_a[1].real / circprops_a[0]
    femm.mo_close()
    # Logging
    thread_logger.debug("A: %s", circprops_a)
    thread_logger.debug("B: %s", circprops_b)
    thread_logger.debug("C: %s", circprops_c)
    thread_logger.debug("Ls: %s", l_s)

    # Winding inductance Ll
    thread_logger.info("Getting L_l")
    femm.mi_selectlabel(22 * np.cos(np.radians(52.5)), 22 * np.sin(np.radians(52.5)))
    femm.mi_setblockprop("Air", 1, 0, "", 0, 1, 0)
    # Anlyzing
    femm.mi_analyze(1)
    femm.mi_loadsolution()
    # Gathering Data
    circprops_a = femm.mo_getcircuitproperties("A")
    circprops_b = femm.mo_getcircuitproperties("B")
    circprops_c = femm.mo_getcircuitproperties("C")
    if circprops_a[0] == 0:
        circprops_a[0] = 1
    l_l = 4 * circprops_a[2] / circprops_a[0]
    l_m = l_s - l_l
    femm.mo_close()
    # Logging
    thread_logger.debug("A: %s", circprops_a)
    thread_logger.debug("B: %s", circprops_b)
    thread_logger.debug("C: %s", circprops_c)

    return TaskData(r_s, l_l, l_m)


if __name__ == "__main__":
    logger = multiprocessing.log_to_stderr(logging.INFO)

    logger.info("Getting Theortical Results")
    E = 113.2
    P = 15.6 * 1500 * 2 * np.pi / 60
    I_S = I_PEAK
    logger.debug("Is: %s", I_S)
    logger.debug("P: %s", P)
    logger.debug("E: %s", E)
    Xs_theory = np.sqrt((I_S**2 - (P**2 / 9 / E**2)) / E**2)**-1

    logger.info("Getting Simulated Results")
    data: TaskData = task_7()
    Xs_measured = 2 * np.pi * 50 * (data.l_l + data.l_m)

    logger.debug("Rs: %s", data.r_s)
    logger.debug("Ll: %s", data.l_l)
    logger.debug("Lm: %s", data.l_m)

    logger.debug("Theoratical Xs: %s", Xs_theory)
    logger.debug("Measured Xs: %s", Xs_measured)

    os.makedirs("../dist/", exist_ok=True)
    with open("../dist/task_7.txt", "w", encoding="utf-8") as file:
        file.write(f"Resistance: {data.r_s}\n")
        file.write(f"Leakage Inductance: {data.l_l}\n")
        file.write(f"Mutual Inductance: {data.l_m}\n")
        file.write(f"Total Inductance: {data.l_m + data.l_l}\n")
        file.write(f"Theoratical Inductance: {Xs_theory / 2 / np.pi / 50}\n")
