"""Offline resolver/comparator regressions and execution of the real JS collector."""
import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone

import penpot_conformance as audit
from penpot_snapshot import decode_transfer


def fixture():
    manifest = audit.build_manifest()
    scope = manifest['scopes']['ReviewSessionSaved']
    manifest['scopes'] = {'ReviewSessionSaved': scope}
    expected = audit.flatten(scope['nodes'])
    manifest['blocked'] = []
    # The focused fixture removes Toolbar to exercise nested Message composition.
    scope['nodes'] = [scope['nodes'][1]]
    expected = audit.flatten(scope['nodes'])
    node = lambda id_, parent, **kw: dict(id=id_, parent=parent, pageId='page', type='board',
        name=id_, hidden=False, opacity=1, bounds=[0, 0, 300, 300], text=None,
        copy=False, head=False, family=None, componentId=None, refId=None,
        variant={}, auditKey=None, slot=None, fills=[], **kw)
    nodes = [node('frame', None)]
    nodes[0]['name'] = scope['frame']
    mapping = {}
    for i, e in enumerate(expected):
        id_ = str(i)
        mapping[e['key']] = id_
        n = node(id_, mapping.get(e['parent'], 'frame'))
        n.update(name=e['name'] or 'Message', auditKey=e['key'], slot=e['slot'])
        if e['kind'] == 'text':
            n.update(type='text', text=e['text'])
        if e['representation'] == 'native':
            n.update(copy=True, head=True, family=e['family'], componentId='progress', refId='main')
        nodes.append(n)
    bar = nodes[-1]
    nodes.extend([node('indicator', bar['id']), node('value', bar['id'])])
    nodes[-2].update(name='Indicator', type='rectangle', bounds=[40, 0, 80, 8])
    nodes[-1].update(name='Value', type='text', hidden=True, text='58%')
    family = bar['family']
    manifest['families'] = {family: {'kind': 'library'}}
    main = node('main', None)
    main.update(head=True, family=family, componentId='progress', refId='main', name='ProgressBar')
    nodes.append(main)
    snapshot = dict(version=2, fingerprint=manifest['fingerprint'], fileName=manifest['fileName'],
                    fileId='file', capturedAt=datetime.now(timezone.utc).isoformat(), complete=True,
                    coverage='full-file',
                    collectionErrors=[], pages=[{'id': 'page', 'name': scope['page']}], nodes=nodes,
                    records=[{'id': 'progress', 'family': family, 'mainId': 'main', 'variant': {}}])
    # Library main belongs to another page; prevents a stray feature-artwork failure.
    snapshot['pages'].append({'id': 'library', 'name': 'Library / PrimeVue'})
    main['pageId'] = 'library'
    return manifest, snapshot


class ConformanceTests(unittest.TestCase):
    def setUp(self):
        self.manifest, self.snapshot = fixture()

    def check(self):
        return audit.compare(self.manifest, self.snapshot)

    def assert_code(self, code):
        result = self.check()
        self.assertNotEqual('PASS', result['status'])
        self.assertIn(code, [i['code'] for i in result['issues']], result)

    def find(self, name):
        return next(n for n in self.snapshot['nodes'] if n['name'] == name)

    def test_nested_saved_message_passes(self):
        self.assertEqual('PASS', self.check()['status'], self.check())

    def add_legacy_orphans(self):
        self.snapshot['fileId'] = audit.LEGACY_ORPHAN_FILE_ID
        self.snapshot['records'].extend(
            dict(id=id_, family=family, mainId=None, variant={})
            for id_, family in audit.LEGACY_ORPHANS.items())

    def test_approved_legacy_orphans_are_reported_without_errors(self):
        self.add_legacy_orphans()
        result = self.check()
        self.assertEqual('PASS', result['status'], result)
        self.assertEqual(set(audit.LEGACY_ORPHANS),
                         {r['id'] for r in result['acceptedOrphans']})

    def test_legacy_orphan_exception_requires_exact_record_and_file(self):
        self.add_legacy_orphans()
        original = copy.deepcopy(self.snapshot)
        for changes in ({'id': 'another-record'}, {'family': 'Component/legacy/Other'},
                        {'mainId': 'main'}, {'variant': {'State': 'active'}}):
            with self.subTest(changes=changes):
                self.snapshot = copy.deepcopy(original)
                self.snapshot['records'][-1].update(changes)
                self.assertNotEqual('PASS', self.check()['status'])
        self.snapshot = copy.deepcopy(original)
        self.snapshot['fileId'] = 'another-file'
        self.assert_code('ORPHAN_RECORD')

    def test_legacy_orphan_exception_rejects_live_dependencies(self):
        self.add_legacy_orphans()
        original = copy.deepcopy(self.snapshot)
        id_, family = next(iter(audit.LEGACY_ORPHANS.items()))
        for key, value in (('componentId', id_), ('refId', id_), ('family', family)):
            with self.subTest(key=key):
                self.snapshot = copy.deepcopy(original)
                self.find('ProgressBar')[key] = value
                self.assert_code('LEGACY_ORPHAN_CHANGED')

    def test_other_legacy_orphans_remain_errors(self):
        self.add_legacy_orphans()
        self.snapshot['records'].append(dict(id='other', family='Component/legacy/Input',
                                             mainId=None, variant={}))
        self.assert_code('UNKNOWN_FAMILY')
        self.assert_code('ORPHAN_RECORD')

    def test_removed_legacy_orphans_need_no_exception(self):
        self.assertEqual([], self.check()['acceptedOrphans'])

    def test_legacy_orphans_remain_protected_in_scoped_sync(self):
        self.add_legacy_orphans()
        baseline = copy.deepcopy(self.snapshot)
        self.snapshot['records'][-1]['family'] = 'Component/legacy/Renamed'
        result = audit.compare(self.manifest, self.snapshot, ['ReviewSessionSaved'], baseline)
        self.assertIn('PROTECTED_CHANGE', [i['code'] for i in result['issues']])

    def custom_main_fixture(self):
        scope = self.manifest['scopes']['ReviewSessionSaved']
        family = 'Component/TestContainer'
        scope.update(mode='custom', family=family, variant='active')
        root_expected = dict(key='custom-root', source='test', name='CustomMain',
                             kind='custom-component', parent=None, slot=None,
                             children=scope['nodes'], props={}, design={},
                             representation='native', family=family, variant='active')
        for child in scope['nodes']:
            child['parent'] = root_expected['key']
        scope['nodes'] = [root_expected]
        self.manifest['families'][family] = {'kind': 'custom'}
        root = self.find(scope['frame'])
        root.update(name='CustomMain', auditKey='custom-root', head=True,
                    family=family, componentId='custom-record', variant={'State': 'active'})
        self.snapshot['records'].append(dict(id='custom-record', family=family,
                                            mainId=root['id'], variant={'State': 'active'}))
        bar = next(n for n in self.snapshot['nodes'] if n['copy'])
        bar['refId'] = None
        return root, bar

    def test_nested_library_copy_in_verified_custom_main_allows_documented_null_ref(self):
        self.custom_main_fixture()
        self.assertEqual('PASS', self.check()['status'], self.check())

    def test_ordinary_page_copy_still_requires_source_reference(self):
        next(n for n in self.snapshot['nodes'] if n['copy'])['refId'] = None
        self.assert_code('BROKEN_SOURCE')
        self.assert_code('WRONG_FAMILY')

    def test_nested_custom_main_non_null_wrong_reference_is_not_exempt(self):
        _, bar = self.custom_main_fixture()
        bar['refId'] = 'frame'
        self.assert_code('BROKEN_SOURCE')

    def test_nested_null_reference_rejects_invalid_native_evidence(self):
        self.custom_main_fixture()
        original = copy.deepcopy(self.snapshot)
        for target, changes, code in (
                ('bar', {'copy': False}, 'DETACHED_INSTANCE'),
                ('bar', {'head': False}, 'WRONG_FAMILY'),
                ('bar', {'family': 'Wrong/Family'}, 'WRONG_FAMILY'),
                ('bar', {'componentId': 'missing'}, 'BROKEN_SOURCE'),
                ('main', {'head': False}, 'BROKEN_SOURCE'),
                ('main', {'copy': True}, 'BROKEN_SOURCE'),
                ('main', {'family': 'Wrong/Family'}, 'BROKEN_SOURCE'),
                ('main', {'componentId': 'wrong-record'}, 'BROKEN_SOURCE')):
            with self.subTest(target=target, changes=changes):
                self.snapshot = copy.deepcopy(original)
                node = (next(n for n in self.snapshot['nodes'] if n['componentId'] == 'progress' and n['copy'])
                        if target == 'bar' else self.find('ProgressBar'))
                node.update(changes)
                self.assert_code(code)

    def test_nested_null_reference_requires_verified_custom_record_and_state(self):
        self.custom_main_fixture()
        original = copy.deepcopy(self.snapshot)
        for changes in ({'mainId': 'missing'}, {'family': 'Wrong/Family'},
                        {'variant': {'State': 'wrong'}}):
            with self.subTest(changes=changes):
                self.snapshot = copy.deepcopy(original)
                next(r for r in self.snapshot['records'] if r['id'] == 'custom-record').update(changes)
                self.assert_code('BROKEN_SOURCE')

    def test_nested_null_reference_requires_actual_custom_main_ancestry(self):
        _, bar = self.custom_main_fixture()
        bar['parent'] = None
        self.assert_code('MISSING_NODE')

    def nested_page_reference_fixture(self):
        scope = self.manifest['scopes']['ReviewSessionSaved']
        bar = next(n for n in self.snapshot['nodes'] if n['copy'])
        expected_bar = next(n for n in audit.flatten(scope['nodes'])
                            if n.get('family') == bar['family'])
        expected_parent = next(n for n in audit.flatten(scope['nodes'])
                               if n['key'] == expected_bar['parent'])
        family = 'Library/PrimeVue/TestContainer'
        wrapper = dict(key='native-wrapper', source='test', name='NativeWrapper',
                       parent=expected_bar['parent'], slot=None, children=[expected_bar],
                       kind='library-component', representation='native', family=family,
                       props={}, design={})
        expected_parent['children'] = [wrapper if n is expected_bar else n
                                       for n in expected_parent['children']]
        expected_bar['parent'] = wrapper['key']
        head = copy.deepcopy(bar)
        head.update(id='wrapper', name='NativeWrapper', auditKey=wrapper['key'],
                    slot=None, family=family, componentId='container', refId='container-main')
        bar.update(parent='wrapper', refId='nested-reference')
        main = copy.deepcopy(head)
        main.update(id='container-main', name='ContainerMain', parent=None,
                    pageId='library', copy=False, auditKey=None, refId=None)
        reference = copy.deepcopy(bar)
        reference.update(id='nested-reference', parent=main['id'], pageId='library',
                         name='NestedSource', auditKey=None, slot=None, refId=None)
        self.snapshot['nodes'].extend([head, main, reference])
        self.manifest['families'][family] = {'kind': 'library'}
        self.snapshot['records'].append(dict(id='container', family=family,
                                            mainId=main['id'], variant={}))

    def paired_board_reference_fixture(self):
        self.nested_page_reference_fixture()
        expected = next(n for n in audit.flatten(
            self.manifest['scopes']['ReviewSessionSaved']['nodes'])
            if n['key'] == 'native-wrapper')
        child = expected['children'][0]
        expected['children'] = [dict(key='slot-board', source='test', name='Footer',
            parent=expected['key'], slot=None, children=[child], kind='section',
            representation='structural', props={}, design={})]
        child['parent'] = 'slot-board'
        head = next(n for n in self.snapshot['nodes'] if n['id'] == 'wrapper')
        board = copy.deepcopy(head)
        board.update(id='slot-board', parent=head['id'], name='Footer', head=False,
                     auditKey='slot-board', refId='source-board')
        source = copy.deepcopy(board)
        source.update(id='source-board', parent='container-main', pageId='library',
                      auditKey=None, refId=None, copy=False, family=None,
                      componentId=None, variant={})
        next(n for n in self.snapshot['nodes'] if n['refId'] == 'nested-reference')['parent'] = board['id']
        next(n for n in self.snapshot['nodes'] if n['id'] == 'nested-reference')['parent'] = source['id']
        self.snapshot['nodes'].extend([board, source])

    def test_page_nested_reference_through_paired_board(self):
        self.paired_board_reference_fixture()
        self.assertEqual('PASS', self.check()['status'], self.check())

    def test_paired_board_reference_rejects_invalid_native_evidence(self):
        self.paired_board_reference_fixture()
        original = copy.deepcopy(self.snapshot)
        for id_, changes in (
                ('slot-board', {'refId': None}),
                ('slot-board', {'refId': 'container-main'}),
                ('slot-board', {'copy': False}),
                ('slot-board', {'head': True}),
                ('slot-board', {'componentId': 'progress'}),
                ('slot-board', {'family': 'Wrong/Family'}),
                ('slot-board', {'variant': {'State': 'wrong'}}),
                ('source-board', {'parent': None}),
                ('source-board', {'copy': True}),
                ('source-board', {'head': True}),
                ('source-board', {'type': 'rectangle'}),
                ('source-board', {'refId': 'main'}),
                ('source-board', {'componentId': 'progress'}),
                ('source-board', {'family': 'Wrong/Family'}),
                ('source-board', {'variant': {'State': 'wrong'}}),
                ('wrapper', {'copy': False}),
                ('wrapper', {'variant': {'State': 'wrong'}}),
                ('container-main', {'copy': True}),
                ('nested-reference', {'parent': 'container-main'}),
                ('nested-reference', {'componentId': 'container'}),
                ('nested-reference', {'refId': 'main'}),
                ('main', {'copy': True})):
            with self.subTest(id=id_, changes=changes):
                self.snapshot = copy.deepcopy(original)
                next(n for n in self.snapshot['nodes'] if n['id'] == id_).update(changes)
                self.assert_code('BROKEN_SOURCE')

    def test_paired_board_reference_rejects_sibling_and_extra_depth(self):
        self.paired_board_reference_fixture()
        source = next(n for n in self.snapshot['nodes'] if n['id'] == 'source-board')
        sibling = copy.deepcopy(source)
        sibling['id'] = 'sibling-board'
        self.snapshot['nodes'].append(sibling)
        board = next(n for n in self.snapshot['nodes'] if n['id'] == 'slot-board')
        board['refId'] = sibling['id']
        self.assert_code('BROKEN_SOURCE')
        board['refId'] = source['id']
        extra = copy.deepcopy(board)
        extra.update(id='extra-board', parent='wrapper', auditKey=None)
        board['parent'] = extra['id']
        self.snapshot['nodes'].append(extra)
        self.assert_code('BROKEN_SOURCE')

    def test_paired_board_reference_still_requires_child_reference_and_source_main(self):
        self.paired_board_reference_fixture()
        original = copy.deepcopy(self.snapshot)
        child_id = next(n['id'] for n in self.snapshot['nodes']
                        if n['refId'] == 'nested-reference')
        for ref in (None, 'frame', 'source-board', 'container-main'):
            with self.subTest(ref=ref):
                self.snapshot = copy.deepcopy(original)
                next(n for n in self.snapshot['nodes'] if n['id'] == child_id)['refId'] = ref
                self.assert_code('BROKEN_SOURCE')
        self.snapshot = copy.deepcopy(original)
        next(r for r in self.snapshot['records'] if r['id'] == 'progress')['mainId'] = None
        self.assert_code('BROKEN_SOURCE')
        self.snapshot = copy.deepcopy(original)
        next(n for n in self.snapshot['nodes'] if n['id'] == child_id)['copy'] = False
        self.assert_code('DETACHED_INSTANCE')

    def test_internal_names_do_not_override_template_family_permissions(self):
        self.nested_page_reference_fixture()
        bar = next(n for n in self.snapshot['nodes'] if n['refId'] == 'nested-reference')
        extra = copy.deepcopy(next(n for n in self.snapshot['nodes'] if n['id'] == 'value'))
        extra.update(id='internal-label', parent=bar['id'], name='InternalLabel',
                     auditKey=None, text='', hidden=True)
        self.snapshot['nodes'].append(extra)
        expected = next(n for n in audit.flatten(
            self.manifest['scopes']['ReviewSessionSaved']['nodes'])
            if n.get('family') == bar['family'])
        expected['contract']['internals'].append('InternalLabel')
        baseline = copy.deepcopy(self.snapshot)
        result = audit.compare(self.manifest, self.snapshot,
                               ['ReviewSessionSaved'], baseline)
        self.assertEqual('PASS', result['status'], result)
        self.find('ProgressBar')['bounds'][2] += 1
        result = audit.compare(self.manifest, self.snapshot,
                               ['ReviewSessionSaved'], baseline)
        self.assertIn('PROTECTED_CHANGE', [i['code'] for i in result['issues']])
        result = audit.compare(self.manifest, self.snapshot,
            ['ReviewSessionSaved'], baseline, allow_families=[bar['family']])
        self.assertEqual('PASS', result['status'], result)

    def test_page_nested_reference_matches_enclosing_native_main(self):
        self.nested_page_reference_fixture()
        self.assertEqual('PASS', self.check()['status'], self.check())

    def test_page_nested_reference_rejects_unpaired_or_invalid_evidence(self):
        self.nested_page_reference_fixture()
        original = copy.deepcopy(self.snapshot)
        for id_, changes in (
                ('wrapper', {'refId': 'main'}),
                ('wrapper', {'copy': False}),
                ('wrapper', {'head': False}),
                ('wrapper', {'componentId': 'missing'}),
                ('wrapper', {'family': 'Wrong/Family'}),
                ('wrapper', {'variant': {'State': 'wrong'}}),
                ('container-main', {'copy': True}),
                ('container-main', {'head': False}),
                ('container-main', {'family': 'Wrong/Family'}),
                ('container-main', {'componentId': 'wrong'}),
                ('container-main', {'variant': {'State': 'wrong'}}),
                ('nested-reference', {'parent': None}),
                ('nested-reference', {'copy': False}),
                ('nested-reference', {'head': False}),
                ('nested-reference', {'componentId': 'container'}),
                ('nested-reference', {'family': 'Wrong/Family'}),
                ('nested-reference', {'variant': {'State': 'wrong'}}),
                ('nested-reference', {'refId': 'frame'}),
                ('main', {'copy': True})):
            with self.subTest(id=id_, changes=changes):
                self.snapshot = copy.deepcopy(original)
                next(n for n in self.snapshot['nodes'] if n['id'] == id_).update(changes)
                self.assert_code('BROKEN_SOURCE')

    def test_page_nested_reference_rejects_null_or_unrelated_reference(self):
        self.nested_page_reference_fixture()
        bar = next(n for n in self.snapshot['nodes']
                   if n['parent'] == 'wrapper')
        for ref in (None, 'frame', 'container-main'):
            with self.subTest(ref=ref):
                bar['refId'] = ref
                self.assert_code('BROKEN_SOURCE')

    def test_button_disabled_adapter_requires_observable_muting(self):
        expected = {'key': 'button', 'contract': {'adapter': 'button', 'observableStates': ['disabled', 'loading']},
                    'props': {'disabled': True}, 'design': {'state': 'disabled'}}
        head = {'id': 'head', 'opacity': 0.5}
        def check():
            issues = []
            audit.verify_control(expected, head, [head], lambda n: not n.get('hidden', False), set(),
                                 lambda code, *args: issues.append(code))
            return issues
        self.assertEqual([], check())
        for opacity in (0, 0.8, 1):
            head['opacity'] = opacity
            self.assertIn('DISABLED_APPEARANCE', check())
        head['opacity'] = 0.5
        expected['props']['disabled'] = False
        self.assertIn('BUTTON_STATE', check())
        expected.update(props={'loading': False}, design={'state': 'loading'})
        self.assertIn('BUTTON_STATE', check())
        expected['props']['loading'] = True
        self.assertIn('MISSING_LOADER', check())

    def test_collapsed_panel_resolver_marks_only_content_hidden(self):
        nodes = audit.flatten(audit.build_manifest()['scopes']['CategoryDetails']['nodes'])
        panels = [n for n in nodes if n.get('family') == 'Library/PrimeVue/AccordionPanel']
        self.assertEqual(4, len(panels))
        for panel in panels:
            for child in panel['children']:
                hidden = panel['design']['state'] == 'collapsed' and child['slot'] == 'content'
                self.assertEqual(not hidden, child.get('expectedVisible', True))

    def test_hide_when_empty_resolves_only_explicit_exact_empty_values(self):
        from pathlib import Path
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(audit.ROOT / 'design', root / 'design')
            shutil.copytree(audit.ROOT / 'scripts', root / 'scripts')
            path = root / 'design/pages/interval-repetition/category-catalog.page.json'
            original = json.loads(path.read_text())
            for value, flag, hidden in [('', True, True), ('12 доступны', True, False),
                                        (' ', True, False), ('', False, False), ('', None, False)]:
                with self.subTest(value=value, flag=flag):
                    page = copy.deepcopy(original)
                    def update(value_):
                        if isinstance(value_, dict):
                            if value_.get('component') == 'CategorySelectionRow':
                                value_['props']['progress'] = value
                            for child in value_.values(): update(child)
                        elif isinstance(value_, list):
                            for child in value_: update(child)
                    update(page)
                    path.write_text(json.dumps(page))
                    component = root / 'design/components/category-selection-row.component.json'
                    definition = json.loads(component.read_text())
                    for state in definition['variants'].values():
                        text = state['composition']['slots']['content'][2]
                        text.pop('hideWhenEmpty', None)
                        if flag is not None: text['hideWhenEmpty'] = flag
                    component.write_text(json.dumps(definition))
                    manifest = audit.build_manifest(root)
                    texts = [n for n in audit.flatten(manifest['scopes']['CategoryCatalog']['nodes'])
                             if n['name'] == 'ProgressText']
                    self.assertEqual(4, len(texts))
                    for text in texts:
                        self.assertEqual(value, text['text'])
                        self.assertEqual(not hidden, text.get('expectedVisible', True))

    def test_omitted_optional_progress_resolves_hidden_without_omitting_node(self):
        manifest = audit.build_manifest()
        texts = [n for n in audit.flatten(manifest['scopes']['CategoryCatalog']['nodes'])
                 if n['name'] == 'ProgressText']
        empty = [n for n in texts if n['text'] == '']
        self.assertEqual(2, len(empty))
        self.assertTrue(all(n['expectedVisible'] is False for n in empty))
        previews = [n for n in audit.flatten(manifest['scopes']['custom:CategorySelectionRow:available']['nodes'])
                    if n['name'] == 'ProgressText']
        self.assertTrue(previews[0]['text'])
        self.assertTrue(previews[0].get('expectedVisible', True))

    def test_empty_hidden_text_retains_structural_and_content_checks(self):
        title = self.find('SavedTitle')
        expected = next(n for n in audit.flatten(self.manifest['scopes']['ReviewSessionSaved']['nodes'])
                        if n['name'] == 'SavedTitle')
        expected.update(text='', expectedVisible=False, hiddenReason='empty-text')
        title.update(text='', hidden=True)
        self.assertEqual('PASS', self.check()['status'], self.check())
        for changes, code in [({'hidden': False}, 'EMPTY_TEXT_VISIBLE'),
                              ({'text': 'unexpected'}, 'TEXT_MISMATCH'),
                              ({'auditKey': 'wrong'}, 'WRONG_IDENTITY'),
                              ({'parent': 'frame'}, 'WRONG_PARENT'),
                              ({'type': 'board'}, 'WRONG_REPRESENTATION'),
                              ({'bounds': [0, 0, 0, 10]}, 'EMPTY_BOUNDS')]:
            with self.subTest(code=code):
                before = copy.deepcopy(title)
                title.update(changes)
                self.assert_code(code)
                title.update(before)
        expected['slot'] = 'content'
        self.assert_code('SLOT_UNVERIFIED')

    def test_nonempty_progress_still_requires_visibility(self):
        self.find('SavedTitle')['hidden'] = True
        self.assert_code('HIDDEN_CONTENT')

    def placeholder_fixture(self):
        bar = next(n for n in self.snapshot['nodes'] if n['copy'])
        expected_bar = next(e for e in audit.flatten(self.manifest['scopes']['ReviewSessionSaved']['nodes'])
                            if e.get('family') == bar['family'])
        expected = dict(key='optional', source='test', name='Optional', kind='text',
                        parent=expected_bar['key'], slot=None, children=[], text='',
                        representation='structural', expectedVisible=False,
                        hiddenReason='empty-text', penpotEmptyPlaceholder=' ')
        expected_bar['children'].append(expected)
        source = copy.deepcopy(self.find('Value'))
        source.update(id='optional-source', name='Optional', parent='main', pageId='library',
                      text='preview', hidden=False)
        text = copy.deepcopy(source)
        text.update(id='optional-copy', parent=bar['id'], pageId='page', copy=True,
                    family=bar['family'], componentId=bar['componentId'], refId=source['id'],
                    text=' ', hidden=True, auditKey=expected['key'])
        self.snapshot['nodes'].extend([source, text])
        return expected, text, source

    def test_placeholder_preserves_semantic_empty_and_native_characters(self):
        expected, text, _ = self.placeholder_fixture()
        self.assertEqual('PASS', self.check()['status'], self.check())
        self.assertEqual('', expected['text'])
        self.assertEqual(' ', text['text'])

    def test_placeholder_rejects_invalid_text_identity_visibility_and_source(self):
        self.placeholder_fixture()
        original = copy.deepcopy(self.snapshot)
        for changes, code in (
                ({'text': '  '}, 'TEXT_MISMATCH'), ({'text': '\t'}, 'TEXT_MISMATCH'),
                ({'text': '\u00a0'}, 'TEXT_MISMATCH'), ({'hidden': False}, 'TEXT_MISMATCH'),
                ({'copy': False}, 'TEXT_MISMATCH'), ({'refId': 'missing'}, 'TEXT_MISMATCH'),
                ({'refId': 'value'}, 'TEXT_MISMATCH'), ({'componentId': 'missing'}, 'TEXT_MISMATCH'),
                ({'family': 'Wrong'}, 'TEXT_MISMATCH'), ({'variant': {'State': 'wrong'}}, 'TEXT_MISMATCH'),
                ({'auditKey': 'wrong'}, 'WRONG_IDENTITY'), ({'parent': 'frame'}, 'WRONG_PARENT'),
                ({'bounds': [0, 0, 0, 10]}, 'EMPTY_BOUNDS')):
            with self.subTest(changes=changes):
                self.snapshot = copy.deepcopy(original)
                next(n for n in self.snapshot['nodes'] if n['id'] == 'optional-copy').update(changes)
                self.assert_code(code)

    def test_placeholder_does_not_exempt_unflagged_nonempty_or_inherited_hidden(self):
        expected, text, _ = self.placeholder_fixture()
        for changes in ({'penpotEmptyPlaceholder': None}, {'text': 'nonempty'},
                        {'hiddenReason': None}, {'expectedVisible': True}):
            with self.subTest(changes=changes):
                before = copy.deepcopy(expected)
                expected.update(changes)
                self.assertNotEqual('PASS', self.check()['status'])
                expected.update(before)
        text['hidden'] = False
        next(n for n in self.snapshot['nodes'] if n['id'] == text['parent'])['hidden'] = True
        self.assert_code('TEXT_MISMATCH')

    def toolbar_fixture(self):
        scope = self.manifest['scopes']['ReviewSessionSaved']
        prototype = copy.deepcopy(self.snapshot['nodes'][0])
        def node(id_, parent, **changes):
            n = copy.deepcopy(prototype)
            n.update(id=id_, name=id_, parent=parent, auditKey=None, **changes)
            self.snapshot['nodes'].append(n)
            return n
        family = 'Library/PrimeVue/Toolbar'
        contract = copy.deepcopy(audit.build_manifest()['families'][family]['contract'])
        expected = dict(key='toolbar', source='test', name='Toolbar', kind='library-component',
                        parent=None, slot=None, children=[], props={}, design={'state': 'root'},
                        representation='native', family=family, contract=contract)
        scope['nodes'].append(expected)
        self.manifest['families'][family] = {'kind': 'library'}
        button_family = 'Library/PrimeVue/Button'
        self.manifest['families'][button_family] = {'kind': 'library'}
        main = node('toolbar-main', None, pageId='library', head=True,
                    family=family, componentId='toolbar-record')
        owner = node('toolbar-copy', 'frame', head=True, copy=True, family=family,
                     componentId='toolbar-record', refId=main['id'])
        owner.update(name='Toolbar', auditKey=expected['key'])
        node('button-main', None, pageId='library', head=True,
             family=button_family, componentId='button-record')
        self.snapshot['records'].extend([
            dict(id='toolbar-record', family=family, mainId=main['id'], variant={}),
            dict(id='button-record', family=button_family, mainId='button-main', variant={})])
        for branch in contract['inactiveNativeBranches']:
            name = branch['sourceName']
            source = node(name+'-source', main['id'], pageId='library', head=True, copy=True,
                          hidden=True, family=button_family, componentId='button-record')
            source['name'] = name
            candidate = node(name+'-copy', owner['id'], head=True, copy=True, hidden=True,
                             family=button_family, componentId='button-record', refId=source['id'])
            for role in branch['children']:
                child = node(name+'-'+role+'-source', source['id'], pageId='library',
                             type='text', text='template', copy=True,
                             family=button_family, componentId='button-record')
                child['name'] = role
                child_copy = copy.deepcopy(child)
                child_copy.update(id=name+'-'+role+'-copy', parent=candidate['id'],
                                  pageId='page', refId=child['id'])
                self.snapshot['nodes'].append(child_copy)
        return expected

    def test_exact_hidden_native_toolbar_branches_pass(self):
        self.toolbar_fixture()
        self.assertEqual('PASS', self.check()['status'], self.check())

    def test_hidden_native_branches_reject_invalid_evidence(self):
        self.toolbar_fixture()
        original = copy.deepcopy(self.snapshot)
        for id_, changes in (
                ('BackButton-copy', {'hidden': False}), ('BackButton-copy', {'copy': False}),
                ('BackButton-copy', {'head': False}), ('BackButton-copy', {'refId': 'missing'}),
                ('BackButton-copy', {'family': 'Wrong'}), ('BackButton-copy', {'slot': 'start'}),
                ('BackButton-copy', {'auditKey': 'arbitrary'}),
                ('BackButton-source', {'refId': 'button-main'}),
                ('BackButton-source', {'hidden': False}),
                ('BackButton-Label-copy', {'refId': 'EndButton-Label-source'}),
                ('BackButton-Label-copy', {'copy': False}),
                ('BackButton-Label-copy', {'name': 'arbitrary'}),
                ('BackButton-Label-copy', {'variant': {'State': 'wrong'}}),
                ('toolbar-copy', {'refId': 'button-main'}),
                ('toolbar-main', {'copy': True}), ('button-main', {'head': False})):
            with self.subTest(id=id_, changes=changes):
                self.snapshot = copy.deepcopy(original)
                next(n for n in self.snapshot['nodes'] if n['id'] == id_).update(changes)
                self.assertNotEqual('PASS', self.check()['status'], self.check())

    def test_hidden_native_branches_reject_duplicates_extra_depth_and_active_slots(self):
        expected = self.toolbar_fixture()
        original = copy.deepcopy(self.snapshot)
        for target in ('BackButton-copy', 'BackButton-Label-copy'):
            with self.subTest(target=target):
                self.snapshot = copy.deepcopy(original)
                extra = copy.deepcopy(next(n for n in self.snapshot['nodes'] if n['id'] == target))
                extra['id'] = 'extra'
                self.snapshot['nodes'].append(extra)
                self.assert_code('UNEXPECTED_NODE')
        self.snapshot = copy.deepcopy(original)
        extra = copy.deepcopy(next(n for n in self.snapshot['nodes'] if n['id'] == 'BackButton-Label-copy'))
        extra.update(id='extra', parent='BackButton-Label-copy')
        self.snapshot['nodes'].append(extra)
        self.assert_code('UNEXPECTED_NODE')
        self.snapshot = copy.deepcopy(original)
        expected['children'].append(dict(key='required', source='test', name='Required', kind='text',
            parent=expected['key'], slot='start', children=[], text='Back', representation='structural'))
        self.assert_code('UNEXPECTED_NODE')

    def test_collapsed_content_still_requires_identity_parent_slot_and_text(self):
        title = self.find('SavedTitle')
        expected = next(n for n in audit.flatten(self.manifest['scopes']['ReviewSessionSaved']['nodes'])
                        if n['name'] == 'SavedTitle')
        expected['expectedVisible'] = False
        title['hidden'] = True
        self.assertEqual('PASS', self.check()['status'], self.check())
        title['hidden'] = False
        self.assert_code('COLLAPSED_CONTENT_VISIBLE')
        title['hidden'] = True
        title['text'] = 'incorrect hidden answer'
        self.assert_code('TEXT_MISMATCH')
        title['text'] = expected['text']
        expected['slot'] = 'content'
        title['slot'] = None
        self.assert_code('SLOT_UNVERIFIED')
        title['slot'] = expected['slot']
        title['parent'] = 'frame'
        self.assert_code('WRONG_PARENT')

    def test_accordion_adapter_rejects_value_panel_state_disagreement(self):
        nodes = audit.flatten(audit.build_manifest()['scopes']['CategoryDetails']['nodes'])
        expected = next(n for n in nodes if n.get('family') == 'Library/PrimeVue/Accordion')
        def check():
            issues = []
            audit.verify_control(expected, {'id': 'head'}, [], lambda n: True, set(),
                                 lambda code, *args: issues.append(code))
            return issues
        self.assertEqual([], check())
        expected['props']['value'] = ['question-1']
        self.assertIn('ACCORDION_STATE', check())
        expected['props']['value'] = 'question-2'
        self.assertIn('ACCORDION_STATE', check())

    def test_panel_adapter_does_not_certify_missing_semantic_content(self):
        expected = {'key': 'panel', 'family': 'Library/PrimeVue/AccordionPanel',
                    'contract': {'adapter': 'container', 'observableStates': ['expanded']},
                    'props': {}, 'design': {'state': 'expanded'},
                    'children': [{'slot': 'header'}]}
        issues = []
        audit.verify_control(expected, {'id': 'head'}, [], lambda n: True, set(),
                             lambda code, *args: issues.append(code))
        self.assertIn('PANEL_EVIDENCE', issues)

    def test_panel_indicator_checks_state_visibility_bounds_and_registered_role(self):
        expected = {'key': 'panel', 'family': 'Library/PrimeVue/AccordionPanel',
                    'contract': {'adapter': 'container', 'internals': ['Secondary'],
                                 'observableStates': ['collapsed', 'expanded']},
                    'props': {}, 'design': {'state': 'collapsed'},
                    'children': [{'slot': 'header'}, {'slot': 'content'}]}
        indicator = dict(id='chevron', parent='head', name='Secondary', type='text',
                         head=False, hidden=False, text='⌄', bounds=[270, 16, 20, 24])
        def check(nodes):
            issues, used = [], set()
            audit.verify_control(expected, {'id': 'head', 'bounds': [0, 0, 300, 64]},
                nodes, lambda n: not n['hidden'], used,
                lambda code, *args: issues.append(code))
            return issues, used
        self.assertEqual(([], {'chevron'}), check([indicator]))
        expected['design']['state'] = 'expanded'
        self.assertIn('PANEL_INDICATOR', check([indicator])[0])
        indicator['text'] = '⌃'
        self.assertEqual(([], {'chevron'}), check([indicator]))
        original = copy.deepcopy(indicator)
        for changes in ({'text': 'arbitrary text'}, {'hidden': True}, {'head': True},
                        {'type': 'rectangle'}, {'parent': 'other'},
                        {'bounds': [300, 16, 20, 24]}, {'bounds': [270, 16, 0, 24]}):
            with self.subTest(changes=changes):
                candidate = dict(original, **changes)
                self.assertEqual((['PANEL_INDICATOR'], set()), check([candidate]))
        self.assertIn('PANEL_INDICATOR', check([])[0])
        self.assertIn('PANEL_INDICATOR', check([original, dict(original, id='duplicate')])[0])
        expected['contract']['internals'] = []
        self.assertEqual(([], set()), check([original]))

    def test_expanded_content_and_headers_cannot_be_hidden(self):
        self.find('SavedTitle')['hidden'] = True
        self.assert_code('HIDDEN_CONTENT')

    def test_fallback_cannot_accept_conflicting_identity(self):
        self.find('SavedTitle')['auditKey'] = 'another-instance|SavedTitle'
        self.assert_code('WRONG_IDENTITY')

    def test_inspection_rejects_invalid_native_source_main(self):
        for changes in ({'head': False}, {'copy': True}, {'family': 'Wrong/Family'},
                        {'componentId': 'another-record'}):
            with self.subTest(changes=changes):
                manifest, snapshot = fixture()
                next(n for n in snapshot['nodes'] if n['id'] == 'main').update(changes)
                result = audit.compare(manifest, snapshot, ['ReviewSessionSaved'], inspect=True)
                self.assertNotEqual('PASS', result['status'])
                self.assertIn('BROKEN_SOURCE', [i['code'] for i in result['issues']], result)

    def test_inspection_rejects_source_state_disagreement(self):
        expected = next(e for e in audit.flatten(self.manifest['scopes']['ReviewSessionSaved']['nodes'])
                        if e['representation'] == 'native')
        expected['variant'] = 'selected'
        next(n for n in self.snapshot['nodes'] if n['copy'])['variant'] = {'State': 'selected'}
        for record_state, main_state in (('available', 'selected'), ('selected', 'available')):
            with self.subTest(record_state=record_state, main_state=main_state):
                self.snapshot['records'][0]['variant'] = {'State': record_state}
                self.find('ProgressBar')['variant'] = {'State': main_state}
                result = audit.compare(self.manifest, self.snapshot, ['ReviewSessionSaved'], inspect=True)
                self.assertIn('WRONG_VARIANT', [i['code'] for i in result['issues']], result)

    def test_opacity_provenance_and_invalid_values(self):
        original = copy.deepcopy(self.snapshot)
        for raw, effective, source, valid in (
            (None, 1, 'penpot-null-default-v1', True),
            (0, 0, 'explicit', True),
            (0.5, 0.5, 'explicit', True),
            (None, 1, 'explicit', False),
            (0, 1, 'penpot-null-default-v1', False),
            (None, 0, 'penpot-null-default-v1', False),
            (1, 1, 'unknown', False),
            (True, 1, 'explicit', False),
            (-1, -1, 'explicit', False),
            (2, 2, 'explicit', False),
            (None, None, 'explicit', False),
            (float('nan'), float('nan'), 'explicit', False),
            (float('inf'), float('inf'), 'explicit', False),
        ):
            with self.subTest(raw=raw, effective=effective, source=source):
                self.snapshot = copy.deepcopy(original)
                self.snapshot['nodes'][0].update(rawOpacity=raw, opacity=effective, opacitySource=source)
                result = self.check()
                self.assertEqual(not valid, result['status'] == 'BLOCKED', result)
                if valid and effective == 0:
                    self.assertNotEqual('PASS', result['status'], result)
        for field in ('rawOpacity', 'opacitySource'):
            self.snapshot = copy.deepcopy(original)
            self.snapshot['nodes'][0].update(rawOpacity=None, opacity=1, opacitySource='penpot-null-default-v1')
            del self.snapshot['nodes'][0][field]
            self.assertEqual('BLOCKED', self.check()['status'])

    def test_resolver_does_not_stop_at_library_slots(self):
        nodes = audit.flatten(audit.build_manifest()['scopes']['ReviewSessionSaved']['nodes'])
        self.assertTrue(any(n['name'] == 'SavedMessageContent' for n in nodes))
        self.assertTrue(any(n.get('family', '').endswith('/ProgressBar') for n in nodes))

    def test_complete_message_shell_is_scoped_and_preserves_semantic_children(self):
        manifest = audit.build_manifest()
        for scope_name in ('ReviewComplete', 'ReviewSessionSaved'):
            nodes = audit.flatten(manifest['scopes'][scope_name]['nodes'])
            messages = [n for n in nodes if n.get('family') == 'Library/PrimeVue/Message']
            self.assertEqual(1, len(messages))
            self.assertEqual('shell', messages[0]['representation'])
            self.assertEqual('library-component', messages[0]['kind'])
        complete = audit.flatten(manifest['scopes']['ReviewComplete']['nodes'])
        content = next(n for n in complete if n.get('name') == 'CompletionMessageContent')
        self.assertEqual('default', content['slot'])
        self.assertEqual(['CompletionTitle', 'CompletionDescription'],
                         [n['name'] for n in content['children']])
        self.assertTrue(all(n['parent'] == content['key'] for n in content['children']))
        policies = json.loads((audit.ROOT / 'design/penpot.json').read_text())['pageStructuralShells']
        self.assertEqual(
            {('ReviewComplete', 'primevue', 'Message'),
             ('ReviewSessionSaved', 'primevue', 'Message')},
            {(p['page'], p['library'], p['component']) for p in policies})

    def test_custom_bindings_use_page_props(self):
        scopes = audit.build_manifest()['scopes']
        nodes = audit.flatten(scopes['custom:CategorySelectionRow:available']['nodes'])
        self.assertIn('Core', [n.get('text') for n in nodes])
        self.assertIn('Добавить', [n['props'].get('label') for n in nodes])

    def test_missing_progress(self):
        bar = next(n for n in self.snapshot['nodes'] if n['copy'])
        self.snapshot['nodes'] = [n for n in self.snapshot['nodes'] if n['id'] != bar['id'] and n['parent'] != bar['id']]
        self.assert_code('MISSING_NODE')

    def test_flattened_progress(self):
        next(n for n in self.snapshot['nodes'] if n['copy'])['parent'] = 'frame'
        self.assert_code('WRONG_PARENT')

    def test_detached_progress(self):
        next(n for n in self.snapshot['nodes'] if n['copy'])['copy'] = False
        self.assert_code('DETACHED_INSTANCE')

    def test_wrong_family(self):
        next(n for n in self.snapshot['nodes'] if n['copy'])['family'] = 'Library / PrimeVue/Button'
        self.assert_code('WRONG_FAMILY')

    def test_visible_percentage(self):
        self.find('Value')['hidden'] = False
        self.assert_code('VISIBLE_PERCENTAGE')

    def test_hidden_ancestor(self):
        self.find('SavedMessageContent')['hidden'] = True
        self.assert_code('HIDDEN_CONTENT')

    def test_changed_text(self):
        self.find('SavedTitle')['text'] = 'wrong'
        self.assert_code('TEXT_MISMATCH')

    def test_duplicate_identity(self):
        duplicate = copy.deepcopy(self.find('SavedTitle'))
        duplicate['id'] = 'duplicate'
        self.snapshot['nodes'].append(duplicate)
        self.assert_code('DUPLICATE_IDENTITY')

    def test_stale_source(self):
        self.snapshot['fingerprint'] = 'stale'
        self.assert_code('INVALID_SNAPSHOT')

    def test_old_timestamp(self):
        self.snapshot['capturedAt'] = '2000-01-01T00:00:00Z'
        self.assert_code('INVALID_SNAPSHOT')

    def test_partial_collection(self):
        self.snapshot['complete'] = False
        self.assertEqual('BLOCKED', self.check()['status'])

    def test_cycle(self):
        self.find('SavedMessageContent')['parent'] = self.find('SavedTitle')['id']
        self.assert_code('INVALID_SNAPSHOT')

    def test_missing_evidence(self):
        del self.find('SavedTitle')['opacity']
        self.assert_code('INVALID_SNAPSHOT')

    def test_missing_slot_evidence(self):
        self.find('SavedMessageContent')['slot'] = None
        self.assert_code('SLOT_UNVERIFIED')

    def test_containment(self):
        self.find('SavedTitle')['bounds'][0] = 500
        self.assert_code('CONTAINMENT')

    def test_unapproved_shell(self):
        e = next(e for e in audit.flatten(self.manifest['scopes']['ReviewSessionSaved']['nodes']) if e['representation'] == 'shell')
        e['representation'] = 'native'
        self.assert_code('DETACHED_INSTANCE')

    def test_unexpected_visible_internal(self):
        self.find('Value').update(hidden=False, text='Action')
        self.assert_code('VISIBLE_PERCENTAGE')

    def test_target_requires_baseline(self):
        result = audit.compare(self.manifest, self.snapshot, ['ReviewSessionSaved'])
        self.assertEqual('BLOCKED', result['status'])
        self.assertIn('BASELINE_REQUIRED', [i['code'] for i in result['issues']])

    def test_inspection_passes_without_baseline_and_reports_limits(self):
        result = audit.compare(self.manifest, self.snapshot, ['ReviewSessionSaved'], inspect=True)
        self.assertEqual('PASS', result['status'], result)
        self.assertEqual('inspection', result['mode'])
        self.assertEqual(['ReviewSessionSaved'], result['requestedScopes'])
        self.assertFalse(result['preservationChecked'])

    def test_inspection_does_not_modify_inputs(self):
        original = copy.deepcopy((self.manifest, self.snapshot))
        audit.compare(self.manifest, self.snapshot, ['ReviewSessionSaved'], inspect=True)
        self.assertEqual(original, (self.manifest, self.snapshot))

    def test_inspection_checks_selected_content_and_source(self):
        for name, changes, code in [
            ('SavedTitle', {'text': 'wrong'}, 'TEXT_MISMATCH'),
            ('SavedTitle', {'hidden': True}, 'HIDDEN_CONTENT'),
            ('SavedTitle', {'bounds': [500, 0, 300, 300]}, 'CONTAINMENT'),
        ]:
            with self.subTest(code=code):
                manifest, snapshot = fixture()
                next(n for n in snapshot['nodes'] if n['name'] == name).update(changes)
                result = audit.compare(manifest, snapshot, ['ReviewSessionSaved'], inspect=True)
                self.assertEqual('FAIL', result['status'], result)
                self.assertIn(code, [i['code'] for i in result['issues']])
        next(n for n in self.snapshot['nodes'] if n['copy'])['refId'] = 'frame'
        result = audit.compare(self.manifest, self.snapshot, ['ReviewSessionSaved'], inspect=True)
        self.assertIn('BROKEN_SOURCE', [i['code'] for i in result['issues']])

    def test_inspection_still_requires_valid_complete_fresh_evidence(self):
        for changes in [{'complete': False}, {'coverage': 'partial'},
                        {'fingerprint': 'stale'}, {'capturedAt': '2000-01-01T00:00:00Z'}]:
            with self.subTest(changes=changes):
                snapshot = copy.deepcopy(self.snapshot)
                snapshot.update(changes)
                result = audit.compare(self.manifest, snapshot, ['ReviewSessionSaved'], inspect=True)
                self.assertEqual('BLOCKED', result['status'], result)
                self.assertFalse(result['preservationChecked'])

    def test_inspection_rejects_change_permissions_and_missing_scopes(self):
        for kwargs in [{}, {'scopes': []}, {'scopes': ['ReviewSessionSaved'], 'baseline': self.snapshot},
                       {'scopes': ['ReviewSessionSaved'], 'allow_families': [self.snapshot['records'][0]['family']]}]:
            with self.subTest(kwargs=kwargs):
                result = audit.compare(self.manifest, self.snapshot, inspect=True, **kwargs)
                self.assertEqual('BLOCKED', result['status'], result)
                self.assertIn('INVALID_INSPECTION_SCOPE', [i['code'] for i in result['issues']])

    def test_inspection_unknown_scope_blocks(self):
        result = audit.compare(self.manifest, self.snapshot, ['unknown'], inspect=True)
        self.assertEqual('BLOCKED', result['status'])
        self.assertIn('UNKNOWN_SCOPE', [i['code'] for i in result['issues']])

    def test_inspection_does_not_certify_unselected_content_or_inventory(self):
        self.manifest['scopes']['Other'] = copy.deepcopy(self.manifest['scopes']['ReviewSessionSaved'])
        self.manifest['scopes']['Other']['frame'] = 'Missing frame'
        self.snapshot['records'].append({'id': 'orphan', 'family': 'Unknown', 'mainId': None, 'variant': {}})
        result = audit.compare(self.manifest, self.snapshot, ['ReviewSessionSaved'], inspect=True)
        self.assertEqual('PASS', result['status'], result)
        self.assertNotEqual('PASS', self.check()['status'])

    def test_inspection_cli_guards_and_exit_codes(self):
        from pathlib import Path
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'snapshot.json'
            path.write_text(json.dumps(self.snapshot))
            command = [sys.executable, '-B', str(audit.ROOT / 'scripts/audit-penpot-drift.py')]
            for args in [['--inspect'], ['--recursive', '--inspect'],
                         ['--recursive', '--inspect', '--snapshot', str(path)],
                         ['--recursive', '--inspect', '--snapshot', str(path), '--scope', 'ReviewSessionSaved', '--baseline', str(path)],
                         ['--recursive', '--inspect', '--snapshot', str(path), '--scope', 'ReviewSessionSaved', '--allow-family', 'Unknown']]:
                with self.subTest(args=args):
                    result = subprocess.run(command + args, text=True, capture_output=True)
                    self.assertEqual(2, result.returncode, result.stdout + result.stderr)
            # The real manifest includes Toolbar omitted by this focused fixture:
            # CLI inspection must surface that drift, not require a fake baseline.
            args = ['--recursive', '--inspect', '--snapshot', str(path), '--scope', 'ReviewSessionSaved']
            result = subprocess.run(command + args, text=True, capture_output=True)
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual('FAIL', report['status'])
            self.assertFalse(report['preservationChecked'])
            self.assertNotIn('BASELINE_REQUIRED', [i['code'] for i in report['issues']])

    def test_review_skill_retains_json_only_and_fail_closed_instructions(self):
        skill = (audit.ROOT / '.cline/skills/design-review/SKILL.md').read_text()
        for instruction in ['JSON-only reviews remain', '**not performed**',
                            '--recursive --snapshot', '--inspect --scope',
                            '**PASS / FAIL / BLOCKED**', 'Do not mutate artwork,',
                            'Never manufacture a baseline', 'Keep those checks separate.']:
            with self.subTest(instruction=instruction):
                self.assertIn(instruction, skill)

    def test_target_pass_with_unchanged_protected_scope(self):
        result = audit.compare(self.manifest, self.snapshot, ['ReviewSessionSaved'], copy.deepcopy(self.snapshot))
        self.assertEqual('PASS', result['status'], result)
        self.assertTrue(result['preservationChecked'])

    def test_target_can_remove_old_stray_child(self):
        baseline = copy.deepcopy(self.snapshot)
        extra = copy.deepcopy(self.find('SavedTitle'))
        extra.update(id='old-stray', auditKey=None)
        baseline['nodes'].append(extra)
        result = audit.compare(self.manifest, self.snapshot, ['ReviewSessionSaved'], baseline)
        self.assertEqual('PASS', result['status'], result)

    def test_target_root_identity_is_preserved(self):
        baseline = copy.deepcopy(self.snapshot)
        for n in self.snapshot['nodes']:
            if n['id'] == 'frame':
                n['id'] = 'replacement'
            if n['parent'] == 'frame':
                n['parent'] = 'replacement'
        result = audit.compare(self.manifest, self.snapshot, ['ReviewSessionSaved'], baseline)
        self.assertIn('TARGET_ROOT_REPLACED', [i['code'] for i in result['issues']])

    def test_cannot_move_protected_object_inside_target(self):
        baseline = copy.deepcopy(self.snapshot)
        self.find('ProgressBar')['parent'] = 'frame'
        self.find('ProgressBar')['pageId'] = 'page'
        result = audit.compare(self.manifest, self.snapshot, ['ReviewSessionSaved'], baseline)
        self.assertIn('PROTECTED_CHANGE', [i['code'] for i in result['issues']])

    def test_explicit_template_permission(self):
        baseline = copy.deepcopy(self.snapshot)
        self.find('ProgressBar')['bounds'][2] = 301
        family = self.snapshot['records'][0]['family']
        result = audit.compare(self.manifest, self.snapshot, ['ReviewSessionSaved'], baseline, allow_families=[family])
        self.assertEqual('PASS', result['status'], result)

    def test_template_permission_requires_all_dependents(self):
        family = self.snapshot['records'][0]['family']
        self.manifest['scopes']['Other'] = copy.deepcopy(self.manifest['scopes']['ReviewSessionSaved'])
        result = audit.compare(self.manifest, self.snapshot, ['ReviewSessionSaved'], self.snapshot, allow_families=[family])
        self.assertIn('DEPENDENT_SCOPE_REQUIRED', [i['code'] for i in result['issues']])

    def test_unknown_family_permission_blocks(self):
        result = audit.compare(self.manifest, self.snapshot, ['ReviewSessionSaved'], self.snapshot, allow_families=['Unknown'])
        self.assertIn('UNKNOWN_FAMILY_SCOPE', [i['code'] for i in result['issues']])

    def test_record_order_does_not_change_preservation(self):
        baseline = copy.deepcopy(self.snapshot)
        baseline['pages'].reverse()
        result = audit.compare(self.manifest, self.snapshot, ['ReviewSessionSaved'], baseline)
        self.assertEqual('PASS', result['status'], result)

    def test_protected_template_change(self):
        baseline = copy.deepcopy(self.snapshot)
        self.find('ProgressBar')['bounds'][2] = 301
        result = audit.compare(self.manifest, self.snapshot, ['ReviewSessionSaved'], baseline)
        self.assertIn('PROTECTED_CHANGE', [i['code'] for i in result['issues']])

    def test_unknown_scope(self):
        result = audit.compare(self.manifest, self.snapshot, ['unknown'])
        self.assertEqual('BLOCKED', result['status'])

    def test_unsupported_state_is_blocked(self):
        bar = next(e for e in audit.flatten(self.manifest['scopes']['ReviewSessionSaved']['nodes']) if e['representation'] == 'native')
        bar['design']['state'] = 'unknown'
        self.assert_code('STATE_UNVERIFIED')

    def test_unresolved_binding(self):
        with self.assertRaisesRegex(ValueError, 'unresolved binding'):
            audit.bind({'bind': 'missing'}, {})

    def test_all_semantic_identities_are_unique(self):
        for scope in audit.build_manifest()['scopes'].values():
            keys = [n['key'] for n in audit.flatten(scope['nodes'])]
            self.assertEqual(len(keys), len(set(keys)))

    def test_malformed_record_is_blocked(self):
        self.snapshot['records'][0] = {'id': 'broken'}
        self.assert_code('INVALID_SNAPSHOT')

    def test_nonfinite_opacity_is_blocked(self):
        self.find('SavedTitle')['opacity'] = float('nan')
        self.assert_code('INVALID_SNAPSHOT')

    def test_zero_size_required_content_fails(self):
        self.find('SavedTitle')['bounds'][2] = 0
        self.assert_code('EMPTY_BOUNDS')

    def test_cross_page_parent_blocks(self):
        self.find('SavedTitle')['pageId'] = 'library'
        self.assert_code('INVALID_SNAPSHOT')

    def test_wrong_source_reference(self):
        next(n for n in self.snapshot['nodes'] if n['copy'])['refId'] = 'frame'
        self.assert_code('BROKEN_SOURCE')

    def test_wrong_custom_state(self):
        expected = self.manifest['scopes']['ReviewSessionSaved']['nodes'][0]
        expected.update(representation='native', family='Component/Example', variant='saved')
        self.assert_code('WRONG_VARIANT')

    def test_missing_rating_option(self):
        expected = self.manifest['scopes']['ReviewSessionSaved']['nodes'][0]
        expected.update(contract={'adapter': 'options', 'textProps': {}, 'internals': [], 'observableStates': ['default']},
                        props={'options': ['1 · плохо', '2 · хорошо']}, design={'state': 'default'})
        self.assert_code('OPTION_MISMATCH')

    def test_legacy_matching_ambiguity(self):
        original = self.find('SavedTitle')
        original['auditKey'] = None
        duplicate = copy.deepcopy(original)
        duplicate['id'] = 'duplicate'
        self.snapshot['nodes'].append(duplicate)
        self.assert_code('AMBIGUOUS_NODE')

    @unittest.skipUnless(shutil.which('node'), 'Node required for collector integration')
    def test_actual_collector_with_mocked_api(self):
        script = '''
const n = {id:'n', type:'text', name:'Title', hidden:false, opacity:1,
 x:1,y:2,width:30,height:20,characters:'hello',fills:[],children:[],
 component:()=>null, isComponentCopyInstance:()=>false,isComponentHead:()=>false,
 componentRefShape:()=>null,getPluginData:()=>''};
const penpot={currentFile:{id:'file',name:'Generated UI (do not edit)',
 pages:[{id:'page',name:'Test',root:{children:[n]}}]},library:{local:{components:[]}}};
const result=(new Function('penpot', COLLECTOR))(penpot);
process.stdout.write(JSON.stringify(result));
'''.replace('COLLECTOR', json.dumps(audit.emit_collector(self.manifest)))
        result = subprocess.run(['node', '-e', script], text=True, capture_output=True, check=True)
        collected = json.loads(result.stdout)
        self.assertTrue(collected['complete'])
        self.assertEqual('hello', collected['nodes'][0]['text'])
        self.assertIsNone(collected['nodes'][0]['parent'])
        self.assertEqual(self.manifest['fingerprint'], collected['fingerprint'])
        for expression, source, effective in (('null', 'penpot-null-default-v1', 1), ('0', 'explicit', 0), ('0.5', 'explicit', 0.5)):
            adapted = script.replace('opacity:1,', f'opacity:{expression},')
            result = subprocess.run(['node', '-e', adapted], text=True, capture_output=True, check=True)
            evidence = json.loads(result.stdout)['nodes'][0]
            self.assertEqual(source, evidence['opacitySource'])
            self.assertEqual(effective, evidence['opacity'])
            self.assertEqual(json.loads(expression), evidence['rawOpacity'])
        result = subprocess.run(['node', '-e', script.replace('opacity:1,', 'opacity:undefined,')],
                                text=True, capture_output=True, check=True)
        evidence = json.loads(result.stdout)['nodes'][0]
        self.assertNotIn('opacity', evidence)
        self.assertNotIn('rawOpacity', evidence)
        failing = script.replace('opacity:1,', "get opacity(){throw Error('opacity unavailable');},")
        result = subprocess.run(['node', '-e', failing], text=True, capture_output=True, check=True)
        self.assertFalse(json.loads(result.stdout)['complete'])
        cyclic = script.replace("const penpot=", "n.children=[n]; const penpot=")
        result = subprocess.run(['node', '-e', cyclic], text=True, capture_output=True, check=True)
        collected = json.loads(result.stdout)
        self.assertFalse(collected['complete'])
        self.assertIn('Duplicate/cyclic', collected['collectionErrors'][0])

    @unittest.skipUnless(shutil.which('node'), 'Node required for transfer integration')
    def test_collector_enumerates_native_variant_records(self):
        script = '''
const variant = (id, state) => ({id, name:'Row',path:'Component',
 mainInstance:()=>({id:'main-'+id}),variantProps:{State:state},isVariant:()=>true});
const a=variant('a','available'), b=variant('b','selected');
const variants={variantComponents:()=>[a,b]};
a.variants=variants; b.variants=variants;
const penpot={currentFile:{id:'file',name:'Generated UI (do not edit)',pages:[]},
 library:{local:{components:[a]}}};
const result=(new Function('penpot', COLLECTOR))(penpot);
process.stdout.write(JSON.stringify(result));
'''.replace('COLLECTOR', json.dumps(audit.emit_collector(self.manifest)))
        def collect(source):
            result = subprocess.run(['node', '-e', source], text=True, capture_output=True, check=True)
            return json.loads(result.stdout)
        result = collect(script)
        self.assertTrue(result['complete'], result)
        self.assertEqual(['a', 'b'], [r['id'] for r in result['records']])
        self.assertEqual(['available', 'selected'], [r['variant']['State'] for r in result['records']])
        result = collect(script.replace('components:[a]', 'components:[a,b]'))
        self.assertTrue(result['complete'], result)
        self.assertEqual(2, len(result['records']))
        for replacement in ('a.variants=null;', 'variants.variantComponents=()=>[];',
                            'variants.variantComponents=()=>[b];',
                            'b.id="a";',
                            'variants.variantComponents=()=>{throw Error("unavailable");};'):
            with self.subTest(replacement=replacement):
                result = collect(script.replace('const penpot=', replacement + '\nconst penpot='))
                self.assertFalse(result['complete'], result)
                self.assertTrue(result['collectionErrors'], result)

    @unittest.skipUnless(shutil.which('node'), 'Node required for transfer integration')
    def test_transfer_roundtrip_unicode_and_corruption(self):
        snapshot = copy.deepcopy(self.snapshot)
        snapshot['unicode'] = 'Привет 🎉 日本語' * 2000
        transfer_js = audit.ROOT.joinpath('scripts/penpot_transfer.js').read_text()
        script = 'const storage={conformanceSnapshot:' + json.dumps(snapshot) + '};\n'
        script += '(new Function("storage", ' + json.dumps(transfer_js) + '))(storage);\n'
        script += 'process.stdout.write(JSON.stringify(storage.conformanceTransfer));'
        result = subprocess.run(['node', '-e', script], text=True, capture_output=True, check=True)
        envelope = json.loads(result.stdout)
        self.assertEqual(snapshot, decode_transfer(envelope))
        with tempfile.TemporaryDirectory() as directory:
            from pathlib import Path
            source, output = Path(directory) / 'transfer.json', Path(directory) / 'snapshot.json'
            source.write_text(json.dumps(envelope))
            command = [sys.executable, '-B', str(audit.ROOT / 'scripts/audit-penpot-drift.py'), '--recursive',
                       '--decode-transfer', str(source), '--snapshot-output', str(output)]
            decoded = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(0, decoded.returncode, decoded.stderr)
            self.assertEqual(snapshot, json.loads(output.read_text()))
            malformed = copy.deepcopy(envelope)
            malformed['checksum'] = 'broken'
            source.write_text(json.dumps(malformed))
            decoded = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(2, decoded.returncode)
        bad = copy.deepcopy(envelope)
        bad['chunks'] = bad['chunks'][:-1]
        with self.assertRaises(ValueError):
            decode_transfer(bad)

        bad = copy.deepcopy(envelope)
        bad['checksum'] = '00000000'
        with self.assertRaisesRegex(ValueError, 'integrity'):
            decode_transfer(bad)
        bad = copy.deepcopy(envelope)
        bad['byteLength'] = 1
        with self.assertRaisesRegex(ValueError, 'exceeds'):
            decode_transfer(bad)
        bad = copy.deepcopy(envelope)
        bad['chunks'][0] = '!!!!'
        with self.assertRaises(ValueError):
            decode_transfer(bad)

    @unittest.skipUnless(shutil.which('node'), 'Node required for emitted transfer syntax')
    def test_emitted_transfer_function_compiles(self):
        javascript = audit.emit_collector(self.manifest, transfer=True)
        result = subprocess.run(['node', '-e', 'new Function("penpot", "storage", ' + json.dumps(javascript) + ');'],
                                text=True, capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)


if __name__ == '__main__':
    unittest.main()