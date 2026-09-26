# .describe( — initialise the brand-system repository
#
# Run once, from this folder, in PowerShell:
#     .\init-repo.ps1
#
# It creates the local git repository and makes the first commit. It does NOT
# create anything on GitHub and does not push — the last step prints what to
# run for that.

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Host "git is not installed. Get it from https://git-scm.com/download/win" -ForegroundColor Red
  exit 1
}

if (Test-Path ".git") {
  Write-Host "This folder is already a git repository — nothing to initialise." -ForegroundColor Yellow
} else {
  git init -b main
  Write-Host "Initialised on branch 'main'."
}

# Set the author on this repo only, so it doesn't touch any global config.
if (-not (git config user.name)) {
  git config user.name  "Wafa'a Al-Hayek"
  git config user.email "info@describe.team"
}

git add -A
git commit -m "Brand system: locked 5a mark, geometry primitives, typography" `
           -m "Geometry (Role 02): astrolabe.py generator, 46 SVG plates in eight families, 92 PNGs, derivation notes. Three system rules enforced as guards in code rather than documented as conventions.

Typography (Role 04): Fraunces for Latin display, Amiri for Arabic display with Reem Kufi for labels, Readex Pro and Vazirmatn for interface Latin and Arabic. Decisions measured live in the specimen rather than asserted. Mono restricted to numerals and short labels.

Brandkit: ten production logo variants at v1.0, generator and QA script.

Open: the wordmark is undrawn, three Arabic tokens are placeholders pending measurement, and site/ carries figures that do not reconcile. See README."

Write-Host ""
Write-Host "Committed." -ForegroundColor Green
git --no-pager log --oneline -1
Write-Host ""
Write-Host "Next — create the repo on GitHub, then connect and push:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. Create a PRIVATE repo at https://github.com/new"
Write-Host "     Owner: describedatateam   Name: describe-brand-system"
Write-Host "     Do NOT add a README, .gitignore or licence — this folder has them."
Write-Host ""
Write-Host "  2. Then run:"
Write-Host ""
Write-Host "     git remote add origin https://github.com/describedatateam/describe-brand-system.git"
Write-Host "     git push -u origin main"
Write-Host ""
