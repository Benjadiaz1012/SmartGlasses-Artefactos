
param(
    [switch]$Local
)

$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$Python = ".\.venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    throw "No se encontro el entorno virtual .venv"
}

if (-not (Test-Path ".env")) {
    throw "No se encontro el archivo .env"
}

$BindAddress = "0.0.0.0"

if ($Local) {
    $BindAddress = "127.0.0.1"
}

Write-Host "Iniciando Smart Glasses API..."
Write-Host "Servidor: $BindAddress"
Write-Host "Puerto: 8000"

& $Python -m uvicorn app:app --host $BindAddress --port 8000
