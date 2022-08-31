from django.shortcuts import render

# Create your views here.
from django.views import View
from django.http import HttpResponse
from todo_in_drf.views import CreateTodoAPI


class Debug(View):
    def get(self, request):
        # url = 'http://127.0.0.1:8000/api/todo/'
        # data = {
        #
        # }
        # headers = {
        #
        # }
        # response = requests.get(url=url, data=data, headers=headers)
        # response.raise_for_status()
        # result = response.content

        result = CreateTodoAPI().get(request=request)
        return HttpResponse(f'Done {result}')
