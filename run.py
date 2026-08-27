import os
import sys
import subprocess
import time
import webbrowser

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "frontend")

    print("=" * 70)
    print("  Starting AI-Powered Enterprise Data Analytics Platform")
    print("=" * 70)
    print(f"Project Root: {root_dir}")

    creation_flag = subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0

    # 1. Start Backend
    print("\n[1/2] Launching Backend API (FastAPI) on http://localhost:8000 ...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=backend_dir,
        creationflags=creation_flag
    )

    time.sleep(2)

    # 2. Start Frontend
    print("[2/2] Launching Frontend UI (Next.js) on http://localhost:3000 ...")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=frontend_dir,
        creationflags=creation_flag
    )

    time.sleep(3)

    print("\n" + "=" * 70)
    print("  Both Backend (8000) and Frontend (3000) have been launched!")
    print("  Opening browser to http://localhost:3000 ...")
    print("=" * 70 + "\n")

    try:
        webbrowser.open("http://localhost:3000")
    except Exception:
        pass

    print("Press Ctrl+C in this window or close the server windows to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
        backend_proc.terminate()
        frontend_proc.terminate()

if __name__ == "__main__":
    main()
