from utils.custom_dict import CustomDict
from utils.thread_lock import ThreadLock


class Config(CustomDict, ThreadLock):  # 模块配置
    def __init__(self, config_name, **conf):
        ThreadLock.__init__(self)  # 调用 ThreadLock 的初始化方法，注意 self 不能去掉
        self.__mandatory_keys = conf.keys()  # 判断配置项是否一致
        self.__config_name = config_name
        self.__file = File("configs", self.__config_name)

        if self.__file.exists:  # 如果已有配置，则读取
            self.read()
        else:  # 否则初始化
            super().__init__(conf)
            self.save()

    def __setattr__(self, __name, __value):  # 更改配置时自动保存
        # ⚠ 注意配置中的 list 等可变元素发生变化时并不会触发此事件
        # 建议做类似操作时手动保存
        super().__setattr__(__name, __value)
        if not __name.startswith("_"):
            self.save()

    def read(self):  # 读取配置并初始化
        lack = []
        config = self.__file.load()
        for key in self.__mandatory_keys:
            if key not in config.keys():
                lack.append(key)
        if lack:
            raise Exception(f"配置文件 {self.__config_name} 缺失配置项 [{', '.join(lack)}]，无法读取")
        else:
            super().__init__(config)

    def save(self):  # 保存配置
        save_data = {k: v for k, v in self.items() if not k.startswith("_")}
        self.__file.save(save_data)