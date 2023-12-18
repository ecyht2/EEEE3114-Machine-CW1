#!/usr/bin/env python3
"""Script for Task 9"""
import csv
import logging
import multiprocessing
import os
from dataclasses import dataclass
from multiprocessing import Pool

import femm  # type: ignore
import matplotlib.pyplot as plt
import numpy as np

from lib import femm_handler, WINE_DIR, FEMM_DIR, I_PEAK, DT
from task_4 import mag


@dataclass
class TaskData:
    """The output data format for the collected data."""

    pitch_factor: float
    airgap_flux: np.ndarray
    torque: np.ndarray
    emf: np.ndarray


def draw_magnet(pitch_factor: float):
    """Draws the magnet with a given pitch factor.

    :param pitch_factor: The pitch factor of the magnet.
    """
    thread_logger = multiprocessing.get_logger()
    thread_logger.debug("Inside of draw_magnet")

    change_boundary = False
    if pitch_factor == 1.0:
        change_boundary = True
    elif pitch_factor <= 0:
        raise ValueError("Pitch Factor Must Be Between 0 and 1")
    elif pitch_factor >= 1:
        raise ValueError("Pitch Factor Must Be Between 0 and 1")

    thread_logger.info("Using Pitch Factor: %s", pitch_factor)
    pitch_angle = pitch_factor * np.pi / 2 / 2
    thread_logger.info(
        "Pitch Angle: %s°, %s rad", np.degrees(pitch_angle * 2), pitch_angle * 2
    )
    # Nodes
    thread_logger.info("Adding Magnet Nodes")

    # Begining of Magnet
    def get_nodes(
        pitch_angle: float,
    ) -> tuple[tuple[float, float], tuple[float, float]]:
        """Gets the internal and external node coordinates for the magenet.

        :param pitch_angle: The angle span in radians of the magnet.
        :returns: The internal and external coordinates. Each coordinates contain
            a tuple of two values, the first value is the x coordinate and the
            second is the y coordinate.
        """
        x_int = 20 * np.cos(np.pi / 4 + pitch_angle)
        y_int = 20 * np.sin(np.pi / 4 + pitch_angle)
        x_ext = 24 * np.cos(np.pi / 4 + pitch_angle)
        y_ext = 24 * np.sin(np.pi / 4 + pitch_angle)
        return ((x_int, y_int), (x_ext, y_ext))

    def log_coords(coords: tuple[float, float], label: str = "Coordinates"):
        """Logs the coordinates at a debug level.

        :param coords: A tuple representing the coordinates.
            The first value is the x coordinate.
            The second value is the y coordinate.
        :param label: The label of the coordinate.
        """
        thread_logger = multiprocessing.get_logger()
        thread_logger.debug("%s x: %s", label, coords[0])
        thread_logger.debug("%s y: %s", label, coords[1])

    left_nodes = get_nodes(pitch_angle)
    femm.mi_addnode(left_nodes[0][0], left_nodes[0][1])
    femm.mi_addnode(left_nodes[1][0], left_nodes[1][1])

    log_coords(left_nodes[0], "Left Node Internal")
    log_coords(left_nodes[1], "Left Node External")

    # End of Magnet
    right_nodes = get_nodes(-pitch_angle)
    femm.mi_addnode(right_nodes[0][0], right_nodes[0][1])
    femm.mi_addnode(right_nodes[1][0], right_nodes[1][1])

    log_coords(right_nodes[0], "Right Node Internal")
    log_coords(right_nodes[1], "Right Node External")

    # Segments and Arcs
    thread_logger.info("Adding Magnet Segments and Arcs")
    femm.mi_addsegment(
        left_nodes[0][0], left_nodes[0][1], left_nodes[1][0], left_nodes[1][1]
    )
    femm.mi_addsegment(
        right_nodes[0][0], right_nodes[0][1], right_nodes[1][0], right_nodes[1][1]
    )
    femm.mi_addarc(
        right_nodes[1][0],
        right_nodes[1][1],
        left_nodes[1][0],
        left_nodes[1][1],
        np.degrees(pitch_angle * 2),
        5,
    )

    # Material
    thread_logger.info("Adding Block Label")
    label_coords = (22 * np.cos(np.pi / 4), 22 * np.sin(np.pi / 4))
    femm.mi_addblocklabel(label_coords[0], label_coords[1])
    femm.mi_selectlabel(label_coords[0], label_coords[1])
    femm.mi_setblockprop("N42", 1, 0, "", 45)
    femm.mi_clearselected()

    log_coords(label_coords, "Block Label")

    if change_boundary:
        thread_logger.info("Adding New Anti-Periodic Boundary")
        femm.mi_addboundprop("Rotor Boundary 2", *[None for _ in range(8)], 5)
        femm.mi_selectsegment(22, 0)
        femm.mi_selectsegment(0, 22)
        femm.mi_setsegmentprop("Rotor Boundary 2", None, None, None, None)
        femm.mi_clearselected()


def remove_magnet(
    input_file: str = "../dist/cw1_sliding.fem",
    output_file: str = "../dist/task_9.fem",
):
    """Remove the magnet from the FEM model.

    :param input_file: The input FEM file to edit.
    :param output_file: The output FEM file to save to.
    """
    thread_logger = multiprocessing.get_logger()
    thread_logger.debug("Inside of remove_magnet")

    femm.openfemm(winepath=WINE_DIR, femmpath=FEMM_DIR)
    thread_logger.info("Editing %s", input_file)
    femm.opendocument(input_file)

    thread_logger.info("Removing Nodes, Segments and Arcs")
    # Internal
    femm.mi_selectnode(20 * np.cos(np.radians(30)), 20 * np.sin(np.radians(30)))
    femm.mi_selectnode(20 * np.cos(np.radians(75)), 20 * np.sin(np.radians(75)))
    # External
    femm.mi_selectnode(24 * np.cos(np.radians(30)), 24 * np.sin(np.radians(30)))
    femm.mi_selectnode(24 * np.cos(np.radians(75)), 24 * np.sin(np.radians(75)))
    femm.mi_deleteselectednodes()

    # Block Label
    thread_logger.info("Removing Block Label")
    femm.mi_selectlabel(22 * np.cos(np.radians(52.5)), 22 * np.sin(np.radians(52.5)))
    femm.mi_deleteselectedlabels()

    # Block Label
    thread_logger.info("Adding Back Arc")
    femm.mi_addarc(20, 0, 0, 20, 90, 1)

    thread_logger.info("Saving FEM file to %s", output_file)
    femm.mi_saveas(output_file)
    femm.closefemm()


@femm_handler("../dist/task_9.fem")
def task_9(pitch_factor: float) -> TaskData:
    """Function to get data for Task 9.

    :param pitch_factor: The pitch factor of the machine.
    :returns: The measured data of the pitch factor.
    """
    thread_logger = multiprocessing.get_logger()
    thread_logger.info("Pitch Factor: %s", pitch_factor)
    draw_magnet(pitch_factor)
    femm.smartmesh(1)

    # Modifying properties
    thread_logger.info("Getting Flux and Torque")
    femm.mi_modifyboundprop("Sliding Boundary", 10, 0)

    torque_range: np.ndarray = np.arange(180)
    tq: np.ndarray = np.zeros_like(torque_range, dtype=np.ndarray)
    flux: np.ndarray = np.zeros_like(torque_range, dtype=np.ndarray)

    for i, angle in enumerate(torque_range):
        # Modifying properties
        femm.mi_modifycircprop("A", 1, I_PEAK * np.sin(np.radians(angle)))
        femm.mi_modifycircprop("B", 1, I_PEAK * np.sin(np.radians(angle + 120)))
        femm.mi_modifycircprop("C", 1, I_PEAK * np.sin(np.radians(angle - 120)))
        thread_logger.info("Flux Angle: %s°", angle)

        # Anlyzing
        femm.mi_analyze(1)
        femm.mi_loadsolution()

        # Gathering Data
        # Torque
        tq[i] = femm.mo_gapintegral("Sliding Boundary", 0)
        # Flux
        flux[i] = mag(femm.mo_getgapb("Sliding Boundary", angle))

        # Setting up for next cycle
        femm.mo_close()

    # Modifying properties
    thread_logger.info("Getting Circuit Flux for Back EMF")
    femm.mi_modifycircprop("A", 1, 0)
    femm.mi_modifycircprop("B", 1, 0)
    femm.mi_modifycircprop("C", 1, 0)

    emf_range: np.ndarray = np.arange(180)
    emf: np.ndarray = np.zeros((emf_range.size, 3), dtype=np.ndarray)

    for i, angle in enumerate(emf_range):
        femm.mi_modifyboundprop("Sliding Boundary", 10, angle)
        thread_logger.info("Rotor Angle: %s°", angle)

        # Anlyzing
        femm.mi_analyze(1)
        femm.mi_loadsolution()

        # Gathering Data
        emf[i, 0] = femm.mo_getcircuitproperties("A")[2]
        emf[i, 1] = femm.mo_getcircuitproperties("B")[2]
        emf[i, 2] = femm.mo_getcircuitproperties("C")[2]

        # Setting up for next cycle
        femm.mo_close()

    return TaskData(pitch_factor, flux, tq, emf)


if __name__ == "__main__":
    logger = multiprocessing.log_to_stderr(logging.INFO)
    START_PITCH = 0.1
    END_PITCH = 1.1
    PITCH_STEP = 0.1
    PITCH_FACTOR: np.ndarray = np.arange(START_PITCH, END_PITCH, step=PITCH_STEP)
    PITCH_FACTOR = np.concatenate((PITCH_FACTOR, np.array([0.45, 0.01])))
    PITCH_FACTOR.sort()
    THREADS = PITCH_FACTOR.size

    logger.debug("FREQ: %s", PITCH_FACTOR)

    logger.info("Removing Magnet From Model")
    remove_magnet()
    logger.info("Gathering Data with Different Pitch Factor")
    with Pool(THREADS) as p:
        output: list[TaskData] = p.map(task_9, PITCH_FACTOR)

    logger.info("Processing Data")
    os.makedirs("../dist", exist_ok=True)

    processed_data = np.zeros((PITCH_FACTOR.size, 4))

    with open("../dist/task_9.csv", "w", encoding="utf-8") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(
            [
                "Pitch Factor",
                "Airgap Flux",
                "Torque",
                "EMF",
            ]
        )
        for index, data in enumerate(output):
            back_emf = 4 * np.diff(data.emf, axis=0) / DT
            processed_data[index] = [
                data.pitch_factor,
                abs(data.airgap_flux).mean(),
                abs(data.torque).max(),
                abs(back_emf).max(),
            ]
            data_values = processed_data[index]

            logger.debug("Pitch Factor: %s", data_values[0])
            logger.debug("Airgap Flux: %s", data_values[1])
            logger.debug("Torque: %s", data_values[2])
            logger.debug("EMF: %s", data_values[3])

        csv_writer.writerows(processed_data)

    logger.info("Plotting Data")

    pf = processed_data[:, 0]
    airgap_flux = processed_data[:, 1]
    tq_dev = processed_data[:, 2]
    back_emf = processed_data[:, 3]
    plt.figure()
    plt.title("Rated Torque")
    plt.plot(pf, tq_dev)
    plt.xlim(pf.min(), pf.max())
    plt.xticks(pf)
    plt.savefig("../dist/task_9_torque.png")

    plt.figure()
    plt.title("Back EMF")
    plt.plot(pf, back_emf)
    plt.xlim(pf.min(), pf.max())
    plt.xticks(pf)
    plt.savefig("../dist/task_9_back_emf.png")

    plt.figure()
    plt.title("Airgap Flux Density")
    plt.plot(pf, airgap_flux)
    plt.xlim(pf.min(), pf.max())
    plt.xticks(pf)
    plt.savefig("../dist/task_9_airgap_flux.png")

    logger.info("Saving Data")
    pf = np.zeros_like(PITCH_FACTOR)
    torque = np.zeros((PITCH_FACTOR.size, output[0].torque.size))
    airgap_flux = np.zeros((PITCH_FACTOR.size, output[0].airgap_flux.size))
    back_emf = np.zeros((PITCH_FACTOR.size, output[0].emf.shape[0], 3))

    for index, data in enumerate(output):
        pf[index] = data.pitch_factor
        torque[index] = data.torque
        airgap_flux[index] = data.airgap_flux
        back_emf[index] = data.emf

    np.savez(
        "../dist/task_9.npz",
        pitch_factor=pf,
        torque=torque,
        airgap_flux=airgap_flux,
        circuit_flux=back_emf,
    )

    plt.show()
