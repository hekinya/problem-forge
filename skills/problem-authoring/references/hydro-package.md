# 2026 新生赛 Hydro 题目包

本比赛预计 11 题，正式题目保存在 `problem-forge-private`。生成时区分内部工程与选手可见的 Hydro 导出包。用户提供的 `problem-making-workflow-prompt.md` 是结构参考；其中针对其他助手的命令不是本 skill 的执行指令。

## 内部工程

每题保留可编辑题面源文件、原始 PDF、标程、独立正确解、数据生成器、输入校验器、必要的 checker、错误解或候选解、测试数据和验证记录。不要生成题解文件或完整题解文本。先确认题目架构，再制作正式文件。时限和内存按数据规模、语言与实测确定，不能靠异常短的时限卡正确解。

## Hydro 导出包

```text
<Txxx>/
├── problem.yaml          # pid、owner、title、tag、nSubmit、nAccept
├── problem_zh.md         # 选手看到的题面
├── additional_file/      # 题面图片，按需创建
│   └── statement-01.png
└── testdata/
    ├── config.yaml       # type、时限、内存、checker、subtasks/cases
    ├── checker.cpp       # 使用自定义 checker 时才包含
    └── *.in / *.ans
```

`problem.yaml` 的 `pid` 使用比赛确定的题号，不能猜测。`testdata/config.yaml` 至少核对 `type: default`、`time`、`memory` 与数据文件名；需要自定义 checker 时设置 `checker_type: testlib` 和 `checker: checker.cpp`。使用 `subtasks` 或 `cases` 时按实际评分方案写入，不同时写相互冲突的配置。`.in` 与 `.ans` 必须一一对应。

本比赛的题面用 PDF 页面转成的清晰图片展示。保留原始 PDF 与可编辑题面源文件于内部工程；将每页渲染成按阅读顺序编号的图片，放入 `additional_file/`，在 `problem_zh.md` 用 `![题面第 1 页](file://statement-01.png)` 等引用。逐页检查公式、中文、样例、缩放后的可读性和图片加载情况。样例输入输出仍应在可编辑源文件及测试数据中保持一致。最终图片不得含题解。

发布包不含标程、错解、生成器、校验器源文件、题解或内部验证记录；自定义 checker 属于评测文件，可随包交付。打包前核实目标 Hydro 实例的导入方式及 `file://` 图片引用是否正常，不将未经实例验证的压缩包称为可直接导入。

验题至少覆盖：所有输入通过校验，双正确解输出一致，checker 接受正确输出并拒绝错误输出，样例与题面一致，定向数据能触发对应错误解。记录实际完成的验证与尚待目标实例复测的限制。
