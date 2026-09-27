' Lanzador Silencioso sin Consola CMD
' PROJ-008: Excel Analytics Studio
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.Run "cmd /c INICIAR_APP.bat", 0, False
Set WshShell = Nothing
