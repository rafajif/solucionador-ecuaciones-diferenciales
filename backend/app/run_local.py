"""Run the local app in one foreground process and open its browser when ready."""
from __future__ import annotations

import os
import getpass
import hashlib
import tempfile
import threading
import time
import webbrowser
from pathlib import Path

import uvicorn
from .main import app, project_root

HOST = "127.0.0.1"
PORT = 8000
URL = f"http://{HOST}:{PORT}"


class InstanceLock:
    def __init__(self, path: Path):
        self.path = path
        self.handle = None

    def acquire(self) -> bool:
        self.handle = self.path.open("a+b")
        self.handle.seek(0, os.SEEK_END)
        if self.handle.tell() == 0:
            self.handle.write(b"\0")
            self.handle.flush()
        self.handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except (OSError, BlockingIOError):
            self.handle.close()
            self.handle = None
            return False

    def release(self):
        if not self.handle:
            return
        try:
            self.handle.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        finally:
            self.handle.close()


def open_when_ready(server: uvicorn.Server):
    deadline = time.monotonic() + 25
    while time.monotonic() < deadline:
        if server.started:
            try:
                if not webbrowser.open(URL, new=2):
                    print(f"No se abrió el navegador automáticamente. Visita {URL}", flush=True)
            except webbrowser.Error as exc:
                print(f"No se pudo abrir el navegador: {exc}. Visita {URL}", flush=True)
            return
        if server.should_exit:
            return
        time.sleep(0.1)
    print("No se pudo confirmar que FastAPI esté disponible. Revisa los mensajes anteriores.", flush=True)


def main():
    user_key = hashlib.sha256(getpass.getuser().encode("utf-8")).hexdigest()[:12]
    lock = InstanceLock(Path(tempfile.gettempdir()) / f"edo-lab-{user_key}.lock")
    if not lock.acquire():
        print("EDO Lab ya está en ejecución. Abriendo la ventana existente.", flush=True)
        webbrowser.open(URL, new=2)
        return 0
    print("Iniciando EDO Lab en http://127.0.0.1:8000", flush=True)
    print("Esta ventana mantiene el servidor local. Presiona Ctrl+C para cerrar EDO Lab.", flush=True)
    server = uvicorn.Server(uvicorn.Config(app, host=HOST, port=PORT, log_level="warning", access_log=False))
    threading.Thread(target=open_when_ready, args=(server,), name="open-browser", daemon=True).start()
    try:
        server.run()
    except OSError as exc:
        print(f"No se pudo abrir el servidor local: {exc}", flush=True)
        return 1
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 1
        if code:
            print("Uvicorn no pudo iniciar. Comprueba si el puerto 8000 ya está ocupado.", flush=True)
        return code
    except KeyboardInterrupt:
        print("EDO Lab se cerró correctamente.", flush=True)
    finally:
        lock.release()
    if not server.started:
        print("FastAPI no pudo iniciar. Comprueba si el puerto 8000 está ocupado.", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    main()
