from __future__ import annotations
import argparse, hashlib, json, urllib.request
from pathlib import Path
import core

ROOT=Path(__file__).resolve().parent.parent

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def import_render(url,task_id,renderer,route,conditioning,guide_midi_used,voice_authorized):
    music_cert=json.loads((ROOT/"hsi_music.hsicert").read_text(encoding="utf-8"))
    lyrics=json.loads((ROOT/"hsi_music_lyrics.json").read_text(encoding="utf-8"))
    out=ROOT/"hsi_music_song.mp3"
    req=urllib.request.Request(url,headers={"User-Agent":"HSI-Music/1.0"})
    with urllib.request.urlopen(req,timeout=120) as r, open(out,"wb") as f:
        while True:
            b=r.read(1024*1024)
            if not b: break
            f.write(b)
    size=out.stat().st_size
    if size<1024:
        raise RuntimeError("rendered audio is unexpectedly small")
    digest=sha256_file(out)
    receipt={
      "protocol":"HSI-MUSIC-RENDER-RECEIPT/1.0",
      "music_uid":music_cert["music_uid"],
      "lyrics_uid":lyrics["lyrics_uid"],
      "renderer":renderer,
      "task_id":task_id,
      "render_route":route,
      "conditioning":conditioning,
      "guide_midi_used":guide_midi_used,
      "output_kind":"audio",
      "status":"SUCCEEDED",
      "asset_ref":"sha256:"+digest,
      "asset_sha256":digest,
      "asset_bytes":size,
      "local_path":out.name,
      "source_url_stored":False,
      "voice_authorized":voice_authorized
    }
    cert=core.certify_render(music_cert,receipt)
    (ROOT/"hsi_music_render_receipt.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (ROOT/"hsi_music_render.hsicert").write_text(json.dumps(cert,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    if cert.get("closed")!=1:
        raise RuntimeError("render certificate failed closed: "+json.dumps(cert,ensure_ascii=False))
    print(json.dumps({"audio":str(out),"sha256":digest,"bytes":size,"render_closed":1,"render_uid":cert["render_uid"]},ensure_ascii=False))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--task-id",required=True)
    ap.add_argument("--renderer",default="external-singing-renderer")
    ap.add_argument("--route",default="lyrics-conditioned-song")
    ap.add_argument("--conditioning",default="lyrics,style,structure")
    ap.add_argument("--guide-midi-used",action="store_true")
    ap.add_argument("--voice-authorized",action="store_true",default=True)
    a=ap.parse_args()
    import_render(
      a.url,a.task_id,a.renderer,a.route,
      [x for x in a.conditioning.split(",") if x],
      a.guide_midi_used,a.voice_authorized
    )
