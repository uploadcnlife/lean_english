import os
import json
import docx
import re


# ==========================================
# 1. LỚP CƠ SỞ - XỬ LÝ FILE
# ==========================================
class BoXuLyFileGoc:
    def __init__(self, duong_dan):
        self.duong_dan = duong_dan

    def mo_file_an_toan(self):
        try:
            if not self.duong_dan.lower().endswith('.docx'):
                return None
            if not os.path.exists(self.duong_dan):
                return None
            return docx.Document(self.duong_dan)
        except Exception as e:
            print(f"❌ Lỗi mở file {os.path.basename(self.duong_dan)}: {e}")
            return None


# ==========================================
# 2. LỚP TRÍCH XUẤT - TẠO CẤU TRÚC PHÂN CẤP
# ==========================================
class TrinhTrichXuat(BoXuLyFileGoc):
    def __init__(self, duong_dan):
        super().__init__(duong_dan)
        self.ket_qua_phan_cap = {}

    def chuan_hoa_ky_nang(self, ten):
        mapping = {"nghe": "nghe", "nói": "noi", "đọc": "doc", "viết": "viet"}
        return mapping.get(ten.lower(), ten.lower())

    def thuc_thi_tao_json(self):
        tai_lieu = self.mo_file_an_toan()
        if not tai_lieu: return

        cac_dong = [p.text.strip() for p in tai_lieu.paragraphs if p.text.strip()]

        phan_hien_tai = ""
        bai_hien_tai = ""
        bo_dem_muc = {}  # Theo dõi thứ tự mục

        for dong in cac_dong:
            # 1. Tìm PHẦN (VD: PHẦN A, Phần B...)
            khop_phan = re.search(r"^PHẦN\s+([A-Z])", dong, re.IGNORECASE)
            if khop_phan:
                phan_hien_tai = khop_phan.group(1).upper()
                if phan_hien_tai not in self.ket_qua_phan_cap:
                    self.ket_qua_phan_cap[phan_hien_tai] = {}
                continue

            # 2. Tìm BÀI (VD: Bài 1, bài: 2...)
            khop_bai = re.search(r"^bài\s*:?\s*(\d+)", dong, re.IGNORECASE)
            if khop_bai:
                bai_hien_tai = f"bai_{khop_bai.group(1)}"
                if phan_hien_tai and bai_hien_tai not in self.ket_qua_phan_cap[phan_hien_tai]:
                    self.ket_qua_phan_cap[phan_hien_tai][bai_hien_tai] = {}
                bo_dem_muc.clear()  # Reset lại bộ đếm khi sang bài mới
                continue

            # 3. Tìm KỸ NĂNG và NỘI DUNG
            # Cập nhật Regex: Bỏ qua các từ "Nội dung", "Đáp án", cho phép linh hoạt hơn (VD: Nghe:, Đáp án nghe:, Nội dung nói:...)
            khop_nd = re.search(r"^(?:Nội dung|Đáp án|Phần)?\s*(nghe|nói|đọc|viết)\s*[:\.]\s*(.*)", dong, re.IGNORECASE)

            if khop_nd and phan_hien_tai and bai_hien_tai:
                ky_nang = self.chuan_hoa_ky_nang(khop_nd.group(1))
                noi_dung = khop_nd.group(2)

                # Khởi tạo kỹ năng nếu chưa có
                if ky_nang not in self.ket_qua_phan_cap[phan_hien_tai][bai_hien_tai]:
                    self.ket_qua_phan_cap[phan_hien_tai][bai_hien_tai][ky_nang] = {}
                    bo_dem_muc[ky_nang] = 1

                # Gán vào theo dạng muc_1, muc_2...
                muc_key = f"muc_{bo_dem_muc[ky_nang]}"
                self.ket_qua_phan_cap[phan_hien_tai][bai_hien_tai][ky_nang][muc_key] = noi_dung
                bo_dem_muc[ky_nang] += 1

        # Lưu file JSON nếu có dữ liệu trích xuất được
        if self.ket_qua_phan_cap:
            duong_dan_json = self.duong_dan.replace(".docx", ".json")
            with open(duong_dan_json, 'w', encoding='utf-8') as f:
                json.dump(self.ket_qua_phan_cap, f, ensure_ascii=False, indent=4)
            print(f"✅ Đã tạo JSON thành công: {os.path.basename(duong_dan_json)}")
        else:
            print(f"⚠️ Không tìm thấy cấu trúc chuẩn trong file: {os.path.basename(self.duong_dan)}")


# ==========================================
# 3. LỚP QUẢN LÝ
# ==========================================
class KhoDuLieuTiengAnh:
    def __init__(self, thu_muc_goc):
        self.thu_muc_goc = thu_muc_goc
        self.kho_tong = {}
        self.cap_nhat_du_lieu()

    # Hàm gộp Dictionary sâu (Tránh bị ghi đè dữ liệu Bài/Phần giữa các file khác nhau)
    def _gop_tu_dien(self, dict_goc, dict_moi):
        for key, value in dict_moi.items():
            if isinstance(value, dict) and key in dict_goc and isinstance(dict_goc[key], dict):
                self._gop_tu_dien(dict_goc[key], value)
            else:
                # Nếu file sau có key trùng lặp (ví dụ muc_1 của nghe), nó sẽ tạo key mới như muc_1_dapan
                # Để đơn giản, ở đây ta gộp đè nếu là string, hoặc bạn có thể thiết kế lại cấu trúc.
                dict_goc[key] = value

    def cap_nhat_du_lieu(self):
        # Bước 1: Quét tạo JSON từ tất cả file .docx
        for goc, _, cac_file in os.walk(self.thu_muc_goc):
            for f in cac_file:
                path = os.path.join(goc, f)
                if f.endswith(".docx") and not f.startswith("~$"):
                    TrinhTrichXuat(path).thuc_thi_tao_json()

        # Bước 2: Đọc tất cả file JSON để đưa vào kho tổng
        for goc, _, cac_file in os.walk(self.thu_muc_goc):
            for f in cac_file:
                path = os.path.join(goc, f)
                if f.endswith(".json"):
                    with open(path, 'r', encoding='utf-8') as jf:
                        try:
                            du_lieu = json.load(jf)
                            self._gop_tu_dien(self.kho_tong, du_lieu)
                        except Exception as e:
                            print(f"Lỗi đọc JSON {f}: {e}")

    def lay_gia_tri(self, cap, so_bai, ky_nang, thu_tu):
        try:
            return self.kho_tong[cap.upper()][f"bai_{so_bai}"][ky_nang.lower()][f"muc_{thu_tu}"]
        except KeyError:
            return "Không tìm thấy dữ liệu"


# ==========================================
# 4. CHẠY CHƯƠNG TRÌNH
# ==========================================
if __name__ == "__main__":
    # Lấy thư mục chứa file code hiện tại đang chạy
    thu_muc = os.path.dirname(os.path.abspath(__file__))

    print("--- BẮT ĐẦU XỬ LÝ FILE ---")
    kho = KhoDuLieuTiengAnh(thu_muc)

    print("\n--- KIỂM TRA DỮ LIỆU ---")
    print(f"Kết quả A-Bai1-Nghe-1: {kho.lay_gia_tri('A', 1, 'nghe', 1)}")

    # In toàn bộ cấu trúc kho dữ liệu để bạn dễ hình dung (chỉ in 500 ký tự đầu)
    print("\n--- CẤU TRÚC KHO TỔNG ---")
    print(json.dumps(kho.kho_tong, ensure_ascii=False, indent=2)[:500] + "\n...")