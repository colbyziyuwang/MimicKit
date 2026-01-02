import subprocess
import os

FPS = 30
FRAME_DIR = "frames"
OUTPUT = "video.mp4"

assert os.path.isdir(FRAME_DIR), f"{FRAME_DIR} not found"

cmd = [
    "ffmpeg",
    "-y",
    "-framerate", str(FPS),
    "-i", os.path.join(FRAME_DIR, "color_%06d.png"),
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-crf", "18",
    OUTPUT,
]

print("Running:", " ".join(cmd))
subprocess.run(cmd, check=True)
print(f"Saved video to {OUTPUT}")
