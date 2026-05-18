import sys
import os
import pytest
from unittest.mock import Mock, patch, mock_open

sys.path.insert(0, os.path.dirname(__file__) + '/../..')

from rsc.da_class import (
    LopKyNang, LopNghe, LopDoc, LopViet, LopNoi,
    LopKiemTra, Ghichu, NguPhap
)


class DummyKhungBaiHoc:
    def __init__(self, level='A', so_bai=1, ky_nang='', **kwargs):
        self.level_hien_tai = level
        self.danh_sach_bai = ['bai_1', 'bai_2', 'bai_3']
        self.vi_tri_bai = 0
        self.ky_nang = ky_nang
        self.muc = 'muc_1'

    def thiet_lap_level(self, level):
        self.level_hien_tai = level

    def lay_bai_hien_tai(self):
        if self.vi_tri_bai < len(self.danh_sach_bai):
            return self.danh_sach_bai[self.vi_tri_bai]
        return 'bai_1'

    def get_data(self, field, sub, bai, ky_nang, muc, *args):
        if field == 'noidungviet':
            return f"Nội dung tiếng Việt {sub}"
        if field == 'noidung':
            # SỬA: muc2 trả về câu đúng 3 từ để len(vals) == 3
            if muc == 'muc_2':
                return "this is test"   # 3 từ
            return f"English content {sub}"
        if field == 'dap_an_ca_bai':
            return f"answer_{sub.lower()}"
        if field == 'ktt_cauhoi':
            return f"Question for {ky_nang}"
        if field == 'ktt_dapan':
            return f"Answer for {ky_nang}"
        return None

    def lay_du_lieu_muc_1(self):
        return {
            "cau_hoiviet": "Câu hỏi mức 1 (Việt)",
            "cau_hoi": "Level 1 question (English)",
            "lua_chon": ["Option A", "Option B", "Option C"],
            "dap_an_dung": "correct"
        }

    def lay_du_lieu_muc_2(self):
        return {
            "cau_hoiviet": "Câu hỏi mức 2 (Việt)",
            "cau_hoi": "Level 2 question (English)",
            "lua_chon": ["Choice X", "Choice Y", "Choice Z"],
            "dap_an_dung": "correct2"
        }


sys.modules['khung'] = Mock()
sys.modules['khung'].KhungBaiHoc = DummyKhungBaiHoc
sys.modules['textnhanh'] = Mock()
sys.modules['textnhanh'].dot = Mock()



# --------------------------------------------------------------
# Fixture mock_dot
# --------------------------------------------------------------
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


def test_lopkynang_init():
    kn = LopKyNang(level='A', so_bai=1, ky_nang='test')
    assert kn.ky_nang == 'test'
    assert kn.muc == 'muc_1'
    assert kn.danh_sach_bai == ['bai_1']

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

def test_lopnghe_muc1_generator():
    nghe = LopNghe(level='A', so_bai=1)
    gen = nghe.muc1()
    typ, *vals = next(gen); assert typ == 'cau_hoiviet' and len(vals)==3
    typ, *vals = next(gen); assert typ == 'cau_hoi' and len(vals)==3
    typ, *vals = next(gen); assert typ == 'dap_an' and len(vals)==3
    assert next(gen) == 'wait'
    result = gen.send(vals[0])
    assert result == ('result', 'next')

def test_lopnghe_muc2_generator():
    nghe = LopNghe(level='A', so_bai=1)
    gen = nghe.muc2()
    typ, *vals = next(gen); assert typ == 'cau_hoiviet' and len(vals)==3
    typ, *vals = next(gen); assert typ == 'cau_hoi' and len(vals)==3   # bây giờ vals có 3 phần tử
    typ, *vals = next(gen); assert typ == 'dap_an' and len(vals)==3
    assert next(gen) == 'wait'
    result = gen.send(vals[0])
    assert result == ('result', 'next')

def test_lopdoc_muc1_generator():
    doc = LopDoc(level='A', so_bai=1)
    gen = doc.muc1()
    next(gen); next(gen)
    typ, *vals = next(gen); assert typ == 'dap_an'
    assert next(gen) == 'wait'
    result = gen.send(vals[0])
    assert result == ('result', 'next')

def test_lopdoc_muc2_generator():
    doc = LopDoc(level='A', so_bai=1)
    gen = doc.muc2()
    next(gen); next(gen)
    typ, *vals = next(gen); assert typ == 'dap_an'
    assert next(gen) == 'wait'
    result = gen.send(vals[0])
    assert result == ('result', 'next')

def test_lopviet_muc1_generator():
    viet = LopViet(level='A', so_bai=1)
    gen = viet.muc1()
    next(gen); next(gen)
    typ, *vals = next(gen); assert typ == 'dap_an'
    assert next(gen) == 'wait'
    result = gen.send(vals[0])
    assert result == ('result', 'next')

def test_lopviet_muc2_generator():
    viet = LopViet(level='A', so_bai=1)
    gen = viet.muc2()
    next(gen); next(gen)
    typ, *vals = next(gen); assert typ == 'dap_an'
    assert next(gen) == 'wait'
    result = gen.send(vals[0])
    assert result == ('result', 'next')

@patch('rsc.da_class.sr.Recognizer')
@patch('rsc.da_class.sr.Microphone')
def test_lopnoi_init_with_mic(mock_mic, mock_recog):
    mock_mic.return_value.__enter__ = Mock()
    mock_mic.return_value.__exit__ = Mock()
    noi = LopNoi(level='A', so_bai=1, ky_nang='noi')
    assert noi.has_mic is True

@patch('rsc.da_class.sr.Recognizer')
@patch('rsc.da_class.sr.Microphone', side_effect=Exception("No mic"))
def test_lopnoi_init_no_mic(mock_mic, mock_recog):
    noi = LopNoi(level='A', so_bai=1, ky_nang='noi')
    assert noi.has_mic is False

def test_lopnoi_thuc_hien_mic_success():
    with patch('rsc.da_class.sr.Recognizer') as mock_recog:
        mock_recog_instance = Mock()
        mock_recog.return_value = mock_recog_instance
        mock_recog_instance.recognize_google = Mock(return_value="correct answer")
        mock_recog_instance.listen = Mock()
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
            assert noi.thuc_hien_muc() is True

# SỬA: test fallback input – giả lập _listen_once trả về None để kích hoạt nhập từ bàn phím
def test_lopnoi_thuc_hien_fallback_input(monkeypatch):
    noi = LopNoi(level='A', so_bai=1, ky_nang='noi')
    noi._lay_du_lieu_hien_tai = Mock(return_value={
        "cau_hoiviet": "viet",
        "cau_hoi": "eng",
        "lua_chon": ["correct", "wrong"],
        "dap_an_dung": "correct"
    })
    # Patch _listen_once để trả về None (không nghe được), buộc rơi vào input
    with patch.object(noi, '_listen_once', return_value=None):
        inputs = iter(["correct", "", ""])   # input trả lời đúng ngay lần đầu
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        assert noi.thuc_hien_muc() is True

def test_lopkiemtra_lay_du_lieu_bai(mock_dot):
    kt = LopKiemTra(level_hien_tai='A')
    def get_data_side(field, level, bai, kn, muc):
        if field == 'ktt_cauhoi': return 'What is the capital?'
        if field == 'ktt_dapan': return 'Hanoi' if level == 'A' else None
        return None
    kt.get_data = Mock(side_effect=get_data_side)
    data = kt.lay_du_lieu_bai('nghe', 1)
    assert data is not None
    assert data['q'] == 'What is the capital?'
    assert data['a'] == 'Hanoi'

def test_lopkiemtra_hoc_mot_bai_success(mock_dot, monkeypatch, capsys):
    kt = LopKiemTra(level_hien_tai='A')
    def get_data_side(field, level, bai, kn, muc):
        if field == 'ktt_cauhoi': return "Question"
        if field == 'ktt_dapan': return "CorrectAnswer"
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
        if field == 'ktt_cauhoi': return "Question"
        if field == 'ktt_dapan': return "CorrectAnswer"
        return None
    kt.get_data = Mock(side_effect=get_data_side)
    kt.thu_am_tra_text = Mock(return_value="wrong")
    monkeypatch.setattr('builtins.input', lambda _: "wrong")
    assert kt.hoc_mot_bai(1) is False
    captured = capsys.readouterr()
    assert "Sai" in captured.out

def test_lopkiemtra_back_flow(monkeypatch):
    kt = LopKiemTra(level_hien_tai='A')
    kt.get_data = Mock(return_value=None)
    kt.hoc_mot_bai = Mock(return_value=True)
    inputs = iter(["", "b", "b", "e"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    kt.back()
    assert kt.hoc_mot_bai.call_count >= 1

def test_ghichu_them():
    dummy = DummyKhungBaiHoc()
    dummy.level_hien_tai = 'B'
    dummy.lay_bai_hien_tai = Mock(return_value='bai_3')
    g = Ghichu(file_note="test_note.txt")
    m = mock_open()
    with patch('builtins.open', m):
        g.them(dummy, "Học từ mới: apple")
    m.assert_called_once_with("test_note.txt", "a", encoding="utf-8")
    written = ''.join(call.args[0] for call in m().write.call_args_list)
    assert "Lvl:B" in written and "Bài:bai_3" in written and "Học từ mới: apple" in written

def test_ghichu_xem_lich_su(capsys):
    g = Ghichu(file_note="test_note.txt")
    mock_content = "[2025-01-01 10:00] Lvl:A | Bài:bai_1 | Ghi chú\n"
    with patch('builtins.open', mock_open(read_data=mock_content)), \
         patch('os.path.exists', return_value=True):
        g.xem_lich_su()
    captured = capsys.readouterr()
    assert "LỊCH SỬ GHI CHÚ" in captured.out and mock_content in captured.out

def test_ghichu_xem_lich_su_no_file(capsys):
    g = Ghichu(file_note="missing.txt")
    with patch('os.path.exists', return_value=False):
        g.xem_lich_su()
    captured = capsys.readouterr()
    assert "Chưa có ghi chú" in captured.out

def test_nguphap_get_data_raw(mock_dot):
    ng = NguPhap()
    data = ng.get_data_raw()
    assert data['A']['bai_1']['Present Simple'] == 'Used for habits...'

def test_nguphap_tim_kiem_nhanh_found(mock_dot, capsys):
    ng = NguPhap()
    ng.tim_kiem_nhanh("Present")
    captured = capsys.readouterr()
    assert "[A - bai_1]" in captured.out and "Present Simple" in captured.out

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
    assert "PRESENT SIMPLE" in captured.out.upper() and "Used for habits..." in captured.out

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