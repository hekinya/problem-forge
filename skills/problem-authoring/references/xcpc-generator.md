# XCPC 命令行排版（默认）

## 来源与固定版本

复用 https://github.com/lihaoze123/xcpc-statement-generator 的 0.2.4 模板。用户提供 ZIP SHA256 为 `5d7dc03d58d488a6cbd02f338d1b3919be47d0a3634b364f1336aff6418406ea`。未修改的 `lib.typ`、AGPL-3.0 LICENSE 及来源记录放在 `vendor/xcpc-statement-generator/`；字体由固定上游 revision 自动下载，不复制进 skill。

当前验证组合：Typst 0.15.1、numbly 0.1.0、cmarker 0.1.6、mitex 0.2.6、oxifmt 1.0.0。生成目录中的模板仅移除本机不存在的备用字体名，保留可用字体及原有顺序；源模板保持原样。编译禁用系统字体，确保使用工具自带字体。

## AI 首次使用时自动安装

先定位 `problem-forge` 仓库并切换到其根目录。AI 在首次构建前主动检查环境：

```powershell
python tools/setup_xcpc.py --check
```

若缺失依赖、文件校验失败或首次克隆后未安装，Windows x64 上直接执行以下安装流程，不要求用户手动下载 ZIP 或逐项安装：

```powershell
python tools/setup_xcpc.py
python tools/setup_xcpc.py --check
```

脚本按 `vendor/xcpc-statement-generator/dependencies.json` 中的固定 URL、版本和 SHA256 安装或修复依赖，不写系统目录、不改变 PATH。Typst 安装到仓库 `.tools/typst-0.15.1/typst.exe`，字体安装到 `.tools/xcpc-fonts/`；这些大文件由安装器自动下载，不提交 Git。四个小型 Typst 宏包的原始归档随仓库保存，含上游许可证，安装时校验并解压到 `.tmp/typst-packages/`。默认安装无需用户原有工具文件夹或下载目录。

两个命令都会用内置的中文、数学公式和样例小题生成测试 PDF，确认转换器、字体、宏包和编译器能协同工作。`--check` 不联网下载或修复依赖，但会在 `.tmp/xcpc-install-smoke/` 写入检查文件。安装成功后，日常构建无需网络、浏览器、npm 或 Pandoc。可选 `--archive` 仅用于离线提供字体，并非正常安装的前提。

当前自动安装支持 Windows x64，Python 3.10+；其它平台需提供可用的 Typst 0.15.1 和字体路径并验证，不能宣称已自动支持。若失败，先读错误和日志，针对性修复后重试；校验失败时不要跳过校验，不要静默换排版后端或把旧 PDF 当作新成果。

## 自动生成

```powershell
# 单题：A=1、B=2；保留比赛页眉和原题号
python tools/build_xcpc.py ../problem-forge-private/problems/<slug> --index 2 --title "已确认的比赛名称" --output ../problem-forge-private/exports/B.pdf

# 整场题册：目录参数顺序就是 A、B……题序
python tools/build_xcpc.py ../problem-forge-private/problems/<slug-a> ../problem-forge-private/problems/<slug-b> --title "已确认的比赛名称" --output ../problem-forge-private/exports/contest.pdf
```

`--titlepage` 可增加封面和题目列表。当前题序支持 A 至 Z。可用 `--typst` 或 `TYPST` 指定编译器，`--font-path` 指定包含八种模板字体的目录。中间 JSON、Typst 源文件及编译日志保存在输出目录的 `.xcpc-build/<文件名>/`，应加入私有仓库忽略规则。编译有错误或警告时不覆盖输出 PDF。

## 题面与验证

正文只维护 `statement.md`，时限内存只维护 `problem.json`，样例只维护 `data/samples/*.in`、对应 `.out`；Markdown 内样例必须与文件一致。`export_xcpc.py` 与命令行构建共用转换器，将输入、输出、约束和样例说明映射到模板，题解不进入输出。当前支持普通文本、数学公式和多组样例；图片、交互题及额外语义小节需要扩展转换器，不能静默丢弃。

生成后逐页检查题号、比赛页眉、四项运行信息、中文字体、公式、表格和分页，再将选定的单题 PDF 保存为题目目录 `statement.pdf` 并运行既有 Hydro 打包脚本。核对 ZIP 中 PDF 字节、数据答案和配置。转换成功并不证明算法正确；继续按主 skill 验题。未在目标 Hydro 实例实测时明确保留该限制。

后端切换时先将比较 PDF 保存在私有工程内，经过内容与排版检查后再替换正式包。

## 可选浏览器编辑

浏览器编辑器是独立的可选工具，不随命令行依赖安装。在用户已有本地部署时使用；不要为日常 PDF 构建启动或安装它。需要网页配置时，用 `tools/export_xcpc.py`（与 build_xcpc.py 相同的题目参数、`--title`、`--output`）导出 JSON，然后“设置 → 导入配置”。JSON 不是 Polygon ZIP。

浏览器改动应回写源文件再生成，不让两套正文独立演化。浏览器编辑器首次初始化可能需要字体授权和联网；日常命令行排版不依赖它。没有用户明确指示，不上传未发布题目或启用云同步。
