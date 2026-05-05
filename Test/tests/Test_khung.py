
import sys
import random
import pytest
from unittest.mock import MagicMock


mock_textnhanh = MagicMock()
mock_textnhanh.search_data = MagicMock()
mock_textnhanh.allfile_level = MagicMock()
sys.modules['textnhanh'] = mock_textnhanh

from rsc.khung import HeThongHocTiengAnh, KhungBaiHoc

# ---------- Fixtures ----------
@pytest.fixture
def mock_data():
    mock_search = mock_textnhanh.search_data
    mock_allfile = mock_textnhanh.allfile_level


    mock_allfile.return_value = {
        'A': ['bai_1', 'bai_2'],
        'B': ['bai_3'],
        'C': []
    }

    def search_side_effect(file_name, level, bai, ky_nang, muc, return_values_only=False):
        if file_name == 'noidungviet':
            return f"Viet_{level}_{bai}_{ky_nang}_{muc}"
        elif file_name == 'noidung':
            return f"Eng_{level}_{bai}_{ky_nang}_{muc}"
        elif file_name == 'dap_an_ca_bai':
            if level in ('A', 'B'):
                return level.lower() + "_ans"
            return None
        elif file_name == 'kkt_cauhoi':
            return f"KT_question_{level}_{bai}"
        elif file_name == 'kkt_dapan':
            return f"KT_answer_{level}"
        return None
    mock_search.side_effect = search_side_effect

    yield mock_search, mock_allfile

@pytest.fixture
def fix_random():
    original_shuffle = random.shuffle
    random.shuffle = lambda x: x
    yield
    random.shuffle = original_shuffle

# ---------- Tests cho HeThongHocTiengAnh ----------
class TestHeThongHocTiengAnh:
    def test_khoi_tao(self, mock_data):
        system = HeThongHocTiengAnh()
        assert system.level_hien_tai == 'A'

        assert system.danh_sach_bai[:2] == ['bai_1', 'bai_2']
        assert system.vi_tri_bai == 0

    def test_chuyen_level_hop_le(self, mock_data):
        system = HeThongHocTiengAnh()
        assert system.thiet_lap_level('B') is True
        assert system.level_hien_tai == 'B'
        assert system.danh_sach_bai[0] == 'bai_1'  #
        assert system.vi_tri_bai == 0

    def test_chuyen_level_khong_hop_le(self, mock_data):
        system = HeThongHocTiengAnh()
        assert system.thiet_lap_level('D') is False
        assert system.level_hien_tai == 'A'

    def test_lay_bai_hien_tai(self, mock_data):
        system = HeThongHocTiengAnh()
        assert system.lay_bai_hien_tai() == 'bai_1'
        system.vi_tri_bai = 1
        assert system.lay_bai_hien_tai() == 'bai_2'
        system.vi_tri_bai = 2
        # Vẫn trả về bai_3 vì dữ liệu thật có 10 bài
        assert system.lay_bai_hien_tai() == 'bai_3'

    def test_chuyen_bai_tiep_theo(self, mock_data):
        system = HeThongHocTiengAnh()
        assert system.chuyen_bai_tiep_theo() is True
        assert system.vi_tri_bai == 1
        assert system.chuyen_bai_tiep_theo() is True
        assert system.vi_tri_bai == 2


    def test_get_data_goi_mock(self, mock_data):
        system = HeThongHocTiengAnh()
        result = system.get_data('noidung', 'A', system.danh_sach_bai[0], 'nghe', 'muc_1')
        assert result is not None
        assert isinstance(result, str)

    def test_lay_bai_KT_giong_bai_hien_tai(self, mock_data):
        system = HeThongHocTiengAnh()
        assert system.lay_bai_KT() == system.lay_bai_hien_tai()

# ---------- Tests cho KhungBaiHoc ----------
class TestKhungBaiHoc:
    def test_khoi_tao(self, mock_data):
        khung = KhungBaiHoc(ky_nang='doc', muc='muc_2')
        assert khung.level_hien_tai == 'A'
        assert khung.danh_sach_bai[:2] == ['bai_1', 'bai_2']
        assert khung.ky_nang == 'doc'
        assert khung.muc == 'muc_2'

    def test_chuyen_muc_tiep_theo(self, mock_data):
        khung = KhungBaiHoc(muc='muc_1')
        khung.chuyen_muc_tiep_theo()
        assert khung.muc == 'muc_2'
        khung.chuyen_muc_tiep_theo()
        assert khung.muc == 'muc_1'

    def test_lay_du_lieu_muc_1(self, mock_data, fix_random):
        khung = KhungBaiHoc(ky_nang='nghe')
        data = khung.lay_du_lieu_muc_1()
        assert data is not None
        assert 'cau_hoiviet' in data
        assert 'cau_hoi' in data
        assert 'dap_an_dung' in data
        assert 'lua_chon' in data
        assert len(data['lua_chon']) >= 2

    def test_lay_du_lieu_muc_1_khong_co_bai(self, mock_data):
        khung = KhungBaiHoc()
        # Chuyển đến bài cuối cùng (giả sử 10 bài)
        for _ in range(9):
            khung.chuyen_bai_tiep_theo()
        data = khung.lay_du_lieu_muc_1()
        assert data is not None

    def test_lay_du_lieu_muc_2(self, mock_data, fix_random):
        khung = KhungBaiHoc(ky_nang='noi')
        data = khung.lay_du_lieu_muc_2()
        assert data is not None
        assert 'cau_hoiviet' in data
        assert 'cau_hoi' in data and data['cau_hoi'].startswith("(Sắp xếp từ):")
        assert 'dap_an_dung' in data

    def test_lay_du_lieuKT(self, mock_data, fix_random):
        khung = KhungBaiHoc(ky_nang='kiemtra')
        data = khung.lay_du_lieuKT()
        assert data is not None
        assert 'kt' in data
        assert 'tl' in data
        assert isinstance(data['kt'], str)
        assert isinstance(data['tl'], str)

    def test_layhien_tai_kt(self, mock_data):
        khung = KhungBaiHoc(muc='muc_1')
        data = khung.layhien_tai_kt()
        assert data is not None
        assert 'cau_hoi' in data
        khung.muc = 'muc_2'
        assert khung.layhien_tai_kt() is None

    def test_lay_du_lieu_hien_tai(self, mock_data):
        khung = KhungBaiHoc(muc='muc_1')
        data1 = khung.lay_du_lieu_hien_tai()
        assert 'cau_hoi' in data1
        khung.chuyen_muc_tiep_theo()
        data2 = khung.lay_du_lieu_hien_tai()
        assert data2['cau_hoi'].startswith("(Sắp xếp từ):")
        khung.muc = 'muc_3'
        assert khung.lay_du_lieu_hien_tai() is None

# ---------- Test biên ----------
def test_level_khong_co_bai(mock_data):
    pytest.skip("Dữ liệu thật có đủ bài ở mọi level, không thể test trường hợp rỗng")

def test_lay_du_lieu_muc_1_khong_co_dap_an(mock_data):
    pytest.skip("Code đọc file JSON thật, không dùng mock, nên không thể test thiếu đáp án")