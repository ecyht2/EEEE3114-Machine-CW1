#!/usr/bin/env python3
"""Test script."""
import csv
import logging
import multiprocessing
import os
from dataclasses import dataclass
from multiprocessing import Process, Queue

import femm  # type: ignore
import matplotlib.pyplot as plt
import numpy as np

from lib import DT, OMEGA, RPM, femm_handler


@dataclass
class TaskData:
    """The output data format for the collected data."""

    angle: float
    coggingtorque: float
    aflux: float
    bflux: float
    cflux: float


@femm_handler("../dist/cw1_sliding.fem")
def task_1_2(initial_angle: int, count: int, out: Queue):
    """Function to get data for Task 1 and 2.

    :param initial_angle: Initial angle of the measurement.
    :param count: The amount of times to rotate the rotor.
    :param out: The queue to output the collected data to.
    """
    thread_logger = multiprocessing.get_logger()
    femm.mi_modifycircprop("A", 1, 0)
    femm.mi_modifycircprop("B", 1, 0)
    femm.mi_modifycircprop("C", 1, 0)
    femm.smartmesh(1)

    for k in range(count):
        current_angle = initial_angle + k
        # Debug
        thread_logger.info("Angle: %s", current_angle)

        femm.mi_modifyboundprop("Sliding Boundary", 10, current_angle)
        # Anlyzing
        femm.mi_analyze(1)
        femm.mi_loadsolution()

        # Gathering Data
        tq = femm.mo_gapintegral("Sliding Boundary", 0)
        circprops_a = femm.mo_getcircuitproperties("A")
        circprops_b = femm.mo_getcircuitproperties("B")
        circprops_c = femm.mo_getcircuitproperties("C")
        out.put(
            TaskData(
                current_angle,
                tq,
                circprops_a[2],
                circprops_b[2],
                circprops_c[2],
            )
        )

        # Setting up for next cycle
        femm.mo_close()


if __name__ == "__main__":
    logger = multiprocessing.log_to_stderr(logging.INFO)
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
    plt.xlabel("Rotation Angle, °")
    plt.ylabel("Torque, Nm")
    plt.title("Cogging Torque of the Machine")
    plt.xlim(0, 360)
    plt.savefig("../dist/task_1.png")

    plt.figure(2)
    va = 4 * np.diff(aflux) / DT
    vb = 4 * np.diff(bflux) / DT
    vc = 4 * np.diff(cflux) / DT
    td = tt[1:] / OMEGA - DT / 2
    plt.plot(td, va, label="Winding A")
    plt.plot(td, vb, label="Winding B")
    plt.plot(td, vc, label="Winding C")
    plt.legend()
    plt.xlabel("Time, s")
    plt.ylabel("Back EMF, V")
    plt.title("Back EMF of the Machine")
    plt.xlim(min(td), max(td))
    plt.savefig("../dist/task_2_1.png")

    plt.figure(3)
    vll = va - vc
    plt.plot(td, vll)
    plt.xlabel("Time, s")
    plt.ylabel("Line-to-Line Back EMF, V")
    plt.title("Line-to-Line Back EMF of the Machine")
    plt.xlim(min(td), max(td))
    plt.savefig("../dist/task_2_2.png")

    # Logging
    logger.info("Cogging Torque: %s", coggingtorque)
    logger.info("Flux A: %s", aflux)
    logger.info("Flux B: %s", bflux)
    logger.info("Flux C: %s", cflux)
    logger.info("Va: %s", va)
    logger.info("Vb: %s", vb)
    logger.info("Vc: %s", vc)
    logger.info("Vll: %s", vll)

    os.makedirs("../dist", exist_ok=True)
    with open("../dist/task_1.csv", "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Angle", "Cogging Torque"])
        csv_array = np.transpose(np.array([tt, coggingtorque]))
        writer.writerows(csv_array)

    with open("../dist/task_2.csv", "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Time", "Va", "Vb", "Vc", "Vll"])
        csv_array = np.transpose(np.array([td, va, vb, vc, vll]))
        writer.writerows(csv_array)

    # Finding frequency
    fft = np.array(abs(np.fft.fft(coggingtorque)))
    freq = np.fft.helper.fftfreq(coggingtorque.size, DT)
    index = np.argmax(fft)
    f = freq[index]
    angle_period = OMEGA * f**-1
    with open("../dist/task_1.txt", "w", encoding="utf-8") as file:
        output = f"Cogging Troque Period: {angle_period}"
        file.write(output)
        logger.info(output)

    # Finding Km
    k_m = max([va.max(), vb.max(), vc.max()]) / (RPM * 2 * np.pi / 60)
    with open("../dist/task_2.txt", "w", encoding="utf-8") as file:
        output = f"Km: {k_m}"
        file.write(output)
        logger.info(output)

    plt.show()
