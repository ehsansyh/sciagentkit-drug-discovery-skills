#!/usr/bin/env bash
set -euo pipefail

# Remote installer. Edit SCIAGENTKIT_REPO after publishing.
# Example:
#   curl -fsSL https://raw.githubusercontent.com/ehsansyh/sciagentkit-drug-discovery-skills/main/scripts/install_from_github.sh | bash -s -- --full --agents

REPO_URL="${SCIAGENTKIT_REPO:-https://github.com/ehsansyh/sciagentkit-drug-discovery-skills.git}"
INSTALL_DIR="${SCIAGENTKIT_DIR:-$HOME/sciagentkit}"
BRANCH="${SCIAGENTKIT_BRANCH:-main}"

# Override the default repo by exporting SCIAGENTKIT_REPO before running.

if ! command -v git >/dev/null 2>&1; then
  echo "git is required for remote installation. Install git first."
  exit 1
fi

if [[ -d "$INSTALL_DIR/.git" ]]; then
  echo "Updating existing SciAgentKit checkout at $INSTALL_DIR"
  git -C "$INSTALL_DIR" pull --ff-only
else
  echo "Cloning SciAgentKit into $INSTALL_DIR"
  git clone --branch "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"
bash scripts/install.sh "$@"
