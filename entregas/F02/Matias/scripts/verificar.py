"""Controles independientes sobre salidas y salvaguardas de la agregación."""
from copy import deepcopy
import csv
from pathlib import Path
import re
from tempfile import TemporaryDirectory
import unittest
from xml.etree import ElementTree

from agregar import audit_rows, close, compatible, fingerprint, inputs, read, run, self_test
from insumos import ROOT, provenance, source_tree
from preparar import CURRENT


def csv_rows(path):
    with path.open(encoding='utf-8-sig', newline='') as file:
        return list(csv.DictReader(file))


class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sources = source_tree()
        cls.sources = sources.__enter__()
        cls.addClassCleanup(sources.__exit__, None, None, None)

    def setUp(self):
        self.catalog, self.plans = inputs(self.sources)
        self.matrix = read(self.sources / CURRENT)

    def test_frozen_inputs_match_manifest(self):
        manifest = provenance()
        for row in manifest['archivos']:
            self.assertEqual(fingerprint(self.sources / row['ruta']), row['sha256'], row['ruta'])
        for path in ('datos/hidratacion/source_terms.txt', 'Enunciados e Instrucciones/source_terms.txt'):
            self.assertEqual(fingerprint(self.sources / path), manifest['adjunto_sha256'])

    def test_fragment_reconciles_every_published_run(self):
        for row in self.matrix['corridas']:
            path = (self.sources / CURRENT).with_stem(f'unica_15kw_12c_{row["curva"]}_{row["clima"]}')
            fragment, = read(path)['corridas']
            for key in ('curva', 'clima', 'peso', 'horizonte_h', 'excede_70', 'excede_20',
                        'pico_no_resuelto', 'Tmax', 'DeltaTmax', 'base_336h'):
                self.assertEqual(fragment[key], row[key])

    def test_csv_reconciles_all_24_current_runs(self):
        actual = csv_rows(ROOT / 'tablas/M4_por_escenario.csv')
        comparison = csv_rows(self.sources / 'resultados/controles_12c/escenarios_malla_0.5_paso900.csv')
        published = {(r['curva'], r['clima']): r for r in comparison if r['caso'] == 'unica_15kw_12c'}
        self.assertEqual(len(actual), len(published))
        for row in actual:
            pair = published[(row['curva'], row['clima'])]
            for key in ('Tmax_C', 'DeltaTmax_K'):
                self.assertTrue(close(float(row[key]), float(pair[key])))
            self.assertEqual(float(row['DeltaTmax_h']), float(pair['hora_DeltaTmax']))
        self.assertEqual(max(float(row['DeltaTmax_h']) for row in actual if close(float(row['DeltaTmax_K']), 17.368140448050845)), 380)

    def test_union_and_exact_boundary(self):
        self_test()

    def test_incomplete_duplicate_weight_and_nonsimultaneous_max_rejected(self):
        for condition in ('incompleta', 'duplicado', 'peso', 'diferencial'):
            with self.subTest(condition=condition):
                d = deepcopy(self.matrix)
                if condition == 'incompleta':
                    d['corridas'].pop()
                elif condition == 'duplicado':
                    d['corridas'][-1] = d['corridas'][0]
                elif condition == 'peso':
                    d['corridas'][0]['peso'] *= 2
                else:
                    d['corridas'][0]['DeltaTmax']['valor'] += 1
                with self.assertRaises(ValueError):
                    audit_rows('Única', d, self.catalog, 'prueba')

    def test_incompatible_physics_or_mesh_rejected(self):
        d = deepcopy(self.matrix)
        d['enfriamiento']['tope_W'] = 12000
        with self.assertRaises(ValueError):
            compatible('unica', d, self.matrix, self.plans)
        d = deepcopy(self.matrix)
        d['lado_m'] = 0.25
        with self.assertRaises(ValueError):
            compatible('unica', d, self.matrix, self.plans)

    def test_repeat_aggregation_and_missing_plans_are_blank(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp)
            run(self.sources, path)
            for rerun in path.glob('*.csv'):
                self.assertEqual(rerun.read_bytes(), (ROOT / 'tablas' / rerun.name).read_bytes())
            table = csv_rows(path / 'M4_comparacion.csv')
            self.assertEqual([r['P_f'] for r in table], ['0.0', '', '', ''])

    def test_figures_parse(self):
        paths = sorted((ROOT / 'figuras').glob('*.svg'))
        self.assertEqual(len(paths), 10)
        for path in paths:
            self.assertTrue(ElementTree.parse(path).getroot().tag.endswith('svg'))
            self.assertEqual(path.with_suffix('.png').read_bytes()[:8], b'\x89PNG\r\n\x1a\n')

    def test_catalog_and_generated_inputs_agree(self):
        rows = csv_rows(ROOT / 'tablas/M2_catalogo_24.csv')
        self.assertEqual(len(rows), 24)
        self.assertEqual({(r['curva'], r['clima']): float(r['peso_conjunto']) for r in rows}, self.catalog)
        self.assertEqual(len(csv_rows(ROOT / 'tablas/M1_curvas.csv')), 8)
        self.assertEqual(len(csv_rows(ROOT / 'tablas/M2_clima_horario.csv')), 3 * 673)

    def test_relative_document_links(self):
        for path in ROOT.glob('*.md'):
            links = re.findall(r'\]\(([^ )]+)\)', path.read_text(encoding='utf-8'))
            for target in links:
                if not target.startswith(('https://', '#')):
                    self.assertTrue((path.parent / target).exists(), f'{path.name}: {target}')


if __name__ == '__main__':
    unittest.main(verbosity=2)
