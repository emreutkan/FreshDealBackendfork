class TestSearch(unittest.TestCase):
    def test_search_restaurants(self):
        """Test searching restaurants"""
        response = self.client.get(
            f'{self.base_url}/search',
            query_string={
                'type': 'restaurant',
                'query': 'Test',
                'category': 'Test Category'
            }
        )

        self.assertEqual(response.status_code, 200)

    def test_search_listings(self):
        """Test searching listings"""
        response = self.client.get(
            f'{self.base_url}/search',
            query_string={
                'type': 'listing',
                'query': 'Test',
                'min_price': '0',
                'max_price': '100'
            }
        )

        self.assertEqual(response.status_code, 200)