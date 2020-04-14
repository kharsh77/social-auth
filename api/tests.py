from django.test import TestCase, Client
from django.db.models import F
from django.urls import reverse
from api.models import User

client = Client()

# Create your tests here.
class ModelTestClass(TestCase):
	@classmethod
	def setUpTestData(cls):
		User.objects.create(name='Testuser', email='test@test.com', phone_number="9072431298")

	def test_name_label(self):
		user = User.objects.get(id=1)
		expected_object_name = "Testuser"
		self.assertEquals(expected_object_name, str(user))

