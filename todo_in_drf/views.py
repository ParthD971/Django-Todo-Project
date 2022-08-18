from rest_framework import mixins
from rest_framework.generics import GenericAPIView, ListCreateAPIView, CreateAPIView

from todo.filter_backends import CurrentUserForTodoFilterBackend, CurrentUserForTaskFilterBackend
from todo.models import Todo, Task
from todo_in_drf.serializers import CreateUpdateTodoSerializer, CreateUpdateTaskSerializer, \
    CreateSubTaskUsingIdsSerializer, CreateSubTaskUsingDataSerializer


class CreateTodoAPI(ListCreateAPIView):
    serializer_class = CreateUpdateTodoSerializer
    queryset = Todo.objects.all()
    filter_backends = [CurrentUserForTodoFilterBackend]


class UpdateDeleteTodoAPI(GenericAPIView, mixins.DestroyModelMixin, mixins.UpdateModelMixin):
    serializer_class = CreateUpdateTodoSerializer
    queryset = Todo.objects.all()
    filter_backends = [CurrentUserForTodoFilterBackend]
    lookup_field = 'id'

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def put(self, request, **kwargs):
        return self.update(request, **kwargs)


class CreateTaskAPI(CreateAPIView):
    serializer_class = CreateUpdateTaskSerializer


class UpdateDeleteTaskAPI(GenericAPIView, mixins.DestroyModelMixin, mixins.UpdateModelMixin):
    serializer_class = CreateUpdateTaskSerializer
    queryset = Task.objects.all()
    filter_backends = [CurrentUserForTaskFilterBackend]
    lookup_field = 'id'

    def get_serializer_context(self):
        context = super(UpdateDeleteTaskAPI, self).get_serializer_context()
        context.update({'is_subtask': self.request.data.get('is_subtask', None)})
        context.update({'is_updating': self.request.method == 'PUT'})
        return context

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class CreateSubTaskUsingIdsAPI(CreateAPIView):
    serializer_class = CreateSubTaskUsingIdsSerializer

    def get_serializer_context(self):
        context = super(CreateSubTaskUsingIdsAPI, self).get_serializer_context()
        context.update({'request': self.request})
        return context


class CreateSubTaskUsingDataAPI(CreateAPIView):
    serializer_class = CreateSubTaskUsingDataSerializer

    def get_serializer_context(self):
        context = super(CreateSubTaskUsingDataAPI, self).get_serializer_context()
        context.update({'request': self.request})
        return context
