# Contributing

Adding a speaker is the point of this repository, so contributions are welcome.
The bar is documentation, not perfection — a measurement with honest caveats is
more useful than a pretty one with none.

## What a new measurement needs

1. A folder `measurements/<brand>-<model>/` containing:
   - `raw/*.mdat` — the REW file(s), unedited
   - `data/` — export with `python scripts/export_data.py` (adjust the paths) or
     by hand from REW: *File → Export → Export measurement as text*
   - `img/` — figures produced by `scripts/plot.py`, plus a photo of the setup
   - `README.md` — copy `measurements/jbl-go-2/README.md` and fill it in
2. Conditions written down, even when they are imperfect: room, distance, angle,
   microphone, interface, input type, volume setting, temperature/humidity.
3. The same caveats as everybody else: say whether the microphone and the SPL scale
   were calibrated. "Not calibrated" is a fine answer.

## Conventions

- At least two input levels if you are claiming anything about output limits.
- Keep the raw `.mdat`. It is the only artefact that cannot be regenerated.
- Do not smooth data before exporting it; smoothing belongs in the plotting step.
- One folder per speaker; keep files out of the repository root.

## Adding to the table

The table in `README.md` and `README.zh-CN.md` is updated by hand — add one row per
device with the date, the input levels used and a link to the folder.
