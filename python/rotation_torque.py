#!/usr/bin/env python3
"""Script for rotation torque."""
import csv
import logging
import multiprocessing
import os
from multiprocessing import Process, Queue
from typing import NamedTuple

import femm  # type: ignore
import matplotlib.pyplot as plt
import numpy as np

from lib import femm_handler


class TaskData(NamedTuple):
    """The output data format for the collected data."""
    rotation_angle: int
    torque_developed: float


@femm_handler("../dist/cw1_sliding.fem")
def rotation_torque(initial_angle: int, count: int, out: Queue):
    """Function to get data for getting the torque for a given rotor rotation.

    :param initial_angle: Initial rotation angle of the rotor.
    :param count: The amount of times to rotate the rotor.
    :param out: The queue to output the collected data to.
    """
    femm.smartmesh(1)
    thread_logger = multiprocessing.get_logger()
    femm.mi_modifycircprop("A", 1, 20 * np.sin(np.radians(0)))
    femm.mi_modifycircprop("B", 1, 20 * np.sin(np.radians(120)))
    femm.mi_modifycircprop("C", 1, 20 * np.sin(np.radians(-120)))

    for a in range(count):
        # Modifying circuit
        angle = initial_angle + a
        femm.mi_modifyboundprop("Sliding Boundary", 10, angle)

        # Debug
        thread_logger.info("Angle %s", angle)

        # Anlyzing
        femm.mi_analyze()
        femm.mi_loadsolution()

        # Getting Data
        tq = femm.mo_gapintegral("Sliding Boundary", 0)
        out.put(TaskData(angle, tq))

        femm.mo_close()


if __name__ == "__main__":
    logger = multiprocessing.log_to_stderr(logging.INFO)
    queue: Queue = Queue()
    processes: list[Process] = []
    THREADS = 10
    COUNT = round(360 / THREADS)

    for i in range(THREADS):
        p = Process(target=rotation_torque, args=(i * COUNT, COUNT, queue))
        p.start()
        processes.append(p)

    for process in processes:
        process.join()

    phase_angle: np.ndarray = np.arange(360)
    dev_torque: np.ndarray = np.zeros(360)
    while queue.qsize() > 0:
        item: TaskData = queue.get()
        dev_torque[item.rotation_angle] = item.torque_developed

    logger.info("Torque Developed: %s", dev_torque)

    os.makedirs("../dist", exist_ok=True)
    with open("../dist/rotation_torque.csv", "w", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Rotation Angle", "Torque Developed"])
        csv_array = np.transpose(np.array([phase_angle, dev_torque]))
        writer.writerows(csv_array)

    # Finding frequency
    with open("../dist/rotation_torque.txt", "w", encoding="utf-8") as file:
        max_phase = dev_torque.argmax()
        output = f"Max Phase: {max_phase}"
        file.write(output)
        file.write("\n")
        min_phase = dev_torque.argmin()
        output = f"Min Phase: {min_phase}"
        file.write(output)
        logger.info(output)

    plt.plot(phase_angle, dev_torque, marker="o")
    plt.xlabel("Rotation Angle, °")
    plt.ylabel("Torque Developed, N*m")
    plt.title("Torque Developed vs Rotation Angle")
    plt.xlim(min(phase_angle), max(phase_angle))
    plt.savefig("../dist/rotation_torque.png")
    plt.show()
