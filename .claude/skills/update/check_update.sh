#!/bin/bash
# ROSE Update Checker
# Lightweight script to check if GitHub has system file updates.
# Outputs structured key:value lines for Claude to parse.

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$REPO_ROOT" ]; then
    echo "STATUS:error"
    echo "MSG:Not in a git repository"
    exit 0
fi

cd "$REPO_ROOT"

# Verify origin remote exists
REMOTE_URL=$(git remote get-url origin 2>/dev/null)
if [ -z "$REMOTE_URL" ]; then
    echo "STATUS:error"
    echo "MSG:No origin remote configured"
    exit 0
fi

# Fetch with timeout (5 seconds), suppress output
timeout 5 git fetch origin 2>/dev/null
if [ $? -ne 0 ]; then
    echo "STATUS:skip"
    echo "MSG:Network unavailable or fetch timed out"
    exit 0
fi

# Check if origin/main exists
if ! git rev-parse origin/main >/dev/null 2>&1; then
    echo "STATUS:skip"
    echo "MSG:No origin/main branch found"
    exit 0
fi

# Get changed SYSTEM files only (not library/, not user config)
CHANGED=$(git diff --name-only HEAD..origin/main -- \
    .claude/commands/ \
    .claude/skills/ \
    .claude/changelog/ \
    CLAUDE.md \
    README.md \
    README-zh.md \
    ROADMAP.md \
    2>/dev/null)

if [ -z "$CHANGED" ]; then
    echo "STATUS:up-to-date"
    exit 0
fi

COUNT=$(echo "$CHANGED" | wc -l | tr -d ' ')

# Extract version numbers from CLAUDE.md for comparison (macOS-compatible, no -P flag)
LOCAL_VER=$(sed -n 's/.*当前版本: v\([0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\).*/\1/p' CLAUDE.md 2>/dev/null)
LOCAL_VER=${LOCAL_VER:-unknown}
REMOTE_VER=$(git show origin/main:CLAUDE.md 2>/dev/null | sed -n 's/.*当前版本: v\([0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\).*/\1/p' 2>/dev/null)
REMOTE_VER=${REMOTE_VER:-unknown}

echo "STATUS:updates-available"
echo "COUNT:$COUNT"
echo "LOCAL_VERSION:$LOCAL_VER"
echo "REMOTE_VERSION:$REMOTE_VER"
echo "FILES:"
echo "$CHANGED"
