from pathlib import Path
from re import match

config_rootpath = Path("/tmp")


REMOTE_PATTERN = r'^[^:]+:'
SPECIAL_PATTERN = r"^(%[^%]+%)"

LOCAL = 0
REMOTE = 1
SPECIAL = 2


class Folder():
    def __init__(self, folder_path):
        self.folder = folder_path
        self.folder.mkdir(parents=True, exist_ok=True)  # 目录不存在则创建

    def glob(self, pattern):
        return self.folder.glob(pattern)


class File():
    def __init__(self, file_path, stream=True):
        self.__virtual_path = file_path
        self.__type = self.__pathtype(self.__virtual_path)
        self.__stream = stream

        if self.__type == LOCAL:
            from .configs import general
            self.__relative_path = self.__virtual_path
            self.__real_path = Path(general.workdir) / Path(self.__relative_path)
        elif self.__type == REMOTE:
            self.__node_id = None
            self.__relative_path = None
        elif self.__type == SPECIAL:
            self.__relative_path = Path(__file__).parent
            self.__real_path = None

    def __pathtype(self, virtual_path):
        if virtual_path[0] == "/":
            return LOCAL
        elif match(REMOTE_PATTERN, virtual_path):
            return REMOTE
        elif match(SPECIAL_PATTERN, virtual_path):
            return SPECIAL

    def virtual_to_real(self, virtual_path):
        pass

if __name__ == "__main__":
    test = File("/vdseaar1:/test/path")