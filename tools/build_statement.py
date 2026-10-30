"""Build a statement with the pinned Polygon Chinese Template (no online Polygon)."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from xml.sax.saxutils import escape

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('problem', type=Path)
parser.add_argument('--pandoc', default=os.environ.get('PANDOC', 'pandoc'))
parser.add_argument('--tectonic', default=os.environ.get('CODEX_TECTONIC_PATH', 'tectonic'))
parser.add_argument('--index', type=int, default=1, help='Contest position, A=1, B=2')
args = parser.parse_args()
root = args.problem.resolve()
vendor = Path(__file__).resolve().parents[1] / 'vendor/polygon-chinese-template'
build = root / '.statement-build'
build.mkdir(exist_ok=True)
meta = json.loads((root / 'problem.json').read_text(encoding='utf-8'))
for key in ('time_limit_ms', 'memory_limit_mb'):
    if meta[key] <= 0:
        raise ValueError(f'Invalid {key}')
# Canonical prose is statement.md; limits always come from judge metadata.
source = root / 'statement.md'
generated = build / 'statement.tex'
if args.index < 1:
    parser.error('--index must be positive')
subprocess.run([
    args.pandoc, str(source),
    '--from=markdown-implicit_figures+fenced_divs+fenced_code_attributes',
    '--to=latex', '--standalone',
    f'--template={vendor / "pandoc/problem.template.tex"}',
    f'--lua-filter={vendor / "pandoc/polygon.lua"}',
    '--metadata=standalone:true', '--metadata=show-metadata:true',
    f'--metadata=time-limit:{meta["time_limit_ms"] / 1000:g} s',
    f'--metadata=memory-limit:{meta["memory_limit_mb"]} MB',
    f'--output={generated}',
], cwd=root, check=True)
tex = generated.read_text(encoding='utf-8')
tex = tex.replace('\\begin{problem}', f'\\setcounter{{problem}}{{{args.index - 1}}}\n\\begin{{problem}}', 1)
generated.write_text(tex, encoding='utf-8')
env = os.environ.copy()
env.setdefault('TECTONIC_CACHE_DIR', str(Path(__file__).resolve().parents[1] / '.tmp/tectonic-cache'))
if os.name == 'nt' and not env.get('FONTCONFIG_FILE'):
    # Windows fontconfig cannot reliably write cache paths containing CJK.
    cache = Path(tempfile.gettempdir()) / 'problem-forge-fontconfig'
    cache.mkdir(parents=True, exist_ok=True)
    fonts = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts'
    config = cache / 'fonts.conf'
    config.write_text(f'<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd"><fontconfig><dir>{escape(fonts.as_posix())}</dir><cachedir>{escape(cache.as_posix())}</cachedir></fontconfig>', encoding='utf-8')
    env['FONTCONFIG_FILE'] = str(config)
result = subprocess.run([
    args.tectonic, '--chatter=minimal', '-Z', f'search-path={vendor}',
    f'--outdir={build}', str(generated),
], cwd=root, env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
log = result.stdout.decode('utf-8', errors='replace')
(build / 'compile.log').write_text(log, encoding='utf-8')
print(log)
if 'Missing character:' in log:
    raise SystemExit('PDF contains missing glyphs; fix typography before packaging')
shutil.copy2(build / 'statement.pdf', root / 'statement.pdf')
print(root / 'statement.pdf')
