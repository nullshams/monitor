# نصب Agent مانیتورینگ در ویندوز (PowerShell)
$AgentPath = "$env:ProgramData\SysAgent"
$Python = "python"
$ServerURL = Read-Host "🌐 Enter the server URL (e.g., http://192.168.1.100:8000)"

Write-Output "📁 Creating Agent folder at $AgentPath..."
New-Item -Path $AgentPath -ItemType Directory -Force | Out-Null
Copy-Item -Path ".\agent.py" -Destination "$AgentPath\agent.py" -Force

Write-Output "📦 Creating virtual environment..."
cd $AgentPath
& $Python -m venv venv

Write-Output "📦 Installing dependencies..."
& "$AgentPath\venv\Scripts\pip.exe" install --upgrade pip
& "$AgentPath\venv\Scripts\pip.exe" install psutil requests

# ایجاد سرویس ویندوز (نیازمند اجرای Admin)
$ServiceScript = @"
`"$AgentPath\venv\Scripts\python.exe`" `"$AgentPath\agent.py`"
"@

sc.exe create "SysAgent" binPath= "$ServiceScript" start= auto
sc.exe description "SysAgent" "System Monitoring Agent - reports to $ServerURL"
sc.exe start "SysAgent"

Write-Output "✅ Agent installed and running."
