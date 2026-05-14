#!/bin/sh
set -e

repo_root=$(git rev-parse --show-toplevel 2>/dev/null)
hooks_path=$(git config --get core.hooksPath || true)

if [ -n "$hooks_path" ]; then
  case "$hooks_path" in
    /*) hooks_dir="$hooks_path" ;;
    *) hooks_dir="$repo_root/$hooks_path" ;;
  esac
else
  hooks_dir="$repo_root/.git/hooks"
fi

mkdir -p "$hooks_dir"

for hook in pre-commit post-commit; do
  source_hook="$repo_root/scripts/hooks/$hook"
  target_hook="$hooks_dir/$hook"

  if [ ! -f "$source_hook" ]; then
    echo "Missing hook template: $source_hook" >&2
    exit 1
  fi

  cp "$source_hook" "$target_hook"
  chmod +x "$target_hook"
  echo "Installed $hook"
done
