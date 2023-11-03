#!/usr/bin/env python
"""Script for Task 1."""
from matplotlib import pyplot as plt
import numpy as np
import femm


if __name__ == "__main__":
    femm.openfemm(1)
    femm.opendocument("Antunes.FEM")

    femm.mi_saveas("temp.fem")

    femm.mi_modifycircprop("A", 1, 0)
    femm.mi_modifycircprop("B", 1, 0)
    femm.mi_modifycircprop("C", 1, 0)

    RPM = 360 / 60
    DT = 5e-6
    DTTA = 2000.0 * RPM * DT

    coggingtorque: list[float] = []
    aflux: list[float] = []
    bflux = []
    cflux = []
    tt = []
    DTTA = 0.06
    n = round(120 / DTTA)
    for k in range(n):
        tta = DTTA * k
        t = DT * k
        femm.mi_modifyboundprop("mySlidingBand", 10, tta)
        femm.mi_analyze(1)
        femm.mi_loadsolution()
        tq = femm.mo_gapintegral("mySlidingBand", 0)
        tt = [tt, t]
        coggingtorque = [coggingtorque, tq]
        circpropsA = femm.mo_getcircuitproperties("A")
        circpropsB = femm.mo_getcircuitproperties("B")
        circpropsC = femm.mo_getcircuitproperties("C")
        aflux = [aflux, circpropsA(3)]
        bflux = [bflux, circpropsB(3)]
        cflux = [cflux, circpropsC(3)]
        femm.mo_close()
        if (k % 100) == 0:
            print(f"{k} :: {n}")

    plt.figure(1)
    plt.plot(tt, coggingtorque)
    plt.xlabel("Time, Seconds")
    plt.ylabel("Cogging Torque, N*m")

    plt.figure(2)
    va = 8 * np.diff(aflux) / DT
    vb = 8 * np.diff(bflux) / DT
    vc = 8 * np.diff(cflux) / DT
    td = tt(range(2, len(tt))) - DT / 2
    plt.plot(td, va, td, vb, td, vc)
    plt.xlabel("Time, Seconds")
    plt.ylabel("Phase-to-Neutral Voltage")

    plt.figure(3)
    vll = va - vc
    plt.plot(td, vll)
    plt.xlabel("Time, Seconds")
    plt.ylabel("Line-to-Line Voltage")
