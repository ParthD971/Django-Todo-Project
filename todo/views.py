from django.shortcuts import render
from django.views import View
from django.http import JsonResponse

from .forms import CreateUpdateTodoForm, CreateUpdateTaskForm, CreateSubTaskUsingIdsForm, CreateSubTaskUsingDataForm
from .models import Todo, Task

from accounts.mixin import LoginRequiredForApiMixin
from .utils import get_dic, check_and_get_todo


def home(request):
    return render(request, template_name='todo/home.html')


class CreateTodoAPI(LoginRequiredForApiMixin, View):
    def get(self, request):
        """
        Lists all Todo with necessary data.
        :param request:
        :return:
        """
        data = Todo.queryset_to_list_of_dict(queryset=Todo.objects.filter(owner=request.user))
        return JsonResponse(data, safe=False)

    def post(self, request):
        """
        Creates Todo.
        :param request: request with logged-in user, POST data [title]
        :return: if POST data is correct then instance data or else form errors
        """
        form = CreateUpdateTodoForm(get_dic(data=request.POST, owner=request.user))
        if form.is_valid():
            todo = form.save()
            return JsonResponse(todo.to_dict())
        return JsonResponse(form.errors)


class UpdateDeleteTodoAPI(LoginRequiredForApiMixin, View):
    def get(self, request, **kwargs):
        """
        Deleting Todo.
        :param request:
        :param kwargs: 'id' for Todo
        :return: success message
        """
        Todo.delete_todo(todo_id=kwargs['id'])
        return JsonResponse({'message': 'Todo deleted successfully.'})

    def post(self, request, **kwargs):
        """
        Updates Todo.
        :param request: request with logged-in user, POST data [title]
        :param kwargs: 'id' for Todo
        :return: if POST data is correct then instance data or else form errors
        """
        form = CreateUpdateTodoForm(
            get_dic(data=request.POST, owner=request.user),
            instance_id=int(kwargs['id'])
        )
        if form.is_valid():
            todo = form.save()
            return JsonResponse(todo.to_dict())
        return JsonResponse(form.errors)


class CreateTaskAPI(LoginRequiredForApiMixin, View):
    def post(self, request):
        """
        Creating Task.
        :param request: 'todo-id' in GET params. POST data
        [title, details, is_completed, completion_date, todo]
        :return: if POST data is correct then instance data or else form errors
        """
        todo, is_todo_id_valid = check_and_get_todo(todo_id=request.GET.get('todo-id', None))
        if not is_todo_id_valid:
            return JsonResponse({'error': 'todo-id in get parameters is missing.'})

        form = CreateUpdateTaskForm(get_dic(data=request.POST, todo=todo))
        if form.is_valid():
            task = form.save()
            return JsonResponse(task.to_dict())
        return JsonResponse(form.errors)


class UpdateDeleteTaskAPI(LoginRequiredForApiMixin, View):
    def get(self, request, **kwargs):
        """
        Deleting Task.
        :param request: request with logged-in user
        :param kwargs: 'id' for Task
        :return: success message
        """
        Task.delete_task(task_id=int(kwargs['id']))
        return JsonResponse({'message': 'Task deleted successfully.'})

    def post(self, request, **kwargs):
        """
        Updating Task.
        1. user can update: title, details, is_completed, and completion_date
        2. user can change from sub-task to main-task
        3. user can change todo of task, it will change todo for all its sub-tasks too.

        :param request: request with logged-in user, and POST data
        [title, details, is_completed, completion_date, todo]
        :param kwargs: 'id' in GET params. POST data
        :return: if POST data is correct then instance data or else form errors
        """
        data, task = Task.fill_data_from_instance(request.POST, instance_id=int(kwargs['id']))
        old_todo = task.todo
        form = CreateUpdateTaskForm(data, instance=task)
        if form.is_valid():
            task = form.save(todo=old_todo, is_subtask=request.POST.get('is_subtask', None))
            return JsonResponse(task.to_dict())
        return JsonResponse(form.errors)


class CreateSubTaskUsingIdsAPI(LoginRequiredForApiMixin, View):
    def post(self, request):
        """
        Creating sub-task using id's of two main-tasks.
        :param request: request with logged-in user, POST data [task, sub_task]
        :return: if POST data is correct then instance data or else form errors
        """
        form = CreateSubTaskUsingIdsForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'Created sub-task successfully.'})
        return JsonResponse(form.errors)


class CreateSubTaskUsingDataAPI(LoginRequiredForApiMixin, View):
    def post(self, request):
        """
        Creating sub-task using id of main-task and data for sub-task.
        :param request: request with logged-in user, POST data
        [title, details, is_completed, completion_date, task, todo]
        :return:
        """
        todo, is_todo_id_valid = check_and_get_todo(todo_id=request.GET.get('todo-id', None))
        if not is_todo_id_valid:
            return JsonResponse({'error': 'todo-id in get parameters is missing.'})

        form = CreateSubTaskUsingDataForm(get_dic(data=request.POST, todo=todo))
        if form.is_valid():
            sub_task_obj = form.save()
            return JsonResponse(sub_task_obj.sub_task.to_dict())
        return JsonResponse(form.errors)
