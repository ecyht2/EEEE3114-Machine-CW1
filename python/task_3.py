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

from lib import EDT, OMEGA_E, femm_handler


class TaskData(NamedTuple):
    """The output data format for the collected data."""
    phase_angle: int
    torque_developed: float


@femm_handler("../dist/cw1_sliding.fem")
def task_1_2(initial_angle: int, count: int, out: Queue):
    """Function to get data for Task 1 and 2.

    :param initial_angle: Initial phase angle of the current.
    :param count: The amount of times to rotate the phase angle.
    :param out: The queue to output the collected data to.
    """
    femm.smartmesh(1)
    thread_logger = multiprocessing.get_logger()
    thread_logger.setLevel(logging.INFO)

    for a in range(count):
        # Modifying circuit
        angle = initial_angle + a
        femm.mi_modifycircprop("A", 1, 20 * np.sin(angle))
        femm.mi_modifycircprop("B", 1, 20 * np.sin(angle + 120))
        femm.mi_modifycircprop("C", 1, 20 * np.sin(angle - 120))
        # femm.mi_modifyboundprop("Sliding Boundary", 10, angle)

        # Debug
        thread_logger.info("Angle %s", angle)

        # Anlyzing
        femm.mi_analyze(1)
        femm.mi_loadsolution()

        # Getting Data
        tq = femm.mo_gapintegral("Sliding Boundary", 0)
        out.put(TaskData(angle, tq))

        femm.mo_close()


if __name__ == '__main__':
    logger = multiprocessing.get_logger()
    logger.setLevel(logging.INFO)
    queue: Queue = Queue()
    processes: list[Process] = []
    THREADS = 10
    COUNT = round(360 / THREADS)

    for i in range(THREADS):
        p = Process(target=task_1_2, args=(i * COUNT, COUNT, queue))
        p.start()
        processes.append(p)

    for process in processes:
        process.join()

    phase_angle = np.arange(360)
    dev_torque = np.zeros(360)
    while queue.qsize() > 0:
        item: TaskData = queue.get()
        dev_torque[item.phase_angle] = item.torque_developed

    logger.info("Torque Developed: %s", dev_torque)

    os.makedirs("../dist", exist_ok=True)
    with open("../dist/task_3.csv", "w", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Load Angle", "Torque Developed"])
        csv_array = np.transpose(np.array([phase_angle, dev_torque]))
        writer.writerows(csv_array)

    # Finding frequency
    fft = np.array(abs(np.fft.fft(dev_torque)))
    freq = np.fft.helper.fftfreq(dev_torque.size, EDT)
    index = np.argmax(fft)
    f = freq[index]
    with open("../dist/task_3.txt", "w", encoding="utf-8") as file:
        period = OMEGA_E * f**-1
        output = f"Torque Ripple Period: {period}"
        file.write(output)
        logger.info(output)

    plt.plot(phase_angle, dev_torque)
    plt.xlabel("Phase Angle, °")
    plt.ylabel("Torque Developed, N*m")
    plt.title("Torque Developed vs Phase Angle")
    plt.xlim(min(phase_angle), max(phase_angle))
    plt.savefig("../dist/task_3.png")
    plt.show()
