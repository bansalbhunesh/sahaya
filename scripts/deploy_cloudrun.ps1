# Deploys Sahaya to Cloud Run from source. Run AFTER: gcloud auth login + project set.
param(
    [string]$ProjectId = $(gcloud config get-value project 2>$null),
    [string]$Region = "asia-south1"
)

$gcloud = "C:\Users\bhune\gcloud-sdk\google-cloud-sdk\bin\gcloud.cmd"
if (-not (Test-Path $gcloud)) { $gcloud = "gcloud" }

if (-not $env:GOOGLE_API_KEY -or -not $env:MDB_MCP_CONNECTION_STRING) {
    Write-Error "Set GOOGLE_API_KEY and MDB_MCP_CONNECTION_STRING in this shell first"; exit 1
}

& $gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com --project $ProjectId

Set-Location "$PSScriptRoot\.."
& $gcloud run deploy sahaya `
    --source . `
    --project $ProjectId `
    --region $Region `
    --allow-unauthenticated `
    --memory 1Gi `
    --min-instances 1 `
    --set-env-vars "GOOGLE_API_KEY=$env:GOOGLE_API_KEY,MDB_MCP_CONNECTION_STRING=$env:MDB_MCP_CONNECTION_STRING,SAHAYA_MODEL=gemini-3-flash-preview"
