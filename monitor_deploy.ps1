# Versión Windows (PowerShell) del monitor de despliegue.
# Uso:  .\monitor_deploy.ps1 -Url http://TU-AMBIENTE.elasticbeanstalk.com
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
