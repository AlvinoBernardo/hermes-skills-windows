"""python3 card_preview.py card_xxx 7.2,9.5,11  -> prev_card_xxx_<t>.jpg
Composites the card layer at y=40 over the real cut.mov frame, plus a yellow box where captions sit (y~1350),
so a subagent can check face clearance, crop and readability with its vision tool."""
import sys, subprocess, importlib
from PIL import Image, ImageDraw
mod = importlib.import_module(sys.argv[1])
for t in [float(x) for x in sys.argv[2].split(",")]:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", "cut.mov", "-frames:v", "1", f"_p_{sys.argv[1]}.png"], check=True)
    bg = Image.open(f"_p_{sys.argv[1]}.png").convert("RGBA")
    L = mod.draw(t)
    if L is not None:
        assert L.size[0] == 1080 and L.size[1] <= 480, L.size
        bg.alpha_composite(L, (0, 40))
    ImageDraw.Draw(bg).rectangle((200, 1310, 880, 1390), outline=(255, 255, 0, 255), width=3)
    bg.convert("RGB").resize((540, 960)).save(f"prev_{sys.argv[1]}_{t:05.2f}.jpg")
    print("saved", f"prev_{sys.argv[1]}_{t:05.2f}.jpg")
