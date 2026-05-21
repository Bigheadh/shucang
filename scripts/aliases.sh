# 术藏 Shell 别名
# 在 ~/.bashrc 或 ~/.zshrc 中 source 此文件:
#   source /root/shucang/scripts/aliases.sh

alias changelog='python3 /root/shucang/scripts/gen-changelog.py'
alias changelog-staged='python3 /root/shucang/scripts/gen-changelog.py --staged'
alias changelog-last='python3 /root/shucang/scripts/gen-changelog.py --commit-range HEAD~1..HEAD'
alias changelog-view='ls -t changelog/*.md 2>/dev/null | head -1 | xargs cat'

# 安装 gitmessage 模板
install-gitmessage() {
    git config commit.template /root/shucang/hooks/gitmessage
    echo "✅ Git 提交模板已安装到当前仓库"
}

# 安装 post-commit 钩子
install-changelog-hook() {
    ln -sf /root/shucang/hooks/post-commit .git/hooks/post-commit
    echo "✅ post-commit 钩子已安装到 $(pwd)"
}
