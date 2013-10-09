param (
    [string]$format = "egg",
    [switch]$dev = $false
)

. ..\buildtools\build_func.ps1

Set-PythonPath @("..\agsadmin\Source", "..\arcpyext\Source", "..\buildtools")

Build-PythonModule "./Source" $format $dev