# Problem Forge

公开的算法竞赛出题工具箱。这里存放通用题目模板、检查工具和工作流程；未发布的题目内容保存在私有仓库 [problem-forge-private](https://github.com/hekinya/problem-forge-private)。

## 开始使用

基础结构检查需要 Python 3.10 或更新版本，不需要安装第三方依赖。中文 PDF 默认使用 XCPC Typst 命令行排版，无需浏览器；见 [排版流程](skills/problem-authoring/references/xcpc-generator.md)。原 Pandoc/LaTeX 方案保留。

```bash
python tools/forge.py new example --root ../problem-forge-private/problems
python tools/forge.py check --root ../problem-forge-private/problems
```

`new` 会复制 `templates/problem`，生成 `problems/<题目代号>/`。填写 `problem.json` 与 `statement.md`，将样例放到 `data/samples/`。检查命令会确认题目基本信息完整、样例输入输出成对；它不替代题意审校、数据生成或标程验证。

两个仓库的分工和建议流程见 [WORKFLOW.md](WORKFLOW.md)。
## 协作出题

用户只填写部分题目信息时，先补全为私有仓库中的待审核草稿；用户确认或提出修改后，才生成正式题目文件。对应的 Codex skill 见 [problem-authoring](skills/problem-authoring/SKILL.md)。

## XCPC PDF 环境

Windows x64、Python 3.10+ 下，在本仓库根目录运行：

```powershell
python tools/setup_xcpc.py
python tools/setup_xcpc.py --check
```

安装器自动准备固定版本的 Typst 和模板字体、解包仓库内的宏包，并生成中文与公式测试 PDF。首次安装需要网络；之后可以离线排版。无需手工提供 ZIP，也不需要浏览器、npm 或 Pandoc。工具、模板、依赖校验清单和宏包归档均随仓库维护；大体积编译器与字体保存在被 Git 忽略的 `.tools/`。

安装出题 skill 时复制完整 `skills/problem-authoring/` 目录，并保留本工具仓库。skill 会引导 AI 在首次构建前自动检查和安装依赖。详细生成命令见 [XCPC 排版流程](skills/problem-authoring/references/xcpc-generator.md)。
