# Data files

All files are plain text, UTF-8, `\n` line endings, tab- or comma-separated.
Numbers are rounded for readability; the `.mdat` in `../raw/` is the exact source.

## `jbl-go-2_<voltage>V.txt`

REW-style export, one file per input level.

```
* header lines, all start with "*"
* Frequency(Hz)	SPL(dB)	Phase(degrees)
0.33646	55.671	-142.31
...
```

- 59 443 rows, 0.336 Hz spacing, 0.34 Hz to 20 kHz.
- SPL is on the uncalibrated REW scale (see `../../method.md`).
- Phase is relative; there was no timing reference during the sweep.

These files can be imported straight into REW (*Import → Import measurement*).

## `jbl-go-2_levels.csv`

Wide format: one frequency column, one SPL column per input level, on the common
frequency axis. Header lines start with `#`.

```
freq_hz,0.213V,0.425V,0.955V,1.698V,1.906V,2.692V
```

## `jbl-go-2_thd.csv`

Total harmonic distortion in percent, 150 Hz – 10 kHz, one column per level.
Computed from the harmonic arrays stored in the `.mdat` (H2 … H9, power sum,
referenced to the fundamental).

Above roughly 2 kHz the higher harmonics run past 20 kHz and drop out of the sum,
so values in that region are lower bounds; the figure only plots up to 2 kHz.
Below 150 Hz the harmonics sit near the noise floor and are not reported.

## `summary.csv`

One row per input level with the headline numbers:

| Column | Meaning |
|---|---|
| `input_v_rms` | input voltage, RMS, measured at the speaker input |
| `spl_1k_db`, `spl_100hz_db`, `spl_500hz_db`, `spl_5khz_db` | SPL at those frequencies |
| `thd_200hz_pct`, `thd_500hz_pct`, `thd_1khz_pct` | THD at those frequencies |
| `thd_max_150_10k_pct` | worst THD between 150 Hz and 10 kHz |
| `snr_db` | sweep signal-to-noise ratio reported by REW |
| `sdr_db` | sweep signal-to-distortion ratio reported by REW |
| `measured_at` | local timestamp of the sweep |
