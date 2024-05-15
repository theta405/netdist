from threading import Lock
from collections import defaultdict


class ThreadLock:  # 线程锁基类
    def __init__(self):
        self.__lock = Lock()  # 未指定类型则返回自身的锁
        self.__locks = defaultdict(Lock)  # 指定类型后返回该类型的锁

    # 代码块用这个锁套
    def acquire_lock(self, type_=None):  # 需要锁的地方用 with 套上就完事
        if type_:
            return self.__locks[type_]
        else:
            return self.__lock

    # 函数用这个锁套
    def deco_lock(self, *args, **kwargs):  # 参数可选的装饰器
        # 在读了之后，还有可能会写的函数外加上就完事了
        lock = self.__lock
        def outer(func):
            nonlocal args, lock
            lock = self.__locks[args[0]]
            args = (func,)
            return inner
        def inner(*inner_args, **inner_kwargs):
            with lock:
                return args[0](*inner_args, **inner_kwargs)
        return inner if callable(args[0]) else outer