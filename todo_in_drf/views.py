from rest_framework import mixins
from rest_framework.generics import GenericAPIView, ListCreateAPIView, CreateAPIView

from todo.filter_backends import CurrentUserForTodoFilterBackend, CurrentUserForTaskFilterBackend
from todo.models import Todo, Task
from todo_in_drf.serializers import CreateUpdateTodoSerializer, CreateUpdateTaskSerializer, \
    CreateSubTaskUsingIdsSerializer, CreateSubTaskUsingDataSerializer


class CreateTodoAPI(ListCreateAPIView):
    """
    description: This View Creates Todo and Lists all Todos of current user.
    with proper format along with tasks.
    data: For creating todo
    {
        [required] title : string
    }
    response:
    List of todo with following attributes
    todo -> {
        id: integer [id of todo object],
        title: string,
        owner: email of owner in string,
        tasks: [
            {
                id: integer [id of main task of current todo],
                content: string,
                details: string,
                is_completed: boolean,
                is_subtask: boolean,
                completion_date: string [yyyy-mm-dd],
                todo: integer [current todo id],
                sub_tasks: [
                    {
                        id: integer [id of sub task of current main task],
                        content: string,
                        details: string,
                        is_completed: boolean,
                        is_subtask: boolean,
                        completion_date: string [yyyy-mm-dd],
                        todo: integer [current todo id]
                    }
                ]
            }
        ]
    }
    permission: IsAuthenticated
    """
    serializer_class = CreateUpdateTodoSerializer
    queryset = Todo.objects.all()
    filter_backends = [CurrentUserForTodoFilterBackend]


class UpdateDeleteTodoAPI(GenericAPIView, mixins.DestroyModelMixin, mixins.UpdateModelMixin):
    """
    description: This View Deletes Todo and Update Todo of current user.
    request: requires 'id' parameter, where id is id of todo object.
    data: For updating todo
    {
        [required] title : string
    }
    response:
    updated todo -> {
        id: integer [id of todo object],
        title: string,
        owner: email of owner in string,
        tasks: [
            {
                id: integer [id of main task of current todo],
                content: string,
                details: string,
                is_completed: boolean,
                is_subtask: boolean,
                completion_date: string [yyyy-mm-dd],
                todo: integer [current todo id],
                sub_tasks: [
                    {
                        id: integer [id of sub task of current main task],
                        content: string,
                        details: string,
                        is_completed: boolean,
                        is_subtask: boolean,
                        completion_date: string [yyyy-mm-dd],
                        todo: integer [current todo id]
                    }
                ]
            }
        ]
    }
    permission: IsAuthenticated
    """
    serializer_class = CreateUpdateTodoSerializer
    queryset = Todo.objects.all()
    filter_backends = [CurrentUserForTodoFilterBackend]
    lookup_field = 'id'

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def put(self, request, **kwargs):
        return self.update(request, **kwargs)


class CreateTaskAPI(CreateAPIView):
    """
    description: This View Creates Tasks.
    data: For creating task
    {
        [required] content : string
        [optional] details : string
        [optional] is_completed : boolean
        [optional] completion_date : string [dd-mm-yyyy]
        [required] todo : integer [id of todo created by current user]
    }
    response:
    created task -> {
        id: integer [id of task created],
        content: string,
        details: string,
        is_completed: boolean,
        completion_date: date[yyyy-mm-dd],
        todo: integer [current todo id],
        is_subtask: boolean
    }
    permission: IsAuthenticated
    """
    serializer_class = CreateUpdateTaskSerializer


class UpdateDeleteTaskAPI(GenericAPIView, mixins.DestroyModelMixin, mixins.UpdateModelMixin):
    """
    description: This View Deletes Task and Update Task of current user.
    request: requires 'id' parameter, where id is id of task object.
    data: For updating todo
    1. Normal Task attribute Update
    {
        [optional] content : string
        [optional] details : string
        [optional] is_completed : boolean
        [optional] completion_date : string [dd-mm-yyyy]
    }
    2. Make Stand-alone task from being subtask
    {
        [optional] is_subtask : boolean
    }
    3. Change todo of task/subtask
    {
        [optional] todo : integer [id of new todo]
    }
    response:
    updated task -> {
        id: integer [id of task updated],
        content: string,
        details: string,
        is_completed: boolean,
        completion_date: date[yyyy-mm-dd],
        todo: integer [current todo id],
        is_subtask: boolean
    }
    permission: IsAuthenticated
    """
    serializer_class = CreateUpdateTaskSerializer
    queryset = Task.objects.all()
    filter_backends = [CurrentUserForTaskFilterBackend]
    lookup_field = 'id'

    def get_serializer_context(self):
        """
        Update serializer context.
        1. is_subtask: If update query is to make standalone task from being sub_task, passing it
        to serializer context so that save() method has access to is_subtask attribute.
        2. is_updating:  If update query is performed so that validate() method can ignore content's
        required validation.
        :return: Updated context for serializer.
        """
        context = super(UpdateDeleteTaskAPI, self).get_serializer_context()
        context.update({'is_subtask': self.request.data.get('is_subtask')})
        context.update({'is_updating': self.request.method == 'PUT'})
        context.update({'user': self.request.user})
        return context

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class CreateSubTaskUsingIdsAPI(CreateAPIView):
    """
    description: This View makes any task (which is already created) to sub-task.
    data: For creating sub-task
    {
        [required] task : integer [id of task to become as main task]
        [required] sub_task : integer [id of task to become sub-task]
    }
    response:
    created task -> {
        task: integer [id of main-task],
        sub_task: integer [id of sub-task],
    }
    permission: IsAuthenticated
    """
    serializer_class = CreateSubTaskUsingIdsSerializer

    def get_serializer_context(self):
        """
        To make access of request's user object in serializer.
        :return: updated context of serializer with request object.
        """
        context = super(CreateSubTaskUsingIdsAPI, self).get_serializer_context()
        context.update({'request': self.request})
        return context


class CreateSubTaskUsingDataAPI(CreateAPIView):
    """
    description: This View creates subtask from task (which is already created).
    data: For creating sub-task
    data: For creating task
    {
        [required] content : string
        [optional] details : string
        [optional] is_completed : boolean
        [optional] completion_date : string [dd-mm-yyyy]
        [required] todo : integer [id of todo for corresponding task of current user]
        [required] task : integer [id of task(already been created) by current user]
    }
    response:
    created task -> {
        id: integer [id of subtask created],
        content: string,
        details: string,
        is_completed: boolean,
        completion_date: string [yyyy-mm-dd]
        todo: integer [id of current task's todo],
        is_subtask: boolean
    }
    permission: IsAuthenticated
    """
    serializer_class = CreateSubTaskUsingDataSerializer

    def get_serializer_context(self):
        """
        To make access of request's user object in serializer.
        :return: updated context of serializer with request object.
        """
        context = super(CreateSubTaskUsingDataAPI, self).get_serializer_context()
        context.update({'request': self.request})
        return context
