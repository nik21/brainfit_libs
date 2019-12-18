from django.conf import settings
from vanilla import ListView
from brainfit_libs.utils import CustomPaginator


class CustomListView(ListView):
    """
    Расширяет vanilia.ListView тем, что поддерживает специальный пагинатор и лимитер
    В настройках укажите что-то вроде:
    CUSTOM_LIST_VIEW_LIMITS = (10, 25, 50, 100)
    """
    paginate_by = settings.CUSTOM_LIST_VIEW_LIMITS[0]

    def get(self, request, *args, **kwargs):
        # Элементов на страницу
        limit = int(self.request.GET.get('limit', 0))
        if limit == 0:
            limit = int(request.session.get('limit', 0))
        if limit in settings.CUSTOM_LIST_VIEW_LIMITS:
            self.paginate_by = limit
        request.session['limit'] = self.paginate_by
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paginate_by'] = self.paginate_by
        return context

    def get_paginator(self, queryset, page_size):
        return CustomPaginator(queryset, page_size)
