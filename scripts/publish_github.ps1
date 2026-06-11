# Creates the public GitHub repo and pushes main. Requires $env:GITHUB_PAT (repo scope).
param([string]$RepoName = "sahaya")

if (-not $env:GITHUB_PAT) { Write-Error "Set GITHUB_PAT first"; exit 1 }
$headers = @{ Authorization = "token $env:GITHUB_PAT"; Accept = "application/vnd.github+json" }

$user = (Invoke-RestMethod -Headers $headers -Uri "https://api.github.com/user").login
Write-Host "Authenticated as $user"

$body = @{ name = $RepoName; description = "Autonomous flood-response ops agent - Gemini 3 + Google Cloud Agent Builder + MongoDB MCP (Rapid Agent Hackathon)"; private = $false } | ConvertTo-Json
try {
    Invoke-RestMethod -Method Post -Headers $headers -Uri "https://api.github.com/user/repos" -Body $body -ContentType "application/json" | Out-Null
    Write-Host "Repo created"
} catch { Write-Host "Repo may already exist: $_" }

Set-Location "$PSScriptRoot\.."
git remote remove origin 2>$null
git remote add origin "https://$user`:$env:GITHUB_PAT@github.com/$user/$RepoName.git"
git push -u origin main
git remote set-url origin "https://github.com/$user/$RepoName.git"  # scrub token from config
Write-Host "Pushed: https://github.com/$user/$RepoName"
