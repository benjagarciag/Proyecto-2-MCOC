"""Materializa los archivos oficiales del commit auditado en una carpeta temporal."""
from contextlib import contextmanager
from io import BytesIO
import json
from pathlib import Path
from subprocess import run
import tarfile
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'insumos/procedencia.json'


def provenance():
    return json.loads(MANIFEST.read_bytes())


@contextmanager
def source_tree():
    manifest = provenance()
    commit = manifest['commit_auditado']
    paths = [item['ruta'] for item in manifest['archivos']]
    detected = run(['git', '-C', str(ROOT), 'rev-parse', '--show-toplevel'],
                   capture_output=True, encoding='utf-8')
    if detected.returncode:
        raise RuntimeError('Ejecuta los scripts desde una copia Git del repositorio.')
    repo = detected.stdout.rstrip('\r\n')
    with TemporaryDirectory(prefix='f02-matias-') as temp:
        root = Path(temp)
        # Los lotes mantienen cada llamada bajo el límite de argumentos de Windows.
        for first in range(0, len(paths), 60):
            command = ['git', '-C', repo, 'archive', '--format=tar', commit,
                       '--', *paths[first:first + 60]]
            result = run(command, capture_output=True)
            if result.returncode:
                detail = result.stderr.decode(errors='replace').strip()
                raise RuntimeError(f'Se necesita el commit {commit} en un clon Git con historial. {detail}')
            with tarfile.open(fileobj=BytesIO(result.stdout), mode='r:') as archive:
                archive.extractall(root, filter='data')
        yield root
