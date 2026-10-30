"""Contact sheets for review: each tile shows the original (left) and the cutout (right), numbered by Machinio ID."""
import json, pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
covers = json.load(open(ROOT / 'covers.json'))
out = ROOT / 'sheets'
out.mkdir(exist_ok=True)
TW, TH, COLS, ROWS = 300, 225, 3, 6          # 18 pairs per sheet
font = ImageFont.load_default(size=22)
done = [c for c in covers if (ROOT / 'cutout' / f"{c['id']}.jpg").exists()]
for s in range(0, len(done), COLS * ROWS):
    batch = done[s:s + COLS * ROWS]
    sheet = Image.new('RGB', (COLS * (TW * 2 + 20), ROWS * (TH + 10)), (120, 120, 120))
    for k, c in enumerate(batch):
        x, y = (k % COLS) * (TW * 2 + 20), (k // COLS) * (TH + 10)
        for j, folder in enumerate(('originals', 'cutout')):
            im = Image.open(ROOT / folder / f"{c['id']}.jpg")
            im.thumbnail((TW, TH))
            tile = Image.new('RGB', (TW, TH), (255, 255, 255))
            tile.paste(im, ((TW - im.width) // 2, (TH - im.height) // 2))
            sheet.paste(tile, (x + j * (TW + 4), y))
        d = ImageDraw.Draw(sheet)
        d.rectangle([x, y, x + 110, y + 26], fill=(0, 0, 0))
        d.text((x + 4, y + 2), c['id'], fill=(255, 255, 255), font=font)
    sheet.save(out / f"sheet-{s // (COLS * ROWS) + 1:02d}.jpg", quality=80)
print('sheets', (len(done) + COLS * ROWS - 1) // (COLS * ROWS))
