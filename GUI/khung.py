from textnhanh import search_data, allfile_level
import random


class HeThongHocTiengAnh:
    """
    CỖ MÁY GỐC: Quản lý toàn bộ cấu trúc Level (A, B, C)
    """

    def __init__(self, level_A='A', level_B='B', level_C='C'):
        # --- 1. ĐỊNH NGHĨA CÁC LEVEL ---
        self.level_A = level_A
        self.level_B = level_B
        self.level_C = level_C

        # --- 2. TRẠNG THÁI HIỆN TẠI ---
        self.level_hien_tai = self.level_A

        # Tự động quét JSON để lấy danh sách bài
        dict_bai = allfile_level(self.level_hien_tai)
        self.danh_sach_bai = dict_bai.get(self.level_hien_tai, [])

        # Con trỏ vị trí Bài (Luôn bắt đầu từ 0)
        self.vi_tri_bai = 0

    # --- 3. CÁC HÀNH ĐỘNG CỦA CỖ MÁY GỐC ---

    def thiet_lap_level(self, level_moi):
        """Hành động: Chuyển đổi Level và load lại danh sách bài"""
        if level_moi in [self.level_A, self.level_B, self.level_C]:
            self.level_hien_tai = level_moi
            dict_bai = allfile_level(self.level_hien_tai)
            self.danh_sach_bai = dict_bai.get(self.level_hien_tai, [])
            self.vi_tri_bai = 0
            return True
        return False

    def lay_bai_hien_tai(self):
        """
        Hành động: Trả về tên bài đang học.
        Máy sẽ nhìn vào con trỏ (vi_tri_bai) để bốc đúng tên bài trong danh_sach_bai.
        """
        if self.vi_tri_bai < len(self.danh_sach_bai):
            return self.danh_sach_bai[self.vi_tri_bai]
        return None

    def chuyen_bai_tiep_theo(self):
        """Hành động: Gạt con trỏ sang bài tiếp theo"""
        if self.vi_tri_bai < len(self.danh_sach_bai) - 1:
            self.vi_tri_bai += 1
            return True
        return False

    def get_data(self, file_name, level_char, bai_char, ky_nang, muc, return_values_only=False):
        """Hành động: Gọi thợ máy (textnhanh) đi lấy dữ liệu JSON"""
        return search_data(file_name, level_char, bai_char, ky_nang, muc, return_values_only)


    def lay_bai_KT(self):
        """
        Hành động: Trả về tên bài đang học.
        Máy sẽ nhìn vào con trỏ (vi_tri_bai) để bốc đúng tên bài trong danh_sach_bai.
        """
        if self.vi_tri_bai < len(self.danh_sach_bai):
            return self.danh_sach_bai[self.vi_tri_bai]
        return None

class KhungBaiHoc(HeThongHocTiengAnh):
    """
    CỖ MÁY XỬ LÝ: Quản lý 'Trục Ngang' (Kỹ năng, Mục)
    """

    def __init__(self, level_A='A', level_B='B', level_C='C',
                 ky_nang='nghe', muc='muc_1',
                 nghe=None, noi=None, doc=None, viet=None,
                 ngu_phap=None, kiem_tra=None, ghi_chu=None):

        super().__init__(level_A=level_A, level_B=level_B, level_C=level_C)

        # --- 1. CÁC TRẠNG THÁI (Trục Ngang) ---
        self.ky_nang = ky_nang
        self.muc = muc

        # Các biến chứa dữ liệu tĩnh
        self.nghe = nghe
        self.noi = noi
        self.doc = doc
        self.viet = viet
        self.ngu_phap = ngu_phap
        self.kiem_tra = kiem_tra
        self.ghi_chu = ghi_chu

    # --- 2. CÁC HÀNH ĐỘNG ĐIỀU HƯỚNG ---
    def chuyen_muc_tiep_theo(self):
        """Hành động: Gạt cần đổi từ Mục 1 sang Mục 2"""
        if self.muc == 'muc_1':
            self.muc = 'muc_2'
        else:
            self.muc = 'muc_1'

    # --- 3. CÁC HÀNH ĐỘNG NHÀO NẶN DỮ LIỆU ---
    def lay_du_lieu_muc_1(self):
        # PHẢI GỌI HÀM (có ngoặc tròn) để cỗ máy gốc tính toán và trả về tên bài
        bai = self.lay_bai_hien_tai()
        if not bai: return None

        nd_viet = self.get_data('noidungviet', self.level_hien_tai, bai, self.ky_nang, 'muc_1')
        nd_anh = self.get_data('noidung', self.level_hien_tai, bai, self.ky_nang, 'muc_1')
        dap_an_dung = self.get_data('dap_an_ca_bai', self.level_hien_tai, bai, self.ky_nang, 'muc_1')

        if not dap_an_dung: return None

        lua_chon = [self.get_data('dap_an_ca_bai', l, bai, self.ky_nang, 'muc_1') for l in
                    [self.level_A, self.level_B, self.level_C]]

        lua_chon = [opt for opt in lua_chon if opt]
        random.shuffle(lua_chon)

        return {
            "cau_hoiviet": nd_viet,
            "cau_hoi": nd_anh,
            "lua_chon": lua_chon,
            "dap_an_dung": dap_an_dung.lower(),


        }

    def lay_du_lieu_muc_2(self):
        # PHẢI GỌI HÀM (có ngoặc tròn)
        bai = self.lay_bai_hien_tai()
        if not bai: return None

        nd_viet = self.get_data('noidungviet', self.level_hien_tai, bai, self.ky_nang, 'muc_2')
        nd_anh = self.get_data('noidung', self.level_hien_tai, bai, self.ky_nang, 'muc_2')
        dap_an_dung = self.get_data('dap_an_ca_bai', self.level_hien_tai, bai, self.ky_nang, 'muc_2')

        if not dap_an_dung: return None

        if nd_anh:
            tu_vung = nd_anh.split()
            random.shuffle(tu_vung)
            nd_anh = f"(Sắp xếp từ): {' '.join(tu_vung)}"

        lua_chon = [self.get_data('dap_an_ca_bai', l, bai, self.ky_nang, 'muc_2') for l in
                    [self.level_A, self.level_B, self.level_C]]
        lua_chon = [opt for opt in lua_chon if opt]
        random.shuffle(lua_chon)

        return {
            "cau_hoiviet": nd_viet,
            "cau_hoi": nd_anh,
            "lua_chon": lua_chon,
            "dap_an_dung": dap_an_dung.lower()
        }



    def lay_du_lieuKT(self):
        # PHẢI GỌI HÀM (có ngoặc tròn) để cỗ máy gốc tính toán và trả về tên bài
        bai = self.lay_bai_KT()
        if not bai: return None

        nd_kt = self.get_data('kkt_cauhoi', self.level_hien_tai, bai, self.ky_nang, 'muc_1')
        tl_kt = self.get_data('kkt_dapan', self.level_hien_tai, bai, self.ky_nang, 'muc_1')
        if not tl_kt: return None
        tl = [self.get_data('kkt_dapan', l, bai, self.ky_nang, 'muc_1') for l in
                    [self.level_A, self.level_B, self.level_C]]

        tl = [opt for opt in tl if opt]
        random.shuffle(tl)
        return { "kt": nd_kt,
                "tl": tl_kt}

    def layhien_tai_kt(self):
        if self.muc == 'muc_1':
            return self.lay_du_lieu_muc_1()
        return None



    def lay_du_lieu_hien_tai(self):
        if self.muc == 'muc_1':
            return self.lay_du_lieu_muc_1()
        elif self.muc == 'muc_2':
            return self.lay_du_lieu_muc_2()
        return None


class Manager:
    pass


manage = Manager()