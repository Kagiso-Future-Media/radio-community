import pytest


@pytest.mark.django_db
class TestHomePageView:
    def test_get_home_page(self, client):
        response = client.get('/')

        assert response.status_code == 200
