import unittest
import core

class HSIMusicTests(unittest.TestCase):
    def test_auto_lyrics_deterministic_and_original(self):
        a=core.auto_lyrics("昴宿星團的藍","zh-TW")
        b=core.auto_lyrics("昴宿星團的藍","zh-TW")
        self.assertEqual(a["lyrics_uid"],b["lyrics_uid"])
        self.assertEqual(a["origin"],"generated-original")
        self.assertIn("chorus",a["sections"])

    def test_full_music_object_closes(self):
        l=core.auto_lyrics("和平與星光")
        v=core.make_vocal_request(l,"song.mid")
        o={"prompt":"和平與星光","lyrics":l,"midi":{"path":"song.mid"},"vocal_request":v,
           "mix_spec":{"sample_rate":44100},"intent":{k:True for k in core.BLUE_DIMENSIONS}}
        c=core.certify(o)
        self.assertEqual(c["closed"],1)

    def test_blue_violation_fails_closed(self):
        l=core.auto_lyrics("test")
        v=core.make_vocal_request(l,"song.mid")
        intent={k:True for k in core.BLUE_DIMENSIONS}
        intent["NON_COERCION"]=False
        c=core.certify({"prompt":"test","lyrics":l,"midi":{"path":"song.mid"},"vocal_request":v,
                        "mix_spec":{},"intent":intent})
        self.assertEqual(c["closed"],0)

    def test_voice_clone_boundary_required(self):
        l=core.auto_lyrics("test")
        v=core.make_vocal_request(l,"song.mid")
        v["constraints"]["no_unauthorized_voice_clone"]=False
        c=core.certify({"prompt":"test","lyrics":l,"midi":{"path":"song.mid"},"vocal_request":v,
                        "mix_spec":{},"intent":{k:True for k in core.BLUE_DIMENSIONS}})
        self.assertEqual(c["closed"],0)

if __name__=="__main__":
    unittest.main()
