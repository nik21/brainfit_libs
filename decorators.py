from django.conf import settings
from django.contrib.auth.decorators import user_passes_test


def group_required(*group_names):
    """
    Требовать у пользователя состоять в той или иной группе. Одновременно проверяет и то, что пользователь залогинен

    Можно использовать:
    - над классом: @method_decorator(group_required('Finance_manager'), name='dispatch')
    - над методом dispatch: @method_decorator(group_required('Finance_manager'))
    - отдельно: group_required('Finance_manager')

    :param group_names:
    :return:
    """
    def in_groups(u):
        if u.is_authenticated():
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        return False
    access_denied_url = settings.ACCESS_DENIED_URL or None
    return user_passes_test(in_groups, login_url=access_denied_url)
