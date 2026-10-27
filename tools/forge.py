#!/usr/bin/env python3
"""Create and check unpublished problem folders using only the standard library."""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path


TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "problem"
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def create(root: Path, slug: str) -> int:
    if not SLUG.fullmatch(slug):
        print("题目代号只能包含小写字母、数字和中间的连字符", file=sys.stderr)
        return 1
    destination = root / slug
    if destination.exists():
        print(f"目录已存在：{destination}", file=sys.stderr)
        return 1
    root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(TEMPLATE, destination)
    print(f"已创建：{destination}")
    return 0


def check_problem(folder: Path) -> list[str]:
    errors = []
    metadata = folder / "problem.json"
    statement = folder / "statement.md"
    if not metadata.is_file():
        errors.append("缺少 problem.json")
    else:
        try:
            data = json.loads(metadata.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("顶层必须是对象")
            title = data.get("title")
            if not isinstance(title, str) or not title.strip() or title.startswith("请填写"):
                errors.append("title 尚未填写")
            for key in ("time_limit_ms", "memory_limit_mb"):
                if type(data.get(key)) is not int or data[key] <= 0:
                    errors.append(f"{key} 必须是正整数")
        except (ValueError, UnicodeError) as exc:
            errors.append(f"problem.json 无效：{exc}")
    if not statement.is_file():
        errors.append("statement.md 缺失")
    else:
        try:
            if not statement.read_text(encoding="utf-8").strip():
                errors.append("statement.md 为空")
        except UnicodeError:
            errors.append("statement.md 不是有效的 UTF-8 文本")
    samples = folder / "data" / "samples"
    if samples.is_dir():
        inputs = {p.stem for p in samples.glob("*.in") if p.is_file()}
        outputs = {p.stem for p in samples.glob("*.out") if p.is_file()}
        for stem in sorted(inputs - outputs):
            errors.append(f"样例 {stem}.in 缺少对应 .out")
        for stem in sorted(outputs - inputs):
            errors.append(f"样例 {stem}.out 缺少对应 .in")
    return errors


def check(root: Path) -> int:
    if not root.is_dir():
        print(f"题目目录不存在：{root}", file=sys.stderr)
        return 1
    folders = sorted(p for p in root.iterdir() if p.is_dir())
    problems_with_errors = 0
    for folder in folders:
        errors = check_problem(folder)
        if errors:
            problems_with_errors += 1
            for error in errors:
                print(f"{folder.name}: {error}", file=sys.stderr)
    if problems_with_errors:
        print(f"检查失败：{problems_with_errors} 个题目目录有问题", file=sys.stderr)
        return 1
    print(f"检查通过：{len(folders)} 个题目")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="题目目录工具")
    subparsers = parser.add_subparsers(dest="command", required=True)
    new_parser = subparsers.add_parser("new", help="从模板新建题目")
    new_parser.add_argument("slug")
    new_parser.add_argument("--root", type=Path, default=Path("problems"))
    check_parser = subparsers.add_parser("check", help="检查题目目录")
    check_parser.add_argument("--root", type=Path, default=Path("problems"))
    args = parser.parse_args()
    if args.command == "new":
        return create(args.root, args.slug)
    return check(args.root)


if __name__ == "__main__":
    raise SystemExit(main())
