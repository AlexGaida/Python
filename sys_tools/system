import sys
import os
import threading


class Periodic(threading.Timer):
    """

    """
    def __init__(self, interval, callable, args=(), kwargs={}):
        self.callable = callable
        threading.Timer.__init__(self, interval, self._f, args, kwargs)

    def _f(self, *args, **kwargs):
        Periodic(self.interval, self.callable, args, kwargs).start()
        self.callable(*args, **kwargs)

