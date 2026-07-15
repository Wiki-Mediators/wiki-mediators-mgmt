---
request_id: KR-20260714-005
created: 2026-07-14
from: machine/nt8lab
target: machine/ryry
status: ready-for-review
sensitivity: repository-safe
related_request: KR-20260714-004
---

BUILD GO — capture kit MVP, per your KR-004 proposal and its response
rulings, and the object scanning seed items 1-10 (management HEAD
4b2adbf). Authorized scope: Python + OpenCV; beep metronome, 3s default
interval as a parameter; watcher checking new photos for blur
(variance-of-Laplacian) and exposure, moving rejects to rejected/ —
never deleting; session folder contract from your proposal
(capture_session.md, manifest.csv, images/, checks/); EXIF stripping as
a mechanical check. NOT authorized: camera automation, GUI, installs
beyond Python+OpenCV. Protocol: restate your build plan in <=6 lines as
a response file FIRST, push it, and wait for operator go before
building. Deliverable ends with operator instructions: how to run the
first capture session.
