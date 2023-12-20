#!/usr/bin/env python3
"""Script for task 10."""
import csv
import logging
import multiprocessing
import os
from dataclasses import dataclass
from multiprocessing import Pool

import femm  # type: ignore
import matplotlib.pyplot as plt
import numpy as np

from lib import femm_handler, I_PEAK, SLOT_ANGLE


@dataclass
class TaskData:
    """The output data format for the collected data."""

    opening_factor: float
    dev_torque: np.ndarray
    cogging_troque: np.ndarray


def change_slot_opening(opening_factor: float):
    """Change the machine slot opening factor.

    The slot opening factor is the variation between slot width and slot opening
    width.


    Note
    ----

    The slot opening factor must be between 0 (exclusive) and 1 (inclusive).

    :param opening_factor: The slot opening factor to change to.
    """
    if not 0 < opening_factor <= 1:
        raise ValueError(
            "The slot opening factor must be between 0 (exclusive) and 1 (inclusive)."
        )
    thread_logger = multiprocessing.get_logger()
    thread_logger.info("Chaging to opening slot factor of: %s", opening_factor)

    # How much to rotate the slot nodes
    rotate_angle = 9.66 * opening_factor / 2 - 1.14
    thread_logger.debug("Rotating Nodes by %s°", rotate_angle)

    for slot in range(6):
        thread_logger.info("Changing Slot %s", slot + 1)
        slot_center = SLOT_ANGLE * slot + 7.5

        right_slot_angle = np.radians(slot_center - 1.14)
        left_slot_angle = np.radians(slot_center + 1.14)
        thread_logger.debug("Slot Center Angle: %s°", slot_center)
        thread_logger.debug("Right Slot Angle: %s°", np.degrees(right_slot_angle))
        thread_logger.debug("Left Slot Angle: %s°", np.degrees(left_slot_angle))

        thread_logger.info("Moving the left side of the slot")
        femm.mi_selectnode(25 * np.cos(left_slot_angle), 25 * np.sin(left_slot_angle))
        femm.mi_selectnode(
            26.4 * np.cos(left_slot_angle), 26.4 * np.sin(left_slot_angle)
        )
        femm.mi_moverotate(0, 0, rotate_angle)
        femm.mi_clearselected()

        thread_logger.info("Moving the right side of the slot")
        femm.mi_selectnode(25 * np.cos(right_slot_angle), 25 * np.sin(right_slot_angle))
        femm.mi_selectnode(
            26.4 * np.cos(right_slot_angle), 26.4 * np.sin(right_slot_angle)
        )
        femm.mi_moverotate(0, 0, -rotate_angle)
        femm.mi_clearselected()


@femm_handler("../dist/cw1_sliding.fem")
def task_10(opening_factor: float) -> TaskData:
    """Function to get data for Task 10.

    :param opening_factor: The slot factor of the machine.
    :returns: The data collected for the simulations.
    """
    thread_logger = multiprocessing.get_logger()
    thread_logger.info("Slot Opening Factor: %s", opening_factor)
    change_slot_opening(opening_factor)
    femm.smartmesh(1)

    thread_logger.info("Getting Torque Ripple and Overall Torque")
    dev_torque = np.zeros(360, float)
    for angle in range(360):
        femm.mi_modifycircprop("A", 1, I_PEAK * np.sin(np.radians(angle + 77)))
        femm.mi_modifycircprop("B", 1, I_PEAK * np.sin(np.radians(angle + 77 + 120)))
        femm.mi_modifycircprop("C", 1, I_PEAK * np.sin(np.radians(angle + 77 - 120)))
        femm.mi_modifyboundprop("Sliding Boundary", 10, angle / 2 + 23.1)

        # Debug
        thread_logger.info("Load Angle %s°", angle + 77)
        thread_logger.debug("A: %s A", I_PEAK * np.sin(np.radians(angle + 77)))
        thread_logger.debug("B: %s A", I_PEAK * np.sin(np.radians(angle + 77 + 120)))
        thread_logger.debug("C: %s A", I_PEAK * np.sin(np.radians(angle + 77 - 120)))

        # Anlyzing
        femm.mi_analyze(1)
        femm.mi_loadsolution()
        dev_torque[angle] = femm.mo_gapintegral("Sliding Boundary", 0)

        thread_logger.debug("Torque: %s", dev_torque[angle])

        # Setting up for next cycle
        femm.mo_close()

    thread_logger.info("Getting Cogging Torque")
    cogging_torque = np.zeros(360, float)

    femm.mi_modifycircprop("A", 1, 0)
    femm.mi_modifycircprop("B", 1, 0)
    femm.mi_modifycircprop("C", 1, 0)

    for angle in range(360):
        femm.mi_modifyboundprop("Sliding Boundary", 10, angle)

        # Debug
        thread_logger.info("Rotor Angle %s°", angle + 77)

        # Anlyzing
        femm.mi_analyze(1)
        femm.mi_loadsolution()
        cogging_torque[angle] = femm.mo_gapintegral("Sliding Boundary", 0)

        thread_logger.debug("Torque: %s", cogging_torque[angle])

        # Setting up for next cycle
        femm.mo_close()

    return TaskData(opening_factor, dev_torque, cogging_torque)


def main():
    """Main script function."""
    logger = multiprocessing.log_to_stderr(logging.INFO)
    start_factor = 0.1
    end_factor = 1.1
    factor_step = 0.1
    slot_factor: np.ndarray = np.arange(start_factor, end_factor, factor_step)  # type: ignore
    threads = slot_factor.size

    logger.debug("Opening Slot Factor: %s", slot_factor)

    logger.info("Gathering Data")
    with Pool(threads) as p:
        data_collected = p.map(task_10, slot_factor)

    os.makedirs("../dist", exist_ok=True)
    logger.info("Analyzing Data")
    mean_torque = np.zeros_like(slot_factor)
    dev_torque = np.zeros((slot_factor.size, 360))
    cogging_torque = np.zeros((slot_factor.size, 360))

    with open("../dist/task_10.csv", "w", encoding="utf-8") as file:
        csv_writer = csv.writer(file)

        csv_writer.writerow(
            (
                "Slot Opening Factor",
                "Overall Torque",
                "Developed Torque Amplitude",
                "Cogging Torque Amplitude",
            )
        )

        for i, data in enumerate(data_collected):
            dev_torque[i] = data.dev_torque
            cogging_torque[i] = data.cogging_troque
            mean_torque[i] = abs(data.dev_torque).mean()

            csv_writer.writerow(
                (
                    data.opening_factor,
                    mean_torque[i],
                    data.dev_torque.max() - data.dev_torque.mean(),
                    data.cogging_troque.max() - data.cogging_troque.mean(),
                )
            )

    logger.info("Saving Data")
    np.savez(
        "../dist/task_10.npz",
        slot_factor=slot_factor,
        developed_torque=dev_torque,
        cogging_torque=cogging_torque,
        mean_torque=mean_torque,
    )

    plot_data(slot_factor, mean_torque, dev_torque, cogging_torque)


def plot_data(
    slot_factor: np.ndarray,
    mean_torque: np.ndarray,
    dev_torque: np.ndarray,
    cogging_torque: np.ndarray,
):
    """Plots all the data.

    :param slot_factor: The list of slot factors.
    :param mean_torque: The list of mean torque.
    :param dev_torque: The list of developed torque.
    :param cogging_torque: The list of cogging torque.
    """
    logger = multiprocessing.get_logger()
    # Plotting Data
    logger.info("Plotting Data")
    max_index = mean_torque.argmax()

    # Overall Torque
    logger.info("Plotting Overall Torque")
    plt.figure()
    plt.plot(slot_factor, mean_torque)
    plt.title("Overall Torque at Different Slot Opening Factor")
    plt.xlim(slot_factor.min(), slot_factor.max())
    plt.xticks(slot_factor)
    plt.xlabel("Slot Opening Factor")
    plt.ylabel("Overall Torque, Nm")
    plt.savefig("../dist/task_10_overall_torque.png")

    plot_ripple(slot_factor, dev_torque, max_index)
    plot_cogging(slot_factor, cogging_torque, max_index)


def plot_ripple(
    slot_factor: np.ndarray, dev_torque: np.ndarray, max_index: np.signedinteger
):
    """Plots the torque ripple data.

    :param slot_factor: The list of slot factors.
    :param dev_torque: The list of developed torque.
    :param max_index: The index where the max developed torque is.
    """
    logger = multiprocessing.get_logger()
    angle = np.arange(360)
    opening_factors = (slot_factor[0], slot_factor[max_index], slot_factor[-1])
    legends = tuple(map(lambda x: f"Opening Factor: {x}", opening_factors))

    # Torque Ripple
    logger.info("Plotting Torque Ripple")
    plt.figure()
    plt.plot(angle, dev_torque[0], angle, dev_torque[max_index], angle, dev_torque[-1])
    plt.title("Torque Ripple at Various Slot Opening Factor")
    plt.xlabel("Load Angle, °")
    plt.ylabel("Developed Torque, Nm")
    plt.xlim(angle.min(), angle.max())
    plt.legend(legends)
    plt.savefig("../dist/task_10_torque_ripple.png")

    # Ripple Amplitude
    logger.info("Plotting Torque Ripple Amplitude")
    plt.figure()
    ripple_max = dev_torque.max(axis=1)
    ripple_mean = dev_torque.mean(axis=1)
    ripple_amplitude = ripple_max - ripple_mean
    plt.plot(slot_factor, ripple_amplitude)
    plt.title("Torque Ripple Amplitude at Different Slot Opening Factor")
    plt.xlim(slot_factor.min(), slot_factor.max())
    plt.xticks(slot_factor)
    plt.xlabel("Slot Opening Factor")
    plt.ylabel("Torque Ripple Amplitude, Nm")
    plt.savefig("../dist/task_10_ripple_amplitude.png")


def plot_cogging(
    slot_factor: np.ndarray, cogging_torque: np.ndarray, max_index: np.signedinteger
):
    """Plots the cogging torque data.

    :param slot_factor: The list of slot factors.
    :param cogging_torque: The list of cogging torque.
    :param max_index: The index where the max developed torque is.
    """
    logger = multiprocessing.get_logger()
    angle = np.arange(360)
    opening_factors = (slot_factor[0], slot_factor[max_index], slot_factor[-1])
    legends = tuple(map(lambda x: f"Opening Factor: {x}", opening_factors))
    # Cogging Torque
    logger.info("Plotting Cogging Torque")
    plt.figure()
    plt.plot(
        angle,
        cogging_torque[0],
        angle,
        cogging_torque[max_index],
        angle,
        cogging_torque[-1],
    )
    plt.title("Cogging Torque at Various Slot Opening Factor")
    plt.xlabel("Load Angle, °")
    plt.ylabel("Cogging Torque, Nm")
    plt.xlim(angle.min(), angle.max())
    plt.legend(legends)
    plt.savefig("../dist/task_10_cogging_torque.png")

    # Cogging Torque Amplitude
    logger.info("Plotting Cogging Torque Amplitude")
    plt.figure()
    cogging_max = cogging_torque.max(axis=1)
    cogging_mean = cogging_torque.mean(axis=1)
    cogging_amplitude = cogging_max - cogging_mean
    plt.plot(slot_factor, cogging_amplitude)
    plt.title("Cogging Torque Amplitude at Different Slot Opening Factor")
    plt.xlim(slot_factor.min(), slot_factor.max())
    plt.xticks(slot_factor)
    plt.xlabel("Slot Opening Factor")
    plt.ylabel("Cogging Torque Amplitude, Nm")
    plt.savefig("../dist/task_10_cogging_amplitude.png")

    plt.show()


if __name__ == "__main__":
    main()
