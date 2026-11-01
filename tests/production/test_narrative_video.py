"""EN06/EN07 — falas sem números literais fora de tokens, perfis 13/14 segmentos, orçamento de tempo e vídeo.

O caminho de sucesso do vídeo usa clipes sintéticos numa pasta temporária; nunca gera vídeo do grupo.
"""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from production import consumer, deck_model, narrative, video
from production.common import REPO


class Narrative(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory(prefix="prod_nar_")
        b = consumer.load(consumer.resolve("latest"))
        cls.res = narrative.build(b, deck_model.build(b), Path(cls._tmp.name))
        cls.out = Path(cls._tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_no_literal_numbers(self):
        self.assertEqual(narrative.lint_literals(), [])

    def test_segment_profiles(self):
        self.assertEqual(len(narrative.segments("pptx9")), 13)
        self.assertEqual(len(narrative.segments("html10")), 14)
        self.assertTrue(all(s["path"].startswith("data/raw/gravacao/html10/") for s in narrative.segments("html10")))

    def test_speech_budget(self):
        for prof, c in self.res["counts"].items():
            self.assertLessEqual(c["planned_seconds"], 600, prof)
            self.assertLessEqual(c["estimated_seconds_at_140wpm"], c["planned_seconds"], prof)

    def test_outputs_per_profile(self):
        for name in ("script_apresentacao.md", "script_apresentacao_html10.md", "perguntas_banca.md", "guia_gravacao.md", "roteiro_narrativo.md"):
            self.assertTrue((self.out / name).is_file(), name)
        self.assertEqual(len(list((self.out / "teleprompter").glob("*.md"))), 4)


class Video(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="prod_vid_")
        self.tmp = Path(self._tmp.name)
        from PIL import Image
        self.slide = self.tmp / "slide.png"
        Image.new("RGB", (1920, 1080), "white").save(self.slide)

    def tearDown(self):
        self._tmp.cleanup()

    def test_no_clips_no_video(self):
        for cfg in ("config/video_segments.json", "config/video_segments_html10.json"):
            rep = video.readiness(REPO / cfg)
            if rep["missing"]:
                self.assertEqual(rep["status"], "awaiting_real_clips")
                out = video.assemble(REPO / cfg, {}, self.tmp / "out")
                self.assertFalse(out["video_created"])

    def test_synthetic_success_path(self):
        clips = []
        for k in range(2):
            c = self.tmp / f"clip{k}.mp4"
            video._ffmpeg(["-y", "-f", "lavfi", "-i", "color=c=gray:s=180x320:r=30", "-f", "lavfi", "-i", "sine=frequency=330:sample_rate=48000",
                           "-t", "0.5", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", c])
            clips.append(c)
        prof = self.tmp / "profile.json"
        prof.write_text(json.dumps({"profile": "fixture", "segments": [{"block": f"F{k}", "speaker": "x", "slide": 1, "path": str(c)}
                                                                       for k, c in enumerate(clips)]}), encoding="utf-8")
        rep = video.assemble(prof, {1: self.slide}, self.tmp / "out")
        self.assertTrue(rep["video_created"])
        self.assertEqual(rep["status"], "draft_video_awaiting_full_human_review")
        self.assertFalse(rep["submitted"])
        self.assertLess(rep["measured_seconds"], 2)

    def test_camera_area_matches_recording_mode(self):
        css = (REPO / "presentation_web/deck.css").read_text(encoding="utf-8")
        x, y, w, h = video.CAMERA
        self.assertIn(f"left: {x}px; top: {y}px; width: {w}px; height: {h}px", css)


if __name__ == "__main__":
    unittest.main()
