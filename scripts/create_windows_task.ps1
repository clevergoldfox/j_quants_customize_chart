param(
  [string]$TaskName = "JQuants_MT4_Stock_Update_0700",
  [string]$ProjectDir = ""
)

if ($ProjectDir -eq "") {
  $ProjectDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
}

$BatPath = Join-Path $ProjectDir "scripts\update_stock_data.bat"

$Action = New-ScheduledTaskAction -Execute $BatPath -WorkingDirectory $ProjectDir
$Trigger = New-ScheduledTaskTrigger -Daily -At 7:00AM
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Update J-Quants stock data for MT4 every morning at 07:00" -Force

Write-Host "Created/updated scheduled task: $TaskName"
