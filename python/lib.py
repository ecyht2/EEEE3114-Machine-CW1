#!/usr/bin/env python3
"""Shared library code for all the scripts."""
import shutil
import tempfile
import os
import logging

from functools import wraps
from typing import Callable, Any
from multiprocessing import Process, Queue

import femm  # type: ignore

FEMM_DIR = "/home/user/.local/share/wineprefixes/default/drive_c/femm42/bin/"
WINE_DIR = "/usr/bin/wine"


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


def femm_handler(document: str, femm_dir: str = FEMM_DIR, wine_dir: str = WINE_DIR):
    """Function decorator to handle FEMM in a seperate instance."""
    logging.debug("Starting FEMM using: %s", document)
    logging.debug("FEMM Directory: %s", femm_dir)
    logging.debug("Using wine binary: %s", wine_dir)

    def custom_handler(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            os.environ["WINEDEBUG"] = "-all"
            with tempfile.TemporaryDirectory() as dirname:
                shutil.copytree(femm_dir, dirname, dirs_exist_ok=True)
                logging.debug("Using FEMM Thread Dir: %s", dirname)

                # Setup FEMM instance
                femm.openfemm(
                    winepath=wine_dir,
                    femmpath=dirname,
                )
                femm.opendocument(document)

                with tempfile.NamedTemporaryFile(suffix=".fem", dir=dirname) as file:
                    file.close()
                    femm.mi_saveas(file.name)
                    logging.debug("Using Temporary File: %s", file.name)

                # Running decorated function
                value = func(*args, **kwargs)

                # Closing FEMM instance
                femm.closefemm()
                logging.debug("Exiting FEMM")
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

        # pytlint: disable = consider-using-with
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
