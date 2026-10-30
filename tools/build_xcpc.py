"""Build XCPC PDFs from canonical problem sources, without a browser."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import re

from export_xcpc import make_contest

REPO = Path(__file__).resolve().parents[1]
WORKSPACE = REPO.parent
FONTS = ('FZHTK.ttf', 'FZKTK.ttf', 'FZSSK.ttf', 'FZXBSK.ttf',
         'NewCMMath-Book.otf', 'cmunss.otf', 'cmunsx.otf', 'cmuntt.ttf')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('problems', nargs='+', type=Path, help='In contest order')
    parser.add_argument('--title', required=True)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--index', type=int, default=1, help='Single problem letter: A=1, B=2')
    parser.add_argument('--titlepage', action='store_true', help='Add cover and problem list')
    parser.add_argument('--typst', default=os.environ.get('TYPST'))
    parser.add_argument('--font-path', type=Path, default=REPO / '.tools/xcpc-fonts')
    args = parser.parse_args()
    if not 1 <= args.index <= 26:
        parser.error('--index must be between 1 and 26')
    if len(args.problems) > 1 and args.index != 1:
        parser.error('--index applies only to single problem exports')
    if len(args.problems) > 26:
        parser.error('This template supports at most 26 lettered problems')
    typst = args.typst or shutil.which('typst')
    if not typst:
        candidates = sorted((REPO / '.tools').glob('typst-*/typst.exe'))
        typst = str(candidates[0]) if len(candidates) == 1 else None
    if not typst:
        parser.error('Typst not found: run tools/setup_xcpc.py, or specify --typst')
    missing = [name for name in FONTS if not (args.font_path / name).is_file()]
    if missing:
        parser.error('Run tools/setup_xcpc.py; missing template fonts: ' + ', '.join(missing))
    data = make_contest([p.resolve() for p in args.problems], args.title)
    if len(data['problems']) == 1:
        problem = data['problems'][0]['problem']
        problem['display_name'] = f'Problem {chr(64 + args.index)}. ' + problem['display_name']
    data['meta']['enable_titlepage'] = args.titlepage
    data['meta']['enable_problem_list'] = args.titlepage
    output = args.output.resolve()
    build = output.parent / '.xcpc-build' / output.stem
    build.mkdir(parents=True, exist_ok=True)
    template = (REPO / 'vendor/xcpc-statement-generator/lib.typ').read_text(encoding='utf-8')
    # Keep the upstream font order, excluding unavailable platform fallbacks.
    # This prevents silent system-font substitutions and noisy native warnings.
    available = subprocess.check_output([
        typst, 'fonts', '--ignore-system-fonts', '--font-path', str(args.font_path.resolve())
    ]).decode('utf-8').splitlines()
    font_start = template.index('#let fonts = (')
    font_end = template.index('#let md =', font_start)
    font_config = template[font_start:font_end]
    font_config = re.sub(r'"([^"\n]+)"\s*,?',
                         lambda m: m.group(0) if m.group(1) in available else '', font_config)
    (build / 'lib.typ').write_text(template[:font_start] + font_config + template[font_end:], encoding='utf-8')
    (build / 'contest.json').write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    (build / 'main.typ').write_text('''#import "lib.typ": contest-conf
#let data = json("contest.json")
#let m = data.meta
#show: contest-conf.with(
  title: m.title, subtitle: m.subtitle, author: m.author, date: m.date,
  language: m.language, problems: data.problems,
  enable-titlepage: m.enable_titlepage,
  enable-header-footer: m.enable_header_footer,
  enable-problem-list: m.enable_problem_list,
  titlepage-language: auto, problem-language: auto,
)
''', encoding='utf-8')
    cache = REPO / '.tmp/typst-packages'
    cache.mkdir(parents=True, exist_ok=True)
    command = [typst, 'compile', '--root', str(build), '--ignore-system-fonts',
               '--font-path', str(args.font_path.resolve()), '--package-cache-path', str(cache),
               '--creation-timestamp', '0', str(build / 'main.typ'), str(build / 'result.pdf')]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log = result.stdout.decode('utf-8', errors='replace')
    (build / 'compile.log').write_text(log, encoding='utf-8')
    if log:
        print(log[:4000])
    if result.returncode:
        raise SystemExit(result.returncode)
    if 'warning:' in log:
        raise SystemExit('Review Typst warnings before publishing; see compile.log')
    shutil.copy2(build / 'result.pdf', output)
    print(output)


if __name__ == '__main__':
    main()
