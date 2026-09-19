"""Read-only asset board contracts, using only synthetic local fixtures."""
from __future__ import annotations

import hashlib
import base64
from contextlib import contextmanager, redirect_stderr
from html.parser import HTMLParser
from html import unescape
import importlib.util
import io
import json
from pathlib import Path
import re
import tempfile
import subprocess
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'drama-studio/scripts/build_production_board.py'


def load_board():
    if not SCRIPT.exists():
        raise AssertionError('production board script not implemented')
    spec = importlib.util.spec_from_file_location('production_board', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.board = load_board()

    def source(self, name='提示词.txt', data=b'Hold.\r\n'):
        path = self.root / name
        path.write_bytes(data)
        return path

    def test_read_and_selection_preserve_bytes_and_hash(self):
        raw = '说明\r\nHold. 🎬 <b>字面</b>\r\n尾注\r\n'.encode('utf-8')
        path = self.source(data=raw)
        source = self.board.read_source(self.root, path)
        self.assertEqual(raw.decode(), source['text'])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), source['sha256'])
        selected = self.board.select_prompt(source, kind='video', start_line=2, end_line=2)
        self.assertEqual('Hold. 🎬 <b>字面</b>\r\n', selected['text'])
        self.assertEqual(raw, path.read_bytes())
        self.assertEqual([2, 2], selected['selection'])

    def test_bom_is_encoding_not_prompt_content(self):
        path = self.source(data=b'\xef\xbb\xbfHello\r\n')
        self.assertEqual('Hello\r\n', self.board.read_source(self.root, path)['text'])

    def test_traversal_and_prefix_sibling_rejected(self):
        project = self.root / 'project'
        project.mkdir()
        outside = self.root / 'project-private'
        outside.mkdir()
        source = outside / 'private.txt'
        source.write_text('outside', encoding='utf-8')
        for value in (source, '../project-private/private.txt'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.board.resolve_source(project, value)

    def test_root_and_file_must_exist_and_be_correct_type(self):
        for root, value in ((self.root/'absent', 'a.txt'), (self.root, self.root),
                            (self.root, 'missing.txt')):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.board.read_source(root, value)

    def test_only_explicit_text_formats(self):
        for name in ('a.html', 'a.svg', 'a.exe', 'a.png'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.board.read_source(self.root, self.source(name))

    def test_network_devices_ads_and_credentials_refused(self):
        for value in ('https://example.org/p.txt', 'javascript:alert(1)', 'data:text/plain,test',
                      '//server/share/a.txt', r'\\server\share\a.txt', r'\\?\C:\a.txt',
                      'NUL', 'COM1.txt', 'p.txt:stream', '.env', 'credentials.json',
                      'cookies.txt', 'secrets/auth.json', 'local-config.json'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.board.resolve_source(self.root, value, must_exist=False)

    def test_symlink_cannot_escape_root(self):
        project = self.root / 'project'
        project.mkdir()
        outside = self.source('outside.txt')
        link = project / 'link.txt'
        try:
            link.symlink_to(outside)
        except OSError as exc:
            self.skipTest(f'symlink unavailable: {exc}')
        with self.assertRaises(ValueError):
            self.board.read_source(project, link)

    def test_bad_utf8_rejected(self):
        with self.assertRaises(ValueError):
            self.board.read_source(self.root, self.source(data=b'\xff'))

    def test_range_requires_both_bounds_valid_kind_and_nonempty_content(self):
        source = self.board.read_source(self.root, self.source())
        for args in ({'kind': 'record'}, {'kind':'image','start_line':1},
                     {'kind':'image','start_line':0,'end_line':1},
                     {'kind':'video','start_line':2,'end_line':1},
                     {'kind':'video','start_line':1,'end_line':8}):
            with self.subTest(args=args), self.assertRaises(ValueError):
                self.board.select_prompt(source, **args)
        with self.assertRaises(ValueError):
            self.board.select_prompt({'text': ' \r\n', 'path': 'empty'}, kind='image')

    def test_unstable_read_is_retried_then_rejected(self):
        path = self.source()
        original = Path.read_bytes
        def changing(file):
            data = original(file)
            file.write_bytes(data + b'changed')
            return data
        with patch.object(Path, 'read_bytes', changing), self.assertRaises(ValueError):
            self.board.read_source(self.root, path)


class AssetProjectionTests(unittest.TestCase):
    def setUp(self):
        self.board = load_board()

    def test_supported_layouts_and_aliases_are_equivalent(self):
        record = {'char_id':'CHAR_A','姓名':'甲','path':'甲.png','type':'character'}
        layouts = ([record], {'assets':[record]}, {'rows':[record]}, {'CHAR_A':record})
        results = [self.board.normalize_assets(data)['rows'] for data in layouts]
        for rows in results:
            self.assertEqual('CHAR_A', rows[0]['id'])
            self.assertEqual('甲.png', rows[0]['file'])
            self.assertEqual('甲', rows[0]['name'])
            self.assertIsNone(rows[0]['usage_status'])
            self.assertIsNone(rows[0]['file_action'])

    def test_panels_share_file_and_identity_reuse_can_need_new_detail(self):
        data = [
            {'id':'SCENE_A','file':'table.png','panel':'P1','decision':'reuse','file_action':'reuse'},
            {'id':'PROP_A','file':'table.png','panel':'P2','decision':'reuse','file_action':'reuse'},
            {'id':'PROP_A','file':'detail.png','decision':'reuse','readiness':'prompt_only','file_action':'generate'},
        ]
        result = self.board.normalize_assets(data)
        summary = self.board.summarize_assets(result['rows'])
        self.assertEqual(2, summary['reference_count'])
        self.assertEqual(2, summary['referenced_file_count'])
        self.assertEqual(1, summary['planned_new_file_count'])
        self.assertEqual('reuse', result['rows'][2]['decision'])
        self.assertTrue(summary['incomplete'])

    def test_reuse_requires_explicit_action_readiness_and_existing_file(self):
        rows = [dict(id=f'A{i}',file=file,file_action='reuse',readiness='file_ready',file_exists=exists)
                for i,(file,exists) in enumerate([('table.png',True),('table.png',True),
                                                ('missing.png',False),('external.png',None)])]
        summary = self.board.summarize_assets(rows)
        self.assertEqual(3, summary['referenced_file_count'])
        self.assertEqual(1, summary['reused_file_count'])
        self.assertTrue(summary['incomplete'])

    def test_character_counts_are_not_fixed(self):
        for count in (1,3,7):
            with self.subTest(count=count):
                rows = [{'char_id':f'C{i}','file':f'{i}.png'} for i in range(count)]
                summary = self.board.summarize_assets(self.board.normalize_assets(rows)['rows'])
                self.assertEqual(count, summary['reference_count'])
                self.assertEqual(count, summary['unknown_file_action_count'])
                self.assertEqual(0, summary['planned_new_file_count'])

    def test_same_identity_multiple_versions_and_unknown_fields_preserved(self):
        rows = [{'id':'A','version':1,'extra':'保留','dependencies':{'status':'pending','id':'B'},'clips':['C01']},
                {'id':'A','version':2,'decision':'new_variant','usage_status':'candidate'}]
        result = self.board.normalize_assets(rows)
        self.assertEqual(2,len(result['rows']))
        self.assertEqual(rows[0],result['rows'][0]['raw'])
        self.assertEqual(rows[0]['dependencies'],result['rows'][0]['dependencies'])
        self.assertEqual(['C01'],result['rows'][0]['clips'])
        self.assertEqual(1,self.board.summarize_assets(result['rows'])['reference_count'])

    def test_conflicting_aliases_and_dictionary_id_warn_without_guessing(self):
        result = self.board.normalize_assets({'A':{'id':'B','path':'a.png','file':'b.png','name':'甲','姓名':'乙'}})
        row = result['rows'][0]
        self.assertIsNone(row['id'])
        self.assertIsNone(row['file'])
        self.assertIsNone(row['name'])
        self.assertGreaterEqual(len(result['warnings']),3)
        self.assertEqual('B',row['raw']['id'])

    def test_same_id_conflicting_identity_is_preserved_but_incomplete(self):
        for field, first, second in (('type','character','scene'), ('name','甲','客厅')):
            with self.subTest(field=field):
                data = [dict(id='A',version='v1',file='same.png',file_action='reuse',
                             readiness='file_ready',**{field:value}) for value in (first,second)]
                result = self.board.normalize_assets(data)
                self.assertTrue(result['warnings'])
                self.assertEqual(data,[row['raw'] for row in result['rows']])
                for row in result['rows']:
                    row['file_exists'] = True
                self.assertTrue(self.board.summarize_assets(result['rows'])['incomplete'])

    def test_same_identity_distinct_versions_files_and_panels_are_not_conflicts(self):
        data = [dict(id='A',name='甲',type='character',version=version,file=file,panel=panel,
                     file_action='reuse',readiness='file_ready')
                for version,file,panel in [('v1','a.png','P1'),('v2','b.png','P2')]]
        result = self.board.normalize_assets(data)
        self.assertEqual([],result['warnings'])
        for row in result['rows']:
            row['file_exists'] = True
        self.assertFalse(self.board.summarize_assets(result['rows'])['incomplete'])

    def test_unknown_layout_bad_entries_and_wrapper_extras_remain_visible(self):
        data = {'旧版说明':['不要丢']}
        result = self.board.normalize_assets(data)
        self.assertTrue(result['warnings'])
        self.assertEqual(data,result['unparsed'])
        result = self.board.normalize_assets({'assets':[{'id':'A'}, '坏条目'], '说明':'保留'})
        self.assertEqual(1,len(result['rows']))
        self.assertIn('坏条目',str(result['unparsed']))
        self.assertIn('保留',str(result['unparsed']))
        self.assertTrue(result['warnings'])

    def test_conflicting_file_actions_are_not_counted_twice_or_as_complete(self):
        rows = [dict(id='A',file='a.png',file_action=action,readiness='file_ready',file_exists=True)
                for action in ('reuse','rework')]
        summary = self.board.summarize_assets(rows)
        self.assertEqual(0,summary['reused_file_count'])
        self.assertEqual(0,summary['planned_new_file_count'])
        self.assertEqual(1,summary['unknown_file_action_count'])
        self.assertTrue(summary['incomplete'])


PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aS1cAAAAASUVORK5CYII=')


class PageParser(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.payloads, self.images, self.scripts = [], [], []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'data-prompt-utf8' in attrs:
            self.payloads.append(base64.b64decode(attrs['data-prompt-utf8']).decode('utf-8'))
        if tag == 'img':
            self.images.append(attrs)
        if tag == 'script':
            self.scripts.append(attrs)


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / '中文项目'
        self.root.mkdir()
        self.board = load_board()

    def write(self, name, content):
        path = self.root / name
        path.write_bytes(content.encode('utf-8') if isinstance(content,str) else content)
        return path

    def assets(self, rows):
        return self.write('assets.json', json.dumps(rows,ensure_ascii=False))

    def test_copy_payload_is_original_not_management_html_or_record(self):
        raw = 'Hold. 🎬\r\n</script><img src=x onerror=alert(1)>\r\n'
        path = self.write('词.txt', raw)
        image = self.write('图片词.md','正脸。\r\n')
        record = self.write('记录.md','=== BLOCK 1 ===\n评审说明，不是词')
        result = self.board.build_board(self.root, record_files=[record],
                    prompts=[{'path':path,'kind':'video'},{'path':image,'kind':'image'}])
        parser = PageParser(result['html'])
        self.assertEqual([raw,'正脸。\r\n'],parser.payloads)
        self.assertEqual([],parser.images)
        self.assertEqual([{}],parser.scripts)
        self.assertIn('评审说明，不是词',result['html'])
        self.assertIn('快照',result['html'])
        self.assertEqual(raw.encode(),path.read_bytes())
        self.assertEqual(3,len(result['sources']))

    def test_explicit_range_and_snapshot_hashes(self):
        path = self.write('多词.txt','说明\r\n甲\r\n乙\r\n尾注')
        spec = {'path':path,'kind':'image','start_line':2,'end_line':3}
        first = self.board.build_board(self.root,prompts=[spec],generated_at='NOW')
        self.assertEqual(['甲\r\n乙\r\n'],PageParser(first['html']).payloads)
        path.write_bytes('说明\r\n新甲\r\n乙\r\n尾注'.encode())
        second = self.board.build_board(self.root,prompts=[spec])
        self.assertNotEqual(first['sources'][0]['sha256'],second['sources'][0]['sha256'])
        self.assertIn('NOW',first['html'])
        self.assertNotIn('新甲',first['html'])

    def test_image_same_file_multiple_panels_one_preview_and_original_usage(self):
        picture = self.write('总表.png',PNG)
        source = self.assets([dict(id=id,file='总表.png',panel=panel,file_action='reuse',
                             readiness='file_ready',usage_status='candidate',version='v1',purpose=purpose)
                        for id,panel,purpose in [('S','P1','场景'),('P','P2','道具')]])
        original = source.read_bytes()
        result = self.board.build_board(self.root,asset_files=[source])
        parser = PageParser(result['html'])
        self.assertEqual(1,len(parser.images))
        self.assertEqual(picture.resolve().as_uri(),parser.images[0].get('data-src'))
        self.assertEqual(1,result['summary']['reused_file_count'])
        self.assertIn('candidate',result['html'])
        self.assertIn('P1',result['html'])
        self.assertIn('P2',result['html'])
        self.assertNotIn('data:image',result['html'])
        self.assertEqual(original,source.read_bytes())

    def test_conflicting_identity_across_sources_names_both_sources(self):
        self.write('same.png',PNG)
        sources = [self.write(name,json.dumps([dict(id='A',version='v1',file='same.png',
                    type=kind,readiness='file_ready',file_action='reuse')]))
                   for name,kind in [('characters.json','character'),('scenes.json','scene')]]
        result = self.board.build_board(self.root,asset_files=sources)
        self.assertTrue(result['summary']['incomplete'])
        warning = '\n'.join(result['warnings'])
        for value in ('A','characters.json','scenes.json'):
            self.assertIn(value,warning)
        for value in ('character','scene'):
            self.assertIn(value,result['html'])

    def test_duplicate_serialized_keys_fail_without_losing_source_data(self):
        cases = [('assets.csv','id,file,file,readiness,file_action\nA,first.png,second.png,file_ready,reuse\n'),
                 ('assets.json','[{"id":"A","file":"first.png","file":"second.png"}]'),
                 ('nested.json','[{"id":"A","dependencies":{"status":"pending","status":"resolved"}}]')]
        for name,content in cases:
            with self.subTest(name=name):
                source = self.write(name,content)
                with self.assertRaisesRegex(ValueError,'[Dd]uplicate|重复'):
                    self.board.build_board(self.root,asset_files=[source])
                self.assertEqual(content.encode('utf-8'),source.read_bytes())

    def test_reuse_overview_distinguishes_path_check_from_image_decoding(self):
        self.write('broken.png',b'\x89PNG\r\n\x1a\ninvalid-image')
        source = self.assets([dict(id='A',file='broken.png',file_action='reuse',readiness='file_ready')])
        result = self.board.build_board(self.root,asset_files=[source])
        self.assertEqual(1,result['summary']['reused_file_count'])
        labels = re.findall(r'<div class="stat"><strong>\d+</strong>(.*?)</div>',result['html'])
        self.assertTrue(any('复用' in label and '解码未核' in label for label in labels))

    def test_missing_disallowed_external_and_fake_images_are_explained(self):
        outside = Path(self.temp.name)/'outside.png'
        outside.write_bytes(PNG)
        fake = self.write('fake.png','<svg onload="bad()"/>')
        svg = self.write('a.svg','<svg/>')
        source = self.assets([{'id':str(i),'file':str(path),'file_action':'reuse','readiness':'file_ready'}
                              for i,path in enumerate(['missing.png',outside,fake,svg,'https://example.org/a.png'])])
        result = self.board.build_board(self.root,asset_files=[source])
        self.assertEqual([],PageParser(result['html']).images)
        self.assertEqual(0,result['summary']['reused_file_count'])
        self.assertGreaterEqual(len(result['warnings']),5)
        self.assertTrue(result['summary']['incomplete'])
        self.assertIn('未预览',result['html'])

    def test_explicit_external_root_allows_only_referenced_file(self):
        external = Path(self.temp.name)/'shared'
        external.mkdir()
        image = external/'shared.png'
        image.write_bytes(PNG)
        (external/'not-used.png').write_bytes(PNG)
        source = self.assets([{'id':'A','file':str(image)}])
        result = self.board.build_board(self.root,asset_files=[source],image_roots=[external])
        self.assertEqual(1,len(PageParser(result['html']).images))
        self.assertNotIn('not-used.png',result['html'])

    def test_unknown_structure_and_pending_dependencies_remain_visible(self):
        source = self.assets({'assets':[{'id':'A','dependencies':{'id':'B','status':'pending'},'unusual':'保留原字段'},
                                          {'id':'C','dependencies':['D']}],'legacy':'原说明'})
        result = self.board.build_board(self.root,asset_files=[source])
        for value in ('保留原字段','原说明','pending','未记录'):
            self.assertIn(value,result['html'])
        self.assertTrue(result['warnings'])

    def test_csp_uses_fixed_hashes_and_local_images_only(self):
        source = self.write('record.txt','<style>body{display:none}</style>')
        result = self.board.build_board(self.root,record_files=[source])
        for required in ("default-src 'none'", "img-src file:", "connect-src 'none'", "script-src 'sha256-", '自动复制不可用', '未加载'):
            self.assertIn(required,unescape(result['html']))
        self.assertNotIn('src="http',result['html'])
        self.assertNotIn('<style>body{display:none}',result['html'])

    def test_illegal_explicit_input_fails_even_with_valid_other_source(self):
        source = self.write('record.txt','ok')
        for extra in ('missing.txt','../outside.txt'):
            with self.assertRaises(ValueError):
                self.board.build_board(self.root,record_files=[source,extra])
        with self.assertRaises(ValueError):
            self.board.build_board(self.root)

    def test_record_only_does_not_claim_zero_complete_assets(self):
        source = self.write('record.txt','本批还有未生成的图。')
        result = self.board.build_board(self.root,record_files=[source])
        self.assertTrue(result['summary']['incomplete'])
        self.assertIn('未提供结构化资产',result['html'])

    def cli(self,*args):
        return subprocess.run([sys.executable,'-X','utf8','-B',str(SCRIPT),'--root',str(self.root),*map(str,args)],
                              cwd=self.temp.name, capture_output=True,text=True,encoding='utf-8')

    def test_cli_exports_one_html_and_requires_overwrite(self):
        source = self.write('词.txt','中文\r\nEnglish 🎬')
        args = ('--video-prompt','词.txt','--output','看板.html')
        result = self.cli(*args)
        self.assertEqual(0,result.returncode,result.stderr)
        self.assertEqual({'词.txt','看板.html'},{p.name for p in self.root.iterdir()})
        self.assertEqual(['中文\r\nEnglish 🎬'],PageParser((self.root/'看板.html').read_text(encoding='utf-8')).payloads)
        self.assertEqual(2,self.cli(*args).returncode)
        self.assertEqual(0,self.cli(*args,'--overwrite').returncode)
        self.assertEqual('中文\r\nEnglish 🎬'.encode(),source.read_bytes())

    def test_cli_invalid_output_input_and_range_are_rejected_without_files(self):
        self.write('词.txt','one\n')
        for args in (('--record','词.txt'), ('--output','x.html'),
                     ('--record','词.txt','--output','../escape.html'),
                     ('--record','词.txt','--output','no-dir/a.html'),
                     ('--record','词.txt','--output','词.txt','--overwrite'),
                     ('--record','missing.txt','--output','x.html'),
                     ('--prompt-range','bad','词.txt','1','1','--output','x.html'),
                     ('--prompt-range','video','词.txt','1','9','--output','x.html')):
            with self.subTest(args=args):
                self.assertEqual(2,self.cli(*args).returncode)
        self.assertEqual({'词.txt'},{p.name for p in self.root.iterdir()})

    def test_output_cannot_overwrite_a_referenced_image_even_if_invalid_html(self):
        source_image = self.write('original.html','ORIGINAL')
        source = self.assets([{'id':'A','file':'original.html'}])
        result = self.cli('--assets',source,'--output',source_image,'--overwrite')
        self.assertEqual(2,result.returncode)
        self.assertEqual('ORIGINAL',source_image.read_text())

    def test_cli_partial_missing_image_is_warning_not_false_success_preview(self):
        source = self.assets([{'id':'A','file':'missing.png'}])
        result = self.cli('--assets',source,'--output','board.html')
        self.assertEqual(0,result.returncode,result.stderr)
        self.assertIn('missing.png',result.stderr)

    def test_overwrite_failure_leaves_original_and_no_temporary_garbage(self):
        self.write('record.txt','data')
        output = self.write('board.html','OLD')
        with redirect_stderr(io.StringIO()), patch.object(self.board.os,'replace',side_effect=OSError('synthetic denial')):
            code = self.board.main(['--root',str(self.root),'--record','record.txt','--output','board.html','--overwrite'])
        self.assertEqual(2,code)
        self.assertEqual('OLD',output.read_text())
        self.assertEqual({'record.txt','board.html'},{p.name for p in self.root.iterdir()})

    def test_new_output_write_failure_does_not_leave_a_partial_board(self):
        self.write('record.txt', 'source')
        output = self.root / 'board.html'
        real_open = Path.open

        @contextmanager
        def limited_open(path, mode='r', *args, **kwargs):
            with real_open(path, mode, *args, **kwargs) as stream:
                if path.resolve() == output.resolve() and mode == 'xb':
                    class FailingDisk:
                        def write(self, data):
                            stream.write(data[:32])
                            raise OSError('synthetic disk full')
                    yield FailingDisk()
                else:
                    yield stream

        with redirect_stderr(io.StringIO()), patch.object(Path, 'open', limited_open):
            code = self.board.main(['--root', str(self.root), '--record', 'record.txt', '--output', 'board.html'])
        self.assertEqual(2, code)
        self.assertEqual({'record.txt'}, {p.name for p in self.root.iterdir()})


if __name__ == '__main__':
    unittest.main()
