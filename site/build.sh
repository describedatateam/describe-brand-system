#!/bin/sh
# Assemble the public site into site/dist for Cloudflare Pages.
# Only what visitors should see is copied: the analysis code and notes in
# site/proof/ stay in the repository and are never published.
set -eu
cd "$(dirname "$0")"
rm -rf dist
mkdir -p dist
cp index.html dist/
cp -R public/. dist/
echo "Built site/dist:"
ls -1 dist
