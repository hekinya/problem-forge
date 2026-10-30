# 中文题面排版

默认使用 `polygon-chinese-template` 的 Pandoc filter、LaTeX 模板及 `olymp.sty`，不需要登录 Polygon。固定版本与来源记录在 `vendor/polygon-chinese-template/UPSTREAM.md`，升级时先在私有题目上验证；不要直接跟随上游最新版本。

## 环境与构建

需要 Python 3.10+、Pandoc 和 Tectonic。优先探测已有程序及 `CODEX_TECTONIC_PATH`；缺失时安装到项目本地工具目录，避免更改系统配置。Tectonic 首次运行需联网下载 TeX 资源，脚本默认缓存到公开仓库忽略的 `.tmp/tectonic-cache`，可通过 `TECTONIC_CACHE_DIR` 覆盖。

在公开仓库根目录执行：

```bash
python tools/build_statement.py ../problem-forge-private/problems/<slug> --index 1
```

`--index` 为比赛题序，A=1、B=2。可用 `--pandoc /path/to/pandoc`、`--tectonic /path/to/tectonic` 指定工具，也可设置 `PANDOC`、`CODEX_TECTONIC_PATH`。输出到题目目录 `statement.pdf`；中间文件位于 `.statement-build/`，不随题包发布。

## 唯一题面源

`statement.md` 开头使用 YAML：

```yaml
---
title: "题目名称"
language: chinese
input-file: 标准输入
output-file: 标准输出
show-metadata: true
contest:
  name: 已确认的比赛名称
---
```

时限、内存由构建脚本从 `problem.json` 注入，不在 Markdown 另维护一份。正文使用普通 Pandoc Markdown 和 `$...$` 数学公式。一级标题使用 `# 输入格式 {#input}`、`# 输出格式 {#output}`、`# 数据范围 {#constraints}`、`# 样例说明 {#explanation}`。不要重复写题目名称作为正文标题。

样例使用 `::: {.samples}` 容器，其中按顺序放置 `.input`、`.output` fenced code blocks。内容必须与 `data/samples/*.in`、对应 `.out` 一致；多组可放入同一容器，生成带边框的样例表。

## 验证与导出

渲染每页 PDF 并目视检查中文、数学符号、标题题号、比赛页眉、四项运行信息、分页和样例表格。检查没有遗漏正文、样例说明或题解泄漏。若上游模板在当前字体环境出现缺字，修复构建环境或明确记录本地兼容补丁，不回退到重复维护正文的绘图脚本。

然后按 `hydro-package.md` 重新打包，核对 ZIP 内 PDF 与最终 PDF 字节相同，所有数据和答案保持一致。未在目标 Hydro 实例实测时保留该限制。单纯排版变更不必重复整个算法验题，但需检查源题面和样例没有语义变化。
