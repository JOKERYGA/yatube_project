# Импортирую CreateView, чтобы создать ему наследника
from django.views.generic import CreateView
# Функция reverse_lazy позволяет получить URL по параметрам функции path()
from django.urls import reverse_lazy
from .forms import CreationForm


# Create your views here.
class SignUp(CreateView):
    # из какого класса взять форму
    # C какой формой будет работать этот view-класс
    form_class = CreationForm
    # После успешной регистрации перенаправляю пользователя на главную.
    success_url = reverse_lazy('posts:index')
    # Какой шаблон применить для отображения веб-формы
    template_name = 'users/signup.html'