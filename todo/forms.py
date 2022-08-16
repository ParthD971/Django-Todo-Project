from django import forms
from django.shortcuts import get_object_or_404

from .models import Todo, Task, SubTask


class CreateUpdateTodoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        """
        For Updating todo
        :param kwargs: instance_id
        """
        todo_id = kwargs.pop('instance_id', None)
        if todo_id:
            todo = get_object_or_404(Todo, id=todo_id)
            kwargs['instance'] = todo
        super(CreateUpdateTodoForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Todo
        fields = '__all__'


class CreateUpdateTaskForm(forms.ModelForm):
    details = forms.CharField(required=False)
    completion_date = forms.DateField(
        required=False,
        input_formats=['%d-%m-%Y'],
        error_messages={'invalid': 'Date is invalid or does not match format DD-MM-YYYY'}
    )

    def save(self, **kwargs):
        todo = kwargs.pop('todo', None)
        # check is is_subtask parameter is False or not
        is_subtask = str(kwargs.pop('is_subtask', None)) != 'False'

        # while updating, if task is subtask and changed to main task
        # or todo of task(is_subtask=True) is changed
        if self.instance.id is not None and \
                (self.instance.is_subtask and not is_subtask) or \
                (self.instance.todo != todo and self.instance.is_subtask):
            self.instance.is_subtask = False
            self.instance.parent_task.delete()

        obj = super(CreateUpdateTaskForm, self).save(**kwargs)

        # while updating, if task is subtask and changed to main task then 0 times loop
        # and when task is main task and its todo is changed then todos of all its sub-task is changed if any.
        if self.instance.id is not None:
            for sub_task_obj in self.instance.sub_tasks.all():
                sub_task = sub_task_obj.sub_task
                sub_task.todo = obj.todo
                sub_task.save()
        return obj

    class Meta:
        model = Task
        fields = ('content', 'details', 'is_completed', 'completion_date', 'todo')


class CreateSubTaskUsingIdsForm(forms.Form):
    task = forms.IntegerField()
    sub_task = forms.IntegerField()

    def clean_task(self):
        task_id = self.data['task']
        task = None

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            self.add_error('task', 'This task id is not valid.')

        if task and task.is_subtask:
            self.add_error('task', 'This task already sub-task.')

        return task_id

    def clean_sub_task(self):
        sub_task_id = self.data['sub_task']
        task_id = self.data['task']
        task, sub_task = None, None

        try:
            sub_task = Task.objects.get(id=sub_task_id)
        except Task.DoesNotExist:
            self.add_error('sub_task', 'This sub-task id is not valid.')

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            pass

        if sub_task and sub_task.sub_tasks and sub_task.sub_tasks.count() > 0:
            self.add_error('sub_task', 'The sub-task is parent task, so cannot become sub-task.')
        try:
            if sub_task and sub_task.parent_task and sub_task.parent_task.task == task:
                self.add_error('sub_task', 'The sub-task is already sub-task of the task.')
            elif sub_task and sub_task.is_subtask:
                self.add_error('sub_task', 'This sub-task is already sub-task of another task.')
        except Task.parent_task.RelatedObjectDoesNotExist:
            if sub_task and sub_task.is_subtask:
                self.add_error('sub_task', 'This sub-task is already sub-task of another task.')

        if sub_task and sub_task.todo != task.todo:
            self.add_error('sub_task', 'The todo of task and sub-task is not matching.')

        if task and sub_task and task == sub_task:
            self.add_error('sub_task', 'The task and sub-task cannot be same.')

        return sub_task_id

    def save(self):
        if self.errors:
            raise ValueError(
                "The SubTask could not be created because the data didn't validate."
            )

        sub_task_id = self.data['sub_task']
        task = self.data['task']

        sub_task_obj = Task.objects.get(id=sub_task_id)
        sub_task_obj.is_subtask = True
        sub_task_obj.save()

        return SubTask.objects.create(task_id=task, sub_task_id=sub_task_id)


class CreateSubTaskUsingDataForm(forms.ModelForm):
    task = forms.IntegerField(required=True)
    details = forms.CharField(required=False)
    completion_date = forms.DateField(
        required=False,
        input_formats=['%d-%m-%Y'],
        error_messages={'invalid': 'Date is invalid or does not match format DD-MM-YYYY'}
    )

    def clean_task(self):
        task_id = self.cleaned_data['task']
        todo = self.cleaned_data['todo']
        task = None
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            self.add_error('task', 'This task id is not valid.')

        if task and task.is_subtask:
            self.add_error('task', 'This task is sub task of another task so it is invalid.')

        if task and task.todo.id != todo.id:
            self.add_error('task', 'Todo for task and sub task does not match.')

        return task_id

    def save(self, **kwargs):
        task = self.cleaned_data.pop('task')

        self.instance.is_subtask = True
        sub_task = super(CreateSubTaskUsingDataForm, self).save()

        return SubTask.objects.create(task_id=task, sub_task=sub_task)

    class Meta:
        model = Task
        fields = ('content', 'details', 'is_completed', 'completion_date', 'todo', 'task')
