class TestReviews(unittest.TestCase):
    def test_create_restaurant_review(self):
        """Test creating a restaurant review"""
        review_data = {
            'rating': 4,
            'comment': 'Great service and food!'
        }

        response = self.client.post(
            f'{self.base_url}/restaurants/{self.restaurant.id}/reviews',
            json=review_data,
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 201)

    def test_create_listing_review(self):
        """Test creating a listing review"""
        review_data = {
            'rating': 5,
            'comment': 'Excellent deal!'
        }

        response = self.client.post(
            f'{self.base_url}/listings/{self.listing.id}/reviews',
            json=review_data,
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 201)