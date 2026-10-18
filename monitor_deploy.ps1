# Monitor de despliegue: consulta /ping cada segundo y registra hora, versión y código HTTP.
# Uso: .\monitor_deploy.ps1 -Url <url-del-ambiente>
param([Parameter(Mandatory = $true)][string]$Url)
while ($true) {
    $hora = Get-Date -Format "HH:mm:ss"
    try {
        $r = Invoke-WebRequest -Uri "$Url/ping" -TimeoutSec 3 -UseBasicParsing
        Write-Host "$hora | $($r.Content) | HTTP $($r.StatusCode)"
    } catch {
        Write-Host "$hora | ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
    Start-Sleep -Seconds 1
}
