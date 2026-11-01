$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$python = 'E:\KhoaLuanTotNghiep\PaddleOCR_Field_Improvement\.venv\Scripts\python.exe'
$server = Join-Path $PSScriptRoot 'serve_review.py'
$port = 8768
$url = "http://127.0.0.1:$port/automatic_review/review_queue.html"
$listener = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue
if (-not $listener) {
    Start-Process -FilePath $python -ArgumentList @($server, '--port', "$port") -WorkingDirectory $root -WindowStyle Hidden | Out-Null
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Milliseconds 300
        try { Invoke-WebRequest -Uri "http://127.0.0.1:$port/api/annotations" -TimeoutSec 1 | Out-Null; break } catch {}
    }
}
try {
    Invoke-WebRequest -Uri "http://127.0.0.1:$port/automatic_review/review_queue.html" -TimeoutSec 3 | Out-Null
} catch {
    throw "Không mở được web rà soát trên cổng $port. Kiểm tra máy chủ hoặc cổng đang dùng."
}
Start-Process $url
Write-Host "Web rà soát: $url"
Write-Host "Tiến độ được lưu trong: $PSScriptRoot\manual_review_progress.json"
