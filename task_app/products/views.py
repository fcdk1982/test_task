from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Max, Avg, Sum, Count, F
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, ListView

from .forms import LoginForm, ProductCreateForm
from .models import Product


class UserLoginView(LoginView):
    form_class = LoginForm
    template_name = 'LoginPage.html'


class ProductCreateView(LoginRequiredMixin, CreateView):
    """
    A view for render product's form, validate date  and them save to DB.
    """
    model = Product
    form_class = ProductCreateForm
    template_name = 'ProductCreatePage.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.create_by = self.request.user
        self.object.save()
        return super(ProductCreateView, self).form_valid(form)

    def get_success_url(self) -> str:
        """Return the URL to redirect to user's stats page after processing a valid form."""
        user_id = self.request.user.id
        return reverse('products:stats_url', kwargs={'pk': user_id})


class StatsView(LoginRequiredMixin, ListView):
    """
    A view for displaying stats info for CoreUser.

    Общее количество товаров, которые ввел пользователь
    Максимальную цену, которую ввел пользователь
    Сумму цены всех товаров, которые ввел пользователь

    Общее количество товаров, которое было введено в системе
    Среднюю цену всех продуктов всех пользователей

    Сумму всех товаров, которые ввел пользователь И длина
    имени которых составляет больше 3 знаков ИЛИ цена которых больше 50,
    независимо от того, кто их создал

    """
    model = Product
    template_name = 'StatsPage.html'
    queryset = Product.objects.all()
    name_length = 3  # довжина назви товару для фільтрації
    price_size = 50  # вартість товару для фільтрації

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        if self.queryset.exists():
            context['total_data'] = self.get_total_data()
            context['sum'] = self.data_with_conditions()
        if self.queryset.filter(create_by=self.request.user).exists():
            context['user_data'] = self.get_user_data()
        return context

    def get_user_data(self) -> dict:
        """
        get  user's stats  info from DB
        """
        user_data = self.queryset.filter(
            create_by=self.request.user
        ).aggregate(
            max_price=Max('price'),
            sum_price=Sum('price'),
            products=Count('id'), )
        return user_data

    def get_total_data(self) -> dict:
        """
        get  all  stats  info from DB
        """
        all_users_data = self.queryset.aggregate(
            products=Count('id'),
            avg_price=Avg('price'))
        return all_users_data

    def data_with_conditions(self) -> int:
        """
        get  data with conditions if exist else 0
        """
        if self.queryset.filter(create_by=self.request.user, name__length__gt=self.name_length).exists():
            data = self.queryset.filter(
                create_by=self.request.user, name__length__gt=self.name_length).aggregate(
                total=Sum('price'))
            return data['total']
        elif self.queryset.filter(price__gt=self.price_size).exists():
            data = self.queryset.filter(price__gt=self.price_size).aggregate(total=Sum('price'))
            return data['total']
        else:
            return 0


class IncreaseView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs) -> HttpResponseRedirect:
        """
        increase all user's product price (if exist)
        """
        user = self.request.user
        qs = Product.objects.filter(create_by=user)
        if qs.exists():
            qs.update(price=F('price') + 1)
        return HttpResponseRedirect(reverse('products:stats_url', kwargs={'pk': user.pk}))
