from khung import KhungBaiHoc
from textnhanh import dot
import random
import speech_recognition as sr
import datetime
import os


class LopKyNang(KhungBaiHoc):
    """Lớp cơ sở cho một kỹ năng (nghe, nói, đọc, viết)"""

    def __init__(self, level, so_bai, ky_nang, **kwargs):
        # Khởi tạo base với level A, B, C mặc định
        super().__init__(**kwargs)
        # Chuyển sang level đang học
        self.thiet_lap_level(level)
        bai_thuc = None
        for bai_key in self.danh_sach_bai:
            # Tách số từ key (ví dụ "bai_1" -> 1, hoặc "1" -> 1)
            try:
                if bai_key.isdigit():
                    so = int(bai_key)
                elif '_' in bai_key:
                    so = int(bai_key.split('_')[-1])
                else:
                    continue
                if so == so_bai:
                    bai_thuc = bai_key
                    break
            except:
                continue

        if bai_thuc is None:
            raise ValueError(f"Không tìm thấy bài {so_bai} trong level {level} (các bài có: {self.danh_sach_bai})")

        # Chỉ giữ lại bài hiện tại
        self.danh_sach_bai = [bai_thuc]
        self.vi_tri_bai = 0

        # Gán kỹ năng và mục hiện tại
        self.ky_nang = ky_nang
        self.muc = 'muc_1'


    def _hien_thi_cau_hoi(self, data):
        """Hiển thị câu hỏi và lựa chọn từ dict dữ liệu"""
        print("\n=== CÂU HỎI (tiếng Việt) ===")
        print(data["cau_hoiviet"])
        print("\n=== CÂU HỎI (tiếng Anh) ===")
        print(data["cau_hoi"])
        print("\n=== LỰA CHỌN ===")
        for i, ch in enumerate(data["lua_chon"], 1):
            print(f"{i}. {ch}")
        return data["lua_chon"], data["dap_an_dung"]

    def _lay_du_lieu_hien_tai(self):
        """Lấy dữ liệu của mục hiện tại """
        if self.muc == 'muc_1':
            return self.lay_du_lieu_muc_1()
        else:
            return self.lay_du_lieu_muc_2()

    def thuc_hien_muc(self):
        """Thực hiện một mục (trả về True nếu qua)"""
        data = self._lay_du_lieu_hien_tai()
        if not data:
            print("Lỗi: không có dữ liệu cho mục này.")
            return False

        lua_chon, dap_an_dung = self._hien_thi_cau_hoi(data)
        nguoi_dung = input("\nNhập đáp án (nội dung chính xác): ").strip().lower()
        if nguoi_dung == dap_an_dung.lower():
            print("✓ Chính xác!")
            return True
        else:
            print(f"✗ Sai rồi. Đáp án đúng là: {dap_an_dung}")
            return False

    def run(self):
        """ muc 1, muc 2"""
        print(f"\n========== BẮT ĐẦU {self.ky_nang.upper()} – MỨC 1 ==========")
        if self.thuc_hien_muc():
            print("\n--- TIẾP TỤC MỨC 2 ---")
            self.muc = 'muc_2'
            if self.thuc_hien_muc():
                print(f"\n*** HOÀN THÀNH KỸ NĂNG {self.ky_nang.upper()} ***")
                return True
            else:
                print(f"\n*** THẤT BẠI Ở MỨC 2, KẾT THÚC {self.ky_nang.upper()} ***")
        else:
            print(f"\n*** THẤT BẠI Ở MỨC 1, KẾT THÚC {self.ky_nang.upper()} ***")
        return False




class LopNghe(LopKyNang):
    """
    Kỹ năng Nghe
    """

    # Thêm level và so_bai vào danh sách tham số để tránh lỗi TypeError
    def __init__(self, level, so_bai, **kwargs):
        # Truyền level, so_bai và các tham số khác lên LopKyNang
        super().__init__(level=level, so_bai=so_bai,  ky_nang='nghe', **kwargs)

        self.ky_nang = 'nghe'
        self.m1 = 'muc_1'
        self.m2 = 'muc_2'

        # Lấy tên bài thực tế (ví dụ: "bai_1") sau khi LopKyNang đã xử lý
        self.so_bai_thuc = self.lay_bai_hien_tai()

    def muc1(self):
        """Dạng Generator"""
        # Sử dụng self.so_bai_thuc để lấy dữ liệu chính xác
        noidung_viet = [self.get_data('noidungviet', cs, self.so_bai_thuc, 'nghe', self.m1, False).lower()
                        for cs in ['A', 'B', 'C']]
        yield 'cau_hoiviet', *noidung_viet

        cau_hoi = [self.get_data('noidung', ch, self.so_bai_thuc, 'nghe', self.m1, False).lower()
                   for ch in ['A', 'B', 'C']]
        yield 'cau_hoi', *cau_hoi

        dap_an_dung = [self.get_data('dap_an_ca_bai', mm, self.so_bai_thuc, 'nghe', self.m1, False).lower()
                       for mm in ['A', 'B', 'C']]

        hien_thi = [d for d in dap_an_dung if d]
        yield 'dap_an', *hien_thi


        user_input = yield 'wait'

        if user_input and user_input.lower() in [d.lower() for d in dap_an_dung if d]:
            yield 'result', 'next'
        else:
            yield 'result', 'wrong'

    def muc2(self):
        noidung_viet = [self.get_data('noidungviet', cs, self.so_bai_thuc, 'nghe', self.m2, False).lower()
                        for cs in ['A', 'B', 'C']]
        yield 'cau_hoiviet', *noidung_viet

        cau_hoi_goc = [self.get_data('noidung', ch, self.so_bai_thuc, 'nghe', self.m2, False).lower()
                       for ch in ['A', 'B', 'C']]

        cau_hoi_tron = []
        for ch in cau_hoi_goc:
            if ch:
                tu = ch.split()
                random.shuffle(tu)
                cau_hoi_tron = tu
            else:
                cau_hoi_tron.append("")
        yield 'cau_hoi', *cau_hoi_tron

        dap_an_dung = [self.get_data('dap_an_ca_bai', mm, self.so_bai_thuc, 'nghe', self.m2, False).lower()
                       for mm in ['A', 'B', 'C']]

        hien_thi = [d for d in dap_an_dung if d]
        random.shuffle(hien_thi)
        yield 'dap_an', *hien_thi


        user_input = yield 'wait'

        if user_input and user_input.lower() in [d.lower() for d in dap_an_dung if d]:
            yield 'result', 'done'
        else:
            yield 'result', 'wrong'




class LopDoc(LopKyNang):
    """
       Kỹ năng đọc
       """

    # Thêm level và so_bai vào danh sách tham số để tránh lỗi TypeError
    def __init__(self, level, so_bai,  **kwargs):
        # Truyền level, so_bai và các tham số khác lên LopKyNang
        super().__init__(level=level, so_bai=so_bai, ky_nang='doc', **kwargs)

        self.ky_nang = 'doc'
        self.m1 = 'muc_1'
        self.m2 = 'muc_2'

        # Lấy tên bài thực tế (ví dụ: "bai_1") sau khi LopKyNang đã xử lý
        self.so_bai_thuc = self.lay_bai_hien_tai()

    def muc1(self):
        # Sử dụng self.so_bai_thuc để lấy dữ liệu chính xác
        noidung_viet = [self.get_data('noidungviet', cs, self.so_bai_thuc, 'doc', self.m1, False).lower()
                        for cs in ['A', 'B', 'C']]
        yield 'cau_hoiviet', *noidung_viet

        cau_hoi = [self.get_data('noidung', ch, self.so_bai_thuc, 'doc', self.m1, False).lower()
                   for ch in ['A', 'B', 'C']]
        yield 'cau_hoi', *cau_hoi

        dap_an_dung = [self.get_data('dap_an_ca_bai', mm, self.so_bai_thuc, 'doc', self.m1, False).lower()
                       for mm in ['A', 'B', 'C']]

        hien_thi = [d for d in dap_an_dung if d]
        yield 'dap_an', *hien_thi

        user_input = yield 'wait'

        if user_input and user_input.lower() in [d.lower() for d in dap_an_dung if d]:
            yield 'result', 'next'
        else:
            yield 'result', 'wrong'

    def muc2(self):
        noidung_viet = [self.get_data('noidungviet', cs, self.so_bai_thuc, 'doc', self.m2, False).lower()
                        for cs in ['A', 'B', 'C']]
        yield 'cau_hoiviet', *noidung_viet

        cau_hoi_goc = [self.get_data('noidung', ch, self.so_bai_thuc, 'doc', self.m2, False).lower()
                       for ch in ['A', 'B', 'C']]

        cau_hoi_tron = []
        for ch in cau_hoi_goc:
            if ch:
                tu = ch.split()
                random.shuffle(tu)
                cau_hoi_tron = tu
            else:
                cau_hoi_tron.append("")
        yield 'cau_hoi', *cau_hoi_tron

        dap_an_dung = [self.get_data('dap_an_ca_bai', mm, self.so_bai_thuc, 'doc', self.m2, False).lower()
                       for mm in ['A', 'B', 'C']]

        hien_thi = [d for d in dap_an_dung if d]
        random.shuffle(hien_thi)
        yield 'dap_an', *hien_thi

        user_input = yield 'wait'

        if user_input and user_input.lower() in [d.lower() for d in dap_an_dung if d]:
            yield 'result', 'done'
        else:
            yield 'result', 'wrong'



class LopViet(LopKyNang):
    """
       Kỹ năng viết
       """
    def __init__(self, level, so_bai, **kwargs):
        super().__init__(level=level, so_bai=so_bai,ky_nang='viet', **kwargs)

        self.ky_nang = 'viet'
        self.m1 = 'muc_1'
        self.m2 = 'muc_2'

        # Lấy tên bài thực tế (ví dụ: "bai_1") sau khi LopKyNang đã xử lý
        self.so_bai_thuc = self.lay_bai_hien_tai()

    def muc1(self):
        # Sử dụng self.so_bai_thuc để lấy dữ liệu chính xác
        noidung_viet = [self.get_data('noidungviet', cs, self.so_bai_thuc, 'viet', self.m1, False).lower()
                        for cs in ['A', 'B', 'C']]
        yield 'cau_hoiviet', *noidung_viet

        cau_hoi = [self.get_data('noidung', ch, self.so_bai_thuc, 'viet', self.m1, False).lower()
                   for ch in ['A', 'B', 'C']]
        yield 'cau_hoi', *cau_hoi

        dap_an_dung = [self.get_data('dap_an_ca_bai', mm, self.so_bai_thuc, 'viet', self.m1, False).lower()
                       for mm in ['A', 'B', 'C']]

        hien_thi = [d for d in dap_an_dung if d]
        yield 'dap_an', *hien_thi

        user_input = yield 'wait'

        if user_input and user_input.lower() in [d.lower() for d in dap_an_dung if d]:
            yield 'result', 'next'
        else:
            yield 'result', 'wrong'

    def muc2(self):
        noidung_viet = [self.get_data('noidungviet', cs, self.so_bai_thuc, 'viet', self.m2, False).lower()
                        for cs in ['A', 'B', 'C']]
        yield 'cau_hoiviet', *noidung_viet

        cau_hoi_goc = [self.get_data('noidung', ch, self.so_bai_thuc, 'viet', self.m2, False).lower()
                       for ch in ['A', 'B', 'C']]

        cau_hoi_tron = []
        for ch in cau_hoi_goc:
            if ch:
                tu = ch.split()
                random.shuffle(tu)
                cau_hoi_tron = tu
            else:
                cau_hoi_tron.append("")
        yield 'cau_hoi', *cau_hoi_tron

        dap_an_dung = [self.get_data('dap_an_ca_bai', mm, self.so_bai_thuc, 'viet', self.m2, False).lower()
                       for mm in ['A', 'B', 'C']]

        hien_thi = [d for d in dap_an_dung if d]
        yield 'dap_an', *hien_thi

        user_input = yield 'wait'

        if user_input and user_input.lower() in [d.lower() for d in dap_an_dung if d]:
            yield 'result', 'done'
        else:
            yield 'result', 'wrong'


class LopNoi(LopKyNang):
    def __init__(self, level, so_bai, ky_nang, language='en-US', **kwargs):
        super().__init__(level, so_bai, ky_nang, **kwargs)
        self.language = language
        self.recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            self.has_mic = True
        except Exception as e:
            print(f"\n[Cảnh báo] Micro không hoạt động ({e}). Chuyển sang chế độ gõ phím.")
            self.has_mic = False

    def _listen_once(self, timeout=5, phrase_time_limit=5):
        if not self.has_mic:
            return None
        try:
            with sr.Microphone() as source:
                print("\n🎤 Đang nghe... (hãy đọc đáp án)")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                text = self.recognizer.recognize_google(audio, language=self.language)
                print(f"   Nhận dạng được: {text}")
                return text.strip().lower()
        except sr.WaitTimeoutError:
            print("   Không phát hiện giọng nói.")
        except sr.UnknownValueError:
            print("   Không hiểu giọng nói.")
        except Exception as e:
            print(f"   Lỗi: {e}")
        return None

    def thuc_hien_muc(self):
        data = self._lay_du_lieu_hien_tai()
        if not data:
            print("Lỗi dữ liệu.")
            return False

        print("\n=== CÂU HỎI (tiếng Việt) ===")
        print(data["cau_hoiviet"])
        print("\n=== CÂU HỎI (tiếng Anh) ===")
        print(data["cau_hoi"])
        print("\n=== ĐÁP ÁN CẦN ĐỌC (hãy đọc to một trong các đáp án sau) ===")
        for i, ch in enumerate(data["lua_chon"], 1):
            print(f"{i}. {ch}")

        dap_an_dung = data["dap_an_dung"].lower()
        for lan in range(3):
            user_answer = self._listen_once()
            if user_answer is None:
                user_answer = input("(Không nghe được) Gõ đáp án của bạn: ").strip().lower()
            if user_answer == dap_an_dung:
                print("✓ Chính xác!")
                return True
            else:
                print(f"✗ Sai (lần {lan+1}/3). Đáp án đúng: {dap_an_dung}")
        return False


class LopKiemTra(KhungBaiHoc):
    def __init__(self, level_hien_tai='A', **kwargs):
        # Kế thừa KhungBaiHoc để lấy dữ liệu từ ktt_cauhoi, ktt_dapan
        super().__init__(**kwargs)
        self.level_hien_tai = level_hien_tai
        self.danh_sach_kn = ['nghe', 'noi', 'doc', 'viet']
        self.ti_le_qua_mon = 0.5  # 50% để qua bài
        self.recognizer = sr.Recognizer()

    def thu_am_tra_text(self):

        try:
            with sr.Microphone() as source:
                print("🎤 Hệ thống đang nghe...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5)
                return self.recognizer.recognize_google(audio, language='en-US').strip().lower()
        except:
            return input("⌨ Mic lỗi, vui lòng gõ đáp án: ").strip().lower()

    def lay_du_lieu_bai(self, kn, so_bai):
        ten_bai = f"bai_{so_bai}"
        cau_hoi = self.get_data('ktt_cauhoi', self.level_hien_tai, ten_bai, kn, 'muc_1')
        dap_an = self.get_data('ktt_dapan', self.level_hien_tai, ten_bai, kn, 'muc_1')

        if not cau_hoi or not dap_an: return None

        # Tạo 3 lựa chọn từ A, B, C (Logic mục 1)
        lua_chon = []
        for lvl in ['A', 'B', 'C']:
            opt = self.get_data('ktt_dapan', lvl, ten_bai, kn, 'muc_1')
            if opt: lua_chon.append(opt)
        random.shuffle(lua_chon)

        return {"q": cau_hoi, "a": dap_an, "opts": lua_chon}

    def hoc_mot_bai(self, so_bai):
        print(f"\n--- ĐANG HỌC BÀI {so_bai} - LEVEL {self.level_hien_tai} ---")
        diem_bai = 0

        for kn in self.danh_sach_kn:
            data = self.lay_du_lieu_bai(kn, so_bai)
            if not data: continue

            print(f"\n[{kn.upper()}] {data['q']}")
            print(f"Gợi ý: {', '.join(data['opts'])}")

            user_ans = self.thu_am_tra_text() if kn == 'noi' else input(" Đáp án: ").strip().lower()

            if user_ans == data['a'].lower():
                print(" Đúng!")
                diem_bai += 2
            else:
                print(f" Sai. Đáp án đúng: {data['a']}")

        # Tính toán kết quả bài học
        phan_tram = diem_bai / 8
        print(f"\n>> Kết quả bài {so_bai}: {diem_bai}/8 ({phan_tram * 100}%)")

        if phan_tram >= self.ti_le_qua_mon:
            print(" ĐẠT! Mở khóa bài tiếp theo.")
            return True
        else:
            print("CHƯA ĐẠT! Bạn nên học lại bài này.")
            return False

    def luong_chinh(self):
        levels = ['A', 'B', 'C']
        idx_lvl = levels.index(self.level_hien_tai)

        while idx_lvl < len(levels):
            self.level_hien_tai = levels[idx_lvl]
            print(f"\n{'=' * 10} LEVEL {self.level_hien_tai} {'=' * 10}")

            so_bai = 1
            while so_bai <= len(self.danh_sach_bai):  # Giả sử mỗi level có 10 bài
                thanh_cong = self.hoc_mot_bai(so_bai)
                if thanh_cong:
                    so_bai += 1  # Chỉ tăng bài khi đạt >50%
                else:
                    tiep_tuc = input("Học lại bài này? (y/n): ")
                    if tiep_tuc.lower() != 'y': break

            print(f"\n Chúc mừng! Bạn đã hoàn thành toàn bộ Level {self.level_hien_tai}")
            idx_lvl += 1
            if idx_lvl < len(levels):
                print(f" TỰ ĐỘNG MỞ KHÓA LEVEL {levels[idx_lvl]}")

    def back(self):
        levels = ['A', 'B', 'C']
        idx_lvl = levels.index(self.level_hien_tai)

        while idx_lvl < len(levels):
            # --- CẤP ĐỘ 2: LỚP (LEVEL) ---
            self.level_hien_tai = levels[idx_lvl]
            # Load lại danh sách bài thực tế từ file JSON của level này
            self.thiet_lap_level(self.level_hien_tai)

            print(f"\n{'=' * 10} BẮT ĐẦU LỚP {self.level_hien_tai} {'=' * 10}")
            print(f"Danh sách bài: {self.danh_sach_bai}")

            idx_bai = 0
            while idx_bai < len(self.danh_sach_bai):
                # --- CẤP ĐỘ 1: BÀI HỌC ---
                ten_bai_thuc = self.danh_sach_bai[idx_bai]
                # Lấy số bài từ tên (vd: "bai_1" -> 1) để hiển thị
                so_bai_hien_thi = ten_bai_thuc.split('_')[-1] if '_' in ten_bai_thuc else ten_bai_thuc

                print(f"\n--- [BÀI {so_bai_hien_thi}] ---")
                print("Lệnh: 'b' (Quay lại), 'e' (Thoát)")

                # Gọi hàm học bài
                thanh_cong = self.hoc_mot_bai(so_bai_hien_thi)

                # XỬ LÝ ĐIỀU HƯỚNG SAU KHI KẾT THÚC BÀI
                chon = input(f"\n[BÀI {so_bai_hien_thi} Xong] Enter: Tiếp | b: Back | e: Thoát: ").strip().lower()

                if chon == 'b':
                    # BACK LẦN 1: Quay lại đầu bài học hiện tại (không tăng index)
                    print("\n<<< BACK 1: Quay lại đầu bài.")

                    back_2 = input(
                        "Bấm 'b' lần nữa để quay về chọn LỚP (Level), hoặc Enter để học lại bài: ").strip().lower()
                    if back_2 == 'b':
                        # BACK LẦN 2: Thoát khỏi vòng lặp bài, về vòng lặp Lớp
                        print("\n<<<<< BACK 2: Quay về danh sách LỚP.")
                        break
                    continue  # Học lại bài hiện tại

                if chon == 'e':
                    # BACK LẦN 3: Thoát hẳn chương trình
                    print("\n<<<<<<<<<< BACK 3: THOÁT CHƯƠNG TRÌNH.")
                    return

                if thanh_cong:
                    idx_bai += 1
                else:
                    print("Bài chưa đạt, vui lòng học lại.")

            # Sau khi break hoặc hết bài trong level
            print(f"\n--- ĐÃ HOÀN THÀNH HOẶC THOÁT LỚP {self.level_hien_tai} ---")
            hanh_dong = input("Enter: Lên Level tiếp | b: Chọn lại Level | e: Thoát: ").strip().lower()

            if hanh_dong == 'e': return
            if hanh_dong == 'b': continue  # Chạy lại vòng lặp Lớp hiện tại

            idx_lvl += 1  # Lên Level tiếp theo
#Chạy chương trình
# if __name__ == "__main__":
#     app = LopKiemTra(level_hien_tai='A')
#     app.luong_chinh()






class Ghichu(KhungBaiHoc):
    def __init__(self, file_note="lich_su_ghi_chu.txt", **kwargs):
        super().__init__(**kwargs)
        self.file_note = file_note

    def them(self, khung_hoc, noi_dung):
        """
        Ghi chú tự động lấy thông tin từ đối tượng KhungBaiHoc
        """
        level = getattr(khung_hoc, 'level_hien_tai', 'Unknown')
        bai = khung_hoc.lay_bai_hien_tai()  # Tự gọi hàm trong KhungBaiHoc

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        data = f"[{timestamp}] Lvl:{level} | Bài:{bai} | {noi_dung}\n"

        with open(self.file_note, "a", encoding="utf-8") as f:
            f.write(data)
        print(" Ghi chú đã lưu.")

    def xem_lich_su(self):
        if not os.path.exists(self.file_note):
            print("Chưa có ghi chú.")
            return
        with open(self.file_note, "r", encoding="utf-8") as f:
            print("\n--- LỊCH SỬ GHI CHÚ ---\n" + f.read())


class NguPhap(KhungBaiHoc):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_name = 'nguphap'

    def menu(self):
        while True:
            print("\n--- QUẢN LÝ NGỮ PHÁP (PRO) ---")
            print("1. Tìm kiếm ngữ pháp theo từ khóa")
            print("2. Duyệt ngữ pháp theo bài học")
            print("3. Thoát")
            choice = input("Chọn chức năng (1-3): ")

            if choice == '1':
                tu_khoa = input(">> Nhập từ khóa: ")
                self.tim_kiem_nhanh(tu_khoa)
            elif choice == '2':
                self.duyet_bai_hoc()
            elif choice == '3':
                print("Tạm biệt!")
                break
            else:
                print("Lựa chọn không hợp lệ!")

    def get_data_raw(self):
        """Lấy dữ liệu thô dạng dict từ object dot của textnhanh"""
        return dot.get('ngu_phap', self.file_name)
    def tim_kiem_nhanh(self, tu_khoa):
        data = self.get_data_raw()
        if not data:
            print("Không có dữ liệu!")
            return

        print(f"\n--- KẾT QUẢ TÌM KIẾM CHO: '{tu_khoa}' ---")
        found = False
        for level, bai_dict in data.items():
            for bai, content in bai_dict.items():
                for chu_de, giai_thich in content.items():
                    if tu_khoa.lower() in chu_de.lower() or tu_khoa.lower() in giai_thich.lower():
                        print(f"\n[{level} - {bai}] {chu_de}")
                        print(f"Nội dung: {giai_thich}")
                        found = True
        if not found:
            print("Không tìm thấy kết quả phù hợp!")

    def duyet_bai_hoc(self):
        data = self.get_data_raw()
        if not data: return

        levels = list(data.keys())
        print("\n--- CHỌN CẤP ĐỘ ---")
        for i, lvl in enumerate(levels, 1):
            print(f"{i}. {lvl}")

        idx_lvl = int(input("Nhập số chọn cấp độ: ")) - 1
        level_chon = levels[idx_lvl]

        bai_list = list(data[level_chon].keys())
        print(f"\n--- CÁC BÀI CỦA {level_chon} ---")
        for i, bai in enumerate(bai_list, 1):
            print(f"{i}. {bai}")

        idx_bai = int(input("Nhập số chọn bài: ")) - 1
        bai_chon = bai_list[idx_bai]

        # In nội dung bài học
        noi_dung = data[level_chon][bai_chon]
        print(f"\n--- NỘI DUNG CHI TIẾT ---")
        for k, v in noi_dung.items():
            print(f"\n>> {k.upper()}\n{v}")


# if __name__ == "__main__":
#     app = NguPhap()
#     app.menu()
