#!/usr/bin/env bash
# .describe( — initialise the brand-system repository.
# Run once, from this folder:   bash init-repo.sh
set -euo pipefail
cd "$(dirname "$0")"

command -v git >/dev/null || { echo "git is not installed."; exit 1; }

if [ -d .git ]; then
  echo "Already a git repository — nothing to initialise."
else
  git init -b main
  echo "Initialised on branch 'main'."
fi

git config user.name  >/dev/null 2>&1 || git config user.name  "Wafa'a Al-Hayek"
git config user.email >/dev/null 2>&1 || git config user.email "info@describe.team"

git add -A
git commit -m "Brand system: locked 5a mark, geometry primitives, typography" -m \
"Geometry (Role 02): astrolabe.py generator, 46 SVG plates in eight families, 92 PNGs, derivation notes. Three system rules enforced as guards in code rather than documented as conventions.

Typography (Role 04): Fraunces for Latin display, Amiri for Arabic display with Reem Kufi for labels, Readex Pro and Vazirmatn for interface Latin and Arabic. Decisions measured live in the specimen rather than asserted. Mono restricted to numerals and short labels.

Brandkit: ten production logo variants at v1.0, generator and QA script.

Open: the wordmark is undrawn, three Arabic tokens are placeholders pending measurement, and site/ carries figures that do not reconcile. See README."

echo
echo "Committed."
git --no-pager log --oneline -1
cat <<'NEXT'

Next — create the repo on GitHub, then connect and push:

  1. Create a PRIVATE repo at https://github.com/new
     Owner: describedatateam   Name: describe-brand-system
     Do NOT add a README, .gitignore or licence — this folder has them.

  2. Then run:

     git remote add origin https://github.com/describedatateam/describe-brand-system.git
     git push -u origin main

NEXT
