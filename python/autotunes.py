#!/usr/bin/env python
"""Script for Task 1."""
from matplotlib import pyplot as plt
import numpy as np
import femm  # type: ignore

from lib import setup_femm, cleanup_femm


if __name__ == "__main__":
    out = setup_femm()

    # Setting current to 0
    femm.mi_modifycircprop("A", 1, 0)
    femm.mi_modifycircprop("B", 1, 0)
    femm.mi_modifycircprop("C", 1, 0)

    RPM = 1500
    OMEGA = RPM * 360 / 60
    DT = 1 / OMEGA
    DTTA = 2000.0 * RPM * DT

    DTTA = 20
    N = round(120 / DTTA)
    N = 360

    # Allocating Arrays
    coggingtorque = np.zeros(N, float)
    aflux = np.zeros(N, float)
    bflux = np.zeros(N, float)
    cflux = np.zeros(N, float)
    tt = np.zeros(N, float)

    for k in range(N):
        print(f"Angle: {k}")

        tta = DTTA * k
        t = DT * k
        femm.mi_analyze(1)
        femm.mi_loadsolution()
        femm.mo_groupselectblock(1)
        tq = femm.mo_blockintegral(21)
        tt[k] = t
        coggingtorque[k] = tq
        circpropsA: list[float] = femm.mo_getcircuitproperties("A")
        circpropsB: list[float] = femm.mo_getcircuitproperties("B")
        circpropsC: list[float] = femm.mo_getcircuitproperties("C")
        aflux[k] = circpropsA[2]
        bflux[k] = circpropsB[2]
        cflux[k] = circpropsC[2]

        # Preparing for next step
        femm.mo_close()
        femm.mi_selectgroup(1)
        femm.mi_moverotate(0, 0, 1)

    cleanup_femm(out)

    plt.figure(1)
    plt.plot(tt, coggingtorque)
    plt.xlabel("Time, Seconds")
    plt.ylabel("Cogging Torque, N*m")

    plt.figure(2)
    va = 8 * np.diff(aflux) / DT
    vb = 8 * np.diff(bflux) / DT
    vc = 8 * np.diff(cflux) / DT
    td = tt[1:len(tt)] - DT / 2
    plt.plot(td, va, td, vb, td, vc)
    plt.xlabel("Time, Seconds")
    plt.ylabel("Phase-to-Neutral Voltage")

    plt.figure(3)
    vll = va - vc
    plt.plot(td, vll)
    plt.xlabel("Time, Seconds")
    plt.ylabel("Line-to-Line Voltage")
    plt.show()
