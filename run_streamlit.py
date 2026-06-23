import asyncio
import sys

from streamlit.web import cli as streamlit_cli


if hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

sys.argv = [
    "streamlit",
    "run",
    "app.py",
    "--server.port",
    "8501",
    "--server.address",
    "127.0.0.1",
    "--server.headless",
    "true",
    "--browser.gatherUsageStats",
    "false",
]

raise SystemExit(streamlit_cli.main())
