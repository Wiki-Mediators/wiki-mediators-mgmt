# Notebook Object-Capture Kit

Notebook-side still-photo ingestion for the 3D-scanning feasibility trial.
The Windows Camera app remains the camera controller. This tool creates the
session record first, paces manual captures with a beep, sanitizes accepted
copies, performs mechanical quality checks, and never deletes rejected inputs.

## First session

Keep the camera shutter closed while preparing the object. Use diffuse, even
light; attach dice or place a ruler/grid in frame as a coarse scale witness.
The first trial is reconstruction-feasibility, not dimensional validation.

From PowerShell (the process-local execution-policy flag is needed on this
notebook):

```powershell
cd .\tools\notebook_capture_kit
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\capture_kit.ps1 init --object "test object" --lighting "diffuse lamp through cloth" --scale-reference "dice plus ruler, +/-0.5 mm" --notes "manual stop-spin-shoot"
```

The command prints the new session path. Start the watcher, which ignores old
Camera Roll content and ingests only photos created after it starts:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\capture_kit.ps1 watch "<printed-session-path>" --interval 3
```

Then open the physical shutter and Windows Camera app. The default watched
source is `%USERPROFILE%\Pictures\Camera Roll`. If Camera saves elsewhere,
pass `--source-dir "<folder>"`. To watch only the session's `incoming\` folder,
pass `--source-dir ""`.

At each beep: move the object, let it settle, and take one still. Target about
60 accepted photographs across three passes: level, 30–45 degrees above, and
a regrip/opposite orientation pass. `images\` receives EXIF-free accepted
JPEGs. Originals are preserved in `originals\`; failed and duplicate inputs
are moved to `rejected\`. Per-frame receipts live in `checks\`, and
`manifest.csv` records every decision.

Press `Ctrl+C` to stop. Close the camera shutter. Before transferring, review
the accepted count and rejection reasons in `manifest.csv`. Transfer the whole
session folder over the approved Wi-Fi/share path to the desktop incoming root:

```text
_DIMENSIONS/3d-printing/artifacts/incoming/<session_id>/
```

Do not commit the session folder or its images. Absolute paths, share details,
host/IP information, and source EXIF stay out of repository-bound records.

## One-shot ingest

To process photos already copied into `incoming\`:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\capture_kit.ps1 ingest "<session-path>"
```

You can also supply source files; the command copies them into `incoming\`
before processing:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\capture_kit.ps1 ingest "<session-path>" "C:\path\photo1.jpg" "C:\path\photo2.jpg"
```

## Thresholds

Defaults are deliberately explicit and recorded in `checks\session_config.json`:

- variance-of-Laplacian blur minimum: `85`
- mean luma range: `35`–`225`
- maximum near-black or near-white fraction: `0.85`

They are warnings implemented as accept/reject gates for trial one, not
universal camera truths. Override with `--blur-min`, `--mean-min`,
`--mean-max`, and `--clipped-fraction-max`, then judge thresholds using the
trial's keep rate and reconstruction outcome.

## Tests

```powershell
$env:PYTHONPATH = ".\vendor;."
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m unittest -v test_capture_kit.py
```
