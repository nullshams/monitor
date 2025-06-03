Write-Output "🧹 Removing SysAgent..."

# توقف و حذف سرویس
sc.exe stop "SysAgent"
sc.exe delete "SysAgent"

# حذف فایل‌ها
$AgentPath = "$env:ProgramData\SysAgent"
Remove-Item -Path $AgentPath -Recurse -Force

Write-Output "✅ Agent removed successfully."

