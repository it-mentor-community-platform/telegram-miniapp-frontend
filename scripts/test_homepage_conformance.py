"""Observable Homepage state/content evidence, independent of audit stamps."""
import copy
import unittest

import penpot_conformance as audit


class HomepageControlTests(unittest.TestCase):
    def verify(self, expected, nodes):
        issues, used = [], set()
        def issue(code, *args):
            issues.append(code)
        audit.verify_control(expected, nodes[0], nodes, lambda n: not n['hidden'] and n['opacity'] > 0,
                             used, issue)
        return issues, used

    def node(self, id_, parent=None, **values):
        return dict(id=id_, parent=parent, name=id_, type='board', head=False,
                    hidden=False, opacity=1, bounds=[0, 0, 300, 90], text=None, **values)

    def expected(self, component, props, state='default'):
        manifest = audit.build_manifest()
        contract = manifest['families'][f'Library/PrimeVue/{component}']['contract']
        return dict(key='test', family=f'Library/PrimeVue/{component}', props=props,
                    contract=contract, design={'state': state})

    def test_locked_avatar_requires_actual_muting_and_visible_label(self):
        expected = self.expected('Avatar', {'label': '🎯'}, 'locked')
        nodes = [self.node('avatar'), self.node('label', 'avatar')]
        nodes[1].update(name='Label', type='text', text='🎯')
        self.assertIn('LOCKED_APPEARANCE', self.verify(expected, nodes)[0])
        nodes[0]['opacity'] = 0.5
        self.assertEqual([], self.verify(expected, nodes)[0])
        nodes[1]['hidden'] = True
        self.assertIn('CONTROL_TEXT', self.verify(expected, nodes)[0])

    def timeline(self):
        items = [dict(icon='✅', title='Project', description='Java', time='Today'),
                 dict(icon='🏆', title='Achievement', description='First', time='Yesterday')]
        nodes = [self.node('timeline')]
        for i, item in enumerate(items):
            row = self.node(f'row{i}', 'timeline')
            row.update(name=f'TimelineItem{i}', bounds=[0, i * 100, 300, 90])
            content = self.node(f'content{i}', row['id'])
            content['name'] = 'Content'
            marker = self.node(f'marker{i}', row['id'])
            marker.update(name='Marker', type='ellipse')
            title = self.node(f'title{i}', content['id'])
            title.update(name='Title', type='text', text=f"{item['icon']} {item['title']}")
            time = self.node(f'time{i}', content['id'])
            time.update(name='Time', type='text', text=f"{item['description']}\n{item['time']}")
            nodes.extend([row, content, marker, title, time])
        return self.expected('Timeline', {'value': items}), nodes

    def test_timeline_accounts_for_exact_ordered_content(self):
        expected, nodes = self.timeline()
        issues, used = self.verify(expected, nodes)
        self.assertEqual([], issues)
        self.assertEqual({n['id'] for n in nodes[1:]}, used)

    def test_timeline_rejects_wrong_content_order_visibility_and_structure(self):
        expected, original = self.timeline()
        for id_, changes, code in (
                ('title0', {'text': 'Wrong'}, 'TIMELINE_ITEM'),
                ('time0', {'text': 'Yesterday'}, 'TIMELINE_ITEM'),
                ('marker0', {'hidden': True}, 'TIMELINE_ITEM'),
                ('content0', {'parent': 'timeline'}, 'TIMELINE_ITEM'),
                ('title0', {'head': True}, 'TIMELINE_ITEM'),
                ('row1', {'bounds': [0, 0, 300, 90]}, 'TIMELINE_ORDER')):
            with self.subTest(id_=id_, changes=changes):
                nodes = copy.deepcopy(original)
                next(n for n in nodes if n['id'] == id_).update(changes)
                self.assertIn(code, self.verify(expected, nodes)[0])


if __name__ == '__main__':
    unittest.main()