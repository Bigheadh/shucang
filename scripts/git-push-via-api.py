#!/usr/bin/env python3
"""
git-push-via-api.py — 通过 GitHub REST API 推送代码
当 git push 连不上 github.com 时使用

Token 从 GITHUB_TOKEN 环境变量读取（优先）或 ~/.git-credentials 提取。
"""
import subprocess, json, sys, os, base64, urllib.request, urllib.error

# 读取 token
TOKEN = os.environ.get("GITHUB_TOKEN")
if not TOKEN:
    # 从 git credentials 提取
    cred_path = os.path.expanduser("~/.git-credentials")
    if os.path.exists(cred_path):
        with open(cred_path) as f:
            for line in f:
                if "github.com" in line:
                    TOKEN = line.strip().split(":")[-1].split("@")[0]
                    break
if not TOKEN:
    print("❌ 未找到 GITHUB_TOKEN，也无法从 git credentials 读取", file=sys.stderr)
    sys.exit(1)

OWNER, REPO = "Bigheadh", "shucang"
API = f"https://api.github.com/repos/{OWNER}/{REPO}"
REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def api(method, path, data=None):
    url = f"{API}/{path}"
    headers = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github.v3+json", "User-Agent": "push"}
    body = json.dumps(data).encode() if data else None
    if data: headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print(f"❌ HTTP {e.code} on {method} {path}: {err}", file=sys.stderr)
        sys.exit(1)

def git(*args):
    return subprocess.run(["git"] + list(args), capture_output=True, text=True, cwd=REPO_DIR)

def main():
    ref = api("GET", "git/refs/heads/main")
    parent_sha = ref["object"]["sha"]
    base_tree_sha = api("GET", f"git/commits/{parent_sha}")["tree"]["sha"]
    print(f"远程 HEAD: {parent_sha[:12]}")

    result = git("ls-tree", "-r", "main", "--name-only")
    files = [f for f in result.stdout.strip().split("\n") if f]
    print(f"本地文件数: {len(files)}")

    tree_items = []
    for f in files:
        content = git("show", f"main:{f}").stdout
        b64 = base64.b64encode(content.encode()).decode()
        blob = api("POST", "git/blobs", {"content": b64, "encoding": "base64"})
        mode = "100755" if f.startswith("hooks/") or f.endswith(".sh") else "100644"
        tree_items.append({"path": f, "mode": mode, "type": "blob", "sha": blob["sha"]})

    new_tree = api("POST", "git/trees", {"base_tree": base_tree_sha, "tree": tree_items})
    print(f"新 tree: {new_tree['sha'][:12]}")

    msg = git("log", "main", "-1", "--format=%s%n%n%b").stdout.strip() or "Update"
    commit = api("POST", "git/commits", {
        "message": msg,
        "author": {"name": "Bigheadh", "email": "821036508@qq.com"},
        "tree": new_tree["sha"],
        "parents": [parent_sha]
    })
    print(f"新 commit: {commit['sha'][:12]}")

    ref = api("PATCH", "git/refs/heads/main", {"sha": commit["sha"], "force": True})
    print(f"✅ 推送成功: {ref['ref']} -> {commit['sha'][:12]}")

if __name__ == "__main__":
    main()
