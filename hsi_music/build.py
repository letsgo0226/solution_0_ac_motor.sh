from __future__ import annotations
import argparse, json, shutil, subprocess
from pathlib import Path
import core

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

def run(prompt,style,language):
    legacy=ROOT/"solution_0_music_2kb.sh"
    subprocess.run(["sh",str(legacy),prompt],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
    src=ROOT/"solution_0_music_2kb.mid"
    midi=ROOT/"hsi_music.mid"
    shutil.copyfile(src,midi)

    lyrics=core.auto_lyrics(prompt,language=language)
    vocal=core.make_vocal_request(lyrics,midi)
    mix={
      "sample_rate":44100,
      "channels":2,
      "target_lufs":-14,
      "true_peak_db":-1.0,
      "stems":["instrumental","lead_vocal"],
      "notes":"Professional target specification; rendering engine may refine arrangement and mastering."
    }
    intent={k:True for k in core.BLUE_DIMENSIONS}
    obj={
      "prompt":prompt,
      "style":style,
      "language":language,
      "lyrics":lyrics,
      "midi":{"path":str(midi.name),"source":"solution_0_music_2kb.sh","deterministic":True},
      "vocal_request":vocal,
      "mix_spec":mix,
      "intent":intent
    }
    cert=core.certify(obj)
    (ROOT/"hsi_music_lyrics.json").write_text(json.dumps(lyrics,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (ROOT/"hsi_music_vocal_request.json").write_text(json.dumps(vocal,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (ROOT/"hsi_music_mix_spec.json").write_text(json.dumps(mix,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (ROOT/"hsi_music_object.json").write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (ROOT/"hsi_music.hsicert").write_text(json.dumps(cert,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(cert,ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("prompt",nargs="?",default="昴宿星團的藍")
    ap.add_argument("--style",default="cinematic-pop")
    ap.add_argument("--language",default="zh-TW")
    a=ap.parse_args()
    run(a.prompt,a.style,a.language)
