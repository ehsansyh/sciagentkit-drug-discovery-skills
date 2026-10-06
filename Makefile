.PHONY: install install-full install-dev install-agents test demo doctor mcp docker-build clean

install:
	bash scripts/install.sh --core

install-full:
	bash scripts/install.sh --full --agents --external

install-dev:
	bash scripts/install.sh --dev --agents --external

install-agents:
	python scripts/setup_agents.py --root "$$(pwd)" --env-name sciagentkit --use-conda 1

test:
	pytest -q

demo:
	sciagent demo --out runs/make_demo

doctor:
	sciagent doctor

mcp:
	python -m sciagentkit.servers.rdkit_server

docker-build:
	docker build -t sciagentkit:latest .

clean:
	rm -rf runs .pytest_cache **/__pycache__ .ruff_cache build dist *.egg-info
