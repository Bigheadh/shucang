#!/usr/bin/env python3
"""
validate-changelog.py — 校验 AI 变更记录完整性和质量

用法:
  python3 validate-changelog.py changelog/2026-05-21-xxx.md
  python3 validate-changelog.py changelog/  # 校验所有
"""
import sys, os, re

CHECKS = {
    "概览表": {
        "pattern": r"\|.*日期.*\|",
        "weight": "must",
        "hint": "缺少日期字段"
    },
    "任务描述": {
        "pattern": r"\|.*任务.*\|.*【?[^【]*】?.*\|",
        "weight": "must",
        "hint": "缺少任务描述"
    },
    "改前代码": {
        "pattern": r"\|.*改前.*\|",
        "weight": "must",
        "hint": "缺少『改前』列，必须列出改动前的代码"
    },
    "改后代码": {
        "pattern": r"\|.*改后.*\|",
        "weight": "must",
        "hint": "缺少『改后』列，必须列出改动后的代码"
    },
    "修改原因": {
        "pattern": r"\|.*原因.*\|",
        "weight": "must",
        "hint": "缺少『原因』列，必须解释为什么改"
    },
    "影响评估": {
        "pattern": r"\|.*影响.*\|",
        "weight": "must",
        "hint": "缺少『影响』列，必须评估影响范围"
    },
    "行号位置": {
        "pattern": r"\|.*位置.*\|",
        "weight": "must",
        "hint": "缺少『位置』列，必须标注行号"
    },
    "风险说明": {
        "pattern": r"## 风险|### 已知风险",
        "weight": "must",
        "hint": "缺少风险说明"
    },
    "验证步骤": {
        "pattern": r"## 验证|### 验证",
        "weight": "must",
        "hint": "缺少验证步骤"
    },
    "结构性摘要": {
        "pattern": r"结构性摘要|## 结构性",
        "weight": "should",
        "hint": "建议添加结构性摘要（新增/删除/重构总览）"
    },
    "回滚方案": {
        "pattern": r"回滚|回退",
        "weight": "should",
        "hint": "建议标注回滚方案"
    },
    "待填写标记检查": {
        "pattern": r"【待填写】|【请填写】|【待评估】|【待判断】",
        "weight": "warn",
        "hint": "存在未填写的字段（【待填写】等标记）",
        "inverse": True
    }
}

def validate_file(filepath):
    with open(filepath) as f:
        content = f.read()
    
    results = []
    for name, check in CHECKS.items():
        found = bool(re.search(check["pattern"], content))
        if check.get("inverse"):
            passed = not found
        else:
            passed = found
        
        if not passed:
            results.append((check["weight"], name, check["hint"]))
    
    return results

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    if os.path.isdir(path):
        files = sorted([os.path.join(path, f) for f in os.listdir(path) if f.endswith(".md")])
    else:
        files = [path]
    
    total_issues = 0
    for f in files:
        basename = os.path.basename(f)
        issues = validate_file(f)
        
        if not issues:
            print(f"  ✅ {basename} — 全部通过")
            continue
        
        must = [i for i in issues if i[0] == "must"]
        should = [i for i in issues if i[0] == "should"]
        warn = [i for i in issues if i[0] == "warn"]
        
        status = "❌" if must else ("⚠️" if should else "⚡")
        print(f"\n  {status} {basename}")
        for w, name, hint in must:
            print(f"      🔴 [必须] {name}: {hint}")
        for w, name, hint in should:
            print(f"      🟡 [建议] {name}: {hint}")
        for w, name, hint in warn:
            print(f"      ⚡ [提示] {hint}")
        
        total_issues += len(issues)
    
    if total_issues == 0:
        print(f"\n  🎉 全部 {len(files)} 个文件通过校验！")
    else:
        print(f"\n  📊 共 {total_issues} 个问题 (must={sum(1 for i in issues if i[0]=='must') if issues else 0})")

if __name__ == "__main__":
    main()
