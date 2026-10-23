"""Regression tests for the approved scoped accessible-blue treatment."""
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative):
    return json.loads((ROOT / relative).read_text())


def walk(value):
    if isinstance(value, dict):
        if 'type' in value:
            yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def luminance(color):
    channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in channels]
    return sum(v * weight for v, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


class AccessibleColorTreatmentTests(unittest.TestCase):
    def test_accessible_token_has_normal_text_contrast_without_changing_primary(self):
        colors = read('design/tokens/tokens.json')['color']
        self.assertEqual('#3B82F6', colors['primary'])
        self.assertEqual('#2563EB', colors['accessiblePrimary'])
        for background in ('background', 'surface', 'primarySurface'):
            with self.subTest(background=background):
                a, b = sorted((luminance(colors['accessiblePrimary']), luminance(colors[background])))
                self.assertGreaterEqual((b + 0.05) / (a + 0.05), 4.5)

    def test_registry_allowlist_is_exact_and_does_not_create_control_families(self):
        components = read('design/libraries/primevue.library.json')['components']
        treated = {name for name, definition in components.items()
                   if 'colorTreatments' in definition['penpotTemplate']}
        self.assertEqual({'Button', 'Tag', 'SelectButton'}, treated)
        for name in treated:
            self.assertEqual(['accessible-blue'], components[name]['penpotTemplate']['colorTreatments'])

    def test_scope_preserves_disabled_secondary_and_danger_semantics(self):
        paths = list((ROOT / 'design/components').glob('*.component.json'))
        paths += list((ROOT / 'design/pages/interval-repetition').glob('*.page.json'))
        treated = 0
        for path in paths:
            for node in walk(json.loads(path.read_text())):
                if node.get('design', {}).get('colorTreatment') != 'accessible-blue':
                    continue
                treated += 1
                self.assertEqual('library-component', node['type'])
                self.assertIn(node['component'], ('Button', 'Tag', 'SelectButton'))
                props = node.get('props', {})
                self.assertIsNot(True, props.get('disabled'))
                if node['component'] == 'Button':
                    self.assertEqual('primary', props['severity'])
        self.assertGreater(treated, 0)
        homepage = list(walk(read('design/pages/home/homepage.page.json')))
        treated = [n for n in homepage if n.get('design', {}).get('colorTreatment') == 'accessible-blue']
        self.assertEqual(5, len(treated))
        self.assertEqual(['Button'] * 4 + ['Tag'], sorted(n['component'] for n in treated))


if __name__ == '__main__':
    unittest.main()