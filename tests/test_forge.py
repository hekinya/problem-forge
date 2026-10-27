import json
import shutil
import unittest
import uuid
from pathlib import Path

from tools.forge import check, check_problem, create


class ForgeTests(unittest.TestCase):
    def test_create_then_check(self):
        scratch = Path(__file__).resolve().parent.parent / ".tmp" / uuid.uuid4().hex
        scratch.mkdir(parents=True)
        try:
            root = scratch / "problems"
            self.assertEqual(create(root, "two-sum"), 0)
            self.assertEqual(create(root, "two-sum"), 1)
            self.assertEqual(create(root, "bad/name"), 1)
            folder = root / "two-sum"
            self.assertIn("title 尚未填写", check_problem(folder))
            metadata = folder / "problem.json"
            data = json.loads(metadata.read_text(encoding="utf-8"))
            data["title"] = "两数之和"
            metadata.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            self.assertEqual(check(root), 0)
            (folder / "data" / "samples" / "01.in").write_text("1 2\n", encoding="utf-8")
            self.assertIn("样例 01.in 缺少对应 .out", check_problem(folder))
            (folder / "data" / "samples" / "01.out").write_text("3\n", encoding="utf-8")
            self.assertEqual(check(root), 0)
        finally:
            shutil.rmtree(scratch)


if __name__ == "__main__":
    unittest.main()
