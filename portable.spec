# PyInstaller one-folder bundle. Build with build_portable.bat on Windows.
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

root = Path(SPECPATH)
sympy_datas, sympy_binaries, sympy_hidden = collect_all("sympy")
datas = sympy_datas + [(str(root / "frontend" / "dist"), "frontend/dist")]

a = Analysis(
    [str(root / "backend" / "run_app.py")],
    pathex=[str(root / "backend")],
    binaries=sympy_binaries,
    datas=datas,
    hiddenimports=sympy_hidden,
    hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=["IPython", "matplotlib", "numpy", "scipy"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="EDOLab", console=True)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="EDOLab")
