from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from accounts.models import User
from todo.models import Todo, Task, SubTask


class CreateUpdateTodoSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(
        read_only=False,
        many=False,
        slug_field='email',
        queryset=User.objects.all()
    )

    def __init__(self, *args, **kwargs):
        """
        For Updating todo
        :param kwargs: instance_id
        """
        todo_id = kwargs.pop('instance_id', None)
        if todo_id:
            todo = get_object_or_404(Todo, id=todo_id)
            kwargs['instance'] = todo
        super(CreateUpdateTodoSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Todo
        fields = '__all__'


class CreateUpdateTaskSerializer(serializers.ModelSerializer):
    details = serializers.CharField(required=False, allow_null=True)
    completion_date = serializers.DateField(
        allow_null=True,
        required=False,
        input_formats=['%d-%m-%Y'],
        error_messages={'invalid': 'Date is invalid or does not match format DD-MM-YYYY'}
    )

    def save(self, **kwargs):
        todo = kwargs.pop('todo', None)
        # check if is_subtask parameter is False or not
        is_subtask = str(kwargs.pop('is_subtask', None)) != 'False'

        # If task updated is main task and its is_complete status is changed to true
        main_task_is_completed_status = False
        if self.instance is not None and \
                not self.instance.is_subtask and \
                not self.instance.is_completed and \
                self.validated_data['is_completed']:
            main_task_is_completed_status = True

        # while updating, if task is subtask and changed to main task
        # or todo of task(is_subtask=True) is changed
        if self.instance is not None:
            if (self.instance.is_subtask and not is_subtask) or \
                    (self.instance.todo != todo and self.instance.is_subtask):
                self.instance.is_subtask = False
                self.instance.parent_task.delete()

        obj = super(CreateUpdateTaskSerializer, self).save(**kwargs)

        # while updating, if task is subtask and changed to main task then 0 times loop
        # and when task is main task and its todo is changed then todos of all its sub-task is changed if any.
        if self.instance is not None:
            for sub_task_obj in self.instance.sub_tasks.all():
                sub_task = sub_task_obj.sub_task
                sub_task.todo = obj.todo
                if main_task_is_completed_status:
                    sub_task.is_completed = True
                sub_task.save()
        return obj

    class Meta:
        model = Task
        fields = ('id', 'content', 'details', 'is_completed', 'completion_date', 'todo')
        optional_fields = ['details', 'completion_date', ]


class CreateSubTaskUsingIdsSerializer(serializers.Serializer):
    task = serializers.IntegerField()
    sub_task = serializers.IntegerField()

    def validate_task(self, task_id):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise serializers.ValidationError('task', 'This task id is not valid.')

        if task and task.is_subtask:
            raise serializers.ValidationError('task', 'This task already sub-task.')

        return task_id

    def validate_sub_task(self, sub_task_id):
        task_id = self.initial_data['task']
        task, sub_task = None, None

        try:
            sub_task = Task.objects.get(id=sub_task_id)
        except Task.DoesNotExist:
            raise serializers.ValidationError('sub_task', 'This sub-task id is not valid.')

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            pass

        if sub_task and sub_task.sub_tasks and sub_task.sub_tasks.count() > 0:
            raise serializers.ValidationError('sub_task', 'The sub-task is parent task, so cannot become sub-task.')
        try:
            if sub_task and sub_task.parent_task and sub_task.parent_task.task == task:
                raise serializers.ValidationError('sub_task', 'The sub-task is already sub-task of the task.')
            elif sub_task and sub_task.is_subtask:
                raise serializers.ValidationError('sub_task', 'This sub-task is already sub-task of another task.')
        except Task.parent_task.RelatedObjectDoesNotExist:
            if sub_task and sub_task.is_subtask:
                raise serializers.ValidationError('sub_task', 'This sub-task is already sub-task of another task.')

        if sub_task and sub_task.todo != task.todo:
            raise serializers.ValidationError('sub_task', 'The todo of task and sub-task is not matching.')

        if task and sub_task and task == sub_task:
            raise serializers.ValidationError('sub_task', 'The task and sub-task cannot be same.')

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


class CreateSubTaskUsingDataSerializer(serializers.ModelSerializer):
    task = serializers.IntegerField(required=True)
    details = serializers.CharField(required=False, allow_null=True)
    completion_date = serializers.DateField(
        required=False,
        allow_null=True,
        input_formats=['%d-%m-%Y'],
        error_messages={'invalid': 'Date is invalid or does not match format DD-MM-YYYY'}
    )

    def validate_task(self, task_id):
        todo = Todo.objects.get(id=int(self.initial_data['todo']))
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise serializers.ValidationError('task', 'This task id is not valid.')

        if task and task.is_subtask:
            raise serializers.ValidationError('task', 'This task is sub task of another task so it is invalid.')

        if task and task.todo.id != todo.id:
            raise serializers.ValidationError('task', 'Todo for task and sub task does not match.')

        return task_id

    def save(self, **kwargs):
        task = self.validated_data.pop('task')
        sub_task = super(CreateSubTaskUsingDataSerializer, self).save(is_subtask=True)
        return SubTask.objects.create(task_id=task, sub_task=sub_task)

    class Meta:
        model = Task
        fields = ('id', 'content', 'details', 'is_completed', 'completion_date', 'todo', 'task')
