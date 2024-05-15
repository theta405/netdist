class CustomDict(dict):  # 可用属性代替键来访问元素
    def __getattr__(self, __name):
        return self.get(__name)

    def __setattr__(self, __name, __value):
        self[__name] = __value

    def __setitem__(self, __key, __value):  # 转换新插入的值
        if isinstance(__value, dict) and not isinstance(__value, CustomDict):
            __value = CustomDict(__value)
        super().__setitem__(__key, __value)

    def __init__(self, data=None):
        if data is None:
            data = {}
        super().__init__(data)
        for val in self.keys():  # 遍历，转换所有 dict
            if isinstance(self[val], dict) and not isinstance(self[val], CustomDict):
                self[val] = CustomDict(self[val])