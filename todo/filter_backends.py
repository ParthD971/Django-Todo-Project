class CurrentUserForTodoFilterBackend:
    def filter_queryset(self, request, queryset, view_class):
        return queryset.filter(owner=request.user)


class CurrentUserForTaskFilterBackend:
    def filter_queryset(self, request, queryset, view_class):
        return queryset.filter(todo__owner=request.user)
