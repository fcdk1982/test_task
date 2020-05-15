from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import Max, Sum, Count, F, Avg
from django.test import TestCase
from django.urls import reverse

from products.models import Product


class ProductCreateViewTest(TestCase):
    """
    class for test ProductCreateView
    """

    def setUp(self):
        # create User
        self.test_user1 = User.objects.create_user(username='user1', password='12345')

    def test_view_url_exists(self):
        login = self.client.login(username='user1', password='12345')
        resp = self.client.get(reverse('products:create_url'))

        # check URL exist
        self.assertEqual(resp.status_code, 200)

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('products:create_url'))

        # ckeck redirect URL
        self.assertRedirects(resp, '/?next=/create/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='user1', password='12345')
        resp = self.client.get(reverse('products:create_url'))

        # check is user logged
        self.assertEqual(str(resp.context['user']), 'user1')
        # check resp status
        self.assertEqual(resp.status_code, 200)

        # check template
        self.assertTemplateUsed(resp, 'ProductCreatePage.html')

    def test_form_is_valid(self):
        login = self.client.login(username='user1', password='12345')

        # form data
        data = {
            'name': 'product11',
            'price': 1,
        }
        resp = self.client.post('/create/', data=data)

        # check product was created by request user
        self.assertEqual(Product.objects.last().create_by, self.test_user1)

    def test_get_success_url(self):
        login = self.client.login(username='user1', password='12345')
        # form data
        data = {
            'name': 'product1',
            'price': 1,
        }
        resp = self.client.post('/create/', data=data)

        # check resp status
        self.assertEqual(resp.status_code, 302)

        # check resp URL
        self.assertRedirects(resp, reverse('products:stats_url', kwargs={'pk': self.test_user1.id}))


class StatsViewTest(TestCase):
    """
    class for test  StatsView
    """

    def setUp(self):
        # create Users
        self.test_user1 = User.objects.create_user(username='user1', password='12345')
        self.test_user2 = User.objects.create_user(username='user2', password='12345')

        # data for filters
        self.name_length = 3
        self.price_size = 50

        # create Products
        data_dict = {'product1': 1, 'product2': 10, 'pr': 33, 'product4': 43, 'product6': 90}
        products = [
            Product(name=name, price=price, create_by=self.test_user2) if index % 2 else
            Product(name=name, price=price, create_by=self.test_user1) for
            index, (name, price) in enumerate(data_dict.items())
        ]
        Product.objects.bulk_create(products)

    def test_view_url_exists(self):
        login = self.client.login(username='user1', password='12345')
        resp = self.client.get(reverse('products:stats_url', kwargs={'pk': 1}))

        # check URL exist
        self.assertEqual(resp.status_code, 200)

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('products:stats_url', kwargs={'pk': 1}))

        # check redirect URL
        self.assertRedirects(resp, '/?next=/stats/1/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='user1', password='12345')
        resp = self.client.get(reverse('products:stats_url', kwargs={'pk': 1}))

        # check is user logged
        self.assertEqual(str(resp.context['user']), 'user1')

        # check resp status
        self.assertEqual(resp.status_code, 200)

        # check template
        self.assertTemplateUsed(resp, 'StatsPage.html')

    def test_get_user_data(self):
        # get all user's products
        user_data = Product.objects.filter(
            create_by=self.test_user1
        ).aggregate(
            max_price=Max('price'),
            sum_price=Sum('price'),
            products=Count('id'), )
        control_data = {'max_price': Decimal('90'), 'sum_price': Decimal('124'), 'products': 3}

        # check data from DB with control data
        self.assertEqual(user_data, control_data)

    def test_get_total_data(self):
        # get data for all products
        total_data = Product.objects.aggregate(
            products=Count('id'),
            avg_price=Avg('price'))
        control_data = {'products': 5, 'avg_price': Decimal('35.4'), }

        # check data from DB with control data
        self.assertEqual(total_data, control_data)

    def test_data_with_conditions_user_and_name_length(self):
        data = Product.objects.filter(create_by=self.test_user1, name__length__gt=self.name_length).aggregate(
            total=Sum('price')
        )['total']
        control_data = 91
        # check data from DB with control data
        self.assertEqual(data, control_data)

    def test_data_with_conditions_user_price_size(self):
        data = Product.objects.filter(price__gt=self.price_size).aggregate(total=Sum('price'))['total']
        control_data = 90
        # check data from DB with control data
        self.assertEqual(data, control_data)


class IncreaseViewTest(TestCase):
    """
    class for test IncreaseView
    """

    def setUp(self):
        # create Users
        self.test_user1 = User.objects.create_user(username='user1', password='12345')

        # create Products
        data_dict = {'product1': 1, 'product2': 2, 'product3': 3, }
        products = [
            Product(name=name, price=price, create_by=self.test_user1) for
            name, price in data_dict.items()
        ]
        Product.objects.bulk_create(products)

    def test_view_url_exists(self):
        login = self.client.login(username='user1', password='12345')
        resp = self.client.get(reverse('products:increase_url', kwargs={'pk': 1}))

        # check redirect URL exist
        self.assertEqual(resp.status_code, 302)

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('products:increase_url', kwargs={'pk': 1}))

        # check redirect URL
        self.assertRedirects(resp, '/?next=/increase/1/')

    def test_get(self):
        login = self.client.login(username='user1', password='12345')

        # increase price for user's product
        Product.objects.filter(create_by=self.test_user1).update(price=F('price') + 1)

        # get total sum
        total_sum = Product.objects.filter(create_by=self.test_user1).aggregate(total=Sum('price'))['total']

        # expected sum
        expected_sum = 9

        # check updated data
        self.assertEqual(total_sum, expected_sum)

    def test_redirect_url(self):
        login = self.client.login(username='user1', password='12345')
        resp = self.client.get(reverse('products:increase_url', kwargs={'pk': self.test_user1.id}))

        # check resp status
        self.assertEqual(resp.status_code, 302)

        # check resp URL
        self.assertRedirects(resp, reverse('products:stats_url', kwargs={'pk': self.test_user1.id}))
