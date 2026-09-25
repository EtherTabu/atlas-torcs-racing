"""Restore only the two textures in the local showcase copy, never installed TORCS."""
from pathlib import Path
import hashlib
import json
import shutil

root = Path(__file__).resolve().parent
manifest = json.loads((root/'manifest.json').read_text())
for asset in manifest['assets']:
    name = asset['relative_target']
    assert Path(name).name == name
    source = root/'originals'/name
    assert hashlib.sha256(source.read_bytes()).hexdigest() == asset['original_sha256']
    shutil.copyfile(source, root/'showcase-track'/name)
print('Local showcase copy restored. Installed TORCS was never modified.')
