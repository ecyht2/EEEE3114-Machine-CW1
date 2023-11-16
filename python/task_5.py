#!/usr/bin/env python3
"""Script for task 5."""
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

from lib import femm_handler


@dataclass
class TaskData:
    """The output data format for the collected data."""

    current: float
    torque: float


@femm_handler("../dist/cw1_sliding.fem")
def task_5(current: float) -> TaskData:
    """Function to get data for Task 5.

    :param current: The current to measure.
    :returns: The mean torque developed.
    """
    thread_logger = multiprocessing.get_logger()
    femm.smartmesh(1)

    femm.mi_modifycircprop("A", 1, current * np.sin(np.radians(0)))
    femm.mi_modifycircprop("B", 1, current * np.sin(np.radians(120)))
    femm.mi_modifycircprop("C", 1, current * np.sin(np.radians(-120)))

    # Debug
    thread_logger.info("Current: %s A", current)
    thread_logger.debug("A: %s A", current * np.sin(np.radians(0)))
    thread_logger.debug("B: %s A", current * np.sin(np.radians(120)))
    thread_logger.debug("C: %s A", current * np.sin(np.radians(-120)))

    femm.mi_modifyboundprop("Sliding Boundary", 10, 60)
    thread_logger.info("%s A, %s°", current, 60)
    # Anlyzing
    femm.mi_analyze(1)
    femm.mi_loadsolution()
    dev_torque = femm.mo_gapintegral("Sliding Boundary", 0)

    thread_logger.debug("Torque: %s", dev_torque)
    output = TaskData(current, dev_torque)

    femm.mo_close()

    return output


if __name__ == "__main__":
    logger = multiprocessing.log_to_stderr(logging.INFO)
    queue: Queue = Queue()

    currents = np.arange(11) * 20
    with Pool(1) as p:
        torque: list[TaskData] = p.map(task_5, currents)

    torque.sort(key=lambda v: v.current)
    logger.debug("Data: %s", torque)

    os.makedirs("../dist", exist_ok=True)
    with open("../dist/task_5.csv", "w", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["current", "torque"])
        writer.writeheader()
        writer.writerows(map(dataclasses.asdict, torque))

    # Torque
    plt.plot(currents, list(map(lambda v: v.torque, torque)), marker="o")

    # Labels
    plt.xlabel("Current, A")
    plt.ylabel("Torque, N*m")
    plt.title("Current vs Torque")
    plt.xlim(min(currents), max(currents))
    plt.xticks(currents)
    plt.savefig("../dist/task_5.png")

    plt.show()
