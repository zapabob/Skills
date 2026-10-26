---
name: implosion-city-video-pipeline
description: Build and publish narrated implosion-to-city videos.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [Blender, VFX, Irodori, FFmpeg, Publishing]
---

# Implosion-to-City Video Pipeline

Build a deterministic Blender 5.2 VFX sequence that matches an implosion-lens ignition into a large-city blast, then adds Hakua narration and optionally publishes the verified MP4. This does not model real weapon construction or replace physical simulation; it produces an artistic visualization with keyed geometry, and depends on Blender JSON-RPC, FFmpeg, Irodori TTS, and explicit approval for public posting.

## When to Use

- “Connect the implosion-lens ignition to a city explosion.”
- “Make the city larger and add flash, air shockwave, ground wave, and crater.”
- “Render representative frames before the full animation.”
- “Add Hakua narration and publish the finished video to X.”
- A long Blender render must be resumable after timeout or restart.

## Prerequisites

- Windows with Blender 5.2.0 LTS running a socket/JSON server at `127.0.0.1:9876`.
- Blender engine identifier `BLENDER_EEVEE`.
- Project Python available through `uv` and FFmpeg/FFprobe on `PATH`.
- Existing implosion PNG sequence or MP4 with a visible white-hot ignition peak.
- Irodori TTS wrapper: `scripts/windows/invoke-irodori-tts.ps1`.
- For X publishing: configured `lm-twitterer`, valid X cookies, and an approved media directory under `~/.hermes/lm-twitterer/media/`.
- Public posting requires an explicit user request. Never infer permission from completion of the video.

## How to Run

Use `read_file` and `search_files` to inspect the existing implosion source and neighboring Blender scripts before editing. Create or modify the scene builder with `write_file` or `patch`, then invoke each stage through the `terminal` tool:

```bash
uv run python _city_megascale_rebuild.py
uv run python _city_megascale_probe.py
uv run python _city_megascale_render.py
```

Use `vision_analyze` on probe frames before starting the full render. Run bounded TTS and FFmpeg commands through `terminal`; use `lm_twitterer_auth_check`, `lm_twitterer_status`, and `lm_twitterer_post` only after the final MP4 passes verification.

## Quick Reference

```text
Blender JSON-RPC: 127.0.0.1:9876
Scene builder: uv run python _city_megascale_rebuild.py
Probe render: uv run python _city_megascale_probe.py
Resume render: uv run python _city_megascale_render.py
Expected build marker: MEGACITY_SCENE_READY
Expected probe marker: MEGA_PROBE_DONE
Expected render marker: MEGACITY_FULL_RENDER_DONE
Render format: PNG, frame_%04d.png
Final video: H.264, yuv420p, 1280x720, 24fps
Final audio: AAC, 48000Hz
TTS voice: hakua
X media root: ~/.hermes/lm-twitterer/media/
```

## Procedure

1. **Inventory the source.**
   - Locate the implosion `.blend`, PNG sequence, and existing MP4 with `search_files`.
   - Inspect render scripts and frame numbering with `read_file`.
   - Extract candidate cut frames through FFmpeg invoked with `terminal`, then inspect them with `vision_analyze`.
   - Completion: one frame clearly shows the lens geometry and a later frame reaches a white-hot center suitable for a match cut.

2. **Split the workload into three Blender stages.**
   - Builder: clears and constructs the scene, then saves the `.blend`.
   - Probe: renders only representative frames.
   - Renderer: renders one frame at a time and skips existing valid PNGs.
   - Send Blender code as newline-terminated JSON:

   ```python
   payload = json.dumps({"type": "execute_code", "params": {"code": code}}).encode("utf-8") + b"\n"
   with socket.create_connection(("127.0.0.1", 9876), timeout=30) as sock:
       sock.sendall(payload)
   ```

   - Completion: the builder prints `MEGACITY_SCENE_READY` and the saved `.blend` is non-empty.

3. **Construct scale without full-city physics.**
   - Use a detailed near field, segmented mid-field buildings, and simplified distant towers.
   - Use deterministic randomness with a fixed seed.
   - Animate building collapse by shock arrival, for example `arrival = ignition_frame + int(distance / speed)`.
   - Keep smoke as bounded meshes or clusters; never place the camera inside a giant volume.
   - Completion: the start probe shows roads and buildings continuing into the distance without black-screen or single-color failure.

4. **Separate the blast effects.**
   - Flash: keyframe point-light energy and scene exposure for a brief peak, then recover quickly.
   - Fireball: expand, rise, contract, and hide before the crater reveal.
   - Air wave: use thin rings at multiple heights.
   - Ground wave: use differently timed orange/brown dust rings near the terrain.
   - Crater: animate a terrain shape key with a depressed center and raised rim; add a separate lip only for silhouette readability.
   - Completion: a single representative frame can distinguish air wave, ground wave, fireball, and crater.

5. **Keep animated rings at constant world-space thickness.**

   ```python
   def set_ring_key(ring, radius, world_thickness, frame, vertical_ratio=0.25):
       if radius <= 0.01:
           ring.scale = (0.01, 0.01, 0.01)
           ring.data.bevel_depth = 0.001
       else:
           ring.scale = (radius, radius, radius * vertical_ratio)
           ring.data.bevel_depth = world_thickness / radius
       ring.keyframe_insert(data_path="scale", frame=frame)
       ring.data.keyframe_insert(data_path="bevel_depth", frame=frame)
   ```

   - Completion: an expanded wave remains a narrow ring instead of becoming a solid white torus.

6. **Probe before the full render.**
   - Render ignition, initial wave, crater/smoke, and final frames; the proven set was `(52, 78, 118, 180)`.
   - Use `vision_analyze` for each image and explicitly check flash clipping, ring visibility, crater readability, delayed collapse, smoke framing, and camera-volume intersection.
   - Patch the scene and rerun builder plus probe until every required effect is readable.
   - Completion: no probe is accepted solely because Blender exited successfully.

7. **Render resume-safely.**

   ```python
   for frame in range(1, 181):
       path = f"{out}/frame_{frame:04d}.png"
       if os.path.exists(path) and os.path.getsize(path) > 50000:
           continue
       scene.frame_set(frame)
       scene.render.filepath = path
       bpy.ops.render.render(write_still=True)
   print("MEGACITY_FULL_RENDER_DONE")
   ```

   - Invoke long bounded renders with `terminal(background=true, notify_on_complete=true)`.
   - Completion: exactly 180 sequential PNGs exist from `frame_0001.png` through `frame_0180.png`.

8. **Create the match cut.**
   - Encode the implosion through its white-hot peak; the proven lead-in was 3.75 seconds at 24fps.
   - Start the city clip near its exposure peak; the proven city start was frame 40.
   - Time-stretch the finite city image sequence without an output frame cap:

   ```bash
   ffmpeg -y -framerate 24 -start_number 40 -i city_frames_megascale/frame_%04d.png \
     -vf "setpts=1.12*PTS,fps=24,eq=contrast=1.05:saturation=0.92:gamma=0.98" \
     -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -movflags +faststart city_cut.mp4
   ```

   - Do not use `-frames:v` after `setpts`; it caps the stretched output and silently removes the extra duration.
   - Completion: the last implosion frame and first city frame are both bright enough to read as one flash rather than two separate explosions.

9. **Generate Hakua narration to fit the measured edit.**
   - Write the final Japanese text with `write_file`.
   - Invoke Irodori through `terminal`:

   ```bash
   powershell.exe -NoProfile -ExecutionPolicy Bypass \
     -File scripts/windows/invoke-irodori-tts.ps1 \
     -InputPath narration/hakua_megascale_city.txt \
     -OutputPath narration/hakua_megascale_city.wav \
     -Voice hakua -Speed 1.25
   ```

   - Check duration with FFprobe. Prefer regenerating at a moderate Irodori speed over using FFmpeg `atempo` when voice character matters.
   - Leave a small visual tail after the final word; do not use `-shortest` when it would cut narration.
   - Completion: audio duration is shorter than video duration and the final word is intact.

10. **Assemble and inspect the final MP4.**
    - Normalize both video inputs to `1280x720`, `24fps`, `yuv420p`, concatenate in a filter graph, and encode narration as AAC 48kHz.
    - Extract frames around the lens, transition, flash, waves, crater, and final cloud with FFmpeg through `terminal`.
    - Inspect all extracted frames with `vision_analyze`.
    - Decode the entire video to a null sink and run `volumedetect` before delivery.
    - Completion: FFprobe reports H.264/AAC, expected dimensions and rate, full decode exits 0, and representative frames contain every requested effect.

11. **Publish only after explicit approval.**
    - Call `lm_twitterer_auth_check` and `lm_twitterer_status`.
    - Copy the verified MP4 under `~/.hermes/lm-twitterer/media/`, using an ASCII filename without spaces, then compare SHA-256 hashes through `terminal`.
    - Run `lm_twitterer_post` with exact `text`, the filename-only `media_paths`, and `dry_run=true`.
    - Publish once with the identical arguments and `dry_run=false` only when the user explicitly says to post.
    - Verify `posted: true`, retain the returned media ID and URL, then use `web_extract` on the public URL.
    - Completion: the public page shows the exact approved text and attached video; never retry a successful call.

## Pitfalls

- **White city after wave expansion:** curve object scaling also scales `bevel_depth`; compensate inversely to radius.
- **Crater never appears:** fireball remains huge or dust occupies ground zero; contract the fireball and keep central sight lines open.
- **Air and ground waves merge:** separate their height, color, thickness, and timing.
- **Black or flat render:** camera is inside a volume, world lighting is too weak, or exposure never recovers.
- **Long render restarts from zero:** render per frame and skip existing PNGs above a minimum valid size.
- **Stretched city clip remains short:** remove `-frames:v` after `setpts` and verify the output duration.
- **Narration loses its last word:** video is shorter than audio and `-shortest` truncates it; regenerate faster or extend the visual tail.
- **FFprobe cannot open `/c/...`:** native Windows FFmpeg may require `C:\...` even when Git Bash utilities accept MSYS paths.
- **Media rejected as missing:** copy it under the active lm-twitterer media directory and pass a filename or an absolute path inside that root.
- **Duplicate public post:** check activity/history, dry-run first, and never repeat a call that returned `posted: true`.
- **X search unavailable:** a credit failure does not invalidate authenticated lm-twitterer history; report the limitation and use available duplicate evidence.

## Verification

Invoke this single check through the `terminal` tool after assembly:

```bash
uv run python -c "from pathlib import Path; fs=sorted(Path('city_frames_megascale').glob('frame_*.png')); ids=[int(p.stem.rsplit('_',1)[1]) for p in fs]; assert ids==list(range(1,181)); print('FRAMES_OK',len(fs))" && \
ffmpeg -v error -i output_implosion_megacity_hakua.mp4 -f null - && \
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,codec_type,width,height,r_frame_rate,sample_rate -of json output_implosion_megacity_hakua.mp4
```
