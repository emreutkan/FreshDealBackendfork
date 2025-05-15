import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, UTC
from flask import Flask
from src.models import db, UserAchievement, Achievement, AchievementType, Purchase, PurchaseStatus, RestaurantComment
from src.services.achievement_service import AchievementService


class TestAchievementService(unittest.TestCase):

    def setUp(self):
        # Create Flask app
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Initialize extensions
        db.init_app(self.app)

        # Create application context
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create tables
        db.create_all()

        # Set up mock achievements for testing
        self.first_purchase = MagicMock()
        self.first_purchase.id = 1
        self.first_purchase.achievement_type = AchievementType.FIRST_PURCHASE
        self.first_purchase.threshold = 1
        self.first_purchase.name = "First Purchase"
        self.first_purchase.description = "Made your first purchase on FreshDeal"
        self.first_purchase.badge_image_url = "/static/badges/first_purchase.png"

        self.regular_buyer = MagicMock()
        self.regular_buyer.id = 2
        self.regular_buyer.achievement_type = AchievementType.PURCHASE_COUNT
        self.regular_buyer.threshold = 5
        self.regular_buyer.name = "Regular Buyer"
        self.regular_buyer.description = "Completed 5 purchases"
        self.regular_buyer.badge_image_url = "/static/badges/regular_buyer.png"

        self.weekly_champion = MagicMock()
        self.weekly_champion.id = 3
        self.weekly_champion.achievement_type = AchievementType.WEEKLY_PURCHASE
        self.weekly_champion.threshold = 5
        self.weekly_champion.name = "Weekly Champion"
        self.weekly_champion.description = "Made 5 purchases in a week"
        self.weekly_champion.badge_image_url = "/static/badges/weekly_champion.png"

        self.regular_commenter = MagicMock()
        self.regular_commenter.id = 4
        self.regular_commenter.achievement_type = AchievementType.REGULAR_COMMENTER
        self.regular_commenter.threshold = 100
        self.regular_commenter.name = "Regular Commenter"
        self.regular_commenter.description = "Made 100 comments in 90 days"
        self.regular_commenter.badge_image_url = "/static/badges/regular_commenter.png"

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_initialize_achievements(self):
        with patch('src.services.achievement_service.Achievement.query') as mock_query, \
                patch('src.services.achievement_service.db.session') as mock_session:
            # Test when achievements already exist
            mock_query.count.return_value = 10
            AchievementService.initialize_achievements()
            mock_session.add_all.assert_not_called()
            mock_session.commit.assert_not_called()

            # Reset mocks
            mock_session.reset_mock()

            # Test when no achievements exist
            mock_query.count.return_value = 0
            AchievementService.initialize_achievements()
            mock_session.add_all.assert_called_once()
            mock_session.commit.assert_called_once()

    def test_check_and_award_achievements(self):
        with patch.object(AchievementService, '_check_first_purchase') as mock_first_purchase, \
                patch.object(AchievementService, '_check_purchase_count_achievements') as mock_purchase_count, \
                patch.object(AchievementService, '_check_weekly_purchase_achievement') as mock_weekly, \
                patch.object(AchievementService, '_check_comment_achievement') as mock_comment:
            user_id = 1
            mock_first_purchase.return_value = ["first_purchase"]
            mock_purchase_count.return_value = ["purchase_count"]
            mock_weekly.return_value = ["weekly"]
            mock_comment.return_value = ["comment"]

            result = AchievementService.check_and_award_achievements(user_id)

            mock_first_purchase.assert_called_once_with(user_id)
            mock_purchase_count.assert_called_once_with(user_id)
            mock_weekly.assert_called_once_with(user_id)
            mock_comment.assert_called_once_with(user_id)

            self.assertEqual(result, ["first_purchase", "purchase_count", "weekly", "comment"])

    def test_check_first_purchase_achievement_already_earned(self):
        user_id = 1

        with patch('src.services.achievement_service.Achievement.query') as mock_achievement_query, \
                patch('src.services.achievement_service.UserAchievement.query') as mock_user_achievement_query:
            mock_filter_by = mock_achievement_query.filter_by.return_value
            mock_filter_by.first.return_value = self.first_purchase

            mock_ua_filter_by = mock_user_achievement_query.filter_by.return_value
            mock_ua_filter_by.first.return_value = MagicMock()  # User already has the achievement

            result = AchievementService._check_first_purchase(user_id)
            self.assertEqual(result, [])  # No new achievements earned

    def test_check_first_purchase_achievement_newly_earned(self):
        user_id = 1

        with patch('src.services.achievement_service.Achievement.query') as mock_achievement_query, \
                patch('src.services.achievement_service.UserAchievement.query') as mock_user_achievement_query, \
                patch('src.services.achievement_service.Purchase.query') as mock_purchase_query, \
                patch('src.services.achievement_service.db.session') as mock_db_session:
            mock_filter_by = mock_achievement_query.filter_by.return_value
            mock_filter_by.first.return_value = self.first_purchase

            mock_ua_filter_by = mock_user_achievement_query.filter_by.return_value
            mock_ua_filter_by.first.return_value = None  # User doesn't have the achievement yet

            mock_purchase_filter = mock_purchase_query.filter.return_value
            mock_purchase_filter.count.return_value = 1  # User has 1 completed purchase

            result = AchievementService._check_first_purchase(user_id)

            # Verify achievement was awarded
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], self.first_purchase)
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()

    def test_check_purchase_count_achievements(self):
        user_id = 1

        with patch('src.services.achievement_service.Achievement.query') as mock_achievement_query, \
                patch('src.services.achievement_service.UserAchievement.query') as mock_user_achievement_query, \
                patch('src.services.achievement_service.Purchase.query') as mock_purchase_query, \
                patch('src.services.achievement_service.db.session') as mock_db_session:
            mock_filter_by = mock_achievement_query.filter_by.return_value
            mock_order_by = mock_filter_by.order_by.return_value
            mock_order_by.all.return_value = [self.regular_buyer]

            mock_purchase_filter = mock_purchase_query.filter.return_value
            mock_purchase_filter.count.return_value = 10  # User has 10 completed purchases

            mock_ua_filter_by = mock_user_achievement_query.filter_by.return_value
            mock_ua_filter_by.first.return_value = None  # User doesn't have the achievement yet

            result = AchievementService._check_purchase_count_achievements(user_id)

            # Verify achievement was awarded
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], self.regular_buyer)
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()

    def test_check_weekly_purchase_achievement(self):
        user_id = 1

        with patch('src.services.achievement_service.Achievement.query') as mock_achievement_query, \
                patch('src.services.achievement_service.UserAchievement.query') as mock_user_achievement_query, \
                patch('src.services.achievement_service.Purchase.query') as mock_purchase_query, \
                patch('src.services.achievement_service.datetime') as mock_datetime, \
                patch('src.services.achievement_service.db.session') as mock_db_session:
            mock_datetime.now.return_value = datetime(2025, 5, 15, 11, 6, 47, tzinfo=UTC)

            mock_filter_by = mock_achievement_query.filter_by.return_value
            mock_filter_by.first.return_value = self.weekly_champion

            mock_ua_filter_by = mock_user_achievement_query.filter_by.return_value
            mock_ua_filter_by.first.return_value = None  # User doesn't have the achievement yet

            mock_purchase_filter = mock_purchase_query.filter.return_value
            mock_purchase_filter.count.return_value = 7  # User has 7 purchases in the last week

            result = AchievementService._check_weekly_purchase_achievement(user_id)

            # Verify achievement was awarded
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], self.weekly_champion)
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()

    def test_check_comment_achievement(self):
        user_id = 1

        with patch('src.services.achievement_service.Achievement.query') as mock_achievement_query, \
                patch('src.services.achievement_service.UserAchievement.query') as mock_user_achievement_query, \
                patch('src.services.achievement_service.db.session') as mock_db_session, \
                patch('src.services.achievement_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 5, 15, 11, 6, 47, tzinfo=UTC)

            mock_filter_by = mock_achievement_query.filter_by.return_value
            mock_filter_by.first.return_value = self.regular_commenter

            mock_ua_filter_by = mock_user_achievement_query.filter_by.return_value
            mock_ua_filter_by.first.return_value = None  # User doesn't have the achievement yet

            # Mock the query count directly
            mock_count = MagicMock(return_value=150)  # User has 150 comments in last 90 days
            with patch('src.services.achievement_service.db.session.query') as mock_query:
                mock_query.return_value.filter.return_value.count = mock_count

                result = AchievementService._check_comment_achievement(user_id)

                # Verify achievement was awarded
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0], self.regular_commenter)
                mock_db_session.add.assert_called_once()
                mock_db_session.commit.assert_called_once()

    def test_get_user_achievements(self):
        user_id = 1

        with patch('src.services.achievement_service.UserAchievement.query') as mock_query:
            mock_ua1 = MagicMock()
            mock_ua1.achievement.id = 1
            mock_ua1.achievement.name = "First Purchase"
            mock_ua1.achievement.description = "Made your first purchase on FreshDeal"
            mock_ua1.achievement.badge_image_url = "/static/badges/first_purchase.png"
            mock_ua1.achievement.achievement_type = AchievementType.FIRST_PURCHASE
            mock_ua1.earned_at = datetime(2025, 5, 10, tzinfo=UTC)

            mock_filter_by = mock_query.filter_by.return_value
            mock_filter_by.all.return_value = [mock_ua1]

            result = AchievementService.get_user_achievements(user_id)

            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["id"], 1)
            self.assertEqual(result[0]["name"], "First Purchase")
            self.assertEqual(result[0]["description"], "Made your first purchase on FreshDeal")
            self.assertEqual(result[0]["badge_image_url"], "/static/badges/first_purchase.png")
            self.assertEqual(result[0]["earned_at"], "2025-05-10T00:00:00+00:00")
            self.assertEqual(result[0]["achievement_type"], AchievementType.FIRST_PURCHASE.value)

    def test_get_available_achievements(self):
        with patch('src.services.achievement_service.Achievement.query') as mock_query:
            mock_achievement = MagicMock()
            mock_achievement.id = 1
            mock_achievement.name = "First Purchase"
            mock_achievement.description = "Made your first purchase on FreshDeal"
            mock_achievement.badge_image_url = "/static/badges/first_purchase.png"
            mock_achievement.achievement_type = AchievementType.FIRST_PURCHASE
            mock_achievement.threshold = 1

            mock_filter_by = mock_query.filter_by.return_value
            mock_filter_by.all.return_value = [mock_achievement]

            result = AchievementService.get_available_achievements()

            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["id"], 1)
            self.assertEqual(result[0]["name"], "First Purchase")
            self.assertEqual(result[0]["description"], "Made your first purchase on FreshDeal")
            self.assertEqual(result[0]["badge_image_url"], "/static/badges/first_purchase.png")
            self.assertEqual(result[0]["achievement_type"], AchievementType.FIRST_PURCHASE.value)
            self.assertEqual(result[0]["threshold"], 1)


if __name__ == '__main__':
    unittest.main()