from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from todo.models import Todo, Task
from todo.utils import get_dic, check_and_get_todo
from todo_in_drf.serializers import CreateUpdateTodoSerializer, CreateUpdateTaskSerializer, \
    CreateSubTaskUsingIdsSerializer, CreateSubTaskUsingDataSerializer


class CreateTodoAPI(APIView):
    def get(self, request):
        data = Todo.queryset_to_list_of_dict(queryset=Todo.objects.filter(owner=request.user))
        return Response(data)

    def post(self, request):
        serializer = CreateUpdateTodoSerializer(data=get_dic(data=request.POST, owner=request.user))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateDeleteTodoAPI(APIView):
    def delete(self, request, **kwargs):
        Todo.delete_todo(todo_id=kwargs['id'])
        message = {'message': 'Todo deleted successfully.'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, **kwargs):
        serializer = CreateUpdateTodoSerializer(
            data=get_dic(data=request.POST, owner=request.user),
            instance_id=int(kwargs['id'])
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateTaskAPI(APIView):
    def post(self, request):
        serializer = CreateUpdateTaskSerializer(data=get_dic(data=request.POST, todo=request.GET.get('todo-id', None)))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateDeleteTaskAPI(APIView):
    def delete(self, request, **kwargs):
        Task.delete_task(task_id=int(kwargs['id']))
        message = {'message': 'Task deleted successfully.'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, **kwargs):
        data, task = Task.fill_data_from_instance(request.POST, instance_id=int(kwargs['id']))
        old_todo = task.todo

        # data is having todo instance which is used in 'todo' app, but here it must be 'id'
        data['todo'] = data['todo'].id
        serializer = CreateUpdateTaskSerializer(data=data, instance=task)
        if serializer.is_valid():
            serializer.save(todo=old_todo, is_subtask=request.POST.get('is_subtask', None))
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateSubTaskUsingIdsAPI(APIView):
    def post(self, request):
        serializer = CreateSubTaskUsingIdsSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            message = {'message': 'Created sub-task successfully.'}
            return Response(message, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateSubTaskUsingDataAPI(APIView):
    def post(self, request):
        todo, is_todo_id_valid = check_and_get_todo(todo_id=request.GET.get('todo-id', None))
        if not is_todo_id_valid:
            return Response({'error': 'todo-id in get parameters is missing.'})

        serializer = CreateSubTaskUsingDataSerializer(data=get_dic(data=request.POST, todo=todo.id))
        if serializer.is_valid():
            instance = serializer.save()
            return Response(instance.sub_task.to_dict(), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
