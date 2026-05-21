.PHONY: help gen changelog install-hook

help: ## 显示帮助
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

gen: ## 从 git diff 自动生成变更记录骨架
	python3 scripts/gen-changelog.py

gen-staged: ## 从 git diff --staged 生成变更记录
	python3 scripts/gen-changelog.py --staged

gen-last: ## 从最近一次 commit 生成变更记录
	python3 scripts/gen-changelog.py --commit-range HEAD~1..HEAD

changelog: gen ## 同 gen

install-hook: ## 安装 post-commit 钩子到当前 Git 仓库
	@cd .git/hooks && ln -sf ../../hooks/post-commit post-commit && echo "✅ 钩子已安装到 $(shell git rev-parse --show-toplevel)"

view: ## 查看最新一条变更记录
	@ls -t changelog/*.md 2>/dev/null | head -1 | xargs cat || echo "暂无变更记录"
