#!/usr/bin/env python3
"""Script to plot Torque based on equivalent circuit."""
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    angle = np.arange(360)
    E_B = 113.2
    omega = 1500 * 2 * np.pi / 60

    X_S = 6.208
    Pd = 3 * (E_B * np.sqrt(20**2 * X_S**2 - E_B**2))\
        / X_S * np.sin(np.radians(angle))

    Td = Pd / omega

    X_S = 6.029
    Pd2 = 3 * (E_B * np.sqrt(20**2 * X_S**2 - E_B**2))\
        / X_S * np.sin(np.radians(angle))

    Td2 = Pd2 / omega

    plt.plot(angle, Td)
    plt.xlim([min(angle), max(angle)])
    plt.xlabel("Load Angle, °")
    plt.ylabel("Torque Developed, Nm")
    plt.title("Torque Developed at Different Load Angle")
    plt.savefig("../dist/task_8_circuit.png")
    plt.show()
