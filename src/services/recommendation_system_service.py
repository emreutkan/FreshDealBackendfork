from datetime import datetime
from sqlalchemy import func, and_
from src.models import db, Purchase, Listing, Restaurant, PurchaseStatus
from sklearn.neighbors import NearestNeighbors
import numpy as np
import pandas as pd


class RecommendationSystemService:
    def __init__(self):
        self.purchase_matrix = None
        self.listing_ids = None
        self.model = None
        self.is_initialized = False
        self.k_neighbors = 10

    def initialize_model(self):
        if self.is_initialized:
            return True

        try:
            # Get all completed purchases
            purchases = Purchase.query.filter_by(status='COMPLETED').all()
            if not purchases:
                return False

            # Create purchase data
            purchase_data = []
            for purchase in purchases:
                purchase_data.append({
                    'user_id': purchase.user_id,
                    'listing_id': purchase.listing_id,
                    'quantity': purchase.quantity
                })

            # Convert to DataFrame
            df = pd.DataFrame(purchase_data)

            if df.empty:
                return False

            # Create user-item matrix
            user_listing_matrix = pd.pivot_table(
                data=df,
                index='listing_id',
                columns='user_id',
                values='quantity',
                fill_value=0
            )

            self.purchase_matrix = user_listing_matrix.values
            self.listing_ids = user_listing_matrix.index.tolist()

            if len(self.listing_ids) == 0:
                return False

            # Create KNN model
            self.model = NearestNeighbors(
                n_neighbors=min(self.k_neighbors, len(self.listing_ids)),
                metric='cosine',
                algorithm='brute'
            )
            self.model.fit(self.purchase_matrix)
            self.is_initialized = True
            return True

        except Exception as e:
            print(f"Error initializing model: {e}")
            return False

    @staticmethod
    def get_recommendations_for_listing(listing_id):
        service = RecommendationSystemService()
        if not service.initialize_model():
            return {
                "success": False,
                "message": "Could not initialize recommendation model"
            }, 404

        try:
            # Get the target listing
            listing = Listing.query.get(listing_id)
            if not listing:
                return {
                    "success": False,
                    "message": "Listing not found"
                }, 404

            # Find listing index
            try:
                listing_idx = service.listing_ids.index(listing_id)
            except ValueError:
                return {
                    "success": False,
                    "message": "Listing not found in training data"
                }, 404

            # Get recommendations using KNN
            distances, indices = service.model.kneighbors(
                [service.purchase_matrix[listing_idx]],
                n_neighbors=min(service.k_neighbors, len(service.listing_ids))
            )

            # Convert distances to similarity scores
            similarities = 1 - distances.flatten()

            listing_recommendations = []
            for idx, similarity in zip(indices.flatten(), similarities):
                rec_id = service.listing_ids[idx]
                if rec_id != listing_id:  # Skip the input listing
                    listing_recommendations.append((rec_id, float(similarity)))

            # Sort by similarity score
            listing_recommendations.sort(key=lambda x: x[1], reverse=True)

            # Extract just the listing IDs
            listing_ids = [rec_id for rec_id, _ in listing_recommendations]

            return {
                "success": True,
                "data": listing_ids
            }, 200

        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return {
                "success": False,
                "message": "Error getting recommendations"
            }, 500


class RestaurantRecommendationSystemService:
    def __init__(self):
        self.restaurant_matrix = None
        self.restaurant_ids = None
        self.model = None
        self.is_initialized = False
        self.k_neighbors = 5  # Reduced from 10 to work better with smaller datasets

    def initialize_model(self):
        if self.is_initialized:
            return True

        try:
            # Get all completed purchases
            purchases = Purchase.query.filter_by(status='COMPLETED').all()

            print(f"Found {len(purchases)} completed purchases for recommendation model")

            if not purchases:
                print("No completed purchases found. Cannot initialize recommendation model.")
                return False

            # Create restaurant purchase data
            data = []
            for purchase in purchases:
                if purchase.listing and purchase.listing.restaurant_id:
                    data.append({
                        'user_id': purchase.user_id,
                        'restaurant_id': purchase.listing.restaurant_id
                    })

            df = pd.DataFrame(data)
            if df.empty:
                print("Empty dataframe after filtering. Cannot initialize recommendation model.")
                return False

            print(f"Created dataframe with {len(df)} purchase records for recommendation model")

            # Check if we have enough unique restaurants and users
            unique_users = df['user_id'].nunique()
            unique_restaurants = df['restaurant_id'].nunique()

            print(f"Recommendation data: {unique_users} unique users, {unique_restaurants} unique restaurants")

            if unique_users < 2 or unique_restaurants < 3:
                print("Not enough unique users or restaurants for meaningful recommendations")
                # We'll still try to proceed, but with lower expectations

            user_restaurant_matrix = df.pivot_table(
                index='restaurant_id',
                columns='user_id',
                aggfunc=lambda x: 1,
                fill_value=0
            )

            self.restaurant_matrix = user_restaurant_matrix.values
            self.restaurant_ids = user_restaurant_matrix.index.tolist()

            print(f"Created user-restaurant matrix with {len(self.restaurant_ids)} restaurants")

            if len(self.restaurant_ids) < 2:
                print("Not enough restaurant data for recommendations")
                return False

            # Reduce neighbors for small datasets
            actual_k = min(self.k_neighbors, max(1, len(self.restaurant_ids) - 1))

            self.model = NearestNeighbors(
                n_neighbors=actual_k,
                metric='cosine',
                algorithm='brute'
            )
            self.model.fit(self.restaurant_matrix)
            self.is_initialized = True
            print(f"Successfully initialized recommendation model with {actual_k} neighbors")
            return True

        except Exception as e:
            print(f"Error initializing restaurant recommendation model: {e}")
            return False

    @staticmethod
    def get_recommendations_by_user(user_id):
        service = RestaurantRecommendationSystemService()

        print(f"Getting recommendations for user ID: {user_id}")

        if not service.initialize_model():
            print(f"Failed to initialize recommendation model for user {user_id}")
            # Instead of returning error, provide fallback recommendations
            return RestaurantRecommendationSystemService.get_fallback_recommendations()

        try:
            purchases = Purchase.query.filter(
                Purchase.user_id == user_id,
                Purchase.status == PurchaseStatus.COMPLETED
            ).all()

            print(f"Found {len(purchases)} completed purchases for user {user_id}")

            if not purchases:
                print(f"No purchase history found for user {user_id}, using fallback")
                return RestaurantRecommendationSystemService.get_fallback_recommendations()

            restaurant_ids = set()
            for purchase in purchases:
                if purchase.listing and purchase.listing.restaurant_id:
                    restaurant_ids.add(purchase.listing.restaurant_id)

            print(f"User {user_id} has purchased from {len(restaurant_ids)} restaurants")

            if not restaurant_ids:
                print(f"No restaurants found in user {user_id}'s purchase history, using fallback")
                return RestaurantRecommendationSystemService.get_fallback_recommendations()

            all_recommendations = []
            for restaurant_id in restaurant_ids:
                try:
                    idx = service.restaurant_ids.index(restaurant_id)
                except ValueError:
                    print(f"Restaurant ID {restaurant_id} not found in model data")
                    continue

                # Get at most k_neighbors or max available
                actual_neighbors = min(service.k_neighbors + 1, len(service.restaurant_ids))

                try:
                    distances, indices = service.model.kneighbors(
                        [service.restaurant_matrix[idx]],
                        n_neighbors=actual_neighbors
                    )

                    similarities = 1 - distances.flatten()

                    for i, sim in zip(indices.flatten(), similarities):
                        rec_id = service.restaurant_ids[i]
                        if rec_id == restaurant_id:
                            continue

                        rec_rest = Restaurant.query.get(rec_id)
                        base_rest = Restaurant.query.get(restaurant_id)

                        if rec_rest and base_rest:
                            # Relaxed category matching to get more recommendations
                            if not any(r[0] == rec_id for r in all_recommendations):
                                all_recommendations.append((rec_id, float(sim)))
                except Exception as e:
                    print(f"Error getting neighbors for restaurant {restaurant_id}: {e}")

            if not all_recommendations:
                print("No recommendations found with collaborative filtering, using fallback")
                return RestaurantRecommendationSystemService.get_fallback_recommendations()

            all_recommendations.sort(key=lambda x: x[1], reverse=True)
            top_recommendations = all_recommendations[:10]

            # Extract just restaurant IDs
            restaurant_ids_list = [rec_id for rec_id, _ in top_recommendations]

            print(f"Found {len(restaurant_ids_list)} recommendations for user {user_id}")

            if not restaurant_ids_list:
                print("Empty recommendations list, using fallback")
                return RestaurantRecommendationSystemService.get_fallback_recommendations()

            return {
                "success": True,
                "data": restaurant_ids_list
            }, 200

        except Exception as e:
            print(f"Error getting recommendations: {e}")
            # Use fallback recommendations instead of error
            return RestaurantRecommendationSystemService.get_fallback_recommendations()

    @staticmethod
    def get_fallback_recommendations():
        """Provide fallback recommendations when personalized ones cannot be generated"""
        try:
            # Get top-rated restaurants or most popular ones
            popular_restaurants = db.session.query(Restaurant.id, func.count(Purchase.id).label('purchase_count')) \
                .join(Listing, Restaurant.id == Listing.restaurant_id) \
                .join(Purchase, Listing.id == Purchase.listing_id) \
                .filter(Purchase.status == PurchaseStatus.COMPLETED) \
                .group_by(Restaurant.id) \
                .order_by(func.count(Purchase.id).desc()) \
                .limit(10).all()

            restaurant_ids = [r[0] for r in popular_restaurants]

            # If we still don't have recommendations, just get any 10 restaurants
            if not restaurant_ids:
                restaurant_ids = [r.id for r in Restaurant.query.limit(10).all()]

            print(f"Using fallback recommendations: {restaurant_ids}")

            return {
                "success": True,
                "data": restaurant_ids
            }, 200
        except Exception as e:
            print(f"Error getting fallback recommendations: {e}")
            # Last resort: empty but successful response
            return {"success": True, "data": []}, 200

