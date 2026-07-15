import csv
import io
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest import mock

import cv2
import numpy as np
from PIL import Image

import capture_kit as kit


def sharp_image(value=128):
    image = np.full((240, 320, 3), value, dtype=np.uint8)
    for y in range(0, 240, 16):
        for x in range(0, 320, 16):
            tile = 220 if ((x // 16) + (y // 16)) % 2 else 40
            cv2.rectangle(image, (x, y), (x + 15, y + 15), (tile,) * 3, -1)
    return image


def jpeg_bytes(image):
    ok, encoded = cv2.imencode(".jpg", image)
    assert ok
    return encoded.tobytes()


class CaptureKitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        args = Namespace(
            sessions_root=str(self.root), session_id="test_session", object="test cube",
            purpose="reconstruction-feasibility", camera_type="webcam", lighting="diffuse",
            scale_reference="dice", known_dimension="ruler +/-0.5 mm", notes="test",
            interval=3.0, blur_min=20.0, mean_min=25.0, mean_max=230.0,
            clipped_fraction_max=0.9,
        )
        kit.init_session(args)
        self.session = self.root / "test_session"
        self.thresholds = kit.Thresholds(20.0, 25.0, 230.0, 0.9)

    def tearDown(self):
        self.temp.cleanup()

    def rows(self):
        with (self.session / "manifest.csv").open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    def test_accept_strips_exif_and_preserves_original(self):
        image = Image.fromarray(cv2.cvtColor(sharp_image(), cv2.COLOR_BGR2RGB))
        exif = Image.Exif()
        exif[0x010E] = "capture test"
        source = self.session / "incoming" / "exif.jpg"
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", exif=exif)
        source.write_bytes(buffer.getvalue())
        row = kit.process_file(self.session, source, self.thresholds, "webcam")
        self.assertEqual(row["status"], "accepted")
        self.assertEqual(row["exif_present_source"], "true")
        self.assertEqual(row["exif_removed"], "true")
        self.assertTrue((self.session / "originals" / "exif.jpg").exists())
        self.assertFalse(kit.has_exif((self.session / "images" / "F0001.jpg").read_bytes()))

    def test_blur_and_exposure_are_rejected_without_deletion(self):
        blurred = np.full((240, 320, 3), 128, dtype=np.uint8)
        source = self.session / "incoming" / "blurred.jpg"
        source.write_bytes(jpeg_bytes(blurred))
        row = kit.process_file(self.session, source, self.thresholds, "webcam")
        self.assertEqual(row["status"], "rejected")
        self.assertIn("blur", row["reason"])
        self.assertTrue((self.session / "rejected" / "blurred.jpg").exists())

        dark = self.session / "incoming" / "dark.jpg"
        dark.write_bytes(jpeg_bytes(np.zeros((240, 320, 3), dtype=np.uint8)))
        row = kit.process_file(self.session, dark, self.thresholds, "webcam")
        self.assertEqual(row["status"], "rejected")
        self.assertIn("underexposed", row["reason"])
        self.assertTrue((self.session / "rejected" / "dark.jpg").exists())

    def test_duplicate_is_rejected(self):
        data = jpeg_bytes(sharp_image())
        first = self.session / "incoming" / "one.jpg"
        first.write_bytes(data)
        kit.process_file(self.session, first, self.thresholds, "webcam")
        duplicate = self.session / "incoming" / "two.jpg"
        duplicate.write_bytes(data)
        row = kit.process_file(self.session, duplicate, self.thresholds, "webcam")
        self.assertEqual(row["reason"], "duplicate")
        self.assertTrue((self.session / "rejected" / "two.jpg").exists())

    def test_manifest_and_receipts_are_deterministic(self):
        source = self.session / "incoming" / "frame.jpg"
        source.write_bytes(jpeg_bytes(sharp_image()))
        kit.process_file(self.session, source, self.thresholds, "webcam")
        rows = self.rows()
        self.assertEqual(rows[0]["frame_id"], "F0001")
        self.assertEqual(rows[0]["accepted_name"], "F0001.jpg")
        self.assertTrue((self.session / "checks" / "F0001.json").exists())

    def test_camera_roll_copy_requires_stable_size_and_ignores_baseline(self):
        camera_roll = self.root / "Camera Roll"
        camera_roll.mkdir()
        old = camera_roll / "old.jpg"
        old.write_bytes(jpeg_bytes(sharp_image()))
        baseline = {old}
        observed = {}
        new = camera_roll / "new.jpg"
        new.write_bytes(jpeg_bytes(sharp_image()))
        incoming = self.session / "incoming"
        self.assertEqual(kit.copy_stable_new_files(camera_roll, incoming, baseline, observed), 0)
        self.assertEqual(kit.copy_stable_new_files(camera_roll, incoming, baseline, observed), 1)
        self.assertFalse((incoming / "old.jpg").exists())
        self.assertTrue((incoming / "new.jpg").exists())

    def test_direct_capture_exports_timed_snapshots(self):
        class FakeCamera:
            def __init__(self):
                self.count = 0

            def read(self):
                self.count += 1
                return True, np.roll(sharp_image(), self.count, axis=1)

            def release(self):
                pass

        args = Namespace(
            session=str(self.session), camera_type="webcam", camera_index=0,
            width=1920, height=1080, interval=0.001, duration=60.0, shots=2,
            prep_seconds=0.0, immediate=True, open_folder=False, blur_min=20.0, mean_min=25.0,
            mean_max=230.0, clipped_fraction_max=0.9,
        )
        with mock.patch.object(kit, "open_camera", return_value=FakeCamera()), mock.patch.object(kit, "beep"):
            self.assertEqual(kit.capture(args), 0)
        rows = self.rows()
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row["status"] == "accepted" for row in rows))
        self.assertEqual(len(list((self.session / "images").glob("*.jpg"))), 2)

    def test_startup_signal_has_alert_delay_and_start_tone(self):
        with mock.patch.object(kit, "beep") as beeper, mock.patch.object(kit.time, "sleep") as sleeper:
            kit.startup_signal(10.0)
        self.assertEqual(beeper.call_args_list, [mock.call(660, 100), mock.call(660, 100), mock.call(1200, 450)])
        self.assertEqual(sleeper.call_args_list, [mock.call(0.12), mock.call(10.0)])


if __name__ == "__main__":
    unittest.main()
