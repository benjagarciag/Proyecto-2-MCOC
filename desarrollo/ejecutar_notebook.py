"""Ejecutar el cuaderno completo con el entorno del proyecto y guardar salidas."""
from pathlib import Path
import os
import nbformat
from nbclient import NotebookClient

root = Path(__file__).resolve().parents[1]
os.environ['JUPYTER_PATH'] = str(root / '.venv/share/jupyter')
os.environ['JUPYTER_RUNTIME_DIR'] = str(root / '.venv/cache/jupyter')
os.environ['IPYTHONDIR'] = str(root / '.venv/cache/ipython')
os.environ['MPLCONFIGDIR'] = str(root / '.venv/cache/matplotlib')
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
p = root / 'documentacion/explicacion_solver_1d.ipynb'
nb = nbformat.read(p, as_version=4)
NotebookClient(nb, timeout=90, kernel_name='python3', resources={'metadata': {'path': str(root)}}).execute()
nbformat.write(nb, p)
print('Cuaderno ejecutado y guardado sin errores.')
