from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import JsonResponse

from .forms import CreateUpdateTodoForm, CreateUpdateTaskForm
from .models import Todo, Task, SubTask


def home(request):
    return render(request, template_name='todo/home.html')


class ListCreateTodoAPI(View):
    def get(self, request):
        data = Todo.queryset_to_list_of_dict(queryset=Todo.objects.order_by('id').prefetch_related('tasks').all())
        return JsonResponse(data, safe=False)

    def post(self, request):
        form = CreateUpdateTodoForm(request.POST)
        if form.is_valid():
            todo = form.save()
            return JsonResponse(todo.to_dict())
        return JsonResponse(form.errors)


class UpdateDeleteTodoAPI(View):
    def get(self, request, *args, **kwargs):
        todo = get_object_or_404(Todo, id=int(kwargs['id']))
        todo.delete()
        return JsonResponse({'message': 'Todo deleted successfully.'})

    def post(self, request, *args, **kwargs):
        todo = get_object_or_404(Todo, id=int(kwargs['id']))
        form = CreateUpdateTodoForm(request.POST, instance=todo)
        if form.is_valid():
            todo = form.save()
            return JsonResponse(todo.to_dict())
        return JsonResponse(form.errors)


class ListCreateTaskAPI(View):
    def get(self, request):
        data = Task.queryset_to_list_of_dict(queryset=Task.objects.order_by('id').all())
        return JsonResponse(data, safe=False)

    def post(self, request):
        todo_id = request.GET.get('todo-id', None)
        if not todo_id or todo_id.strip() == '':
            return JsonResponse({'error': 'todo-id in get parameters is missing.'})

        todo = get_object_or_404(Todo, id=todo_id)
        form = CreateUpdateTaskForm(request.POST)
        if form.is_valid():
            task = form.save(todo=todo)
            return JsonResponse(task.to_dict())
        return JsonResponse(form.errors)


class UpdateDeleteTaskAPI(View):
    def get(self, request, *args, **kwargs):
        task = get_object_or_404(Task, id=int(kwargs['id']))
        task.delete()
        return JsonResponse({'message': 'Task deleted successfully.'})

    def post(self, request, *args, **kwargs):
        task = get_object_or_404(Task, id=int(kwargs['id']))

        todo_id = request.POST.get('todo', None)
        if todo_id:
            todo = get_object_or_404(Todo, id=todo_id)
        else:
            todo = task.todo

        form = CreateUpdateTaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(todo=todo)
            return JsonResponse(task.to_dict())
        return JsonResponse(form.errors)
