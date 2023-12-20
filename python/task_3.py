#!/usr/bin/env python3
"""Script for task 3."""
import csv
import logging
import multiprocessing
import os
from multiprocessing import Process, Queue
from typing import NamedTuple

import femm  # type: ignore
import matplotlib.pyplot as plt
import numpy as np

from lib import femm_handler, EDT, OMEGA_E


class TaskData(NamedTuple):
    """The output data format for the collected data."""
    phase_angle: int
    torque_developed: float


@femm_handler("../dist/cw1_sliding.fem")
def task_3(initial_angle: int, count: int, out: Queue):
    """Function to get data for Task 3.

    :param initial_angle: Initial phase angle of the current.
    :param count: The amount of times to rotate the phase angle.
    :param out: The queue to output the collected data to.
    """
    femm.smartmesh(1)
    thread_logger = multiprocessing.get_logger()

    for a in range(count):
        # Modifying circuit
        angle = initial_angle + a
        femm.mi_modifycircprop("A", 1, 20 * np.sin(np.radians(angle + 77)))
        femm.mi_modifycircprop("B", 1, 20 * np.sin(np.radians(angle + 77 + 120)))
        femm.mi_modifycircprop("C", 1, 20 * np.sin(np.radians(angle + 77 - 120)))
        femm.mi_modifyboundprop("Sliding Boundary", 10, angle / 2 + 23.1)

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
        p = Process(target=task_3, args=(i * COUNT, COUNT, queue))
        p.start()
        processes.append(p)

    for process in processes:
        process.join()

    phase_angle: np.ndarray = np.arange(360)
    dev_torque: np.ndarray = np.zeros(360)
    while queue.qsize() > 0:
        item: TaskData = queue.get()
        dev_torque[item.phase_angle] = item.torque_developed

    logger.info("Torque Developed: %s", dev_torque)

    os.makedirs("../dist", exist_ok=True)
    with open("../dist/task_3_ripple.csv", "w", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Load Angle", "Torque Developed"])
        csv_array = np.transpose(np.array([phase_angle, dev_torque]))
        writer.writerows(csv_array)

    # Finding frequency
    fft = np.array(abs(np.fft.fft(dev_torque)))
    freq = np.fft.helper.fftfreq(dev_torque.size, EDT)
    # Removing DC offset
    fft[0] = 0
    index = np.argmax(fft)
    f = freq[index]
    ANGLE_PERIOD = 0
    if f > 0:
        ANGLE_PERIOD = OMEGA_E * f**-1
    with open("../dist/task_3_ripple.txt", "w", encoding="utf-8") as file:
        output = f"Torque Ripple Period: {ANGLE_PERIOD}"
        file.write(output)
        logger.info(output)

    plt.plot(phase_angle, dev_torque)
    plt.xlabel("Load Angle, °")
    plt.ylabel("Torque Developed, Nm")
    plt.title("Torque Ripple of the Machine")
    plt.xlim(min(phase_angle), max(phase_angle))
    plt.savefig("../dist/task_3_ripple.png")
    plt.show()
