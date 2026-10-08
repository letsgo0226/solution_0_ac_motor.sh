from __future__ import annotations
import json, os, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
url=os.environ.get("HSI_MUSIC_RENDER_URL","").strip()
if not url:
    raise SystemExit("HSI_MUSIC_RENDER_URL is not set")

obj=json.loads((ROOT/"hsi_music_object.json").read_text(encoding="utf-8"))
payload={
  "protocol":"HSI-MUSIC-RENDER-REQUEST/1.0",
  "music_object":obj,
  "requirements":{
    "output_kind":"audio",
    "singing":True,
    "voice_authorized":True,
    "no_unauthorized_voice_clone":True,
    "return_url":True
  }
}
headers={"Content-Type":"application/json","User-Agent":"HSI-Music/1.0"}
token=os.environ.get("HSI_MUSIC_RENDER_TOKEN","").strip()
if token:
    headers["Authorization"]="Bearer "+token
req=urllib.request.Request(url,data=json.dumps(payload,ensure_ascii=False).encode(),headers=headers,method="POST")
with urllib.request.urlopen(req,timeout=int(os.environ.get("HSI_MUSIC_RENDER_TIMEOUT","600"))) as r:
    ans=json.loads(r.read().decode())
(ROOT/"hsi_music_remote_response.json").write_text(json.dumps(ans,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if str(ans.get("status","")).upper()!="SUCCEEDED" or not ans.get("url"):
    raise SystemExit("renderer did not return synchronous SUCCEEDED + url; response saved to hsi_music_remote_response.json")
print(json.dumps(ans,ensure_ascii=False))
