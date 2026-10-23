"""Approved specification contracts; does not certify browser behavior."""
import json
import unittest
from pathlib import Path

import penpot_conformance as audit

DESIGN = Path(__file__).resolve().parents[1] / 'design'


def page(name):
    return json.loads((DESIGN / 'pages/interval-repetition' / f'{name}.page.json').read_text())


def nodes(value):
    if isinstance(value, dict):
        if 'type' in value:
            yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


class IntervalRepetitionSpecTests(unittest.TestCase):
    def test_continue_saves_before_navigation(self):
        spec = page('category-setup')
        button = next(n for n in nodes(spec['children']) if n.get('props', {}).get('label') == 'Продолжить')
        self.assertEqual({'type': 'submit', 'name': 'saveInitialCategorySelection'}, button['action'])
        self.assertIn('Only after', spec['states']['saveSuccess'])
        self.assertIn('RepetitionDashboard', spec['states']['saveSuccess'])
        self.assertIn('never navigate on failure', spec['states']['saveFailure'])
        self.assertIn('saveInitialCategorySelection', spec['states']['saveFailure'])

    def test_details_defines_both_mutations_and_outcomes(self):
        spec = page('category-details')
        self.assertTrue({'selected', 'unselected', 'addOrRemoveSaving', 'addSuccess',
                         'removeSuccess', 'mutationFailure'}.issubset(spec['states']))
        self.assertIn('addCategory', spec['states']['unselected'])
        self.assertIn('removeCategory', spec['states']['selected'])
        self.assertIn('last confirmed selection', spec['states']['mutationFailure'])
        action = next(n for n in nodes(spec['children']) if n.get('name') == 'CategorySelectionAction')
        self.assertEqual('removeCategory', action['action']['name'])

    def test_review_progress_is_remaining_count_only(self):
        spec = page('review-session')
        self.assertFalse(any(n.get('component') == 'ProgressBar' for n in nodes(spec['children'])))
        label = next(n for n in nodes(spec['children']) if n.get('name') == 'ReviewProgressLabel')
        self.assertEqual('Осталось: 7', label['value'])

    def test_icon_only_navigation_has_explicit_accessible_name(self):
        registry = json.loads((DESIGN / 'libraries/primevue.library.json').read_text())
        self.assertEqual('string', registry['components']['Button']['props']['aria-label']['type'])
        checked = 0
        for path in (DESIGN / 'pages/interval-repetition').glob('*.page.json'):
            for node in nodes(json.loads(path.read_text())['children']):
                props = node.get('props', {})
                if node.get('component') == 'Button' and props.get('icon') in ('pi pi-arrow-left', 'pi pi-times') and not props.get('label'):
                    self.assertTrue(props.get('aria-label', '').strip(), path)
                    checked += 1
        self.assertGreater(checked, 0)

    def test_catalog_search_has_explicit_accessible_name(self):
        registry = json.loads((DESIGN / 'libraries/primevue.library.json').read_text())
        self.assertEqual({'type': 'string'},
                         registry['components']['InputText']['props']['aria-label'])
        search = page('category-catalog')['children'][1]['slots']['default'][0]
        self.assertEqual('InputText', search['component'])
        self.assertEqual('Поиск тем и специализаций', search['props']['aria-label'])
        self.assertEqual('Найти тему или специализацию', search['props']['placeholder'])

    def test_search_name_survives_resolution_without_visual_label_claim(self):
        manifest = audit.build_manifest()
        search = next(n for n in audit.flatten(manifest['scopes']['CategoryCatalog']['nodes'])
                      if n.get('family') == 'Library/PrimeVue/InputText')
        self.assertEqual('Поиск тем и специализаций', search['props']['aria-label'])
        # Penpot cannot prove a browser accessible name from visible artwork.
        self.assertNotIn('aria-label', search['contract']['textProps'])


if __name__ == '__main__':
    unittest.main()