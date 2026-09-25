"""Deterministic showcase artwork; never writes installed TORCS assets."""
from pathlib import Path
import hashlib
import json
import re
import shutil
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
TRACK = Path('/usr/local/torcs/share/games/torcs/tracks/road/corkscrew')
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
TAGLINE = 'HUMAN LED AI ACCELERATED RACE PROVEN'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def artwork(name, title, subtitle, size):
    w, h = size
    im = Image.new('RGB', size, '#07111d')
    draw = ImageDraw.Draw(im)
    draw.rectangle((0, 0, w, max(3, h // 28)), fill='#32e6c4')
    items = []
    for text, center, limit in [(title, h * .42, h * .55), (subtitle, h * .82, h * .18)]:
        fs = int(limit)
        while True:
            font = ImageFont.truetype(FONT, fs)
            box = draw.textbbox((0, 0), text, font=font)
            if box[2] <= w * .93: break
            fs -= 1
        x = (w - box[2]) / 2
        y = center - (box[3] - box[1]) / 2 - box[1]
        draw.text((x, y), text, font=font, fill='white')
        items.append(f'<text x="{w/2}" y="{center}" text-anchor="middle" dominant-baseline="central" font-family="DejaVu Sans" font-weight="bold" font-size="{fs}" fill="white">{text}</text>')
    im.save(ROOT/'artwork'/f'{name}.png')
    im.save(ROOT/'artwork'/f'{name}.rgb', format='SGI')
    (ROOT/'artwork'/f'{name}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="#07111d"/><rect width="100%" height="{max(3,h//28)}" fill="#32e6c4"/>'+''.join(items)+'</svg>')
    return im

def main():
    for d in ['originals', 'modified', 'artwork', 'showcase-track']:
        (ROOT/d).mkdir(exist_ok=True)
    # Inspect model references; these two complete images depict signage, not road surfaces.
    model = (TRACK/'corkscrew.acc').read_text()
    definitions = [('hero','ATLAS',TAGLINE,'corkscrew_arbor.png'),
                   ('engineering','ATLAS','SENSE PLAN CONTROL PROVE','kilo.png')]
    assets = []
    for name,title,subtitle,target in definitions:
        assert f'texture "{target}"' in model
        source = TRACK/target
        shutil.copyfile(source, ROOT/'originals'/target)
        size = Image.open(source).size
        im = artwork(name,title,subtitle,size)
        im.save(ROOT/'modified'/target)
        assets.append(dict(name=name,target=str(source),relative_target=target,
            original_sha256=sha(source),modified_sha256=sha(ROOT/'modified'/target),
            dimensions=list(size),rgb_sha256=sha(ROOT/'artwork'/f'{name}.rgb'),
            model_reference_count=model.count(f'texture "{target}"')))
    artwork('evidence','84.388','QUALIFIED CORKSCREW',(1024,256))
    artwork('method','ATLAS','MEASURE FALSIFY IMPROVE',(1024,256))
    artwork('opening','ATLAS',TAGLINE,(2048,512))
    # A separate full track copy makes restore trivial and cannot affect the installed race.
    baseline = {}
    for source in TRACK.iterdir():
        if source.is_file():
            baseline[source.name] = sha(source)
            shutil.copyfile(source,ROOT/'showcase-track'/source.name)
    for a in assets:shutil.copyfile(ROOT/'modified'/a['relative_target'],ROOT/'showcase-track'/a['relative_target'])
    differences = [n for n,h in baseline.items() if sha(ROOT/'showcase-track'/n) != h]
    assert sorted(differences)==sorted(a['relative_target'] for a in assets)
    report = dict(official_video='Stock textures only',showcase='Offline prepared copy; not installed or race-tested',
        installed_files_changed=[],copy_files_changed=differences,assets=assets,
        original_track_hashes=baseline,primary_tagline=TAGLINE,
        format_note='Corkscrew model binds PNG filenames. Modified PNGs preserve those bindings; SGI RGB exports are included but must not be renamed over PNGs or require model edits.',
        rights_note='Original track credited to Gabor Kmetyko and Andrew Sumner, GPL v2, with TORCS integration by Bernhard Wymann. Originals and full track copy remain local.')
    (ROOT/'manifest.json').write_text(json.dumps(report,indent=2))
    sheet=Image.new('RGB',(1024,768),'#07111d')
    for i,name in enumerate(['opening','engineering','evidence','method']):
        im=Image.open(ROOT/'artwork'/f'{name}.png');im.thumbnail((1000,180))
        sheet.paste(im,((1024-im.width)//2,i*192))
    sheet.save(ROOT/'review.png')
    print(json.dumps(dict(copy_files_changed=differences,installed_files_changed=[])))

if __name__=='__main__':main()
