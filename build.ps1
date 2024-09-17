./pax export
$scriptDir = ".\scripts\dev\build_server"
& "$scriptDir\.venv\Scripts\activate"
py "$scriptDir/build_server.py" ./.out/Crumbs.zip ./.out/Crumbs-Server.zip