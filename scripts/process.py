"""Cover photo processing for the BioLabTek Shopify import.

For each cover in covers.json (a slice of it, so the work can run in parallel):
  originals/<id>.jpg     the photo as downloaded
  cutout/<id>.jpg        background removed onto white, logo watermark at 25% opacity
  watermark/<id>.jpg     original photo with the same watermark (fallback when a cutout looks wrong)
  sheets/                before/after contact sheets for review
"""
import io, json, sys, time, pathlib
import requests
from PIL import Image, ImageDraw, ImageFont
from rembg import remove, new_session

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOGO = Image.open(ROOT / 'assets' / 'logo.png').convert('RGBA')
OPACITY = 0.25        # watermark strength
LOGO_WIDTH = 0.5      # watermark width as a share of the photo width
MAX_SIDE = 2048       # longest side of the output photo

part, parts = (int(x) for x in (sys.argv[1:3] if len(sys.argv) > 2 else (0, 1)))
covers = json.load(open(ROOT / 'covers.json'))
mine = [c for i, c in enumerate(covers) if i % parts == part]
MODEL = 'birefnet-general'   # best general-purpose cutout model in rembg; needs the 16 GB GitHub runner
try:
    session = new_session(MODEL)
except Exception as e:
    print('falling back to birefnet-general-lite:', e)
    session = new_session('birefnet-general-lite')
for d in ('originals', 'cutout', 'watermark'):
    (ROOT / d).mkdir(exist_ok=True)


def watermark(img):
    img = img.convert('RGBA')
    w = int(img.width * LOGO_WIDTH)
    logo = LOGO.resize((w, int(LOGO.height * w / LOGO.width)), Image.LANCZOS)
    alpha = logo.getchannel('A').point(lambda a: int(a * OPACITY))
    logo.putalpha(alpha)
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    layer.paste(logo, ((img.width - logo.width) // 2, (img.height - logo.height) // 2), logo)
    return Image.alpha_composite(img, layer).convert('RGB')


def fit(img):
    if max(img.size) > MAX_SIDE:
        img = img.copy()
        img.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
    return img


for c in mine:
    out_cut = ROOT / 'cutout' / f"{c['id']}.jpg"
    if out_cut.exists():
        continue
    for attempt in range(3):
        try:
            r = requests.get(c['url'], timeout=60)
            r.raise_for_status()
            break
        except Exception as e:
            print('retry', c['id'], e); time.sleep(5)
    else:
        print('FAILED', c['id']); continue
    src = fit(Image.open(io.BytesIO(r.content)).convert('RGB'))
    src.save(ROOT / 'originals' / f"{c['id']}.jpg", quality=92)
    cut = remove(src, session=session)                      # RGBA with transparent background
    white = Image.new('RGBA', cut.size, (255, 255, 255, 255))
    white.alpha_composite(cut)
    watermark(white).save(out_cut, quality=92)
    watermark(src).save(ROOT / 'watermark' / f"{c['id']}.jpg", quality=92)
    print('done', c['id'])
