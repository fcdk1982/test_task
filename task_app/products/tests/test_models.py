from django.test import TestCase

from products.models import Product


class ProductModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Product.objects.create(name='prod1', price=5)

    def test_name_verbose_name(self):
        product = Product.objects.get(id=1)
        field_label = product._meta.get_field('name').verbose_name
        self.assertEquals(field_label, 'Назва продукту')

    def test_price_verbose_name(self):
        product = Product.objects.get(id=1)
        field_label = product._meta.get_field('price').verbose_name
        self.assertEquals(field_label, 'Ціна продукту')

    def test_create_by_verbose_name(self):
        product = Product.objects.get(id=1)
        field_label = product._meta.get_field('create_by').verbose_name
        self.assertEquals(field_label, 'Кліент')
