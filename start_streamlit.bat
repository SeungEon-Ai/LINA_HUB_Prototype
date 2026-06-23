@echo off
cd /d "%~dp0"
"C:\Users\seungeon99\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" run_streamlit.py > work\streamlit.stdout.log 2> work\streamlit.stderr.log
