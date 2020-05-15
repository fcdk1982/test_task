from django.test import TestCase

from products.forms import ProductCreateForm


class ProductCreateFormTest(TestCase):

    def test_form_field_name_min_length(self):
        form_data = {'name': 'a', 'price': 1}
        form = ProductCreateForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_field_price_is_0(self):
        form_data = {'name': 'ab', 'price': 0}
        form = ProductCreateForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_field_price_lt_0(self):
        form_data = {'name': 'ab', 'price': -0.1}
        form = ProductCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
