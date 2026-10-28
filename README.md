# Problem Forge

公开的算法竞赛出题工具箱。这里存放通用题目模板、检查工具和工作流程；未发布的题目内容保存在私有仓库 [problem-forge-private](https://github.com/hekinya/problem-forge-private)。

## 开始使用

需要 Python 3.10 或更新版本，不需要安装第三方依赖。

```bash
python tools/forge.py new example --root ../problem-forge-private/problems
python tools/forge.py check --root ../problem-forge-private/problems
```

`new` 会复制 `templates/problem`，生成 `problems/<题目代号>/`。填写 `problem.json` 与 `statement.md`，将样例放到 `data/samples/`。检查命令会确认题目基本信息完整、样例输入输出成对；它不替代题意审校、数据生成或标程验证。

两个仓库的分工和建议流程见 [WORKFLOW.md](WORKFLOW.md)。
## 协作出题

用户只填写部分题目信息时，先补全为私有仓库中的待审核草稿；用户确认或提出修改后，才生成正式题目文件。对应的 Codex skill 见 [problem-authoring](skills/problem-authoring/SKILL.md)。
