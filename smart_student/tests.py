from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Userinformation



class UserinformationModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@gmail.com",
            password="testpass123"
        )
        self.user_info = Userinformation.objects.create(
            user=self.user,
            User_name="testuser",
            Email="testuser@gmail.com"
        )

    def test_userinformation_str(self):
        
        self.assertEqual(str(self.user_info), "testuser")

    def test_userinformation_linked_to_user(self):
        
        self.assertEqual(self.user_info.user, self.user)

    def test_userinformation_email(self):
        
        self.assertEqual(self.user_info.Email, "testuser@gmail.com")



class URLRoutingTest(TestCase):

    def test_login_page_url_resolves(self):
        """Root URL should resolve to login_page."""
        response = self.client.get(reverse("login_page"))
        self.assertEqual(response.status_code, 200)

    def test_smart_url_redirects_unauthenticated(self):
        """'/smart/' should be accessible (no login required based on current views)."""
        response = self.client.get(reverse("smart"))
        self.assertIn(response.status_code, [200, 302])

    def test_logout_url_resolves(self):
        """Logout URL should redirect."""
        response = self.client.get(reverse("logout_page"))
        self.assertEqual(response.status_code, 302)

    def test_clear_chat_url_redirects(self):
        """clear_chat should redirect to smart."""
        response = self.client.get(reverse("clear_chat"))
        self.assertRedirects(response, reverse("smart"))



class LoginPageViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.login_url = reverse("login_page")
      
        self.existing_user = User.objects.create_user(
            username="existinguser",
            email="existing@gmail.com",
            password="validpass123"
        )

        Userinformation.objects.create(
            user=self.existing_user,
            User_name="existinguser",
            Email="existing@gmail.com"
        )

    def test_login_page_get(self):
        
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")

    def test_register_new_user_valid(self):
     
        response = self.client.post(self.login_url, {
            "username": "newuser",
            "email": "newuser@gmail.com",
            "password": "newpass123"
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_invalid_email_format(self):
       
        response = self.client.post(self.login_url, {
            "username": "baduser",
            "email": "baduser@hotmail.com",
            "password": "validpass123"
        })
        self.assertRedirects(response, self.login_url)
        self.assertFalse(User.objects.filter(username="baduser").exists())

    def test_register_short_password(self):
       
        response = self.client.post(self.login_url, {
            "username": "shortpass",
            "email": "shortpass@gmail.com",
            "password": "abc"
        })
        self.assertRedirects(response, self.login_url)
        self.assertFalse(User.objects.filter(username="shortpass").exists())

    def test_login_existing_user_correct_password(self):
        
        response = self.client.post(self.login_url, {
            "username": "existinguser",
            "email": "existing@gmail.com",
            "password": "validpass123"
        })
        self.assertRedirects(response, "/smart/")

    def test_login_existing_user_wrong_password(self):
        
        response = self.client.post(self.login_url, {
            "username": "existinguser",
            "email": "existing@gmail.com",
            "password": "wrongpass999"
        })
        self.assertRedirects(response, self.login_url)

    def test_register_duplicate_email(self):
       
        response = self.client.post(self.login_url, {
            "username": "anotheruser",
            "email": "existing@gmail.com", 
            "password": "anotherpass123"
        })
        self.assertRedirects(response, self.login_url)
        self.assertFalse(User.objects.filter(username="anotheruser").exists())



class LogoutViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="logoutuser",
            email="logoutuser@gmail.com",
            password="logoutpass123"
        )
        self.client.login(username="logoutuser", password="logoutpass123")

    def test_logout_redirects_to_login(self):
       
        response = self.client.get(reverse("logout_page"))
        self.assertRedirects(response, reverse("login_page"))

    def test_user_logged_out_after_logout(self):
       
        self.client.get(reverse("logout_page"))
        response = self.client.get(reverse("login_page"))
        self.assertFalse(response.wsgi_request.user.is_authenticated)




class SmartViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.smart_url = reverse("smart")

    def test_smart_page_get(self):
       
        response = self.client.get(self.smart_url)
        self.assertEqual(response.status_code, 200)

    def test_api_key_stored_in_session(self):
        
        response = self.client.post(self.smart_url, {
            "password_key": "test-groq-api-key-123"
        })
        self.assertRedirects(response, self.smart_url)
        session = self.client.session
        self.assertEqual(session.get("groq_api_key"), "test-groq-api-key-123")

    def test_logout_action_clears_session(self):
        
        session = self.client.session
        session["groq_api_key"] = "some-key"
        session["chat_history"] = [{"role": "user", "content": "hello"}]
        session.save()

        response = self.client.post(self.smart_url, {"action": "logout"})
        self.assertRedirects(response, self.smart_url)
        session = self.client.session
        self.assertIsNone(session.get("groq_api_key"))
        self.assertIsNone(session.get("chat_history"))

    def test_clear_chat_resets_history(self):
     
        session = self.client.session
        session["chat_history"] = [{"role": "user", "content": "test msg"}]
        session.save()

        self.client.get(reverse("clear_chat"))
        session = self.client.session
        self.assertEqual(session.get("chat_history"), [])
