#!/bin/bash
# Restores the working folders the build scripts expect (/home/claude/cozy and /home/claude/wk).
set -e
R=$(cd "$(dirname "$0")" && pwd)
mkdir -p /home/claude/cozy /home/claude/wk/music /home/claude/wk/pages /home/claude/wk/posts /home/claude/wk/color
cp -r $R/assets/books/* /home/claude/cozy/
cp $R/assets/work/book.json $R/assets/work/item_*.json /home/claude/wk/
for f in $R/assets/music/*.m4a; do ffmpeg -loglevel error -y -i "$f" "/home/claude/wk/music/$(basename "${f%.m4a}").wav"; done
python3 -c "import docx" 2>/dev/null || true
echo "setup done: $(ls /home/claude/wk/music | wc -l) tracks"
