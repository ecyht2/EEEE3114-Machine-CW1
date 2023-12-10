#!/usr/bin/env python3
"""Shared library code for all the scripts."""
import multiprocessing
import os
import shutil
import tempfile
from functools import wraps
from multiprocessing import Process, Queue
from typing import Any, Callable

import femm  # type: ignore
import numpy as np
import matplotlib.pyplot as plt

FEMM_DIR = "/home/user/.local/share/wineprefixes/default/drive_c/femm42/bin/"
WINE_DIR = "/usr/bin/wine"

RPM = 1500  # Mechanical RPM
OMEGA = RPM * 360 / 60  # Mechanical °/sec
DT = 1 / OMEGA  # Mechanical sec/°
F_E = 2 * RPM / 60  # Electrical Frequency
OMEGA_E = 360 * F_E  # Electrical °/sec
EDT = 1 / OMEGA_E  # Electrical sec/°
MIDDLE = 52.5  # Angle of the middle of the magnet
SLOT_ANGLE = 15  # Angle between each slot
SLOT = 11.4  # The total angle of a slot
TEETH = 3.6  # The total angle of a teeth
I_PEAK = 20  # Rated current


def get_data(file_path: str) -> np.ndarray:
    """Gets the data from a CSV file.

    :param file_path: The file path of the CSV file.
    """
    return np.genfromtxt(file_path, skip_header=True, delimiter=",")


def plot_graph(x: list, y: list):
    """Gets the data from a CSV file.

    :param x: The items on the x-axis.
    :param y: The items on the y-axis.
    """
    plt.plot(x, y)
    plt.show()


def setup_femm() -> str:
    """Starts a new FEMM simulation."""
    os.environ["WINEDEBUG"] = "-all"
    femm_dir = "/home/user/.local/share/wineprefixes/default/drive_c/femm42/bin/"

    femm.openfemm(
        winepath="/usr/bin/wine",
        femmpath=femm_dir,
    )
    femm.opendocument("../cw1.fem")

    with tempfile.NamedTemporaryFile(suffix=".fem") as file:
        file.close()
        femm.mi_saveas(file.name)

    return file.name


def cleanup_femm(femm_file: str):
    """Cleans up the FEMM simulation."""
    femm.closefemm()
    os.remove(femm_file)


def extract_queue(queue: Queue) -> np.ndarray:
    """Extracts all the data from the queue."""
    array = np.empty(queue.qsize(), dtype=None)
    for i in range(queue.qsize()):
        array[i] = queue.get()
    return array


def femm_handler(document: str, femm_dir: str = FEMM_DIR, wine_dir: str = WINE_DIR):
    """Function decorator to handle FEMM in a seperate instance.

    :param document: The document to open in FEMM.
    :param femm_dir: The location of the FEMM binary.
    :param wine_dir: The location of the wine runtime binary.
    :returns: Wrapped function.
    """
    logger = multiprocessing.get_logger()
    logger.debug("Starting FEMM using: %s", document)
    logger.debug("FEMM Directory: %s", femm_dir)
    logger.debug("Using wine binary: %s", wine_dir)

    def custom_handler(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            os.environ["WINEDEBUG"] = "-all"
            with tempfile.TemporaryDirectory() as dirname:
                shutil.copytree(femm_dir, dirname, dirs_exist_ok=True)
                logger.debug("Using FEMM Thread Dir: %s", dirname)

                # Setup FEMM instance
                femm.openfemm(
                    winepath=wine_dir,
                    femmpath=dirname,
                )
                femm.opendocument(document)

                with tempfile.NamedTemporaryFile(suffix=".fem", dir=dirname) as file:
                    file.close()
                    femm.mi_saveas(file.name)
                    logger.debug("Using Temporary File: %s", file.name)

                # Running decorated function
                value = func(*args, **kwargs)

                # Closing FEMM instance
                femm.closefemm()
                logger.debug("Exiting FEMM")
                return value

        return wrapper

    return custom_handler


class FEMMWorker(Process):
    """Worker for an FEMM simulation."""

    def __init__(
        self,
        setup: Callable[[], None],
        loop: Callable[[Any], Any],
        queue: Queue,
        out: Queue,
    ):
        super().__init__()
        self.queue = queue
        self.loop = loop
        self.out_queue = out

        femm_dir = "/home/user/.local/share/wineprefixes/default/drive_c/femm42/bin/"
        os.environ["WINEDEBUG"] = "-all"

        # pylint: disable = consider-using-with
        self.dirname = tempfile.TemporaryDirectory()
        shutil.copytree(femm_dir, self.dirname.name, dirs_exist_ok=True)

        femm.openfemm(
            winepath="/usr/bin/wine",
            femmpath=self.dirname.name,
        )
        femm.opendocument("../cw1.fem")

        with tempfile.NamedTemporaryFile(suffix=".fem", dir=self.dirname.name) as file:
            file.close()
            femm.mi_saveas(file.name)

        setup()

    def run(self):
        """Loop to run all the qued items."""
        for data in iter(self.queue.get, None):
            self.out_queue.put(self.loop(data))

    def __del__(self):
        print("Deleting")
        self.dirname.cleanup()
        femm.closefemm()
