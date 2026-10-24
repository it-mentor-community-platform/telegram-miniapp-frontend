"""Component-only contract, action forwarding and new variant preservation."""
import copy
import json
import unittest

import penpot_conformance as audit
from test_validate_design import design
from test_penpot_conformance import fixture


class RoadmapProjectCardTests(unittest.TestCase):
    def setUp(self):
        self.validator = design.Validator()
        self.validator.validate_tokens()
        self.validator.validate_libraries()
        self.validator.validate_custom_components()
        self.document = self.validator.custom_components['RoadmapProjectCard']

    def test_contract_and_both_complete_states_validate(self):
        self.assertEqual([], self.validator.errors)
        self.assertEqual({'title', 'languagesText'}, set(self.document.value['props']))
        for state, status, severity in [('submitted', 'Сдан', 'success'),
                                        ('notSubmitted', 'Не сдан', 'secondary')]:
            slots = self.document.value['variants'][state]['composition']['slots']
            self.assertEqual({'value': status, 'severity': severity}, slots['content'][1]['props'])
            self.assertEqual(state == 'submitted', any(n['name'] == 'Languages' for n in slots['content']))
            button = slots['footer'][0]
            self.assertEqual({'type': 'owner-action'}, button['action'])
            self.assertFalse(button['props']['disabled'])
            self.assertFalse(button['props']['loading'])

    def test_instance_requires_concrete_action(self):
        node = dict(type='custom-component', component='RoadmapProjectCard', variant='submitted',
                    props={'title': 'Unrelated display label'})
        self.validator.validate_node(node, self.document.path, '$')
        self.assertIn('requires a concrete action', '\n'.join(self.validator.errors))
        self.validator.errors.clear()
        node['action'] = {'type': 'command', 'name': 'openHangman'}
        self.validator.validate_node(node, self.document.path, '$')
        self.assertEqual([], self.validator.errors)

    def test_delegation_forwards_exact_identity_without_mutating_source(self):
        tree = self.document.value['variants']['submitted']['composition']
        original = copy.deepcopy(tree)
        action = {'type': 'command', 'name': 'openCurrencyExchange'}
        result = audit.bind_owner_action(tree, action)
        self.assertEqual(action, result['slots']['footer'][0]['action'])
        self.assertEqual(original, tree)
        with self.assertRaisesRegex(ValueError, 'concrete owning'):
            audit.bind_owner_action(tree, None)

    def test_owner_action_only_allowed_on_composition_buttons(self):
        for owner, component, extra in [(None, 'Button', {}), ('RoadmapProjectCard', 'Tag', {}),
                                         ('RoadmapProjectCard', 'Button', {'name': 'unsafe'})]:
            self.validator.errors.clear()
            node = dict(type='library-component', library='primevue', component=component,
                        action={'type': 'owner-action', **extra})
            self.validator.validate_node(node, self.document.path, '$', owner)
            self.assertIn('owner-action requires', '\n'.join(self.validator.errors))

    def test_manifest_exposes_two_native_states_and_native_nested_controls(self):
        manifest = audit.build_manifest()
        for state in ('submitted', 'notSubmitted'):
            scope = manifest['scopes'][f'custom:RoadmapProjectCard:{state}']
            root, *children = audit.flatten(scope['nodes'])
            self.assertEqual('native', root['representation'])
            controls = [n for n in children if n['kind'] == 'library-component']
            self.assertEqual(['Library/PrimeVue/Tag', 'Library/PrimeVue/Button'], [n['family'] for n in controls])
            self.assertTrue(all(n['representation'] == 'native' for n in controls))
            self.assertEqual({'type': 'owner-action'}, controls[-1]['action'])

    def container_fixture(self):
        manifest, after = fixture()
        template = copy.deepcopy(after['nodes'][-1])
        before = copy.deepcopy(after)
        family = 'Component/RoadmapProjectCard'
        manifest['families'][family] = {'kind': 'custom'}
        for state in ('submitted', 'notSubmitted'):
            scope = f'custom:RoadmapProjectCard:{state}'
            expected = dict(key=scope, source='fixture', name=None, kind='custom-component',
                            parent=None, slot=None, children=[], props={}, design={}, representation='native',
                            family=family, variant=state)
            manifest['scopes'][scope] = dict(page='Components', mode='custom', family=family,
                                           variant=state, nodes=[expected])
            n = copy.deepcopy(template)
            n.update(id=state, parent='container', pageId='components', family=family, componentId=state,
                     refId=None, variant={'State': state}, auditKey=scope, name='Component/RoadmapProjectCard')
            after['nodes'].append(n)
            after['records'].append(dict(id=state, family=family, mainId=state, variant={'State': state}))
        for snapshot in (before, after):
            snapshot['pages'].append({'id': 'components', 'name': 'Components'})
        container = copy.deepcopy(template)
        container.update(id='container', parent=None, pageId='components', name=family, head=False,
                         family=None, componentId=None, refId=None, variant={}, auditKey=None,
                         variantContainer=True, variantMembers=['submitted', 'notSubmitted'])
        after['nodes'].append(container)
        return manifest, before, after

    def check_container(self, manifest, before, after):
        return audit.compare(manifest, after, list(manifest['scopes']), before,
                             allow_families=['Component/RoadmapProjectCard'])

    def test_new_verified_container_passes_preservation(self):
        result = self.check_container(*self.container_fixture())
        self.assertEqual('PASS', result['status'], result)
        self.assertTrue(result['preservationChecked'])

    def test_container_requires_native_membership_and_no_extra_children(self):
        for mutation in ('native', 'members', 'extra', 'old', 'outside'):
            manifest, before, after = self.container_fixture()
            container = after['nodes'][-1]
            if mutation == 'native': container['variantContainer'] = False
            if mutation == 'members': container['variantMembers'] = ['submitted']
            if mutation == 'extra':
                extra = copy.deepcopy(container)
                extra.update(id='extra', parent='container', variantContainer=False)
                after['nodes'].append(extra)
            if mutation == 'old': before['nodes'].append(copy.deepcopy(container))
            if mutation == 'outside': after['nodes'][0]['bounds'][0] += 10
            result = self.check_container(manifest, before, after)
            self.assertNotEqual('PASS', result['status'], (mutation, result))

    def recovery_fixture(self):
        manifest, before, after = self.container_fixture()
        root = copy.deepcopy(next(n for n in after['nodes'] if n['id'] == 'submitted'))
        root.update(parent=None, family=None, componentId=None, head=False, variant={}, auditKey=None)
        child = copy.deepcopy(root)
        child.update(id='retained-child', parent='submitted', name='Content')
        before['nodes'].extend([root, child])
        after['nodes'].append(copy.deepcopy(child))
        inventory = {'fileId': after['fileId'], 'targets': [dict(
            scope='custom:RoadmapProjectCard:submitted', rootId='submitted',
            nodeIds=['submitted', 'retained-child'])]}
        return manifest, before, after, inventory

    def test_explicit_partial_recovery_preserves_same_root_and_descendants(self):
        manifest, before, after, inventory = self.recovery_fixture()
        # This synthetic descendant is deliberately outside the semantic contract;
        # test preservation separately from that independent structural diagnostic.
        result = audit.compare(manifest, after, list(manifest['scopes']), before,
                               allow_families=['Component/RoadmapProjectCard'], partial_recovery=inventory)
        self.assertTrue(result['preservationChecked'])
        self.assertFalse(any(i['code'] in ('PROTECTED_CHANGE', 'INVALID_PARTIAL_RECOVERY') for i in result['issues']), result)
        without = self.check_container(manifest, before, after)
        self.assertTrue(any(i['code'] == 'PROTECTED_CHANGE' for i in without['issues']))

    def test_partial_recovery_rejects_invalid_inventory_or_lost_identity(self):
        for mutation in ('file', 'scope', 'missing', 'extra', 'duplicate', 'root', 'registered', 'lost', 'moved', 'replacement'):
            manifest, before, after, inventory = self.recovery_fixture()
            target = inventory['targets'][0]
            if mutation == 'file': inventory['fileId'] = 'wrong'
            if mutation == 'scope': target['scope'] = 'unknown'
            if mutation == 'missing': target['nodeIds'].pop()
            if mutation == 'extra': target['nodeIds'].append('unrelated')
            if mutation == 'duplicate': target['nodeIds'].append('submitted')
            if mutation == 'root': target['rootId'] = 'replacement'
            if mutation == 'registered': before['nodes'][-2]['head'] = True
            if mutation == 'lost': after['nodes'].pop()
            if mutation == 'moved': after['nodes'][-1]['parent'] = None
            if mutation == 'replacement':
                next(n for n in after['nodes'] if n['id'] == 'submitted')['id'] = 'replacement'
                next(r for r in after['records'] if r['id'] == 'submitted')['mainId'] = 'replacement'
                after['nodes'][-1]['parent'] = 'replacement'
            result = audit.compare(manifest, after, list(manifest['scopes']), before,
                                   allow_families=['Component/RoadmapProjectCard'], partial_recovery=inventory)
            self.assertTrue(any(i['code'] == 'INVALID_PARTIAL_RECOVERY' for i in result['issues']), (mutation, result))

    def test_recovery_does_not_absorb_unrelated_baseline_artwork(self):
        for mutation in ('change', 'move', 'remove'):
            manifest, before, after, inventory = self.recovery_fixture()
            unrelated = copy.deepcopy(before['nodes'][-1])
            unrelated.update(id='unrelated', parent=None)
            before['nodes'].append(unrelated)
            after['nodes'].append(copy.deepcopy(unrelated))
            if mutation == 'change': after['nodes'][-1]['bounds'][0] += 1
            if mutation == 'move': after['nodes'][-1]['parent'] = 'submitted'
            if mutation == 'remove': after['nodes'].pop()
            result = audit.compare(manifest, after, list(manifest['scopes']), before,
                                   allow_families=['Component/RoadmapProjectCard'], partial_recovery=inventory)
            self.assertTrue(any(i['code'] == 'PROTECTED_CHANGE' for i in result['issues']), (mutation, result))


if __name__ == '__main__':
    unittest.main()