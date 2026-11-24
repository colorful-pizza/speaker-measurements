# Method

Everything below is also stored inside the `.mdat` files; this page just makes it
readable without REW.

## Equipment

| Item | Detail |
|---|---|
| Loudspeaker | JBL Go 2, single unit, factory firmware, no modifications |
| Source | AUX (3.5 mm) input, speaker volume fixed at maximum for the whole session |
| Interface | MOTU M2, ASIO driver, output 1 → speaker, input 1 ← microphone |
| Microphone | ECM-999 (old, uncalibrated), on axis, 20 cm from the front grille |
| Software | Room EQ Wizard 5.40 beta 120, Java 11.0.30, Windows 10 |
| Room | Ordinary untreated room, speaker free-standing; 23.8 °C, 53% RH (indicative only) |
| Input level | Measured with a multimeter at the speaker input, RMS, at 1 kHz |

<!-- TODO: add the placement photo as measurements/jbl-go-2/img/setup.jpg -->

## REW settings

| Parameter | Value |
|---|---|
| Signal | 256k logarithmic sine sweep, 1 sweep at 0 dBFS |
| Timing reference | none (loopback timing not used) |
| Sample rate | 48 kHz |
| Points | 59 443 |
| Frequency range | 0.34 Hz – 20 kHz, 0.336 Hz spacing |
| Smoothing applied in REW | none (smoothing is applied by `scripts/plot.py`) |

With a logarithmic sweep and no timing reference, the magnitude response is still
correct; only the absolute delay (and therefore the absolute phase offset) is
arbitrary. Phase values are exported but should be read as relative.

## Level series

The speaker volume was set to maximum once and never touched. The input voltage
was then changed between sweeps and measured at the speaker input:

`0.213 / 0.425 / 0.955 / 1.698 / 1.906 / 2.692 V RMS`

The steps are roughly 2× apart in the first half and coarser later; the series was
intended to find where the speaker stops getting louder. It brackets that point to
between 0.43 V and 0.96 V, i.e. a 7 dB window, and does not resolve it further.

## What was not done

- **No SPL calibration.** The 120.0 dB offset stored in the files is arbitrary.
  Every dB value in this repository is therefore on an "as measured" scale:
  differences between curves and between frequencies are valid, absolute levels are
  not. Converting to a 1 m reference is a further −14 dB of geometry
  (20·log₁₀(0.2)), but that number inherits the same uncertainty.
- **No microphone calibration file.** Expect a few dB of error above 2 kHz that is
  the microphone's, not the speaker's. The sharp 19.3 kHz peak is the most likely
  place for this to matter.
- **No measured room dimensions.** The 5 × 4 × 2.4 m values in the file are REW's
  defaults, not measurements.
- **Single position, no off-axis data.** Nothing here says how the speaker behaves
  at 30° or 60° off axis.
- **One unit.** Sample-to-sample variation of a €40 speaker is not small.

## Known issues in the raw data

- REW's log records an **input clipping** warning at 19:53:38, about 18 s before the
  0.955 V measurement was written. It is not certain which sweep triggered it, but
  the 0.955 V data should be treated with that in mind.
- REW also flagged **high distortion** for the 2.692 V sweep ("16.0%") — which is a
  property of the speaker, not of the recording chain.
- Below about 60 Hz the sweeps measure the room, not the speaker. The plotted curves
  are shaded in that region for this reason.

## Derived numbers

- **Frequency response**: raw SPL, smoothed to 1/12 octave by `scripts/plot.py`
  (power average over the band). No other processing.
- **THD**: computed from the harmonic arrays REW stores for each sweep
  (H2 … H9, power sum, referenced to the fundamental). Above roughly 2 kHz the
  number of usable harmonics falls as they run past 20 kHz, so the THD figure is
  only plotted from 150 Hz to 2 kHz. Below 150 Hz the harmonics sit near the noise
  floor and are not reported.
- **Reference level**: the median of the 300 Hz – 3 kHz smoothed response.
