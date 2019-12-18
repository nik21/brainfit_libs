from threading import Timer
import math

from django.core.paginator import Paginator


# http://stackoverflow.com/questions/2398661/schedule-a-repeating-event-in-python-3
class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.function = function
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


# Переделка стандартного Django-пагинатора так, чтобы тот выдавал страницы только кусками
class CustomPaginator(Paginator):
    _current_page = None
    _max_pages_buttons = 10

    def page(self, number):
        self._current_page = number
        return super().page(number)

    def has_show_first_page(self):
        return self._left_range > 1

    def has_show_last_page(self):
        return self._right_range < self.num_pages

    def _get_page_range(self):
        left = self._left_range
        if self.has_show_first_page():
            left += 1

        right = self._right_range
        if self.has_show_last_page():
            right -= 1
        return list(range(left, right + 1))

    @property
    def _left_right_gap(self):
        return math.floor((self._max_pages_buttons - 1) / 2)

    @property
    def _left_range(self):
        return max(self._current_page - self._left_right_gap, 1)

    @property
    def _right_range(self):
        return min(self._current_page + self._left_right_gap, self.num_pages)

    page_range = property(_get_page_range)




