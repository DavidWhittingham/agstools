Function Set-PythonPath ([string[]] $paths) {
    [string[]] $resolvedPaths = @()
    foreach ($path in $paths) {
        $resolvedPaths+= [System.IO.Path]::GetFullPath((Join-Path (pwd) $path))
    }
    $env:PYTHONPATH=$resolvedPaths -join ";"
}

Function Build-PythonModule ([string] $path, [string] $format = "egg", [bool] $dev = $false) {
    [string] $oldPath = (Get-Location).Path
    [string] $buildCommand = "python.exe setup.py "
    
    Set-Location $path
    
    if ($format -eq "egg") {
        $buildCommand = $buildCommand + "bdist_egg"
    } else {
        $buildCommand = $buildCommand + "bdist --formats=" + $format
    }

    if ($dev -eq $true) {
        $datestamp = Get-Date -format "yyyyMMdd HHmmss"
        $buildCommand = $buildCommand + " egg_info -b .dev" + $datestamp
    }
    
    Invoke-Expression $buildCommand

    Remove-Item ./*.egg-info -recurse
    Remove-Item ./build -recurse

    Set-Location $oldPath
}