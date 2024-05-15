from json import dump, load, dumps
from pathlib import Path
from .thread_manager import ThreadLock


class Folder(ThreadLock):
    def __init__(self, name):
        try:
            from main import ROOT  # 避免循环导入
        except ImportError:
            ROOT = Path(__file__).parent.parent  # 导入不了就默认用上级目录
        super().__init__()
        self.folder = ROOT / name
        self.folder.mkdir(parents=True, exist_ok=True)  # 目录不存在则创建

    def glob(self, pattern):
        return self.folder.glob(pattern)


class File(Folder):
    def __init__(self, folder, name, indented=True, incremental=False, type_=None, **args):
        super().__init__(folder)
        self.__args = args
        if type_ is None:
            type_ = f"json{'l' if incremental else ''}"
        self.file_name = f"{name}.{type_}"
        self.file = self.folder / self.file_name
        self.__incremental = incremental
        self.__indented = indented

    @property
    def exists(self):  # 是否存在
        return self.file.exists()
    
    @property
    def lines(self):  # 统计行数
        lines = 0
        with open(self.file, "r", encoding="utf-8", **self.__args) as file:
            for _ in file:
                lines += 1
        return lines

    def load(self):  # 加载文件
        with open(self.file, "r", encoding="utf-8", **self.__args) as file:
            return load(file)

    def save(self, data):  # 保存文件
        if self.__incremental:  # 对全量和增量分别处理
            with open(self.file, "a", encoding="utf-8", **self.__args) as file:
                for item in data:
                    file.write(dumps(item, ensure_ascii=False) + "\n")
        else:
            with open(self.file, "w+", encoding="utf-8", **self.__args) as file:
                dump(data, file, ensure_ascii=False, indent=4 if self.__indented else None)

    def read(self):  # 读取文件
        with open(self.file, "r", encoding="utf-8", **self.__args) as file:
            return file.read()

    def write(self, data):  # 写入文件
        with open(self.file, "w+", encoding="utf-8", **self.__args) as file:
            file.write(data)