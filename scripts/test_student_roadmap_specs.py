"""Approved roadmap design contracts; these do not execute runtime behavior."""
import json
import unittest
from pathlib import Path

import penpot_conformance as audit

DESIGN = Path(__file__).resolve().parents[1] / 'design'
DIRECTORY = DESIGN / 'pages/student-roadmap'
TYPES = ['Hangman', 'Simulation', 'CurrencyExchange', 'TennisScoreboard', 'CloudStorage', 'TaskScheduler']


def nodes(value):
    if isinstance(value, dict):
        if 'name' in value and value.get('type') in ('library-component', 'custom-component', 'text', 'section', 'row', 'column', 'grid'):
            yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


def load(slug):
    return json.loads((DIRECTORY / (slug + '.page.json')).read_text())


def named(spec, name):
    return next(n for n in nodes(spec['children']) if n.get('name') == name)


class StudentRoadmapSpecTests(unittest.TestCase):
    def test_exact_approved_preview_set(self):
        expected = {
            'my-projects-new', 'my-projects-in-progress', 'my-projects-multilanguage',
            'my-projects-completed', 'my-projects-other-languages',
            'project-type-first-submission', 'project-type-first-submission-with-deployment',
            'project-type-implementations', 'project-type-add-implementation',
            'project-type-submission-error', 'implementation-no-reviews',
            'implementation-with-reviews', 'implementation-no-deployment',
            'implementation-edit-repository', 'implementation-edit-deployment',
            'implementation-repository-error',
        }
        self.assertEqual(expected, {p.name.removesuffix('.page.json') for p in DIRECTORY.glob('*.page.json')})

    def test_progress_is_derived_from_distinct_types_and_all_sources(self):
        for path in DIRECTORY.glob('my-projects-*.page.json'):
            spec = json.loads(path.read_text())
            fixtures = spec['states']['representativeData']['implementations']
            for language in ('Java', 'Python', 'Go'):
                count = len({f['projectType'] for f in fixtures if f['language'] == language})
                controls = {n.get('name'): n for n in nodes(spec['children'])}
                if count:
                    self.assertEqual(f'{language} Backend · {count}/6', controls[language+'ProgressLabel']['value'])
                    self.assertAlmostEqual(round(count/6*100, 2), controls[language+'ProgressBar']['props']['value'])
                else:
                    self.assertNotIn(language+'ProgressBar', controls)
            rows = named(spec, 'ProjectList')['children']
            self.assertEqual([t+'Card' for t in TYPES], [r['name'] for r in rows])
            for kind in TYPES:
                languages = sorted({f['language'] for f in fixtures if f['projectType'] == kind})
                card = named(spec, kind+'Card')
                self.assertEqual('RoadmapProjectCard', card['component'])
                self.assertEqual('custom-component', card['type'])
                self.assertEqual('submitted' if languages else 'notSubmitted', card['variant'])
                self.assertTrue(card['props']['title'].strip())
                self.assertEqual({'type': 'command', 'name': 'open'+kind}, card['action'])
                if languages:
                    self.assertEqual('Языки: '+', '.join(languages), card['props']['languagesText'])
                else:
                    self.assertNotIn('languagesText', card['props'])
                self.assertEqual(kind, spec['states']['openProjectType']['open'+kind]['projectType'])
        multi = load('my-projects-multilanguage')['states']['representativeData']['implementations']
        self.assertEqual({'mini-app', 'telegram-bot', 'import'}, {f['source'] for f in multi})
        self.assertEqual(4, sum(f['language'] == 'Java' for f in multi))
        for slug in ('new', 'other-languages'):
            self.assertFalse(any(n.get('component') == 'ProgressBar' for n in nodes(load('my-projects-'+slug)['children'])))

    def test_submission_visibility_and_deployment_eligibility(self):
        for path in DIRECTORY.glob('project-type-*.page.json'):
            spec = json.loads(path.read_text())
            controls = {n.get('name'): n for n in nodes(spec['children'])}
            expanded = spec['states']['preview']['formExpanded']
            self.assertEqual(expanded, 'SubmissionForm' in controls)
            self.assertEqual(not expanded, 'AddImplementation' in controls)
            if expanded:
                self.assertEqual(spec['states']['projectType'] in TYPES[2:], 'DeploymentField' in controls)
                self.assertEqual('submit', controls['SubmitImplementation']['action']['type'])
            for language in ('Java', 'Python', 'Go'):
                self.assertIn(spec['states']['projectType'], controls['Specification'+language]['action']['url'])
            self.assertIn('global', spec['states']['validation'])
            self.assertIn('all draft fields retained', spec['states']['saveFailure'])
        additional = load('project-type-add-implementation')
        self.assertEqual('Другой язык', named(additional, 'LanguageField')['props']['modelValue'])
        self.assertEqual('Rust', named(additional, 'OtherLanguageField')['props']['modelValue'])
        error = load('project-type-submission-error')
        self.assertTrue(named(error, 'RepositoryField')['props']['invalid'])
        self.assertEqual('invalid', named(error, 'RepositoryField')['design']['state'])

    def test_existing_implementations_have_links_dates_and_identity_actions(self):
        spec = load('project-type-implementations')
        fixtures = spec['states']['representativeData']['implementations']
        for i, item in enumerate(fixtures, 1):
            self.assertEqual(item['repository'], named(spec, f'Implementation{i}Repository')['action']['url'])
            self.assertIn(item['date'], named(spec, f'Implementation{i}Date')['value'])
            self.assertEqual(item['id'], spec['states']['openImplementations'][f'openImplementation{i}']['implementationId'])
            controls = {n.get('name') for n in nodes(spec['children'])}
            self.assertEqual(bool(item['deployment']), f'Implementation{i}Deployment' in controls)

    def test_implementation_editing_preserves_confirmed_data(self):
        for path in DIRECTORY.glob('implementation-*.page.json'):
            spec = json.loads(path.read_text())
            state = spec['states']
            self.assertEqual(state['representativeData']['confirmedRepository'], named(spec, 'RepositoryLink')['action']['url'])
            self.assertIn('old confirmed GitHub URL remains unchanged', state['repositorySaveFailure'])
            self.assertIn('reviews and progress', state['repositorySaveSuccess'])
            self.assertIn('read-only', state['immutable'])
            self.assertFalse(any(n.get('action', {}).get('name') in ('deleteImplementation', 'changeLanguage', 'changeProjectType') for n in nodes(spec['children'])))
        error = load('implementation-repository-error')
        self.assertNotEqual(named(error, 'RepositoryLink')['action']['url'], named(error, 'RepositoryField')['props']['modelValue'])
        self.assertTrue(named(error, 'RepositoryField')['props']['invalid'])
        unsupported = load('implementation-no-reviews')
        self.assertFalse(any(n.get('name') == 'DeploymentSection' for n in nodes(unsupported['children'])))
        self.assertEqual('addDeployment', named(load('implementation-no-deployment'), 'EditDeployment')['action']['name'])
        self.assertEqual('removeDeployment', named(load('implementation-edit-deployment'), 'RemoveDeployment')['action']['name'])

    def test_review_authors_are_plain_text(self):
        spec = load('implementation-with-reviews')
        for i in (1, 2):
            author = named(spec, f'Review{i}Author')
            self.assertEqual('text', author['type'])
            self.assertNotIn('action', author)
            self.assertTrue(named(spec, f'Review{i}Date')['value'])
            self.assertEqual('external-link', named(spec, f'Review{i}Link')['action']['type'])
        named(load('implementation-no-reviews'), 'NoReviews')

    def test_permissions_traceability_accessible_fields_and_stable_names(self):
        for path in DIRECTORY.glob('*.page.json'):
            spec = json.loads(path.read_text())
            self.assertIn('STUDENT', spec['states']['access'])
            self.assertIn('multi-role', spec['states']['access'])
            self.assertIn('meta/business-analytics/functionality/student-roadmap-completion.md', spec['requirements']['sources'])
            self.assertTrue(spec['requirements']['approvedAssumptions'])
            names = []
            for node in nodes(spec['children']):
                names.append(node['name'])
                if node['type'] == 'custom-component':
                    self.assertEqual('RoadmapProjectCard', node['component'])
                if node.get('component') in ('InputText', 'Select'):
                    self.assertTrue(node['props']['aria-label'])
            self.assertEqual(len(names), len(set(names)), path)

    def test_homepage_shortcuts_and_manifest_resolution(self):
        home = json.loads((DESIGN / 'pages/home/homepage.page.json').read_text())
        self.assertIn('submission-choice', home['states']['openProjectSubmission'])
        self.assertIn('MyProjects', home['states']['openOwnProjects'])
        manifest = audit.build_manifest()
        for path in DIRECTORY.glob('*.page.json'):
            spec = json.loads(path.read_text())
            self.assertIn(spec['page'], manifest['scopes'])
        registry = json.loads((DESIGN / 'libraries/primevue.library.json').read_text())
        self.assertEqual('primevue/select', registry['components']['Select']['import'])


if __name__ == '__main__':
    unittest.main()