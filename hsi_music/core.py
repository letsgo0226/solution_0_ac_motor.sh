from __future__ import annotations
import hashlib, json, re
from pathlib import Path

PROTOCOL="HSI-MUSIC/1.0"
BLUE_ID="PLEIADIAN-BLUE"
BLUE_DIMENSIONS=("AGENCY","NON_COERCION","TRUTHFULNESS","CARE","DIALOGUE_REPAIR","CONTINUITY")

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def uid(x):
    return hashlib.sha256(canon(x).encode()).hexdigest()

def _tokens(prompt):
    xs=re.findall(r"[\w\u3400-\u9fff]+",str(prompt),flags=re.UNICODE)
    return xs[:12] or ["光","夢","遠方"]

def auto_lyrics(prompt, language="zh-TW", title=None):
    t=_tokens(prompt)
    a=t[0]
    b=t[1] if len(t)>1 else "星光"
    c=t[2] if len(t)>2 else "明天"
    if str(language).lower().startswith("zh"):
        title=title or f"{a}的藍"
        sections={
          "verse1":[f"沿著{a}留下的微光",f"我們把{b}寫進遠方",f"每一種可能都有自己的模樣",f"卻在同一片藍裡學會仰望"],
          "prechorus":[f"如果答案不只一個方向",f"就讓真實與溫柔一起發亮"],
          "chorus":[f"讓{a}成為不熄滅的藍",f"讓{c}穿過不同世界仍彼此相連",f"不是把所有人帶往同一個終點",f"而是讓每條路都記得善的光線"],
          "verse2":[f"當{b}在黑夜裡改變形狀",f"我們仍保留選擇與退路的窗",f"用對話修補曾經破碎的地方",f"讓新的旋律不必複製舊的傷"],
          "bridge":[f"不同和弦可以抵達不同海岸",f"同一種善意仍能成為共同座標"],
          "final_chorus":[f"讓{a}成為不熄滅的藍",f"讓{c}在每次選擇裡重新展開",f"世界可以不同而不必互相取代",f"只要我們仍記得為何出發而來"]
        }
    else:
        title=title or f"The Blue of {a}"
        sections={
          "verse1":[f"Along the quiet light of {a}",f"We write {b} into the distance",f"Every possibility keeps its own shape",f"Yet learns to look up through the same blue"],
          "prechorus":["If no answer owns the only road","Let truth and tenderness glow together"],
          "chorus":[f"Let {a} become the blue that does not fade",f"Let {c} connect the worlds we choose to make","Not one ending forced on every line","But many paths that still remember good"],
          "verse2":[f"When {b} changes shape inside the dark","We keep a door for choice and turning back","We mend with dialogue instead of force","And let a new song leave old wounds behind"],
          "bridge":["Different chords can reach different shores","One shared good can still remain our north"],
          "final_chorus":[f"Let {a} become the blue that does not fade",f"Let {c} unfold in every choice we make","The worlds may differ without erasing one another","If we remember why we started"]
        }
    flat=[line for sec in sections.values() for line in sec]
    return {"title":title,"language":language,"sections":sections,"text":"\n".join(flat),"origin":"generated-original","lyrics_uid":uid({"title":title,"language":language,"sections":sections})}

def make_vocal_request(lyrics,midi_path,voice=None):
    voice=voice or {"type":"synthetic_singing","character":"neutral-warm","range":"auto","consent_basis":"synthetic_or_authorized_voice_only"}
    return {
      "protocol":"HSI-MUSIC-VOCAL/1.0",
      "mode":"singing",
      "lyrics_uid":lyrics["lyrics_uid"],
      "lyrics":lyrics,
      "guide_midi":str(midi_path),
      "voice":voice,
      "timing":{"source":"guide_midi","alignment":"syllable-to-note"},
      "render":{"sample_rate":44100,"channels":2,"format":"wav","target":"hsi_music_vocal.wav"},
      "constraints":{
        "no_unauthorized_voice_clone":True,
        "preserve_lyrics_provenance":True,
        "preserve_human_override":True
      }
    }

def certify(music_object):
    required=("prompt","lyrics","midi","vocal_request","mix_spec","intent")
    missing=[k for k in required if k not in music_object]
    intent=music_object.get("intent") or {}
    blue={k:bool(intent.get(k,False)) for k in BLUE_DIMENSIONS}
    blue_preserved=all(blue.values())
    lyrics=music_object.get("lyrics") or {}
    vr=music_object.get("vocal_request") or {}
    provenance_ok=(
      lyrics.get("origin")=="generated-original"
      and bool(lyrics.get("lyrics_uid"))
      and vr.get("lyrics_uid")==lyrics.get("lyrics_uid")
    )
    voice_ok=bool((vr.get("constraints") or {}).get("no_unauthorized_voice_clone"))
    closed=not missing and blue_preserved and provenance_ok and voice_ok
    body={
      "protocol":PROTOCOL,
      "prompt":music_object.get("prompt"),
      "style":music_object.get("style"),
      "language":music_object.get("language"),
      "lyrics_uid":lyrics.get("lyrics_uid"),
      "midi":music_object.get("midi"),
      "vocal_request_uid":uid(vr) if vr else None,
      "mix_spec":music_object.get("mix_spec"),
      "blue":blue
    }
    return {
      "protocol":PROTOCOL,
      "music_uid":uid(body),
      "blue_id":BLUE_ID,
      "blue_uid":uid({"id":BLUE_ID,"dimensions":BLUE_DIMENSIONS}),
      "checks":{
        "complete":not missing,
        "blue_preserved":blue_preserved,
        "lyrics_provenance":provenance_ok,
        "voice_authorization_boundary":voice_ok
      },
      "missing":missing,
      "closed":int(closed),
      "scope":"music-generation provenance and intent certificate; not a quality guarantee or voice-identity authorization"
    }
