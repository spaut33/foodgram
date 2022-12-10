import pytest

from tests.common import APITestBase


@pytest.mark.django_db(transaction=True)
class TestUserAPI(APITestBase):
    def test_deactivate_user_access(self, blocked_client, blocked_user):
        """Test deactivated user access"""
        # Get methods return 401
        urls = [
            'users_me',
            'set_password',
            'delete_token',
            'shopping_cart',
            'users_detail',
        ]
        for url in urls:
            response = blocked_client.get(
                self.urls[url].format(user_id=blocked_user.id)
            )
            self.assert_status_code(401, response)
        # Post methods return 400
        urls = ['get_token', 'users']
        for url in urls:
            response = blocked_client.post(self.urls[url])
            self.assert_status_code(400, response)
