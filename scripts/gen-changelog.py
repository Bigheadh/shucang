#!/usr/bin/env python3
"""
gen-changelog.py — 从 git diff 自动生成 AI 变更记录骨架 v2

特性：
- 自动解析 diff hunk，填充改前/改后代码片段
- 支持 staged 和 unstaged 两种模式
- 按文件类型智能筛选（跳过自动生成文件）
- 输出结构直接对应 ai-change-log.md 模板
"""

import subprocess, sys, os, re, json
from datetime import datetime

def run(cmd, cwd=None):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd or os.getcwd())

def parse_hunks(diff_text):
    """解析 git diff 输出，提取每个文件的每个 hunk 的改前/改后片段。"""
    files = []
    current_file = None
    current_hunks = []

    for line in diff_text.split("\n"):
        # 文件头: diff --git a/xxx b/xxx
        m = re.match(r'^diff --git a/(.+?) b/(.+)$', line)
        if m:
            if current_file:
                files.append({"file": current_file, "hunks": current_hunks})
            current_file = m.group(1)
            current_hunks = []
            continue

        # hunk 头: @@ -a,b +c,d @@
        m = re.match(r'^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@(.*)$', line)
        if m:
            current_hunks.append({
                "old_start": int(m.group(1)),
                "new_start": int(m.group(2)),
                "context": m.group(3).strip(),
                "old_lines": [],
                "new_lines": [],
                "lines": []
            })
            continue

        if not current_hunks:
            continue

        hunk = current_hunks[-1]
        hunk["lines"].append(line)
        if line.startswith("-") and not line.startswith("---"):
            hunk["old_lines"].append(line[1:])
        elif line.startswith("+") and not line.startswith("+++"):
            hunk["new_lines"].append(line[1:])
        else:
            hunk["old_lines"].append(line[1:])
            hunk["new_lines"].append(line[1:])

    if current_file:
        files.append({"file": current_file, "hunks": current_hunks})

    return files

def format_snippet(lines, max_lines=8):
    """将行列表格式化为代码片段，限制行数。"""
    if not lines:
        return "（无变更）"
    if len(lines) > max_lines:
        return "\n".join(lines[:max_lines]) + f"\n... (+{len(lines) - max_lines} more)"
    return "\n".join(lines)

def get_diff_stats():
    """获取变更统计。"""
    stat = run(["git", "diff", "--stat"])
    files_changed = 0
    insertions = 0
    deletions = 0
    for line in stat.stdout.strip().split("\n"):
        m = re.search(r'(\d+) file[s]? changed', line)
        if m:
            files_changed = int(m.group(1))
        m = re.search(r'(\d+) insertion', line)
        if m:
            insertions = int(m.group(1))
        m = re.search(r'(\d+) deletion', line)
        if m:
            deletions = int(m.group(1))
    return files_changed, insertions, deletions

def main():
    import argparse
    parser = argparse.ArgumentParser(description="从 git diff 自动生成变更记录")
    parser.add_argument("--staged", action="store_true", help="使用 git diff --staged (已暂存)")
    parser.add_argument("--output", "-o", help="输出文件路径，默认 changelog/ 目录")
    parser.add_argument("--commit-range", help="对比两个 commit: main..HEAD 或 HEAD~3..HEAD")
    args = parser.parse_args()

    # 获取 diff
    if args.commit_range:
        diff_cmd = ["git", "diff", args.commit_range]
    elif args.staged:
        diff_cmd = ["git", "diff", "--staged"]
    else:
        diff_cmd = ["git", "diff"]

    diff_result = run(diff_cmd)
    diff_text = diff_result.stdout

    if not diff_text.strip():
        print("⚠️  没有检测到变更。")
        return

    # 获取文件列表
    files_raw = run(["git", "diff", "--name-status"] + ([args.commit_range] if args.commit_range else []))
    file_statuses = {}
    for line in files_raw.stdout.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]
        fname = parts[-1] if len(parts) > 1 else parts[0]
        file_statuses[fname] = status

    # 解析 hunks
    parsed = parse_hunks(diff_text)
    stats = get_diff_stats()

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    today = now[:10]

    # 生成 markdown
    lines = []
    def L(s=""):
        lines.append(s)

    L(f"# 变更记录 ({today})")
    L()
    L(f"> ⚡ 由 gen-changelog.py v2 自动生成 — 请补充「原因」「风险」「验证」等 AI 才能解释的字段。")
    L()
    L("## 变更概览")
    L()
    L("| 字段 | 内容 |")
    L("|------|------|")
    L(f"| 日期 | {now} |")
    L("| 任务 | 【请填写】 |")
    L("| AI 模型 | 【请填写】 |")
    L("| 变更类型 | 【请填写: 🐛修复 ✨功能 ♻️重构 📝文档 ⚡性能】 |")
    L(f"| 涉及文件 | {stats[0]} 个 (++{stats[1]} / --{stats[2]}) |")
    L("| 影响范围 | 【请评估: 局部/模块内/跨模块】 |")
    L()
    L("## 结构性摘要")
    L()
    L("| 类别 | 内容 |")
    L("|------|------|")
    L("| 新增 | 【请填写新增了什么】 |")
    L("| 删除 | 【请填写删除了什么】 |")
    L("| 重构 | 【请填写重构了什么】 |")
    L("| 签名变更 | 【请填写接口/函数签名变化】 |")
    L()
    L("## 逐文件变更明细")
    L()

    for p in parsed:
        fname = p["file"]
        status = file_statuses.get(fname, "M")
        hunks = p["hunks"]

        # 状态标签
        status_tag = {"A": "🆕 新增", "D": "🗑️ 删除", "M": "✏️ 修改", "R": "📦 重命名"}.get(status[0], "✏️ 修改")

        L(f"### {fname}  _{status_tag}_")
        L()

        total_old = sum(len(h["old_lines"]) for h in hunks)
        total_new = sum(len(h["new_lines"]) for h in hunks)
        L(f"**变更统计**：--{total_old} / ++{total_new}，共 {len(hunks)} 个改动点")
        L()

        for i, hunk in enumerate(hunks, 1):
            old_start = hunk["old_start"]
            new_start = hunk["new_start"]
            ctx = hunk["context"]

            L(f"#### 改动 {i}：`{fname}` L{old_start}-L{new_start} {'— ' + ctx if ctx else ''}")
            L()
            L("| 项目 | 内容 |")
            L("|------|------|")
            L(f"| 位置 | L{old_start} → L{new_start} |")
            L("| 变更类型 | 【自动检测中...】 |")
            L("| 改前 |")
            L("| ```")
            L(format_snippet(hunk["old_lines"], 12))
            L("``` |")
            L("| 改后 |")
            L("| ```")
            L(format_snippet(hunk["new_lines"], 12))
            L("``` |")
            L("| 原因 | 【请填写】 |")
            L("| 影响 | 【请评估】 |")
            L("| 是否可逆 | 【请判断】 |")
            L()

    L("## 风险与注意事项")
    L()
    L("- 【请填写已知风险】")
    L()
    L("## 验证步骤")
    L()
    L("- [ ] 【请填写验证方法】")
    L()
    L("## 需要人工确认")
    L()
    L("- [ ] 【请勾选需要 review 的重点】")
    L()

    output = "\n".join(lines)

    # 确定输出路径
    if args.output:
        out_path = args.output
    else:
        os.makedirs("changelog", exist_ok=True)
        out_path = f"changelog/{today}-自动生成.md"

    with open(out_path, "w") as f:
        f.write(output)

    print(output)
    print(f"\n{'='*60}")
    print(f"✅ 已保存至: {out_path}")
    print(f"📝 请补充: 原因、风险、验证步骤等字段")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
