import unittest
from unittest.mock import patch
from rsc.textnhanh import (tong_doc,
                           search_data,
                           allfile_level,
                           dot)

class TestTongDoc(unittest.TestCase):

    def setUp(self):
        self.mock_data = {
            'dap_an': {
                'file_test': {
                    'A': {
                        'bai_1': {
                            'nghe': {'muc_1': 'nội dung 1', 'muc_2': 'nội dung 2'},
                            'doc': {'muc_1': 'đọc 1'}
                        },
                        'bai_2': {}
                    }
                }
            },
            'ngu_phap': {},
            'kiem_tra': {},
            'noidung_bai': {}
        }
        dot.data = self.mock_data

    def test_search_data_specific_item(self):
        result = search_data('file_test', level='A', bai='bai_1', ky_nang='nghe', muc='muc_1')
        self.assertEqual(result, 'nội dung 1')

    def test_search_data_list_keys(self):
        result = search_data('file_test', level='A', bai='bai_1', return_values_only=False)
        self.assertIn('nghe', result)
        self.assertIn('doc', result)

    def test_search_data_list_values(self):
        result = search_data('file_test', level='A', bai='bai_1', return_values_only=True)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

    def test_search_data_not_found(self):
        res_file = search_data('file_la', level='A')
        self.assertTrue("Không tìm thấy file" in res_file)
        res_level = search_data('file_test', level='C')
        self.assertTrue("Không tìm thấy Level C" in res_level)

    def test_search_data_all_files(self):
        result = search_data(None, level='A', bai='bai_1', ky_nang='nghe', muc='muc_1')
        self.assertIn('nội dung 1', str(result))

    def test_allfile_level_sorting(self):
        dot.data['ngu_phap']['file_2'] = {
            'A': {
                'bai_10': {},
                'bai_2': {}
            }
        }
        result = allfile_level('A')
        expected_order = ['bai_1', 'bai_2', 'bai_10']
        self.assertEqual(result['A'], expected_order)

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.glob')
    def test_load_all_structure(self, mock_glob, mock_exists):
        mock_exists.return_value = True
        mock_glob.return_value = []
        test_obj = tong_doc()
        self.assertIn('dap_an', test_obj.data)
        self.assertIn('ngu_phap', test_obj.data)

if __name__ == '__main__':
    unittest.main()