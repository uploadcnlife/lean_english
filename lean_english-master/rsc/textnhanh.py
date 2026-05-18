import json
from pathlib import Path


class tong_doc:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.data = {
            'dap_an': {},
            'ngu_phap': {},
            'noidung_bai': {},
            'kiem_tra': {}
        }
        self.load_all()

    def load_all(self):
        text_dir = self.base_path / 'LearnEnglish' / 'Data' / 'Text'

        for category in ['dap_an', 'ngu_phap', 'kiem_tra', 'noidung_bai']:
            category_dir = text_dir / category
            if category_dir.exists():
                for json_file in category_dir.glob('*.json'):
                    if not json_file.name.startswith('~$'):
                        key = json_file.stem
                        with open(json_file, 'r', encoding='utf-8') as f:
                            self.data[category][key] = json.load(f)
                        print(f" Loaded: {category}/{key}")

    def get(self, category, name):
        if category is None:
            for cat_data in self.data.values():
                if name in cat_data:
                    return cat_data[name]
            return None
        return self.data.get(category, {}).get(name)

    def get_all_answers(self):
        return self.data['dap_an']

    def get_all_grammar(self):
        return self.data['ngu_phap']

    def get_all_conten(self):
        return self.data['kiem_tra']

    def get_all_content(self):
        return self.data['noidung_bai']



dot = tong_doc()


def search_data(file_name, level=None, bai=None, ky_nang=None, muc=None, return_values_only=True):
    """
    Tìm kiếm dữ liệu.

    Nếu kết quả là một dict:
        - return_values_only = True  → trả về list các giá trị (values)
        - return_values_only = False → trả về list các key

    """
    # 1. Xử lý file_name = None -> lấy toàn bộ dữ liệu từ mọi file
    if file_name is None:
        all_data = {}
        for cat in dot.data:
            all_data.update(dot.data[cat])
        result = all_data if all_data else "Không có dữ liệu"
        if isinstance(result, dict):
            return list(result.values()) if return_values_only else list(result.keys())
        return result

    # 2. Tìm file
    file_data = dot.get(None, file_name)
    if not file_data:
        return f"Không tìm thấy file JSON: {file_name}"

    # 3. Duyệt theo cấu trúc
    if level is None:
        result = file_data
    else:
        data_level = file_data.get(level)
        if data_level is None:
            return f"Không tìm thấy Level {level} trong file {file_name}"
        if bai is None:
            result = data_level
        else:
            data_bai = data_level.get(bai)
            if data_bai is None:
                return f"Không tìm thấy bài {bai} trong Level {level}"
            if ky_nang is None:
                result = data_bai
            else:
                data_skill = data_bai.get(ky_nang)
                if data_skill is None:
                    return f"Không tìm thấy kỹ năng {ky_nang} trong bài {bai}"
                if muc is None:
                    result = data_skill
                else:
                    result = data_skill.get(muc, f"Không tìm thấy mục {muc} trong {ky_nang}")

    # 4. Xử lý kết quả nếu là dict
    if isinstance(result, dict):
        if return_values_only:
            return list(result.values())
        else:
            return list(result.keys())
    return result


def allfile_level(level_name):
    """
    Quét toàn bộ tất cả các file trong tất cả thư mục,
    tìm level tương ứng và gom tất cả các 'bài' lại.
    """
    danh_sach_bai = set()
    for category, files in dot.data.items():
        for file_name, file_data in files.items():
            if level_name in file_data:
                danh_sach_bai.update(file_data[level_name].keys())

    return {level_name: sorted(set(danh_sach_bai), key=lambda x: int(x.split('_')[1]))}

if __name__ == "__main__":
    # 5. Lấy một mục cụ thể (kết quả là string, không phải dict) -> trả về nguyên bản
    muc_1 = search_data(None, level='A', bai='bai_1', ky_nang='nghe', muc='muc_1')
    print("Muc_1:", muc_1)  # 'nội dung 1'

    keys_bai = search_data(None, level='A', bai=None, return_values_only=True)
    print("key", keys_bai)


    ket_qua = allfile_level('B')
    print(ket_qua)