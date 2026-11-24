#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate the figures from the exported CSV data.

    python scripts/plot.py

Reads  measurements/jbl-go-2/data/*.csv
Writes measurements/jbl-go-2/img/frequency-response.png
       measurements/jbl-go-2/img/level-and-distortion.png
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "measurements", "jbl-go-2", "data")
IMG = os.path.join(ROOT, "measurements", "jbl-go-2", "img")

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.edgecolor": "#c9ced6",
    "axes.labelcolor": "#1f2328",
    "text.color": "#1f2328",
    "xtick.color": "#3d444d",
    "ytick.color": "#3d444d",
    "grid.color": "#e3e6ea",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
})

LEVELS = [0.213, 0.425, 0.955, 1.698, 1.906, 2.692]
COLORS = ["#2166ac", "#4393c3", "#92c5de", "#f4a582", "#d6604d", "#b2182b"]
REF = 0.425


def load_levels():
    raw = np.genfromtxt(os.path.join(DATA, "jbl-go-2_levels.csv"),
                        delimiter=",", comments="#")
    return raw[:, 0], {v: raw[:, i + 1] for i, v in enumerate(LEVELS)}


def load_thd():
    raw = np.genfromtxt(os.path.join(DATA, "jbl-go-2_thd.csv"),
                        delimiter=",", comments="#")
    return raw[:, 0], {v: raw[:, i + 1] for i, v in enumerate(LEVELS)}


def smooth_oct(f, y, frac=12):
    """Fractional-octave power smoothing (default 1/12 oct)."""
    lf = np.log2(f)
    out = np.empty_like(y)
    bw = 0.5 / frac
    lo = np.searchsorted(lf, lf - bw)
    hi = np.searchsorted(lf, lf + bw)
    for i in range(len(y)):
        a, b = lo[i], max(hi[i], lo[i] + 1)
        out[i] = 10 * np.log10(np.mean(10 ** (y[a:b] / 10)))
    return out


def fig_response():
    f, spl = load_levels()
    fig, ax = plt.subplots(figsize=(10.2, 6.0))

    m = (f >= 20) & (f <= 20000)
    ax.axvspan(20, 58, color="#f4f5f7", zorder=0, lw=0)
    for v, c in zip(LEVELS, COLORS):
        s = smooth_oct(f, spl[v])
        ax.semilogx(f[m], s[m], color=c, lw=2.8 if v == REF else 1.5,
                    label="%g V RMS%s" % (v, "   <-- max clean output" if v == REF else ""),
                    zorder=3 if v == REF else 2)

    ax.axvline(116, color="#8c959f", lw=0.9, ls=(0, (4, 3)), zorder=1)
    ax.annotate("-6 dB at 116 Hz", xy=(116, 57), xytext=(130, 56),
                fontsize=8.5, color="#5c636d", va="bottom")
    ax.annotate("below 60 Hz:\nroom noise, not the speaker",
                xy=(30, 61), xytext=(25, 70), fontsize=8, color="#6b7280")
    ax.annotate("100 Hz stays at 80-84 dB\nat every level", xy=(100, 82), xytext=(20.5, 90),
                fontsize=8.5, color="#3d444d",
                arrowprops=dict(arrowstyle="->", color="#8c959f", lw=1,
                                connectionstyle="arc3,rad=-0.15"))
    ax.annotate("+5 dB", xy=(315, 100.4), xytext=(205, 105), fontsize=8.5,
                color="#3d444d", arrowprops=dict(arrowstyle="->", color="#8c959f", lw=1))
    ax.annotate("+4.7 dB", xy=(5000, 102.2), xytext=(5600, 106.5), fontsize=8.5,
                color="#3d444d", arrowprops=dict(arrowstyle="->", color="#8c959f", lw=1))
    ax.annotate("19.3 kHz cone/breakup peak\n(+17 dB, may be the microphone)",
                xy=(19300, 112.5), xytext=(3200, 111.5), fontsize=8,
                color="#3d444d", ha="left",
                arrowprops=dict(arrowstyle="->", color="#8c959f", lw=1))

    ax.set_xlim(20, 20000)
    ax.set_ylim(55, 116)
    ax.set_xticks([20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000])
    ax.set_xticklabels(["20", "50", "100", "200", "500", "1k", "2k", "5k", "10k", "20k"])
    ax.set_yticks(range(55, 116, 5))
    ax.grid(True, which="major", axis="both", lw=0.7)
    ax.set_axisbelow(True)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Sound pressure level (dB, uncalibrated scale)")
    ax.set_title("JBL Go 2 \u2014 frequency response at six input levels\n"
                 "AUX input, volume at maximum, 20 cm on axis, 1/12 octave smoothing",
                 fontsize=11.5, loc="left", pad=10)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=3, fontsize=8.2,
              frameon=False, handlelength=1.8, columnspacing=1.6)
    ax.text(0.995, 0.02, "REW 5.40 \u00b7 ECM-999 (no calibration file) \u00b7 MOTU M2",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color="#8c959f")
    fig.tight_layout()
    fig.savefig(os.path.join(IMG, "frequency-response.png"), dpi=170,
                bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)


def fig_level_distortion():
    f, spl = load_levels()
    tf, thd = load_thd()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.6, 4.9))

    # --- left: output ceiling -------------------------------------------
    for hz, c, mk in [(100, "#b2182b", "s"), (1000, "#e08214", "o"), (5000, "#2166ac", "^")]:
        y = [np.interp(hz, f, spl[v]) for v in LEVELS]
        a1.plot(LEVELS, y, marker=mk, ms=5, lw=1.6, color=c, label="%s Hz" % (("%g" % hz)))
    y0 = np.interp(1000, f, spl[LEVELS[0]])
    a1.plot(LEVELS, [y0 + 20 * np.log10(v / LEVELS[0]) for v in LEVELS],
            ls=(0, (5, 4)), lw=1.2, color="#8c959f", label="ideal +20 dB/decade")
    a1.set_xscale("log")
    a1.set_xticks(LEVELS)
    a1.set_xticklabels(["%g" % v for v in LEVELS], fontsize=7.5, rotation=40, ha="right")
    a1.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    a1.set_xlim(0.19, 3.1)
    a1.set_ylim(70, 118)
    a1.set_xlabel("Input voltage (V RMS, measured at the speaker input)")
    a1.set_ylabel("Sound pressure level (dB)")
    a1.set_title("Output ceiling: 12.6x the voltage, +4 dB of sound", fontsize=10.5, loc="left")
    a1.grid(True, lw=0.7)
    a1.set_axisbelow(True)
    a1.legend(fontsize=8, frameon=False, loc="lower right")

    # --- right: THD ------------------------------------------------------
    m = (tf >= 150) & (tf <= 2000)
    for v, c in zip(LEVELS, COLORS):
        y = smooth_oct(tf, thd[v], frac=12)
        a2.semilogx(tf[m], y[m], lw=1.6, color=c, label="%g V" % v)
    a2.set_xlim(150, 2000)
    a2.set_ylim(0.05, 100)
    a2.set_yscale("log")
    a2.set_yticks([0.1, 0.3, 1, 3, 10, 30, 100])
    a2.set_yticklabels(["0.1", "0.3", "1", "3", "10", "30", "100"])
    a2.set_xticks([200, 500, 1000, 2000])
    a2.set_xticklabels(["200", "500", "1k", "2k"])
    a2.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    a2.set_xlabel("Frequency (Hz)")
    a2.set_ylabel("THD (%)")
    a2.set_title("Total harmonic distortion (H2-H9, 1/12 oct)", fontsize=10.5, loc="left")
    a2.grid(True, lw=0.7)
    a2.set_axisbelow(True)
    a2.legend(fontsize=8, frameon=False, title="input", title_fontsize=8,
              loc="upper right", ncol=2, columnspacing=1.2)

    fig.tight_layout()
    fig.savefig(os.path.join(IMG, "level-and-distortion.png"), dpi=170)
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    fig_response()
    fig_level_distortion()
    print("figures written to", IMG)
