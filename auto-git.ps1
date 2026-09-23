$folder = Get-Location

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $folder
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

$action = {
    Start-Sleep -Seconds 3

    git add .
    
    $status = git status --porcelain

    if ($status) {
        $time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

        git commit -m "Auto commit: $time"
        git push origin main

        Write-Host "Changes pushed to GitHub: $time"
    }
}

Register-ObjectEvent $watcher "Changed" -Action $action
Register-ObjectEvent $watcher "Created" -Action $action
Register-ObjectEvent $watcher "Deleted" -Action $action
Register-ObjectEvent $watcher "Renamed" -Action $action

Write-Host "Auto Git is running..."
Write-Host "Press Ctrl+C to stop."

while ($true) {
    Start-Sleep -Seconds 10
}