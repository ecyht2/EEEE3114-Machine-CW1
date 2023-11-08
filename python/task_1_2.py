#!/usr/bin/env python3
"""Test script."""
import csv
import math
from dataclasses import dataclass
from multiprocessing import Process, Queue

import femm  # type: ignore
import matplotlib.pyplot as plt
import numpy as np

from lib import femm_handler


@dataclass
class TaskData:
    """The output data format for the collected data."""

    angle: float
    coggingtorque: float
    aflux: float
    bflux: float
    cflux: float


@femm_handler()
def task_1_2(initial_angle: int, count: int, out: Queue):
    """Function to get data for Task 1 and 2.

    :param initial_angle: Initial angle of the measurement.
    :param count: The amount of times to rotate the rotor.
    :param out: The queue to output the collected data to.
    """
    femm.mi_selectgroup(1)
    femm.mi_moverotate(0, 0, initial_angle)

    for k in range(count):
        # Debug
        print(f"Angle: {initial_angle + k}")
        # Anlyzing
        femm.mi_analyze(1)
        femm.mi_loadsolution()

        # Gathering Data
        femm.mo_groupselectblock(1)
        tq = femm.mo_blockintegral(22)
        circprops_a = femm.mo_getcircuitproperties("A")
        circprops_b = femm.mo_getcircuitproperties("B")
        circprops_c = femm.mo_getcircuitproperties("C")
        out.put(
            TaskData(
                initial_angle + k,
                tq,
                circprops_a[2],
                circprops_b[2],
                circprops_c[2],
            )
        )

        # Setting up for next cycle
        femm.mo_close()
        femm.mi_selectgroup(1)
        femm.mi_moverotate(0, 0, 1)


if __name__ == "__main__":
    queue: Queue = Queue()
    processes: list[Process] = []
    THREADS = 12
    COUNT = round(360 / THREADS)

    for i in range(THREADS):
        p = Process(target=task_1_2, args=(i * COUNT, COUNT, queue))
        p.start()
        processes.append(p)

    for process in processes:
        process.join()

    RPM = 1500
    OMEGA = RPM * 360 / 60
    DT = 1 / OMEGA

    tt = np.zeros(360)
    aflux = np.zeros(360)
    bflux = np.zeros(360)
    cflux = np.zeros(360)
    coggingtorque = np.zeros(360)

    while queue.qsize() > 0:
        item: TaskData = queue.get()
        angle = int(item.angle)
        tt[angle] = angle
        aflux[angle] = item.aflux
        bflux[angle] = item.bflux
        cflux[angle] = item.cflux
        coggingtorque[angle] = item.coggingtorque

    plt.figure(1)
    plt.plot(tt, coggingtorque)
    plt.xlabel("Time, Seconds")
    plt.ylabel("Cogging Torque, N*m")

    plt.figure(2)
    va = np.diff(aflux) / DT
    vb = np.diff(bflux) / DT
    vc = np.diff(cflux) / DT
    td = tt[1:] / OMEGA - DT / 2
    plt.plot(td, va, td, vb, td, vc)
    plt.xlabel("Time, Seconds")
    plt.ylabel("Phase-to-Neutral Voltage")

    plt.figure(3)
    vll = va - vc
    plt.plot(td, vll)
    plt.xlabel("Time, Seconds")
    plt.ylabel("Line-to-Line Voltage")
    plt.show()

    with open("task_1.csv", "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Angle", "Cogging Torque"])
        csv_array = np.transpose(np.array([tt, coggingtorque]))
        writer.writerows(csv_array)

    with open("task_2.csv", "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Time", "Va", "Vb", "Vc", "Vll"])
        csv_array = np.transpose(np.array([td, va, vb, vc, vll]))
        writer.writerows(csv_array)
