#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export the REW .mdat measurements to plain text / CSV.

    python scripts/export_data.py

Input : measurements/jbl-go-2/raw/jbl-go-2_6levels_2026-11-22.mdat
Output: measurements/jbl-go-2/data/*.txt, *.csv
"""

import datetime
import os
import re

import numpy as np

from mdat_reader import load_measurements

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "measurements", "jbl-go-2", "raw",
                   "jbl-go-2_6levels_2026-11-22.mdat")
OUT = os.path.join(ROOT, "measurements", "jbl-go-2", "data")

CONDITIONS = ("JBL Go 2, single unit, AUX input, speaker volume fixed at maximum, "
              "ECM-999 microphone on axis at 20 cm, MOTU M2 interface, ordinary room")


def voltage_of(name):
    m = re.search(r"([0-9.]+)\s*V", name)
    return float(m.group(1)) if m else float("nan")


def main():
    os.makedirs(OUT, exist_ok=True)
    meas = load_measurements(RAW)
    meas.sort(key=lambda m: voltage_of(m["name"]))
    print("%d measurements" % len(meas))

    # ---- per-level text files -------------------------------------------
    for m in meas:
        v = voltage_of(m["name"])
        dt = datetime.datetime.fromtimestamp(m["measurement_date"] / 1000)
        fn = os.path.join(OUT, "jbl-go-2_%sV.txt" % ("%g" % v))
        with open(fn, "w", encoding="utf-8", newline="\n") as f:
            f.write("* JBL Go 2 -- frequency response -- %g V RMS at speaker input\n" % v)
            f.write("* %s\n" % CONDITIONS)
            f.write("* Measured %s with REW %s\n" % (dt.strftime("%Y-%m-%d %H:%M:%S"),
                                                    m["rew_version"].strip()))
            f.write("* %s\n" % (m["sweep_format"] or "").replace("\n", " / "))
            f.write("* %d points, %.6f Hz step, SPL offset %.1f dB "
                    "(not verified against an SPL meter)\n"
                    % (len(m["freqs"]), m["step"], m["spl_offset"]))
            f.write("* Frequency(Hz)\tSPL(dB)\tPhase(degrees)\n")
            for fr, sp, ph in zip(m["freqs"], m["spl"], m["phase"]):
                f.write("%.5f\t%.3f\t%.2f\n" % (fr, sp, ph))
        print("  wrote", os.path.basename(fn))

    # ---- wide CSV: one column per input level ---------------------------
    freqs = meas[0]["freqs"]
    assert all(len(m["freqs"]) == len(freqs) for m in meas)
    cols = ["freq_hz"] + ["%gV" % voltage_of(m["name"]) for m in meas]
    arr = np.column_stack([freqs] + [m["spl"] for m in meas])
    fn = os.path.join(OUT, "jbl-go-2_levels.csv")
    with open(fn, "w", encoding="utf-8", newline="\n") as f:
        f.write("# JBL Go 2 frequency response, SPL in dB on the as-calibrated "
                "REW scale (unverified)\n")
        f.write("# columns: %s\n" % ",".join(cols))
        np.savetxt(f, arr, delimiter=",", fmt=["%.5f"] + ["%.3f"] * len(meas))
    print("  wrote", os.path.basename(fn))

    # ---- THD ------------------------------------------------------------
    fn = os.path.join(OUT, "jbl-go-2_thd.csv")
    thd_freqs = meas[0]["thd_freqs"]
    band = (thd_freqs >= 150) & (thd_freqs <= 10000)
    cols = ["freq_hz"] + ["%gV" % voltage_of(m["name"]) for m in meas]
    arr = np.column_stack([thd_freqs[band]] + [m["thd_pct"][band] for m in meas])
    with open(fn, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Total harmonic distortion in %, computed from the harmonic "
                "arrays stored in the .mdat (H2..H9, power sum, re fundamental)\n")
        f.write("# Below 150 Hz the stored harmonics are limited by the "
                "measurement noise floor and are not reported.\n")
        f.write("# columns: %s\n" % ",".join(cols))
        np.savetxt(f, arr, delimiter=",", fmt=["%.2f"] + ["%.3f"] * len(meas))
    print("  wrote", os.path.basename(fn))

    # ---- summary --------------------------------------------------------
    fn = os.path.join(OUT, "summary.csv")
    head = ("input_v_rms,spl_1k_db,spl_100hz_db,spl_500hz_db,spl_5khz_db,"
            "thd_200hz_pct,thd_500hz_pct,thd_1khz_pct,thd_max_150_10k_pct,"
            "snr_db,sdr_db,measured_at\n")
    with open(fn, "w", encoding="utf-8", newline="\n") as f:
        f.write(head)
        for m in meas:
            tf, tp = m["thd_freqs"], m["thd_pct"]
            pick = lambda hz: float(np.interp(hz, tf, tp))
            dt = datetime.datetime.fromtimestamp(m["measurement_date"] / 1000)
            f.write("%g,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%s\n" % (
                voltage_of(m["name"]),
                np.interp(1000, m["freqs"], m["spl"]),
                np.interp(100, m["freqs"], m["spl"]),
                np.interp(500, m["freqs"], m["spl"]),
                np.interp(5000, m["freqs"], m["spl"]),
                pick(200), pick(500), pick(1000),
                np.max(tp[(tf >= 150) & (tf <= 10000)]),
                m["snr_db"], m["sdr_db"],
                dt.strftime("%Y-%m-%d %H:%M:%S")))
    print("  wrote", os.path.basename(fn))


if __name__ == "__main__":
    main()
