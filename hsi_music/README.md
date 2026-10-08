# HSI Music v1

HSI Music integrates the existing deterministic `solution_0_music_2kb.sh` generator with a professional, auditable music object:

```text
Prompt
  -> automatic original lyrics
  -> deterministic MIDI / arrangement guide
  -> singing-vocal render request
  -> mix/master specification
  -> HSI-MUSIC/1.0 certificate
```

The existing 2 KB generator remains unchanged.

## Outputs

Running `python3 hsi_music/build.py "your prompt"` produces:

- `hsi_music.mid`
- `hsi_music_lyrics.json`
- `hsi_music_vocal_request.json`
- `hsi_music_mix_spec.json`
- `hsi_music_object.json`
- `hsi_music.hsicert`

The lyric generator is deterministic and marks its output as `generated-original`.

## Singing vocals

HSI Music now defines a real singing stage through `HSI-MUSIC-VOCAL/1.0`. The request binds lyrics, guide MIDI, voice requirements, timing, sample rate, and authorization constraints. A connected singing synthesizer can consume that request and return `hsi_music_vocal.wav`.

The repository itself does not impersonate or clone a real person's voice. The certificate fails closed unless the request preserves the `no_unauthorized_voice_clone` boundary.

## Pleiadian Blue / intent

The music certificate carries the shared Blue dimensions:

- Agency
- Non-coercion
- Truthfulness
- Care
- Dialogue/Repair
- Continuity

This is symbolic normative protocol language, not an astronomical or physical claim.

## Verification

```sh
cd hsi_music
python3 -m unittest -v test_core.py
cd ..
python3 hsi_music/build.py "昴宿星團的藍"
```

## Completed audio binding

When a connected singing renderer returns a finished audio asset, HSI Music binds it with `HSI-MUSIC-RENDER/1.0`.

A render closes only when the source `HSI-MUSIC/1.0` certificate is already closed, the receipt points to the same `music_uid`, the renderer task succeeded, the output is audio, the lyrics are bound, the voice is authorized, and an asset reference exists.

The certificate stores only an `asset_uid` digest. A private or signed media URL does not need to be committed to Git.

This separates:

```text
composition certificate
        +
actual singing render receipt
        =
auditable finished-song provenance
```
