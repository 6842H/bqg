# coding: utf-8 
# @Time : 2019/6/29 下午 04:37 
# @Author : gyn 
# @email : guogyn@foxmail.com 


from threading import Event, Thread
from time import sleep
from traceback import format_exc


# 线程单元，传入线程要执行的方法和方法需要的参数
class MThread(Thread):

    def __init__(self, tid, func=None, *args):
        super().__init__()
        self.tid = tid            # 线程 id or name
        self.__flag = Event()     # 用于暂停线程的标识
        self.__running = Event()  # 用于停止线程的标识
        self.__flag.set()         # 设置为True, 不暂停
        self.__running.set()      # 将running设置为True，不停止

        self.func = func          # 要执行的方法
        self.args = args          # func的参数

    def pause_on(self, pause_time):    # 暂停
        self.__flag.clear()  # 设置为False, 让线程阻塞
        sleep(pause_time)   # pause_time 秒后恢复
        self.resume()

    def pause(self):    # 暂停
        self.__flag.clear()  # 设置为False, 让线程阻塞

    def resume(self):   # 恢复
        self.__flag.set()  # 设置为True, 让线程停止阻塞
        print("线程【%s】苏醒，继续工作" % self.tid)

    def stop(self):     # 停止
        self.__flag.set()  # 将线程从暂停状态恢复, 如果已经暂停的话
        self.__running.clear()  # 设置为False

    def run(self):
        print(self.tid, '启动')
        # while True:
        while self.__running.is_set():   # 判断是否可运行
            self.__flag.wait()  # 再判断是否处于暂停状态，为True时立即返回, 为False时则一直阻塞到内部的标识位为True后继续
            try:
                # op
                if self.func:
                    self.func(*self.args)
                pass
            except Exception as e:
                print(format_exc(), e)


def pp(a):
    print(a)


def test():
    a = MThread('pp', pp, 'hellow')
    a.start()
    a.pause_on(3)   # 暂停3秒3秒后恢复
    sleep(5)
    a.stop()    # 5秒后停止
# test()