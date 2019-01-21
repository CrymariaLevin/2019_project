
import datetime as DT

class RunTimer(object):
    """ 执行函数计时工具 """
    def __init__(self, logger=None):
        self._start_ts = DT.datetime.now()
        self._end_ts = DT.datetime.now()
        self._obj_name = "unknown"
        self.logger = logger

    def begin(self, obj_name, action="begin"):
        """
        开始执行计时
        :param obj_name: 对象名
        :param action: 执行动作
        """
        self._obj_name = obj_name
        self._start_ts = DT.datetime.now()
        log_msg = "[%s] %s %s()" % (self._start_ts, action, self._obj_name)
        if self.logger is None:
            print(log_msg)
        else:
            self.logger.info(log_msg)

    def end(self, obj_name=None, action="end"):
        """
        结束执行计时并报告
        :param obj_name: 对象名
        :param action: 执行动作
        """
        if obj_name is not None and len(obj_name.strip()) > 0:
            self._obj_name = obj_name
        self._end_ts = DT.datetime.now()
        _t_cost = self._end_ts - self._start_ts
        log_msg = "[%s] %s %s(): costs %s" % (self._end_ts, action, self._obj_name, _t_cost)
        if self.logger is None:
            print(log_msg)
        else:
            self.logger.info(log_msg)