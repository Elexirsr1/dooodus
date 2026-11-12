"""Encode the rendered PNG sequence into the delivery MP4 and print its stream facts.

H.264 High, 1920x1080, 120 fps constant, 1800 frames = 15.000 s, BT.709 limited range, yuv420p.
Usage: python3 scripts/encode_video.py [--frames renders/frames] [--out output/gothic_heart_trophy_1080p120.mp4]
"""
import argparse
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--frames", default=os.path.join(ROOT, "renders", "frames"))
    p.add_argument("--out", default=os.path.join(ROOT, "output", "gothic_heart_trophy_1080p120.mp4"))
    p.add_argument("--crf", type=int, default=15)
    a = p.parse_args()
    frames = sorted(glob.glob(os.path.join(a.frames, "frame_*.png")))
    expected = [os.path.join(a.frames, f"frame_{i:04d}.png") for i in range(1, 1801)]
    missing = [f for f in expected if not os.path.exists(f)]
    if missing or len(frames) != 1800:
        print(f"expected 1800 frames, found {len(frames)}; missing e.g. {missing[:3]}", file=sys.stderr)
        return 1
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "warning", "-y",
        "-framerate", "120", "-start_number", "1", "-i", os.path.join(a.frames, "frame_%04d.png"),
        # full-range sRGB PNG -> limited-range BT.709 4:2:0, tagged so players decode colours correctly
        "-vf", "scale=in_range=pc:out_range=tv:out_color_matrix=bt709:flags=lanczos+accurate_rnd+full_chroma_int,"
               "format=yuv420p",
        "-c:v", "libx264", "-preset", "slow", "-tune", "film", "-crf", str(a.crf),
        "-profile:v", "high", "-level:v", "5.2", "-x264-params", "keyint=240:min-keyint=24",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
        "-r", "120", "-frames:v", "1800", "-an", "-movflags", "+faststart", a.out,
    ]
    subprocess.run(cmd, check=True)
    probe = subprocess.run([
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
        "-show_entries", "stream=codec_name,profile,width,height,r_frame_rate,avg_frame_rate,nb_read_frames,"
                         "pix_fmt,color_space,duration",
        "-show_entries", "format=duration,size,bit_rate", "-of", "json", a.out], check=True, capture_output=True,
        text=True)
    info = json.loads(probe.stdout)
    print(json.dumps(info, indent=2))
    s, f = info["streams"][0], info["format"]
    ok = (s["codec_name"] == "h264" and (s["width"], s["height"]) == (1920, 1080) and s["r_frame_rate"] == "120/1"
          and int(s["nb_read_frames"]) == 1800 and abs(float(f["duration"]) - 15.0) < 0.01)
    print("VIDEO CHECK", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
