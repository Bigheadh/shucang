# AGENTS.md — 术藏项目 AI 行为规范

> 本项目是 Bigheadh 的个人技能仓库。
> 任何 AI（包括我）修改本仓库代码后，必须遵守以下规范。

## 核心规则

### 1. 每次改动必须输出变更明细
每次修改本仓库的任何文件后，必须按 `术藏/模板/ai-change-log.md` 模板输出变更明细。
变更记录写入 `changelog/` 目录。

### 2. 变更明细要求
- 每个文件每处改动单独列一条
- 必须包含：位置、改前、改后、原因、影响
- 宁可过细，不可遗漏

### 3. 提交信息规范
格式：`<emoji> <type>(<scope>): <描述>`
示例：`♻️ refactor(template): 优化 ai-change-log 结构，新增质量门禁`

### 4. 质量门禁
输出变更记录后，自检附录 E 质量门禁清单，全部通过才算完成。

### 5. 修改模板本身
如果修改 ai-change-log.md 模板本身，必须在 changelog/ 中记录本次修改。
这是元规范 —— 模板的修改也需要被记录。

## 项目结构速览
```
shucang/                    # 项目根目录
├── 术藏/                   # 核心技能库
│   ├── 索引.md             # 技能总索引
│   └── 模板/               # 各类模板
│       ├── ai-change-log.md # AI 变更记录模板（核心）
│       └── skill-template.md
├── changelog/              # 变更记录归档
├── scripts/                # 工具脚本
│   ├── gen-changelog.py
│   ├── validate-changelog.py
│   ├── git-push-via-api.py
│   ├── aliases.sh
│   └── changelog-snippets.code-snippets
├── hooks/                  # Git 钩子
│   ├── post-commit
│   └── gitmessage
├── Makefile
├── README.md
└── AGENTS.md               # 本文件
```
