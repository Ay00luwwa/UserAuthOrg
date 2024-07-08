from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from datetime import timedelta
from authOrgApp.models import User, Organisation

User = get_user_model()

class TokenTests(APITestCase):

    def test_token_generation(self):
        user = User.objects.create_user(
            email='john@example.com',
            first_name='John',
            last_name='Doe',
            password='password123'
        )
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        

        self.assertEqual(refresh.access_token.payload['exp'], (refresh.access_token.payload['iat'] + timedelta(minutes=5)).timestamp())
        

        self.assertEqual(refresh.access_token.payload['user_id'], user.id)
        self.assertEqual(refresh.access_token.payload['email'], user.email)
        

        self.assertTrue(access_token.startswith('eyJ')) 
        self.assertIn(user.email, access_token)




class OrganisationAccessTests(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create(
            email='user1@example.com',
            first_name='User1',
            last_name='One',
            password='password123'
        )
        self.user2 = User.objects.create(
            email='user2@example.com',
            first_name='User2',
            last_name='Two',
            password='password123'
        )
        self.org1 = Organisation.objects.create(
            name="User1's Organisation",
            description="Organisation for User1"
        )
        self.org1.users.add(self.user1)
        self.org2 = Organisation.objects.create(
            name="User2's Organisation",
            description="Organisation for User2"
        )
        self.org2.users.add(self.user2)

    def test_user_cannot_access_other_org(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('organisation-detail', args=[self.org2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)




class AuthTests(APITestCase):

    def test_register_user_successfully(self):
        url = reverse('register')
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'password123',
            'phone': '1234567890'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('accessToken', response.data['data'])
        self.assertEqual(response.data['data']['user']['first_name'], 'John')
        self.assertEqual(response.data['data']['user']['last_name'], 'Doe')
        self.assertEqual(response.data['data']['user']['email'], 'john@example.com')
        self.assertTrue(User.objects.filter(email='john@example.com').exists())
        self.assertTrue(Organisation.objects.filter(name="John's Organisation").exists())

    def test_login_user_successfully(self):
        user = User.objects.create_user(
            email='john@example.com',
            first_name='John',
            last_name='Doe',
            password='password123'
        )
        url = reverse('login')
        data = {
            'email': 'john@example.com',
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('accessToken', response.data['data'])
        self.assertEqual(response.data['data']['user']['email'], 'john@example.com')

    def test_register_user_missing_fields(self):
        url = reverse('register')
        data = {
            'first_name': '',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'password123',
            'phone': '1234567890'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('errors', response.data)

    def test_register_user_duplicate_email(self):
        User.objects.create_user(
            email='john@example.com',
            first_name='John',
            last_name='Doe',
            password='password123'
        )
        url = reverse('register')
        data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'password123',
            'phone': '0987654321'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('errors', response.data)
