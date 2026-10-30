"""Install and verify pinned XCPC dependencies inside this repository (Windows x64)."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import tarfile
import urllib.request
from zipfile import ZipFile

from build_xcpc import REPO

VENDOR = REPO / 'vendor/xcpc-statement-generator'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fetch(url):
    print('Downloading ' + url, flush=True)
    with urllib.request.urlopen(url, timeout=90) as response:
        return response.read()


def ensure_file(target, spec, check, archive=None):
    if target.is_file() and digest(target.read_bytes()) == spec['sha256']:
        return
    if check:
        raise RuntimeError(f'Missing or invalid dependency: {target}')
    data = archive() if archive else fetch(spec['url'])
    if digest(data) != spec['sha256']:
        raise RuntimeError(f'SHA256 mismatch: {target.name}')
    target.parent.mkdir(parents=True, exist_ok=True)
    pending = target.with_suffix(target.suffix + '.part')
    pending.write_bytes(data)
    pending.replace(target)


def install_package(spec, check):
    payload = (VENDOR / spec['file']).read_bytes()
    if digest(payload) != spec['sha256']:
        raise RuntimeError('Bundled package hash mismatch: ' + spec['name'])
    target = REPO / '.tmp/typst-packages/preview' / spec['name'] / spec['version']
    with tarfile.open(fileobj=io.BytesIO(payload), mode='r:gz') as archive:
        for member in archive.getmembers():
            if not member.isfile():
                continue
            dest = (target / member.name).resolve()
            if not dest.is_relative_to(target.resolve()):
                raise ValueError('Unsafe package path')
            data = archive.extractfile(member).read()
            if dest.is_file() and digest(dest.read_bytes()) == digest(data):
                continue
            if check:
                raise RuntimeError('Missing or invalid package file: ' + str(dest))
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)


def smoke_test(compiler, fonts):
    root = REPO / '.tmp/xcpc-install-smoke'
    samples = root / 'data/samples'
    samples.mkdir(parents=True, exist_ok=True)
    (root / 'problem.json').write_text(json.dumps({
        'title': '安装验证', 'time_limit_ms': 1000, 'memory_limit_mb': 256,
    }, ensure_ascii=False), encoding='utf-8')
    (samples / '01.in').write_text('1\n', encoding='utf-8')
    (samples / '01.out').write_text('2\n', encoding='utf-8')
    (root / 'statement.md').write_text(
        '计算 $a+1$。\n# 输入格式 {#input}\n一个整数。\n'
        '# 输出格式 {#output}\n答案。\n::: {.samples}\n'
        '``` {.input}\n1\n```\n``` {.output}\n2\n```\n:::\n', encoding='utf-8')
    subprocess.run([sys.executable, str(REPO / 'tools/build_xcpc.py'), str(root),
                    '--title', 'XCPC 安装验证', '--output', str(root / 'smoke.pdf'),
                    '--typst', str(compiler), '--font-path', str(fonts)], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Verify offline without downloading or repairing')
    parser.add_argument('--archive', type=Path, help='Optional original XCPC ZIP to supply fonts offline')
    args = parser.parse_args()
    if platform.system() != 'Windows' or platform.machine().lower() not in ('amd64', 'x86_64'):
        parser.error('Automatic compiler installation supports Windows x64. On other platforms install Typst 0.15.1 and pass --typst/--font-path to build_xcpc.py.')
    manifest = json.loads((VENDOR / 'dependencies.json').read_text(encoding='utf-8'))
    native = manifest['typst']
    tools = REPO / '.tools'
    compiler = tools / ('typst-' + native['version']) / 'typst.exe'
    if not compiler.is_file() or digest(compiler.read_bytes()) != native['executable_sha256']:
        if args.check:
            raise RuntimeError('Typst missing or hash mismatch; run setup_xcpc.py')
        payload = fetch(native['url'])
        if digest(payload) != native['sha256']:
            raise RuntimeError('Typst archive SHA256 mismatch')
        with ZipFile(io.BytesIO(payload)) as archive:
            member = next(n for n in archive.namelist() if n.endswith('/typst.exe'))
            data = archive.read(member)
        if digest(data) != native['executable_sha256']:
            raise RuntimeError('Typst executable SHA256 mismatch')
        compiler.parent.mkdir(parents=True, exist_ok=True)
        compiler.write_bytes(data)
    fonts = tools / 'xcpc-fonts'
    archive_fonts = {}
    if args.archive:
        with ZipFile(args.archive) as archive:
            for spec in manifest['fonts']:
                member = next(n for n in archive.namelist() if n.endswith('/assets/fonts/' + spec['name']))
                archive_fonts[spec['name']] = archive.read(member)
    def install_font(spec):
        data = archive_fonts.get(spec['name'])
        ensure_file(fonts / spec['name'], spec, args.check, (lambda: data) if data else None)
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(install_font, manifest['fonts']))
    for spec in manifest['packages']:
        install_package(spec, args.check)
    smoke_test(compiler, fonts)
    print('XCPC dependencies verified; sample PDF built without browser/npm/Pandoc')


if __name__ == '__main__':
    main()
