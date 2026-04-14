.PHONY: help orbit-snapshot audit audit-strict

help:
	@echo "Targets:"
	@echo "  make orbit-snapshot  - git status + behind/ahead + submodule gitlink (OIS)"
	@echo "  make audit           - uv export + pip-audit (OSV, interim ignore) + bandit"
	@echo "  make audit-strict    - uv export + pip-audit (OSV, NO ignore; may exit 1)"

orbit-snapshot:
	@bash scripts/oissnapshot.sh

audit:
	uv export --all-groups --format requirements.txt --no-hashes -o /tmp/python-craft-reqs.txt
	uv tool run pip-audit -r /tmp/python-craft-reqs.txt --skip-editable -s osv \
		--ignore-vuln CVE-2025-69872
	uv tool run bandit -r src/craft -ll -f txt

audit-strict:
	uv export --all-groups --format requirements.txt --no-hashes -o /tmp/python-craft-reqs.txt
	uv tool run pip-audit -r /tmp/python-craft-reqs.txt --skip-editable -s osv -f markdown
