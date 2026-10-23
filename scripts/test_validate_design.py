"""Regression tests for explicit per-state custom compositions (stdlib only)."""
import copy
import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name('validate-design.py')
SPEC = importlib.util.spec_from_file_location('validate_design', SCRIPT)
design = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = design
SPEC.loader.exec_module(design)


class CustomStateTests(unittest.TestCase):
    def setUp(self):
        self.validator = design.Validator()
        self.validator.validate_tokens()
        self.validator.validate_libraries()
        self.validator.validate_custom_components()
        self.assertEqual([], self.validator.errors)
        self.document = copy.deepcopy(self.validator.custom_components['CategoryReviewCard'])
        self.validator.custom_components['CategoryReviewCard'] = self.document

    def validate(self):
        self.validator.validate_custom_states(self.document, 'CategoryReviewCard')
        return '\n'.join(self.validator.errors)

    def primary(self, state='active'):
        return self.document.value['variants'][state]['composition']['slots']['footer'][0]

    def test_all_seven_states_validate(self):
        self.assertEqual(7, sum(len(d.value['variants']) for d in self.validator.custom_components.values()))
        self.assertEqual('', self.validate())

    def test_legacy_shared_composition_rejected(self):
        self.document.value['composition'] = {}
        self.assertIn('unsupported custom field', self.validate())

    def test_arbitrary_flags_rejected(self):
        self.document.value['variants']['active']['loading'] = False
        self.assertIn('exactly previewProps and composition', self.validate())

    def test_missing_composition_rejected(self):
        del self.document.value['variants']['active']['composition']
        self.assertIn('exactly previewProps and composition', self.validate())

    def test_duplicate_names_rejected(self):
        self.primary()['name'] = 'Title'
        self.assertIn('duplicate node name', self.validate())

    def test_unnamed_control_rejected(self):
        del self.primary()['name']
        self.assertIn('every state node requires', self.validate())

    def test_binding_type_rejected(self):
        self.primary()['props']['disabled'] = {'bind': 'title'}
        self.assertIn('must have type boolean', self.validate())

    def test_unknown_preview_rejected(self):
        self.document.value['variants']['active']['previewProps']['unknown'] = 'x'
        self.assertIn('unknown preview prop', self.validate())

    def test_missing_required_preview_rejected(self):
        del self.document.value['variants']['active']['previewProps']['title']
        self.assertIn('missing required prop', self.validate())

    def test_preview_type_rejected(self):
        self.document.value['variants']['active']['previewProps']['title'] = False
        self.assertIn('must be string', self.validate())

    def test_loading_state_requires_loading_prop(self):
        self.primary('loading')['props']['loading'] = False
        self.assertIn('must be true for loading design state', self.validate())

    def test_loading_prop_requires_loading_state(self):
        self.primary()['props']['loading'] = True
        self.assertIn('must be loading when loading is true', self.validate())

    def test_disabled_prop_requires_disabled_state(self):
        self.primary()['props']['disabled'] = True
        self.assertIn('must be disabled', self.validate())

    def test_library_allowlist_in_every_state(self):
        self.primary('nothingDue')['props']['invented'] = True
        self.assertIn('does not declare this prop', self.validate())

    def test_preview_cannot_contain_bindings(self):
        self.document.value['variants']['active']['previewProps']['title'] = {'bind': 'title'}
        self.assertIn('bindings are only allowed', self.validate())

    def test_dependency_in_later_state_is_checked(self):
        self.document.value['variants']['loading']['composition'] = {
            'type': 'custom-component', 'name': 'RecursiveCard',
            'component': 'CategoryReviewCard', 'variant': 'active',
            'props': self.document.value['variants']['active']['previewProps'],
        }
        self.validate()
        self.validator.validate_cycles()
        self.assertIn('cycle:', '\n'.join(self.validator.errors))

    def test_optional_bound_preview_is_required(self):
        self.document.value['props']['title']['required'] = False
        del self.document.value['variants']['active']['previewProps']['title']
        self.assertIn('missing bound preview prop', self.validate())

    def test_bound_preview_enum_is_checked(self):
        self.primary()['props']['severity'] = {'bind': 'title'}
        self.assertIn('bound preview must be one of', self.validate())

    def test_missing_explicit_button_flags_rejected(self):
        del self.primary()['props']['loading']
        self.assertIn('require literal disabled and loading booleans', self.validate())

    def test_unknown_binding_rejected(self):
        self.primary()['props']['label'] = {'bind': 'unknown'}
        self.assertIn('unknown binding', self.validate())

    def test_structural_shell_families_are_validated(self):
        self.validator.validate_structural_card_shells(['CategoryReviewCard', 'CategorySelectionRow'], design.PENPOT)
        self.assertEqual([], self.validator.errors)

    def test_unknown_structural_shell_rejected(self):
        self.validator.validate_structural_card_shells(['Unknown'], design.PENPOT)
        self.assertIn('unknown custom family', '\n'.join(self.validator.errors))

    def test_duplicate_structural_shell_rejected(self):
        self.validator.validate_structural_card_shells(['CategoryReviewCard'] * 2, design.PENPOT)
        self.assertIn('unique family names', '\n'.join(self.validator.errors))

    def test_non_card_structural_shell_rejected(self):
        self.document.value['variants']['active']['composition']['component'] = 'Button'
        self.validator.validate_structural_card_shells(['CategoryReviewCard'], design.PENPOT)
        self.assertIn('must have a PrimeVue Card root', '\n'.join(self.validator.errors))


class PageShellTests(unittest.TestCase):
    def setUp(self):
        self.validator = design.Validator()
        self.validator.pages = {'Homepage': None}

    def check(self, names):
        self.validator.validate_page_structural_card_shells(names, design.PENPOT)
        return '\n'.join(self.validator.errors)

    def test_approved_page(self):
        self.assertEqual('', self.check(['Homepage']))

    def test_unknown_page(self):
        self.assertIn('unknown page', self.check(['Unknown']))

    def test_duplicate_page(self):
        self.assertIn('unique page names', self.check(['Homepage', 'Homepage']))

    def test_invalid_list(self):
        self.assertIn('array of page names', self.check('Homepage'))

    def test_invalid_member(self):
        self.assertIn('array of page names', self.check([None]))


class ScopedShellTests(unittest.TestCase):
    def setUp(self):
        self.validator = design.Validator()
        self.validator.validate_tokens()
        self.validator.validate_libraries()
        self.validator.validate_custom_components()
        self.validator.validate_pages()
        self.assertEqual([], self.validator.errors)
        self.policy = {'page': 'ReviewSessionSaved', 'library': 'primevue', 'component': 'Message'}

    def check(self, entries):
        self.validator.validate_page_structural_shells(entries, design.PENPOT)
        return '\n'.join(self.validator.errors)

    def test_saved_message_policy(self):
        self.assertEqual('', self.check([self.policy]))

    def test_empty_policy_list(self):
        self.assertEqual('', self.check([]))

    def test_invalid_list(self):
        self.assertIn('array of scoped shell policies', self.check({}))

    def test_malformed_entries(self):
        for entry in [None, {}, dict(self.policy, extra=True), dict(self.policy, page=None), dict(self.policy, page='')]:
            with self.subTest(entry=entry):
                self.validator.errors.clear()
                self.assertIn('requires exactly', self.check([entry]))

    def test_duplicate_policy(self):
        self.assertIn('duplicate scoped shell policy', self.check([self.policy, self.policy]))

    def test_unknown_page(self):
        self.assertIn('unknown page', self.check([dict(self.policy, page='Unknown')]))

    def test_unknown_component(self):
        self.assertIn('unknown library component', self.check([dict(self.policy, component='Unknown')]))

    def test_unknown_library(self):
        self.assertIn('unknown library component', self.check([dict(self.policy, library='unknown')]))

    def test_leaf_control_cannot_be_shell(self):
        self.assertIn('slot-bearing', self.check([dict(self.policy, component='InputText')]))

    def test_component_must_exist_on_page(self):
        self.assertIn('does not reference', self.check([dict(self.policy, page='CategorySetup')]))


if __name__ == '__main__':
    unittest.main()