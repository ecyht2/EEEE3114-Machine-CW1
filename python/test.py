#!/usr/bin/env python3
"""Test script of coursework"""
import numpy as np
import matplotlib.pyplot as plt


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


if __name__ == "__main__":
    pass
