import json
import os
import uuid


class QuanLyTaiKhoan:
    def __init__(self, ten_file="users_data.json"):
        """Chạy đầu tiên khi tạo đối tượng"""
        self.file_json = ten_file
        # Tự động tải dữ liệu khi khởi động chương trình (không cần tải lại nhiều lần)
        self.data = self._doc_du_lieu_json()
        self.nguoi_dung_hien_tai = None  # Trạng thái đăng nhập

    def _doc_du_lieu_json(self):
        """ đọc dữ liệu từ file"""
        try:
            if not os.path.exists(self.file_json):
                return {}
            with open(self.file_json, 'r', encoding='utf-8') as file:
                return json.load(file)
        except json.JSONDecodeError:
            print("[-] Lỗi: File JSON bị hỏng định dạng. Đang khởi tạo dữ liệu trống.")
            return {}
        except Exception as e:
            print(f"[-] Đã xảy ra lỗi khi đọc file: {e}")
            return {}

    def _luu_du_lieu_json(self):
        """ lưu dữ liệu xuống file"""
        try:
            with open(self.file_json, 'w', encoding='utf-8') as file:
                json.dump(self.data, file, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[-] Lỗi khi lưu file JSON: {e}")

    def dang_ky(self):
        """Phương thức đăng ký"""
        print("\n--- ĐĂNG KÝ TÀI KHOẢN ---")
        try:
            # Ép nhập dữ liệu (chống trôi lệnh)
            tai_khoan = ""
            while not tai_khoan:
                tai_khoan = input("Nhập tên tài khoản (username): ").strip()

            # Kiểm tra tài khoản tồn tại (dùng self.data)
            for user_info in self.data.values():
                if user_info['tai_khoan'] == tai_khoan:
                    print("[-] Lỗi: Tên tài khoản này đã tồn tại!")
                    return

            mat_khau = ""
            while not mat_khau:
                mat_khau = input("Nhập mật khẩu: ").strip()

            id_nguoi_dung = str(uuid.uuid4())[:8]

            # Thêm vào bộ nhớ (self.data)
            self.data[id_nguoi_dung] = {
                "tai_khoan": tai_khoan,
                "mat_khau": mat_khau
            }

            # Lưu xuống file
            self._luu_du_lieu_json()
            print(f"[+] Tạo tài khoản thành công! Tên đăng nhập của bạn là: {tai_khoan}")

        except Exception as e:
            print(f"[-] Lỗi trong quá trình đăng ký: {e}")

    def dang_nhap(self):
        """Phương thức đăng nhập"""
        print("\n--- ĐĂNG NHẬP ---")
        try:
            if not self.data:
                print("[-] Chưa có tài khoản nào. Vui lòng đăng ký trước!")
                return

            tai_khoan_nhap = ""
            while not tai_khoan_nhap:
                tai_khoan_nhap = input("Nhập Tên tài khoản: ").strip()

            mat_khau_nhap = ""
            while not mat_khau_nhap:
                mat_khau_nhap = input("Nhập mật khẩu: ").strip()

            # Tìm kiếm người dùng
            id_tim_thay = None
            for uid, thong_tin in self.data.items():
                if thong_tin['tai_khoan'] == tai_khoan_nhap:
                    id_tim_thay = uid
                    break

            if id_tim_thay:
                if self.data[id_tim_thay]['mat_khau'] == mat_khau_nhap:
                    print(f"[+] ĐĂNG NHẬP THÀNH CÔNG! Xin chào, {tai_khoan_nhap}.")
                    # Lưu trạng thái đăng nhập vào class
                    self.nguoi_dung_hien_tai = tai_khoan_nhap
                else:
                    print("[-] Lỗi: Sai mật khẩu!")
            else:
                print("[-] Lỗi: Tên tài khoản không tồn tại!")

        except Exception as e:
            print(f"[-] Lỗi trong quá trình đăng nhập: {e}")

    def dang_xuat(self):
        """Phương thức đăng xuất"""
        self.nguoi_dung_hien_tai = None
        print("[+] Đã đăng xuất thành công!")

    def chay_chuong_trinh(self):
        """Vòng lặp menu chính của hệ thống"""
        while True:
            try:
                print("\n" + "=" * 30)
                if self.nguoi_dung_hien_tai:
                    print(f"[ TRẠNG THÁI: ĐÃ ĐĂNG NHẬP - User: {self.nguoi_dung_hien_tai} ]")
                    print("1. Đăng xuất")
                    print("2. Thoát chương trình")

                    chon = input("Chọn chức năng (1-2): ").strip()
                    if chon == '1':
                        self.dang_xuat()
                    elif chon == '2':
                        print("Tạm biệt!")
                        break
                    else:
                        print("[-] Lựa chọn không hợp lệ.")
                else:
                    print("[ TRẠNG THÁI: CHƯA ĐĂNG NHẬP ]")
                    print("1. Đăng ký tài khoản")
                    print("2. Đăng nhập")
                    print("3. Thoát chương trình")

                    chon = input("Chọn chức năng (1-3): ").strip()
                    if chon == '1':
                        self.dang_ky()
                    elif chon == '2':
                        self.dang_nhap()
                    elif chon == '3':
                        print("Tạm biệt!")
                        break
                    else:
                        print("[-] Lựa chọn không hợp lệ.")

            except KeyboardInterrupt:
                print("\nĐã ép buộc thoát chương trình.")
                break
            except Exception as e:
                print(f"[-] Lỗi hệ thống: {e}")


# =========================================
# CHẠY CHƯƠNG TRÌNH
# =========================================
if __name__ == "__main__":
    # Tạo một đối tượng (instance) từ Class
    he_thong = QuanLyTaiKhoan("users_data.json")

    # Kích hoạt vòng lặp chính
    he_thong.chay_chuong_trinh()