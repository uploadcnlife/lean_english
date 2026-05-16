import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'GUI'))
sys.path.append(os.path.join(current_dir, 'rsc'))

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QListView
from PyQt5.QtCore import QStringListModel, Qt
from PyQt5.QtWidgets import QPushButton
from GUI.khungthan import Ui_khungchung
from rsc.da_class import LopNghe, LopNoi, LopDoc, LopViet, LopKiemTra, NguPhap
from rsc.khung import KhungBaiHoc
import subprocess



class MainApp(QMainWindow, Ui_khungchung):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.btn_next = QPushButton("truoc >", self.bang_ndkt)#
        self.btn_prev = QPushButton("< sau", self.bang_ndkt)#

        #  kích thước  để mặc định
        self.btn_next.setFixedSize(100, 20)
        self.btn_prev.setFixedSize(100, 20)

        self.setup_navigation()  # căn chỉnh vị trí ban đầu


        # Khởi tạo đối tượng quản lý dữ liệu chính
        self.manager = KhungBaiHoc()

        # Biến trạng thái hiện tại
        self.current_level = 'A'      # A, B, C
        self.current_lesson_index = 0  # 0-based
        self.current_skill = 'nghe'    # nghe, noi, doc, viet, kiemtra


        # Đối tượng kỹ năng hiện tại
        self.skill_obj = None

        # Gán sự kiện cho các nút cấp độ
        self.capa.clicked.connect(lambda: self.set_level('A'))
        self.capb.clicked.connect(lambda: self.set_level('B'))
        self.capc.clicked.connect(lambda: self.set_level('C'))

        # Gán sự kiện cho các nút bài học
        self.bai1.clicked.connect(lambda: self.set_lesson(0))
        self.bai2.clicked.connect(lambda: self.set_lesson(1))
        self.bai3.clicked.connect(lambda: self.set_lesson(2))
        self.bai4.clicked.connect(lambda: self.set_lesson(3))
        self.bai5.clicked.connect(lambda: self.set_lesson(4))
        self.bai6.clicked.connect(lambda: self.set_lesson(5))
        self.bai7.clicked.connect(lambda: self.set_lesson(6))
        self.bai8.clicked.connect(lambda: self.set_lesson(7))
        self.bai9.clicked.connect(lambda: self.set_lesson(8))
        self.bai10.clicked.connect(lambda: self.set_lesson(9))

        # Gán sự kiện cho nút ngữ pháp
        self.nguphap.clicked.connect(self.show_grammar)

        # Gán sự kiện tìm kiếm ngữ pháp
        self.pushButton_tmkiem.clicked.connect(self.search_grammar)

        # Gán sự kiện khi đổi tab (kỹ năng)
        self.bang_ndkt.currentChanged.connect(self.on_tab_changed)

        # Gán sự kiện cho các nút trả lời (sẽ được kết nối động)
        self.connect_answer_buttons()

        # Gán sự kiện cho nút ghi âm kiểm tra
        self.ghi_amkt.clicked.connect(self.record_test_answer)
        self.pushButton_10.clicked.connect(self.record_speaking_answer)

        # Khởi tạo giao diện mặc định
        self.set_level('A')
        self.set_lesson(0)
        self.on_tab_changed(0)   # tab Nghe
        self.canhan.clicked.connect(self.show_login_ui) #

    def setup_navigation(self):
        """Căn chỉnh vị trí 2 nút bên trong góc trên bên phải của bang_ndkt"""
        if not self.bang_ndkt:
            return

        # Kích thước vùng chứa
        w = self.bang_ndkt.width()
        btn_w = self.btn_prev.width()
        btn_h = self.btn_prev.height()

        right_margin = 20   # khoảng cách từ mép phải
        top_margin = 20     # khoảng cách từ mép trên

        # Vị trí nút "Tiếp"
        btn_next_x = w - btn_w - right_margin
        btn_next_y = top_margin
        self.btn_next.move(btn_next_x, btn_next_y)

        # Vị trí nút "Quay lại" nằm bên trái, cách 10px
        spacing = 10
        btn_prev_x = btn_next_x - btn_w - spacing
        self.btn_prev.move(btn_prev_x, btn_next_y)

        # Đưa 2 nút lên trên cùng để không bị che
        self.btn_prev.raise_()
        self.btn_next.raise_()

        # Kết nối sự kiện (chỉ một lần)
        if not self.btn_next.receivers(self.btn_next.clicked):
            self.btn_next.clicked.connect(lambda: self.navigate_page(1))
        if not self.btn_prev.receivers(self.btn_prev.clicked):
            self.btn_prev.clicked.connect(lambda: self.navigate_page(-1))

    def resizeEvent(self, event):
        """Cập nhật dlại vị trí nút khi cửa sổ thay đổi kích thước"""
        self.setup_navigation()
        super().resizeEvent(event)


    def navigate_page(self, direction):
        stack_map = {
            'nghe': self.stackednghe,
            'noi': self.stackednoi,
            'doc': self.stackeddoc_2,
            'viet': self.stackedviet_3,
            'kiemtra': self.stackedkt_4
        }

        stack = stack_map.get(self.current_skill)
        if stack:
            new_index = stack.currentIndex() + direction
            if 0 <= new_index < stack.count():
                stack.setCurrentIndex(new_index)
                self.load_current_skill()

    # ------------------ CẤP ĐỘ ------------------
    def set_level(self, level):
        """Thiết lập cấp độ hiện tại (A, B, C)"""
        self.current_level = level
        self.manager.thiet_lap_level(level)
        # Cập nhật trạng thái nhấn nút
        self.capa.setChecked(level == 'A')
        self.capb.setChecked(level == 'B')
        self.capc.setChecked(level == 'C')
        # Tải lại bài học hiện tại
        self.set_lesson(self.current_lesson_index)

    # ------------------ BÀI HỌC ------------------
    def set_lesson(self, index):
        """Chọn bài học theo chỉ số (0-9)"""
        if not self.manager.danh_sach_bai:
            QMessageBox.warning(self, "Lỗi", f"Không có bài học cho cấp {self.current_level}")
            return
        if index >= len(self.manager.danh_sach_bai):
            QMessageBox.warning(self, "Lỗi", f"Chỉ có {len(self.manager.danh_sach_bai)} bài ở cấp này")
            return
        self.current_lesson_index = index
        self.manager.vi_tri_bai = index
        # Tải kỹ năng hiện tại
        self.load_current_skill()

    # ------------------ KỸ NĂNG ------------------
    def on_tab_changed(self, tab_index):
        """Khi đổi tab kỹ năng (Nghe, Nói, Đọc, Viết, Kiểm tra)"""
        tab_text = self.bang_ndkt.tabText(tab_index)
        if tab_text == "nghe":
            self.current_skill = 'nghe'
            self.stackednghe.setCurrentIndex(0)
        elif tab_text == "nói":
            self.current_skill = 'noi'
            self.stackednoi.setCurrentIndex(0)
        elif tab_text == "đọc":
            self.current_skill = 'doc'
            self.stackeddoc_2.setCurrentIndex(0)
        elif tab_text == "viết":
            self.current_skill = 'viet'
            self.stackedviet_3.setCurrentIndex(0)
        elif tab_text == "kiểm tra":
            self.current_skill = 'kiemtra'
            self.stackedkt_4.setCurrentIndex(1)   # hiển thị trang kiểm tra
        self.load_current_skill()

    def load_current_skill(self):
        """Tải dữ liệu cho kỹ năng hiện tại, bài hiện tại"""
        if self.current_skill == 'kiemtra':
            self.load_test()
        else:
            self.load_skill()

    def load_skill(self):
        """Tải kỹ năng bình thường (Nghe, Nói, Đọc, Viết)"""
        bai = self.manager.lay_bai_hien_tai()
        if not bai:
            return
        # Tạo đối tượng kỹ năng tương ứng
        so_bai = int(bai.split('_')[-1]) if '_' in bai else int(bai)
        if self.current_skill == 'nghe':
            self.skill_obj = LopNghe(level=self.current_level, so_bai=so_bai)
        elif self.current_skill == 'noi':
            self.skill_obj = LopNoi(level=self.current_level, so_bai=so_bai, ky_nang='noi')
        elif self.current_skill == 'doc':
            self.skill_obj = LopDoc(level=self.current_level, so_bai=so_bai)
        elif self.current_skill == 'viet':
            self.skill_obj = LopViet(level=self.current_level, so_bai=so_bai)
        else:
            return

        # Lấy dữ liệu mức 1 và mức 2
        data_muc1 = self.skill_obj.lay_du_lieu_muc_1()
        data_muc2 = self.skill_obj.lay_du_lieu_muc_2()

        # Hiển thị mức 1
        if data_muc1:
            self.display_muc1(data_muc1)
        # Hiển thị mức 2
        if data_muc2:
            self.display_muc2(data_muc2)

    def display_muc1(self, data):
        """Hiển thị câu hỏi mức 1 vào các ô tương ứng theo kỹ năng"""
        if self.current_skill == 'nghe':
            self.text_viet_nghe1.setPlainText(data['cau_hoi'])
            self.text_en_nghe_1.setPlainText(data['cau_hoiviet'])
            self.tl_nghe_1.clear()
        elif self.current_skill == 'noi':
            self.text_vi_noi_2.setPlainText(data['cau_hoiviet'])
            self.tl_noi_2.clear()
        elif self.current_skill == 'doc':
            self.text_en_doc_1.setPlainText(data['cau_hoi'])
            self.text_vi_doc_1.setPlainText(data['cau_hoiviet'])
            self.tl_doc_1.clear()
        elif self.current_skill == 'viet':
            self.text_en_viet_1.setPlainText(data['cau_hoi'])
            self.text_vi_viet_1.setPlainText(data['cau_hoiviet'])
            self.tl_viet_1.clear()

        # Lưu đáp án đúng để kiểm tra
        self.correct_answer_muc1 = data['dap_an_dung']

    def display_muc2(self, data):
        """Hiển thị câu hỏi mức 2"""
        if self.current_skill == 'nghe':
            self.text_viet_nghe_5.setPlainText(data['cau_hoiviet'])
            self.text_anh_nghe_2.setPlainText(data['cau_hoi'])
            self.tl_nghe_2.clear()
        elif self.current_skill == 'noi':
            # Nói mức 2 có thể dùng cùng ô với mức 1? Theo mapping, không có ô riêng cho nói mức2
            # Tạm bỏ qua
            pass
        elif self.current_skill == 'doc':
            self.text_vi_doc_2.setPlainText(data['cau_hoiviet'])
            self.text_en_doc_2.setPlainText(data['cau_hoi'])
            self.tl_doc_2.clear()
        elif self.current_skill == 'viet':
            self.text_vi_viet_2.setPlainText(data['cau_hoiviet'])
            self.text_en_viet_2.setPlainText(data['cau_hoi'])
            self.tl_viet_2.clear()
        self.correct_answer_muc2 = data['dap_an_dung']

    # ------------------ KIỂM TRA ------------------
    def load_test(self):
        """Tải câu hỏi kiểm tra cho tab kiểm tra"""
        bai = self.manager.lay_bai_hien_tai()
        if not bai:
            return
        so_bai = int(bai.split('_')[-1]) if '_' in bai else int(bai)
        self.test_obj = LopKiemTra(level_hien_tai=self.current_level)
        # Lấy dữ liệu cho từng kỹ năng trong bài kiểm tra
        # Hiển thị câu hỏi vào các page tương ứng
        for kn, page_name in [('nghe', self.page_12), ('noi', self.page_13), ('doc', self.page_18), ('viet', self.page_10)]:
            data = self.test_obj.lay_du_lieu_bai(kn, so_bai)
            if data:
                if kn == 'nghe':
                    self.text_en_kt_5.setPlainText(data['q'])
                    # Các lựa chọn có thể hiển thị ở đâu đó
                elif kn == 'noi':
                    self.text_vi_kt_3.setPlainText(data['q'])
                elif kn == 'doc':
                    self.text_en_kt_1.setPlainText(data['q'])
                elif kn == 'viet':
                    self.text_en_kt_2.setPlainText(data['q'])
                # Lưu đáp án
                setattr(self, f'correct_{kn}', data['a'])

    def record_test_answer(self):
        """Ghi âm câu trả lời cho phần kiểm tra (nói)"""
        if hasattr(self, 'test_obj'):
            user_ans = self.test_obj.thu_am_tra_text()
            # So sánh với đáp án đúng của kỹ năng nói
            if user_ans == getattr(self, 'correct_noi', ''):
                self.tbao_kt_3.setPlainText(" Chính xác!")
            else:
                self.tbao_kt_3.setPlainText(f" Sai. Đáp án: {getattr(self, 'correct_noi', '')}")

    def record_speaking_answer(self):
        """Ghi âm cho kỹ năng nói (tab Nói)"""
        if self.current_skill == 'noi' and self.skill_obj:
            user_ans = self.skill_obj._listen_once()
            if user_ans == self.correct_answer_muc1:
                self.tbao_noi_2.setPlainText(" Chính xác!")
            else:
                self.tbao_noi_2.setPlainText(f" Sai. Đáp án đúng: {self.correct_answer_muc1}")

    # ------------------ XỬ LÝ TRẢ LỜI ------------------
    def connect_answer_buttons(self):
        """Kết nối các ô nhập và nút kiểm tra (sẽ dùng editingFinished hoặc nút riêng)"""
        # Tạo các nút kiểm tra nếu chưa có? Trong UI có sẵn các nút? Không có nhiều.
        # Thay vào đó, ta dùng tín hiệu returnPressed của QLineEdit
        self.tl_nghe_1.returnPressed.connect(lambda: self.check_answer('nghe', 1))
        self.tl_nghe_2.returnPressed.connect(lambda: self.check_answer('nghe', 2))
        self.tl_noi_2.returnPressed.connect(lambda: self.check_answer('noi', 1))
        self.tl_doc_1.returnPressed.connect(lambda: self.check_answer('doc', 1))
        self.tl_doc_2.returnPressed.connect(lambda: self.check_answer('doc', 2))
        self.tl_viet_1.returnPressed.connect(lambda: self.check_answer('viet', 1))
        self.tl_viet_2.returnPressed.connect(lambda: self.check_answer('viet', 2))
        # Kiểm tra
        self.tl_kt_1.returnPressed.connect(lambda: self.check_test_answer('doc'))
        self.tl_kt_2.returnPressed.connect(lambda: self.check_test_answer('viet'))
        self.tl_kt_3.returnPressed.connect(lambda: self.check_test_answer('noi'))
        self.tl_kt_5.returnPressed.connect(lambda: self.check_test_answer('nghe'))

    def check_answer(self, skill, muc):
        """Kiểm tra câu trả lời cho kỹ năng và mức"""
        if muc == 1:
            correct = getattr(self, 'correct_answer_muc1', '')
        else:
            correct = getattr(self, 'correct_answer_muc2', '')
        # Lấy ô nhập tương ứng
        if skill == 'nghe':
            user_input = self.tl_nghe_1.text() if muc == 1 else self.tl_nghe_2.text()
            msg_box = self.dan_nghe_1 if muc == 1 else self.tbao_nghe_2
        elif skill == 'noi':
            user_input = self.tl_noi_2.text()
            msg_box = self.tbao_noi_2
        elif skill == 'doc':
            user_input = self.tl_doc_1.text() if muc == 1 else self.tl_doc_2.text()
            msg_box = self.tbao_doc_1 if muc == 1 else self.tbao_doc_2
        elif skill == 'viet':
            user_input = self.tl_viet_1.text() if muc == 1 else self.tl_viet_2.text()
            msg_box = self.tbao_viet_1 if muc == 1 else self.tbao_viet_2
        else:
            return

        if user_input.strip().lower() == correct.lower():
            msg_box.setPlainText(" Chính xác!")
        else:
            msg_box.setPlainText(f" Sai. Đáp án đúng: {correct}")

    def check_test_answer(self, test_skill):
        """Kiểm tra câu trả lời kiểm tra"""
        correct = getattr(self, f'correct_{test_skill}', '')
        if test_skill == 'nghe':
            user_input = self.tl_kt_5.text()
            msg_box = self.tbao_kt_5
        elif test_skill == 'noi':
            user_input = self.tl_kt_3.text()
            msg_box = self.tbao_kt_3
        elif test_skill == 'doc':
            user_input = self.tl_kt_1.text()
            msg_box = self.tbao_kt_1
        elif test_skill == 'viet':
            user_input = self.tl_kt_2.text()
            msg_box = self.tbao_kt_2
        else:
            return

        if user_input.strip().lower() == correct.lower():
            msg_box.setPlainText(" Chính xác!")
        else:
            msg_box.setPlainText(f" Sai. Đáp án đúng: {correct}")

    # ------------------ NGỮ PHÁP ------------------
    def show_grammar(self):
        """Hiển thị khung ngữ pháp và ẩn các khung khác"""
        self.bang_ngu_phap.show()
        self.bang_ndkt.hide()
        # Kết nối sự kiện click cho listView
        try:
            self.listView.clicked.disconnect()
        except:
            pass
        self.listView.clicked.connect(self.on_grammar_item_clicked)
        # Tải tất cả chủ đề ngữ pháp (gộp chung) lên listView
        self.load_all_grammar()

    def load_all_grammar(self):
        """Hiển thị tất cả chủ đề ngữ pháp lên listView (gộp chung)"""
        grammar = NguPhap()
        data = grammar.get_data_raw()
        if not data:
            self.listView.setModel(QStringListModel([]))
            return
        items = []
        self.grammar_contents = {}  # lưu nội dung chi tiết cho từng chủ đề
        for level, bai_dict in data.items():
            for bai, content in bai_dict.items():
                for chu_de, giai_thich in content.items():
                    display_text = f"[{level} - {bai}] {chu_de}"
                    items.append(display_text)
                    self.grammar_contents[display_text] = giai_thich
        model = QStringListModel(items)
        self.listView.setModel(model)

    def search_grammar(self):
        """Tìm kiếm ngữ pháp theo từ khóa, hiển thị kết quả lên listView"""
        keyword = self.timkiem.text().strip()
        grammar = NguPhap()
        data = grammar.get_data_raw()
        if not data:
            self.listView.setModel(QStringListModel([]))
            return
        if not keyword:
            self.load_all_grammar()
            return
        items = []
        self.grammar_contents = {}
        for level, bai_dict in data.items():
            for bai, content in bai_dict.items():
                for chu_de, giai_thich in content.items():
                    if keyword.lower() in chu_de.lower() or keyword.lower() in giai_thich.lower():
                        display_text = f"[{level} - {bai}] {chu_de}"
                        items.append(display_text)
                        self.grammar_contents[display_text] = giai_thich
        model = QStringListModel(items)
        self.listView.setModel(model)

    def on_grammar_item_clicked(self, index):
        """hiển thị nội dung ở listView_5"""
        model = self.listView.model()
        if not model:
            return
        item_text = model.data(index, Qt.DisplayRole)
        if not item_text:
            return
        content = self.grammar_contents.get(item_text, "Không có nội dung chi tiết.")
        # Hiển thị nội dung dưới dạng danh sách các dòng
        content_lines = content.split('\n')
        model_content = QStringListModel(content_lines)
        self.listView_5.setModel(model_content)

    def show_login_ui(self):
        try:

            current_path = Path(__file__).resolve()
            project_source_dir = None

 
            for parent in current_path.parents:
                if (parent / "GUI").exists() and (parent / "rsc").exists():
                    project_source_dir = parent
                    break

 
            if not project_source_dir:
                project_source_dir = current_path.parent


            moi_path_obj = project_source_dir / "GUI" / "MOI.py"

            if moi_path_obj.exists():
                moi_path = os.fspath(moi_path_obj)
                source_dir_str = os.fspath(project_source_dir)


                env = os.environ.copy()
                if "PYTHONPATH" in env:
                    env["PYTHONPATH"] = source_dir_str + os.pathsep + env["PYTHONPATH"]
                else:
                    env["PYTHONPATH"] = source_dir_str

                subprocess.Popen(
                    ["cmd.exe", "/k", sys.executable, moi_path],
                    env=env
                )
            else:
                QMessageBox.warning(self, "Lỗi Path",
                                    f"Không tìm thấy file MOI.py tại đường dẫn dự kiến:\n{moi_path_obj}")

        except Exception as e:
            QMessageBox.warning(self, "Lỗi Hệ Thống", f"Gặp lỗi khi thực thi: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
