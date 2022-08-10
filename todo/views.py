from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import JsonResponse

from .forms import CreateUpdateTodoForm, CreateUpdateTaskForm, CreateSubTaskUsingIdsForm, CreateSubTaskUsingDataForm
from .models import Todo, Task

from accounts.mixin import AnonymousUserRequired, LoginRequiredForApiMixin


def home(request):
    return render(request, template_name='todo/home.html')


class CreateTodoAPI(LoginRequiredForApiMixin, View):
    def post(self, request):
        data = request.POST.copy()
        data['owner'] = request.user
        form = CreateUpdateTodoForm(data)
        if form.is_valid():
            todo = form.save()
            return JsonResponse(todo.to_dict())
        return JsonResponse(form.errors)


class UpdateDeleteTodoAPI(LoginRequiredForApiMixin, View):
    def get(self, request, *args, **kwargs):
        todo = get_object_or_404(Todo, id=int(kwargs['id']))
        todo.delete()
        return JsonResponse({'message': 'Todo deleted successfully.'})

    def post(self, request, *args, **kwargs):
        todo = get_object_or_404(Todo, id=int(kwargs['id']))
        data = request.POST.copy()
        data['owner'] = request.user
        form = CreateUpdateTodoForm(data, instance=todo)
        if form.is_valid():
            todo = form.save()
            return JsonResponse(todo.to_dict())
        return JsonResponse(form.errors)


class CreateTaskAPI(LoginRequiredForApiMixin, View):
    def post(self, request):
        todo_id = request.GET.get('todo-id', None)
        if not todo_id or todo_id.strip() == '':
            return JsonResponse({'error': 'todo-id in get parameters is missing.'})

        todo = get_object_or_404(Todo, id=todo_id)

        data = request.POST.copy()
        data['todo'] = todo
        form = CreateUpdateTaskForm(data)
        if form.is_valid():
            task = form.save()
            return JsonResponse(task.to_dict())
        return JsonResponse(form.errors)


class UpdateDeleteTaskAPI(LoginRequiredForApiMixin, View):
    def get(self, request, *args, **kwargs):
        task = get_object_or_404(Task, id=int(kwargs['id']))
        task.delete()
        return JsonResponse({'message': 'Task deleted successfully.'})

    def post(self, request, *args, **kwargs):
        task = get_object_or_404(Task, id=int(kwargs['id']))
        todo = task.todo

        data = Task.fill_data_from_instance(request.POST, instance=task)
        form = CreateUpdateTaskForm(data, instance=task)
        if form.is_valid():
            task = form.save(todo=todo, is_subtask=request.POST.get('is_subtask', None))
            return JsonResponse(task.to_dict())
        return JsonResponse(form.errors)


class CreateSubClassUsingIdsAPI(LoginRequiredForApiMixin, View):
    def post(self, request):
        form = CreateSubTaskUsingIdsForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'Created successfully'})
        return JsonResponse(form.errors)


class CreateSubClassUsingDataAPI(LoginRequiredForApiMixin, View):
    def post(self, request):
        todo_id = request.GET.get('todo-id', None)
        if not todo_id or todo_id.strip() == '':
            return JsonResponse({'error': 'todo-id in get parameters is missing.'})

        todo = get_object_or_404(Todo, id=todo_id)

        data = request.POST.copy()
        data['todo'] = todo

        form = CreateSubTaskUsingDataForm(data)
        if form.is_valid():
            sub_task_obj = form.save()
            return JsonResponse(sub_task_obj.sub_task.to_dict())
        return JsonResponse(form.errors)

