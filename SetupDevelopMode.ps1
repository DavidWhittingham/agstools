. ..\buildtools\build_func.ps1

Set-PythonPath @("..\agsadmin\Source", "..\arcpyext\Source", "..\buildtools")

Set-Location "./Source"

Invoke-Expression "python.exe setup.py develop"