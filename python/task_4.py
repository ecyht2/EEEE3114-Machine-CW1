#!/usr/bin/env python3
"""Script for task 4."""
import csv
import dataclasses
import logging
import multiprocessing
import os
from dataclasses import dataclass
from multiprocessing import Pool, Queue

import femm  # type: ignore
import matplotlib.pyplot as plt
import numpy as np

from lib import MIDDLE, SLOT, TEETH, femm_handler


@dataclass
class TaskData:
    """The output data format for the collected data."""

    current: float
    yoke: float
    teeth: float
    magnet: float


def mag(b_values: tuple[float, float]):
    """Finds the magnitude of the B field."""
    return np.sqrt(b_values[0] ** 2 + b_values[1] ** 2)


@femm_handler("../dist/cw1_sliding.fem")
def task_4(current: float) -> TaskData:
    """Function to get data for Task 4.

    :param current: The current to measure.
    :returns: The flux at important points.
    """
    thread_logger = multiprocessing.get_logger()
    femm.smartmesh(1)

    a = current * np.sin(np.radians(0))
    b = current * np.sin(np.radians(120))
    c = current * np.sin(np.radians(-120))

    # Debug
    thread_logger.info("Current %s A", current)
    thread_logger.debug("Current A: %s A", a)
    thread_logger.debug("Current B: %s A", b)
    thread_logger.debug("Current C: %s A", c)

    femm.mi_modifycircprop("A", 1, a)
    femm.mi_modifycircprop("B", 1, b)
    femm.mi_modifycircprop("C", 1, c)
    femm.mi_modifyboundprop("Sliding Boundary", 10, 60)

    teeth_angle = np.radians((SLOT + TEETH) * 5)
    # Anlyzing
    femm.mi_analyze(1)
    femm.mi_loadsolution()

    stator = np.zeros(2, float)
    stator[0] = mag(
        femm.mo_getb(46.5 * np.cos(teeth_angle), 46.5 * np.sin(teeth_angle))
    )

    stator[1] = mag(femm.mo_getb(36 * np.cos(teeth_angle), 36 * np.sin(teeth_angle)))

    magnet_x = 22 * np.cos(np.radians(MIDDLE))
    magnet_y = 22 * np.sin(np.radians(MIDDLE))
    magnet = mag(femm.mo_getb(magnet_x, magnet_y))

    thread_logger.debug("Yoke Fluxes: %s", stator[0])
    thread_logger.debug("Teeth Fluxes: %s", stator[1])
    thread_logger.debug("Magnet Fluxes: %s", magnet)

    output = TaskData(current, stator[0], stator[1], magnet)

    femm.mo_close()

    return output


if __name__ == "__main__":
    logger = multiprocessing.log_to_stderr(logging.INFO)
    queue: Queue = Queue()

    currents = np.arange(11) * 20
    with Pool(11) as p:
        flux: list[TaskData] = p.map(task_4, currents)

    flux.sort(key=lambda v: v.current)

    # Debug
    logger.debug("Fluxes: %s", flux)

    os.makedirs("../dist", exist_ok=True)
    with open("../dist/task_4.csv", "w", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file, fieldnames=["current", "yoke", "teeth", "magnet"]
        )
        writer.writeheader()
        writer.writerows(map(dataclasses.asdict, flux))

    # Yoke
    plt.plot(currents, list(map(lambda v: v.yoke, flux)), label="Yoke", marker="o")

    # Teeth
    plt.plot(currents, list(map(lambda v: v.teeth, flux)), label="Teeth", marker="o")

    # Magnet
    plt.plot(currents, list(map(lambda v: v.magnet, flux)), label="Magnet", marker="o")

    # Labels
    plt.xlabel("Current, A")
    plt.ylabel("Flux, T")
    plt.title("Current vs Flux")
    plt.xlim(min(currents), max(currents))
    plt.xticks(currents)
    plt.legend()
    plt.savefig("../dist/task_4.png")

    plt.show()
