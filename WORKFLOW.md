# 出题流程

1. 在私有仓库的 `problems/` 下用 `forge.py new` 新建题目。代号只用小写字母、数字和连字符。
2. 编写题面与元数据；样例按 `01.in`、`01.out` 这样的同名文件成对保存。
3. 将数据生成器、标程、验题程序等放在对应题目目录，避免将未发布内容放进公开仓库。
4. 运行 `forge.py check`，再由出题人检查题意、边界和测试数据。
5. 发布前另行确认题目内容与数据是否可以公开；本仓库的模板和工具可以独立发布。

题目目录约定：

```text
problems/<slug>/
├── problem.json       # 标题、时间和内存限制
├── statement.md       # 题面
└── data/samples/      # 01.in / 01.out 等样例
```

`statement.md` 采用 Markdown，可按目标平台另行排版；默认使用 XCPC 模板经本地 Typst 命令行生成 PDF；以 `statement.md` 为唯一题面正文源，时空限制读取 `problem.json`。具体命令见 [排版流程](skills/problem-authoring/references/xcpc-generator.md)。
