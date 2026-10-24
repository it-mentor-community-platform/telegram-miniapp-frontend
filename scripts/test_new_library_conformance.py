"""An incremental library addition must never authorize page mutations."""
import copy
import unittest

import penpot_conformance as audit
from test_penpot_conformance import fixture


class NewLibraryTests(unittest.TestCase):
    def setUp(self):
        self.manifest, self.before = fixture()
        self.family = 'Library/PrimeVue/Select'
        self.key = 'Library|' + self.family
        self.manifest['families'][self.family] = dict(kind='library', page='Library / PrimeVue', templateKey=self.key,
            contract=dict(internals=['Value', 'Placeholder', 'DropdownIcon'], textProps=dict(modelValue='Value', placeholder='Placeholder')))
        self.after = copy.deepcopy(self.before)
        self.after['records'].append(dict(id='select-record', family=self.family, mainId='select-main', variant={}))
        main = copy.deepcopy(next(n for n in self.after['nodes'] if n['id'] == 'main'))
        main.update(id='select-main', name='Library / PrimeVue/Select', componentId='select-record', family=self.family,
                    auditKey=self.key, bounds=[400, 0, 280, 44], parent=None, refId=None, variant={})
        self.after['nodes'].append(main)
        for name, value, x, w in [('Value', 'Java', 412, 220), ('Placeholder', 'Выберите язык', 412, 220), ('DropdownIcon', '⌄', 648, 16)]:
            n = copy.deepcopy(main)
            n.update(id='select-'+name, name=name, parent='select-main', type='text', head=False, copy=False,
                     componentId=None, family=None, refId=None, text=value, bounds=[x, 10, w, 24],
                     auditKey=self.key+'/'+name, hidden=name=='Value')
            self.after['nodes'].append(n)

    def check(self):
        return audit.compare_new_library(self.manifest, self.after, self.before, self.family)

    def test_new_main_passes_without_dependent_page_scope_exemptions(self):
        self.assertEqual('PASS', self.check()['status'], self.check())
        self.assertTrue(self.check()['preservationChecked'])

    def test_preserves_every_existing_shape_record_and_page(self):
        original = copy.deepcopy(self.after)
        mutations = [lambda: self.after['nodes'][0].update(text='changed'),
                     lambda: self.after['records'][0].update(family='changed'),
                     lambda: self.after['pages'][0].update(name='changed'),
                     lambda: self.after['nodes'].pop(0)]
        for mutate in mutations:
            self.after = copy.deepcopy(original)
            mutate()
            self.assertNotEqual('PASS', self.check()['status'])

    def test_requires_complete_fresh_baseline(self):
        for change in ({'complete': False}, {'fingerprint': 'stale'}, {'fileId': 'other'}, {'capturedAt': '2000-01-01T00:00:00Z'}):
            original = copy.deepcopy(self.before)
            self.before.update(change)
            self.assertEqual('BLOCKED', self.check()['status'])
            self.before = original
        self.assertEqual('BLOCKED', audit.compare_new_library(self.manifest, self.after, None, self.family)['status'])

    def test_rejects_existing_family_and_reused_shapes(self):
        self.assertEqual('BLOCKED', audit.compare_new_library(self.manifest, self.after, self.after, self.family)['status'])
        self.after['nodes'][-1]['id'] = self.before['nodes'][0]['id']
        self.assertNotEqual('PASS', self.check()['status'])

    def test_rejects_invalid_native_main_and_internals(self):
        original = copy.deepcopy(self.after)
        for index, change in [(-4, {'copy': True}), (-4, {'parent': 'main'}),
                              (-1, {'bounds': [900, 0, 16, 24]}), (-1, {'hidden': True}),
                              (-1, {'text': ''}), (-2, {'hidden': True}),
                              (-1, {'auditKey': 'wrong'}), (-1, {'name': 'Unknown'})]:
            self.after = copy.deepcopy(original)
            self.after['nodes'][index].update(change)
            self.assertNotEqual('PASS', self.check()['status'], change)

    def test_no_copies_or_extra_artwork(self):
        duplicate = copy.deepcopy(self.after['nodes'][-4])
        duplicate.update(id='unexpected-copy', copy=True, refId='select-main', parent=None)
        self.after['nodes'].append(duplicate)
        self.assertNotEqual('PASS', self.check()['status'])


if __name__ == '__main__':
    unittest.main()