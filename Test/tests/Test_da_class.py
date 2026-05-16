import sys
import pytest
from unittest.mock import Mock, patch, mock_open

from rsc.da_class import (
    LopKyNang, LopNghe, LopDoc, LopViet, LopNoi,
    LopKiemTra, Ghichu, NguPhap
)

# ----------------------------------------------------------------------
# Create a dummy KhungBaiHoc class (replaces the missing module)
# ----------------------------------------------------------------------
class DummyKhungBaiHoc:
    def __init__(self, **kwargs):
        self.level_hien_tai = kwargs.get('level_hien_tai', 'A')
        self.danh_sach_bai = ['bai_1', 'bai_2', 'bai_3']
        self.vi_tri_bai = 0

    def thiet_lap_level(self, level):
        self.level_hien_tai = level
        self.danh_sach_bai = ['bai_1', 'bai_2', 'bai_3']

    def lay_bai_hien_tai(self):
        if self.vi_tri_bai < len(self.danh_sach_bai):
            return self.danh_sach_bai[self.vi_tri_bai]
        return None

    def get_data(self, field, sub, bai, ky_nang, muc, *args):
        # For muc2 cau_hoi we need a short sentence (3 words) to get length 3 after shuffle
        if field == 'noidung' and muc == 'muc_2':
            return "word1 word2 word3"
        elif field == 'noidungviet':
            return f"Vietnamese {sub}"
        elif field == 'noidung':
            return f"English {sub}"
        elif field == 'dap_an_ca_bai':
            return f"answer_{sub.lower()}"
        elif field == 'ktt_cauhoi':
            return f"Question for {ky_nang}"
        elif field == 'ktt_dapan':
            return f"Answer for {ky_nang}"
        return None

    def lay_du_lieu_muc_1(self):
        return {
            "cau_hoiviet": "Câu hỏi tiếng Việt",
            "cau_hoi": "English question",
            "lua_chon": ["Option A", "Option B", "Option C"],
            "dap_an_dung": "correct"
        }

    def lay_du_lieu_muc_2(self):
        return {
            "cau_hoiviet": "Câu hỏi tiếng Việt mức 2",
            "cau_hoi": "English question level 2",
            "lua_chon": ["Choice X", "Choice Y", "Choice Z"],
            "dap_an_dung": "correct2"
        }

# ----------------------------------------------------------------------
# Patch the missing modules BEFORE importing da_class
# ----------------------------------------------------------------------
sys.modules['khung'] = Mock()
sys.modules['khung'].KhungBaiHoc = DummyKhungBaiHoc
sys.modules['textnhanh'] = Mock()
sys.modules['textnhanh'].dot = Mock()

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def mock_dot():
    nguphap_data = {
        'A': {'bai_1': {'Present Simple': 'Used for habits...', 'Past Simple': 'Actions completed...'}},
        'B': {'bai_1': {'Conditionals': 'If clauses...'}}
    }
    kiemtra_data = {
        'A': {
            'bai_1': {
                'nghe': {'muc_1': {'ktt_cauhoi': 'What is the capital?', 'ktt_dapan': 'Hanoi'}},
                'noi': {'muc_1': {'ktt_cauhoi': 'Speak the answer', 'ktt_dapan': 'hello'}},
                'doc': {'muc_1': {'ktt_cauhoi': 'Read the text', 'ktt_dapan': 'reading answer'}},
                'viet': {'muc_1': {'ktt_cauhoi': 'Write the word', 'ktt_dapan': 'writing answer'}}
            }
        }
    }
    def dot_get_side_effect(key, filename):
        if filename == 'nguphap':
            return nguphap_data
        return kiemtra_data
    with patch('rsc.da_class.dot') as mock_dot_obj:
        mock_dot_obj.get = Mock(side_effect=dot_get_side_effect)
        yield mock_dot_obj

# ----------------------------------------------------------------------
# Tests for LopKyNang base class
# ----------------------------------------------------------------------

def test_lopkynang_init():
    kn = LopKyNang(level='A', so_bai=1, ky_nang='test')
    assert kn.ky_nang == 'test'
    assert kn.muc == 'muc_1'
    assert len(kn.danh_sach_bai) == 1

def test_lopkynang_init_not_found():
    with pytest.raises(ValueError, match="Không tìm thấy bài 99"):
        LopKyNang(level='A', so_bai=99, ky_nang='test')

def test_hien_thi_cau_hoi(capsys):
    kn = LopKyNang(level='A', so_bai=1, ky_nang='test')
    data = {
        "cau_hoiviet": "Câu hỏi Việt",
        "cau_hoi": "English question",
        "lua_chon": ["A", "B", "C"],
        "dap_an_dung": "B"
    }
    lua_chon, dap_an = kn._hien_thi_cau_hoi(data)
    captured = capsys.readouterr()
    assert "Câu hỏi Việt" in captured.out
    assert "English question" in captured.out
    assert "1. A" in captured.out
    assert lua_chon == ["A", "B", "C"]
    assert dap_an == "B"

def test_thuc_hien_muc_success(monkeypatch):
    kn = LopKyNang(level='A', so_bai=1, ky_nang='test')
    kn._lay_du_lieu_hien_tai = Mock(return_value={
        "cau_hoiviet": "test",
        "cau_hoi": "test",
        "lua_chon": ["yes", "no"],
        "dap_an_dung": "yes"
    })
    monkeypatch.setattr('builtins.input', lambda _: "yes")
    assert kn.thuc_hien_muc() is True

def test_thuc_hien_muc_fail(monkeypatch):
    kn = LopKyNang(level='A', so_bai=1, ky_nang='test')
    kn._lay_du_lieu_hien_tai = Mock(return_value={
        "cau_hoiviet": "test",
        "cau_hoi": "test",
        "lua_chon": ["yes", "no"],
        "dap_an_dung": "yes"
    })
    monkeypatch.setattr('builtins.input', lambda _: "no")
    assert kn.thuc_hien_muc() is False

def test_run_success_both_levels():
    kn = LopKyNang(level='A', so_bai=1, ky_nang='test')
    kn.thuc_hien_muc = Mock(side_effect=[True, True])
    assert kn.run() is True
    assert kn.muc == 'muc_2'
    assert kn.thuc_hien_muc.call_count == 2

def test_run_fail_first():
    kn = LopKyNang(level='A', so_bai=1, ky_nang='test')
    kn.thuc_hien_muc = Mock(return_value=False)
    assert kn.run() is False
    assert kn.thuc_hien_muc.call_count == 1

# ----------------------------------------------------------------------
# Tests for LopNghe (corrected generator handling)
# ----------------------------------------------------------------------

def test_lopnghe_muc1_generator():
    nghe = LopNghe(level='A', so_bai=1)
    gen = nghe.muc1()
    # First yield: cau_hoiviet
    typ, *vals = next(gen)
    assert typ == 'cau_hoiviet'
    assert len(vals) == 3
    # Second yield: cau_hoi
    typ, *vals = next(gen)
    assert typ == 'cau_hoi'
    assert len(vals) == 3
    # Third yield: dap_an (this yields the correct answer)
    typ, *vals = next(gen)
    assert typ == 'dap_an'
    assert len(vals) == 3
    correct_answer = vals[0]   # lấy đáp án đúng từ generator
    # Fourth yield: 'wait'
    wait_val = next(gen)
    assert wait_val == 'wait'
    # Send the correct answer
    result = gen.send(correct_answer)
    assert result == ('result', 'next')

def test_lopnghe_muc2_generator():
    nghe = LopNghe(level='A', so_bai=1)
    gen = nghe.muc2()
    # First yield: cau_hoiviet
    typ, *vals = next(gen)
    assert typ == 'cau_hoiviet'
    assert len(vals) == 3
    # Second yield: cau_hoi (shuffled words)
    typ, *vals = next(gen)
    assert typ == 'cau_hoi'
    assert len(vals) > 0
    # Third yield: dap_an
    typ, *vals = next(gen)
    assert typ == 'dap_an'
    assert len(vals) == 3
    correct_answer = vals[0]
    # Fourth yield: 'wait'
    wait_val = next(gen)
    assert wait_val == 'wait'
    # Send answer
    result = gen.send(correct_answer)
    assert result == ('result', 'done')

# ----------------------------------------------------------------------
# Tests for LopNoi
# ----------------------------------------------------------------------

@patch('rsc.da_class.sr.Recognizer')
@patch('rsc.da_class.sr.Microphone')
def test_lopnoi_init_with_mic(mock_mic, mock_recognizer):
    mock_mic.return_value.__enter__ = Mock()
    mock_mic.return_value.__exit__ = Mock()
    noi = LopNoi(level='A', so_bai=1, ky_nang='noi')
    assert noi.has_mic is True

@patch('rsc.da_class.sr.Recognizer')
@patch('rsc.da_class.sr.Microphone', side_effect=Exception("No mic"))
def test_lopnoi_init_no_mic(mock_mic, mock_recognizer):
    noi = LopNoi(level='A', so_bai=1, ky_nang='noi')
    assert noi.has_mic is False

def test_lopnoi_thuc_hien_mic_success(monkeypatch):
    with patch('rsc.da_class.sr.Recognizer') as mock_recog:
        mock_recog_instance = Mock()
        mock_recog.return_value = mock_recog_instance
        mock_recog_instance.recognize_google = Mock(return_value="correct answer")
        mock_recog_instance.listen = Mock()
        mock_recog_instance.adjust_for_ambient_noise = Mock()
        with patch('rsc.da_class.sr.Microphone') as mock_mic:
            mock_mic.return_value.__enter__ = Mock()
            mock_mic.return_value.__exit__ = Mock()
            noi = LopNoi(level='A', so_bai=1, ky_nang='noi')
            noi._lay_du_lieu_hien_tai = Mock(return_value={
                "cau_hoiviet": "viet",
                "cau_hoi": "eng",
                "lua_chon": ["correct answer", "wrong"],
                "dap_an_dung": "correct answer"
            })
            monkeypatch.setattr('builtins.input', lambda _: "")
            assert noi.thuc_hien_muc() is True

def test_lopnoi_thuc_hien_fallback_input(monkeypatch):
    with patch('rsc.da_class.sr.Recognizer') as mock_recog:
        mock_recog_instance = Mock()
        mock_recog.return_value = mock_recog_instance
        mock_recog_instance.recognize_google = Mock(side_effect=Exception("recog fail"))
        mock_recog_instance.listen = Mock()
        with patch('rsc.da_class.sr.Microphone'):
            noi = LopNoi(level='A', so_bai=1, ky_nang='noi')
            noi._lay_du_lieu_hien_tai = Mock(return_value={
                "cau_hoiviet": "viet",
                "cau_hoi": "eng",
                "lua_chon": ["correct", "wrong"],
                "dap_an_dung": "correct"
            })
            inputs = iter(["correct", "", ""])
            monkeypatch.setattr('builtins.input', lambda _: next(inputs))
            assert noi.thuc_hien_muc() is True

# ----------------------------------------------------------------------
# Tests for LopKiemTra
# ----------------------------------------------------------------------

def test_lopkiemtra_lay_du_lieu_bai(mock_dot):
    kt = LopKiemTra(level_hien_tai='A')
    def get_data_side(field, level, bai, kn, muc):
        if field == 'ktt_cauhoi':
            return 'What is the capital?'
        elif field == 'ktt_dapan':
            return 'Hanoi' if level == 'A' else None
        return None
    kt.get_data = Mock(side_effect=get_data_side)
    data = kt.lay_du_lieu_bai('nghe', 1)
    assert data is not None
    assert data['q'] == 'What is the capital?'
    assert data['a'] == 'Hanoi'
    assert len(data['opts']) == 1
    assert data['opts'][0] == 'Hanoi'

def test_lopkiemtra_hoc_mot_bai_success(mock_dot, monkeypatch, capsys):
    kt = LopKiemTra(level_hien_tai='A')
    def get_data_side(field, level, bai, kn, muc):
        if field == 'ktt_cauhoi':
            return "Question"
        elif field == 'ktt_dapan':
            return "CorrectAnswer"
        return None
    kt.get_data = Mock(side_effect=get_data_side)
    kt.thu_am_tra_text = Mock(return_value="correctanswer")
    monkeypatch.setattr('builtins.input', lambda _: "correctanswer")
    assert kt.hoc_mot_bai(1) is True
    captured = capsys.readouterr()
    assert "Đúng!" in captured.out

def test_lopkiemtra_hoc_mot_bai_fail(mock_dot, monkeypatch, capsys):
    kt = LopKiemTra(level_hien_tai='A')
    def get_data_side(field, level, bai, kn, muc):
        if field == 'ktt_cauhoi':
            return "Question"
        elif field == 'ktt_dapan':
            return "CorrectAnswer"
        return None
    kt.get_data = Mock(side_effect=get_data_side)
    kt.thu_am_tra_text = Mock(return_value="wrong")
    monkeypatch.setattr('builtins.input', lambda _: "wrong")
    assert kt.hoc_mot_bai(1) is False
    captured = capsys.readouterr()
    assert "Sai" in captured.out

def test_lopkiemtra_back_flow(mock_dot, monkeypatch):
    with patch('rsc.da_class.KhungBaiHoc', DummyKhungBaiHoc):
        kt = LopKiemTra(level_hien_tai='A')
        kt.get_data = Mock(return_value=None)
        kt.hoc_mot_bai = Mock(return_value=True)
        inputs = iter(["", "b", "b", "e"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        kt.back()
        assert kt.hoc_mot_bai.call_count >= 1

# ----------------------------------------------------------------------
# Tests for Ghichu
# ----------------------------------------------------------------------

def test_ghichu_them():
    dummy_khung = DummyKhungBaiHoc()
    dummy_khung.level_hien_tai = 'B'
    dummy_khung.lay_bai_hien_tai = Mock(return_value='bai_3')
    g = Ghichu(file_note="test_note.txt")
    m = mock_open()
    with patch('builtins.open', m):
        g.them(dummy_khung, "Học từ mới: apple")
    m.assert_called_once_with("test_note.txt", "a", encoding="utf-8")
    written = ''.join(call.args[0] for call in m().write.call_args_list)
    assert "Lvl:B" in written
    assert "Bài:bai_3" in written
    assert "Học từ mới: apple" in written

def test_ghichu_xem_lich_su(capsys):
    g = Ghichu(file_note="test_note.txt")
    mock_content = "[2025-01-01 10:00] Lvl:A | Bài:bai_1 | Ghi chú\n"
    with patch('builtins.open', mock_open(read_data=mock_content)), \
         patch('os.path.exists', return_value=True):
        g.xem_lich_su()
    captured = capsys.readouterr()
    assert "LỊCH SỬ GHI CHÚ" in captured.out
    assert mock_content in captured.out

def test_ghichu_xem_lich_su_no_file(capsys):
    g = Ghichu(file_note="missing.txt")
    with patch('os.path.exists', return_value=False):
        g.xem_lich_su()
    captured = capsys.readouterr()
    assert "Chưa có ghi chú" in captured.out

# ----------------------------------------------------------------------
# Tests for NguPhap
# ----------------------------------------------------------------------

def test_nguphap_get_data_raw(mock_dot):
    ng = NguPhap()
    data = ng.get_data_raw()
    assert data['A']['bai_1']['Present Simple'] == 'Used for habits...'

def test_nguphap_tim_kiem_nhanh_found(mock_dot, capsys):
    ng = NguPhap()
    ng.tim_kiem_nhanh("Present")
    captured = capsys.readouterr()
    assert "[A - bai_1]" in captured.out
    assert "Present Simple" in captured.out

def test_nguphap_tim_kiem_nhanh_not_found(mock_dot, capsys):
    ng = NguPhap()
    ng.tim_kiem_nhanh("xyz")
    captured = capsys.readouterr()
    assert "Không tìm thấy" in captured.out

def test_nguphap_duyet_bai_hoc(mock_dot, monkeypatch, capsys):
    ng = NguPhap()
    inputs = iter(["1", "1"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    ng.duyet_bai_hoc()
    captured = capsys.readouterr()
    assert "PRESENT SIMPLE" in captured.out
    assert "Used for habits..." in captured.out

def test_nguphap_menu_choice1(mock_dot, monkeypatch):
    ng = NguPhap()
    inputs = iter(["1", "Present", "3"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    with patch.object(ng, 'tim_kiem_nhanh') as mock_search:
        ng.menu()
        mock_search.assert_called_once_with("Present")

def test_nguphap_menu_choice2(mock_dot, monkeypatch):
    ng = NguPhap()
    inputs = iter(["2", "3"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    with patch.object(ng, 'duyet_bai_hoc') as mock_duyet:
        ng.menu()
        mock_duyet.assert_called_once()
