"""Export canonical Problem Forge statements to XCPC Generator v0.2.4 JSON."""
import argparse
import json
from pathlib import Path
import re

def load_problem(root):
    meta = json.loads((root / 'problem.json').read_text(encoding='utf-8'))
    for key in ('time_limit_ms', 'memory_limit_mb'):
        if not isinstance(meta.get(key), (int, float)) or meta[key] <= 0:
            raise ValueError(f'{root}: invalid {key}')
    text = (root / 'statement.md').read_text(encoding='utf-8')
    text = re.sub(r'\A---\n.*?\n---\n', '', text, count=1, flags=re.S)
    text = re.split(r'^# .*?\{#tutorial\}\s*$', text, maxsplit=1, flags=re.M)[0]
    if re.search(r'!\[|<img\b', text):
        raise ValueError(f'{root}: images require explicit asset mapping')
    for heading in re.findall(r'^# .+$', text, re.M):
        if not re.search(r'\{#[a-z-]+\}\s*$', heading):
            raise ValueError(f'{root}: section needs a supported semantic ID: {heading}')
    embedded = re.findall(r'``` \{\.(?:input|output)\}\n(.*?)\n```', text, re.S)
    samples = []
    for source in sorted((root / 'data/samples').glob('*.in')):
        samples.append({'input': source.read_text(encoding='utf-8').rstrip('\r\n'),
                        'output': source.with_suffix('.out').read_text(encoding='utf-8').rstrip('\r\n')})
    if not samples:
        raise ValueError(f'{root}: no samples found')
    if embedded != [s[k] for s in samples for k in ('input', 'output')]:
        raise ValueError(f'{root}: Markdown samples differ from data/samples')
    text = re.sub(r'::: \{\.samples\}.*?:::', '', text, flags=re.S)
    parts = re.split(r'^# .*?\{#([a-z-]+)\}\s*\n', text, flags=re.M)
    sections = {'description': parts[0].strip()}
    for index in range(1, len(parts), 2):
        name, content = parts[index], parts[index + 1].strip()
        if name not in ('input', 'output', 'constraints', 'explanation', 'tutorial'):
            raise ValueError(f'Unsupported section {name}: adapt exporter explicitly')
        sections[name] = content
    if not all(sections.get(name) for name in ('description', 'input', 'output')):
        raise ValueError(f'{root}: description/input/output must be nonempty')
    if sections.get('constraints'):
        sections['description'] += '\n\n## 数据范围\n\n' + sections['constraints']
    return {'problem': {
        'display_name': meta['title'], 'format': 'markdown', 'interactive': False,
        'samples': samples, 'limits': [
            {'key': '输入文件', 'value': '标准输入'},
            {'key': '输出文件', 'value': '标准输出'},
            {'key': '时间限制', 'value': f'{meta["time_limit_ms"] / 1000:g} s'},
            {'key': '内存限制', 'value': f'{meta["memory_limit_mb"]} MB'},
        ]}, 'statement': {
            'description': sections['description'], 'input': sections.get('input', ''),
            'output': sections.get('output', ''), 'notes': sections.get('explanation', ''),
        }}


def make_contest(roots, title):
    problems = [load_problem(root) for root in roots]
    data = {'meta': {
        'title': title, 'subtitle': '', 'author': '', 'date': '', 'language': 'zh',
        'titlepage_language': 'auto', 'problem_language': 'auto',
        'enable_titlepage': False, 'enable_header_footer': True, 'enable_problem_list': False,
    }, 'problems': problems, 'images': []}
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('problems', nargs='+', type=Path, help='In contest order')
    parser.add_argument('--title', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    data = make_contest(args.problems, args.title)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(args.output)


if __name__ == '__main__':
    main()
