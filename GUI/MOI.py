import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from dang_nhap import Ui_MainWindow as LoginUI

from dang_ki import Ui_MainWindow as RegisterUI
from rsc.profile import QuanLyTaiKhoan


class MainApp:
    def __init__(self):
        self.quan_ly = QuanLyTaiKhoan()

        # Khởi tạo cửa sổ Đăng Nhập
        self.login_window = QMainWindow()
        self.ui_login = LoginUI()
        self.ui_login.setupUi(self.login_window)

        # Khởi tạo cửa sổ Đăng Ký
        self.register_window = QMainWindow()
        self.ui_reg = RegisterUI()
        self.ui_reg.setupUi(self.register_window)

        # Kết nối sự kiện nút bấm
        self.ui_login.pushButton.clicked.connect(self.xu_ly_dang_nhap)
        self.ui_login.nut_2.clicked.connect(lambda: self.chuyen_man_hinh(self.register_window, self.login_window))

        self.ui_reg.pushButton.clicked.connect(self.xu_ly_dang_ky)
        self.ui_reg.nut_1.clicked.connect(lambda: self.chuyen_man_hinh(self.login_window, self.register_window))

    def chuyen_man_hinh(self, show_win, hide_win):
        hide_win.hide()
        show_win.show()

    def xu_ly_dang_nhap(self):
        user = self.ui_login.lineEdit.text()
        pwd = self.ui_login.lineEdit_2.text()

        # Tìm trong dữ liệu
        is_success = False
        for uid, info in self.quan_ly.data.items():
            if info['tai_khoan'] == user and info['mat_khau'] == pwd:
                is_success = True
                break

        if is_success:
            QMessageBox.information(self.login_window, "Thông báo", "Đăng nhập thành công!")
        else:
            QMessageBox.warning(self.login_window, "Lỗi", "Sai tài khoản hoặc mật khẩu!")

    def xu_ly_dang_ky(self):
        user = self.ui_reg.lineEdit.text()
        pwd = self.ui_reg.lineEdit_2.text()

        # Gọi hàm đăng ký từ profile.py (cần chỉnh sửa nhẹ class profile để nhận tham số)
        # Hoặc viết trực tiếp logic kiểm tra ở đây:
        if any(item['tai_khoan'] == user for item in self.quan_ly.data.values()):
            QMessageBox.warning(self.register_window, "Lỗi", "Tài khoản đã tồn tại!")
        else:
            # Thêm user vào quan_ly.data và lưu
            import uuid
            uid = str(uuid.uuid4())[:8]
            self.quan_ly.data[uid] = {"tai_khoan": user, "mat_khau": pwd}
            self.quan_ly._luu_du_lieu_json()
            QMessageBox.information(self.register_window, "Thành công", "Đăng ký thành công!")
            self.chuyen_man_hinh(self.login_window, self.register_window)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainApp()
    main.login_window.show()
    sys.exit(app.exec_())