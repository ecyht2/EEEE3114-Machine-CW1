#!/usr/bin/env python3
"""Script to plot all the data from CSV file."""
import matplotlib.pyplot as plt
import numpy as np


def get_data(file_path: str) -> np.ndarray:
    """Gets the data from a CSV file.

    :param file_path: The file path of the CSV file.
    """
    return np.genfromtxt(file_path, skip_header=True, delimiter=",")


if __name__ == "__main__":
    # Importing Data
    task_1 = get_data("../dist/task_1.csv")
    task_2 = get_data("../dist/task_2.csv")
    task_3 = get_data("../dist/task_3.csv")
    task_3_ripple = get_data("../dist/task_3_ripple.csv")
    task_4 = get_data("../dist/task_4.csv")
    task_5 = get_data("../dist/task_5.csv")

    # Task 1
    plt.figure()
    tt = task_1[:, 0]
    coggingtorque = task_1[:, 1]
    plt.plot(tt, coggingtorque)
    plt.xlim(tt.min(), tt.max())
    plt.xlabel("Rotation Angle, °")
    plt.ylabel("Torque, Nm")
    plt.title("Cogging Torque of the Machine")
    plt.savefig("../dist/task_1.png")

    # Task 2
    # Phase Eb
    plt.figure()
    td = task_2[:, 0]
    va = task_2[:, 1]
    vb = task_2[:, 2]
    vc = task_2[:, 3]
    plt.plot(td, va, label="Winding A")
    plt.plot(td, vb, label="Winding B")
    plt.plot(td, vc, label="Winding C")
    plt.legend()
    plt.xlabel("Time, s")
    plt.ylabel("Back EMF, V")
    plt.title("Back EMF of the Machine")
    plt.xlim(min(td), max(td))
    plt.savefig("../dist/task_2_1.png")

    # Line-to-Line Eb
    plt.figure()
    vll = task_2[:, 4]
    plt.plot(td, vll)
    plt.xlabel("Time, s")
    plt.ylabel("Line-to-Line Back EMF, V")
    plt.title("Line-to-Line Back EMF of the Machine")
    plt.xlim(min(td), max(td))
    plt.savefig("../dist/task_2_2.png")

    # Task 3
    # Load Angle
    plt.figure()
    phase_angle = task_3[:, 0]
    dev_torque = task_3[:, 1]
    plt.plot(phase_angle, dev_torque)
    plt.xlabel("Load Angle, °")
    plt.ylabel("Torque Developed, Nm")
    plt.title("Torque Developed at Different Load Angle")
    plt.xlim(min(phase_angle), max(phase_angle))
    plt.savefig("../dist/task_3.png")

    # Torque Ripple
    plt.figure()
    phase_angle = task_3_ripple[:, 0]
    dev_torque = task_3_ripple[:, 1]
    plt.plot(phase_angle, dev_torque)
    plt.xlabel("Load Angle, °")
    plt.ylabel("Torque Developed, Nm")
    plt.title("Torque Ripple of the Machine")
    plt.xlim(min(phase_angle), max(phase_angle))
    plt.savefig("../dist/task_3_ripple.png")

    # Task 4
    plt.figure()
    currents = task_4[:, 0]
    yoke = task_4[:, 1]
    teeth = task_4[:, 2]
    magnet = task_4[:, 3]
    # Yoke
    plt.plot(currents, yoke, label="Yoke")
    # Teeth
    plt.plot(currents, teeth, label="Teeth")
    # Magnet
    plt.plot(currents, magnet, label="Magnet")
    # Labels
    plt.xlabel("Peak Current, A")
    plt.ylabel("Magnetic Field Density, T")
    plt.title("Magnetic Field Density at Different Peak Current")
    plt.xlim(min(currents), max(currents))
    plt.xticks(currents)
    plt.legend()
    plt.savefig("../dist/task_4.png")

    # Task 5
    plt.figure()
    currents = task_5[:, 0]
    mean_torque = task_5[:, 1]
    plt.plot(currents, mean_torque)
    # Labels
    plt.xlabel("Peak Current, A")
    plt.ylabel("Mean Torque, Nm")
    plt.title("Mean Torque at Different Peak Current")
    plt.xlim(min(currents), max(currents))
    plt.xticks(currents)
    plt.savefig("../dist/task_5.png")
