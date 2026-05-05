import unittest
import os
from unittest.mock import patch

from rsc.profile import QuanLyTaiKhoan


class TestQuanLyTaiKhoan(unittest.TestCase):

    def setUp(self):
        """Chạy trước mỗi bài test: Thiết lập file tạm để test"""
        self.test_file = "test_users.json"
        self.he_thong = QuanLyTaiKhoan(self.test_file)

    def tearDown(self):
        """Chạy sau mỗi bài test: Xóa file test để giữ sạch môi trường"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_dang_ky_thanh_cong(self):
        """Test chức năng đăng ký tài khoản mới"""
        # Giả lập nhập username là 'admin' và mật khẩu là '123'
        with patch('builtins.input', side_effect=['admin', '123']):
            self.he_thong.dang_ky()

        # Kiểm tra dữ liệu đã được lưu vào self.data chưa
        users = self.he_thong.data
        self.assertEqual(len(users), 1)

        # Lấy user đầu tiên trong dictionary để kiểm tra
        user_info = list(users.values())[0]
        self.assertEqual(user_info['tai_khoan'], 'admin')
        self.assertEqual(user_info['mat_khau'], '123')

    def test_dang_ky_trung_ten(self):
        """Test trường hợp đăng ký tên tài khoản đã tồn tại"""
        # Tạo sẵn một user
        self.he_thong.data['id123'] = {"tai_khoan": "user1", "mat_khau": "pass"}
        self.he_thong._luu_du_lieu_json()

        # Thử đăng ký lại với tên 'user1'
        with patch('builtins.input', side_effect=['user1', 'any_pass']):
            self.he_thong.dang_ky()

        # Kiểm tra số lượng user vẫn là 1 (không thêm mới được)
        self.assertEqual(len(self.he_thong.data), 1)

    def test_dang_nhap_thanh_cong(self):
        """Test chức năng đăng nhập với đúng tài khoản/mật khẩu"""
        # Tạo user mẫu
        self.he_thong.data['id456'] = {"tai_khoan": "testuser", "mat_khau": "hello"}

        with patch('builtins.input', side_effect=['testuser', 'hello']):
            self.he_thong.dang_nhap()

        # Kiểm tra trạng thái đăng nhập
        self.assertEqual(self.he_thong.nguoi_dung_hien_tai, "testuser")

    def test_dang_nhap_sai_mat_khau(self):
        """Test đăng nhập khi nhập sai mật khẩu"""
        self.he_thong.data['id456'] = {"tai_khoan": "testuser", "mat_khau": "hello"}

        with patch('builtins.input', side_effect=['testuser', 'wrong_pass']):
            self.he_thong.dang_nhap()

        # Trạng thái phải là None
        self.assertIsNone(self.he_thong.nguoi_dung_hien_tai)

    def test_dang_xuat(self):
        """Test chức năng đăng xuất"""
        self.he_thong.nguoi_dung_hien_tai = "admin"
        self.he_thong.dang_xuat()
        self.assertIsNone(self.he_thong.nguoi_dung_hien_tai)


if __name__ == "__main__":
    unittest.main()