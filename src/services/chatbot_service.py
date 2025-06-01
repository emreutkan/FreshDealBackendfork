from src.models import db, Purchase, User, CustomerAddress, Restaurant, Listing, UserFavorites
from datetime import datetime, timedelta
from sqlalchemy import desc, func


class ChatbotService:

    @staticmethod
    def start_conversation(user_id):
        """Initial chatbot greeting with main navigation options"""
        return {
            "success": True,
            "message": "Hello! I'm your FreshDeal assistant 🤖 How can I help you today?",
            "options": [
                "🛒 Orders & Purchases",
                "🏠 Address Management",
                "🔍 Finding Food & Restaurants",
                "❤️ Favorites & Saved Items",
                "🏆 Rankings & Achievements",
                "💰 Flash Deals & Discounts",
                "👤 Account Settings",
                "❓ App Navigation Help"
            ]
        }

    # === ORDER MANAGEMENT ===
    @staticmethod
    def get_order_status(user_id):
        """Get current order status"""
        purchase = Purchase.query.filter_by(user_id=user_id).filter(
            Purchase.status != 'CANCELED'
        ).order_by(Purchase.created_at.desc()).first()

        if purchase:
            return {
                "success": True,
                "order_status": purchase.status,
                "listing_id": purchase.listing_id,
                "created_at": purchase.created_at.isoformat(),
                "next_steps": ChatbotService._get_order_next_steps(purchase.status)
            }
        else:
            return {
                "success": False,
                "message": "No active orders found.",
                "suggestion": "Browse restaurants and flash deals to place your first order! 🍽️"
            }

    @staticmethod
    def cancel_order(user_id):
        """Cancel the most recent active order"""
        purchase = Purchase.query.filter_by(user_id=user_id).filter(
            Purchase.status != 'CANCELED'
        ).order_by(Purchase.created_at.desc()).first()

        if not purchase:
            return {
                "success": False,
                "message": "No active order to cancel.",
                "suggestion": "Check your order history in the Orders tab 📋"
            }

        purchase.status = 'CANCELED'
        purchase.canceled_at = datetime.utcnow()
        db.session.commit()

        return {
            "success": True,
            "message": "Your order has been successfully canceled.",
            "next_action": "You can browse new deals or check your order history."
        }

    @staticmethod
    def get_order_history(user_id, limit=5):
        """Get user's order history"""
        orders = Purchase.query.filter_by(user_id=user_id).order_by(
            Purchase.created_at.desc()
        ).limit(limit).all()

        if orders:
            order_list = [{
                "id": order.id,
                "status": order.status,
                "created_at": order.created_at.isoformat(),
                "listing_id": order.listing_id
            } for order in orders]

            return {
                "success": True,
                "orders": order_list,
                "message": f"Here are your last {len(orders)} orders",
                "navigation_tip": "Tap on any order to see details, or visit Orders tab for full history"
            }
        else:
            return {
                "success": False,
                "message": "No order history found.",
                "suggestion": "Start exploring restaurants to place your first order! 🍕"
            }

    # === ADDRESS MANAGEMENT ===
    @staticmethod
    def update_user_address(user_id, address_data):
        """Add or update user address"""
        user = User.query.get(user_id)
        if not user:
            return {"success": False, "message": "User not found."}

        new_address = CustomerAddress(
            user_id=user_id,
            title=address_data.get("title", "Primary Address"),
            longitude=address_data["longitude"],
            latitude=address_data["latitude"],
            street=address_data.get("street"),
            neighborhood=address_data.get("neighborhood"),
            district=address_data.get("district"),
            province=address_data.get("province"),
            country=address_data.get("country"),
            postalCode=address_data.get("postalCode"),
            apartmentNo=address_data.get("apartmentNo"),
            doorNo=address_data.get("doorNo"),
            is_primary=address_data.get("is_primary", False)
        )

        db.session.add(new_address)
        db.session.commit()

        return {
            "success": True,
            "message": "Your address has been successfully updated.",
            "tip": "You can set multiple addresses and choose them during checkout! 📍"
        }

    @staticmethod
    def get_user_addresses(user_id):
        """Get all user addresses"""
        addresses = CustomerAddress.query.filter_by(user_id=user_id).all()

        if addresses:
            address_list = [{
                "id": addr.id,
                "title": addr.title,
                "street": addr.street,
                "neighborhood": addr.neighborhood,
                "is_primary": addr.is_primary
            } for addr in addresses]

            return {
                "success": True,
                "addresses": address_list,
                "navigation_tip": "Go to Account → Address Management to edit or add new addresses"
            }
        else:
            return {
                "success": False,
                "message": "No saved addresses found.",
                "suggestion": "Add your address in Account settings for faster checkout! 🏠"
            }

    # === FAVORITES MANAGEMENT ===
    @staticmethod
    def get_user_favorites(user_id):
        """Get user's favorite restaurants/items"""
        favorites = UserFavorites.query.filter_by(user_id=user_id).all()

        if favorites:
            return {
                "success": True,
                "favorites_count": len(favorites),
                "message": f"You have {len(favorites)} favorite items",
                "navigation_tip": "Visit the Favorites tab ❤️ to see all your saved restaurants and deals"
            }
        else:
            return {
                "success": False,
                "message": "No favorites yet!",
                "suggestion": "Tap the heart icon ❤️ on restaurants or deals to save them for later"
            }

    @staticmethod
    def add_to_favorites_guide():
        """Guide user on how to add favorites"""
        return {
            "success": True,
            "message": "To add items to favorites:",
            "steps": [
                "1. Browse restaurants or food deals",
                "2. Tap the heart icon ❤️ on any item",
                "3. Find all saved items in the Favorites tab",
                "4. Get quick access to your preferred restaurants!"
            ],
            "tip": "Favorited restaurants will show your past orders for easy reordering 🔄"
        }

    # === SEARCH & DISCOVERY ===
    @staticmethod
    def search_guidance():
        """Help users with search functionality"""
        return {
            "success": True,
            "message": "Here's how to find exactly what you're craving:",
            "search_tips": [
                "🔍 Use the search bar to find specific restaurants or food types",
                "📍 Filter by distance to find nearby options",
                "💰 Sort by price to find the best deals",
                "⭐ Check ratings and reviews before ordering",
                "🕒 Look for restaurants with fast delivery times"
            ],
            "navigation": "Access search from the home screen search bar or Search tab"
        }

    @staticmethod
    def flash_deals_guide():
        """Guide users to flash deals"""
        return {
            "success": True,
            "message": "Save money with Flash Deals! ⚡",
            "tips": [
                "💰 Flash deals offer significant discounts for limited time",
                "⏰ Check expiration times - deals change throughout the day",
                "🔔 Enable notifications to get alerts for new deals",
                "🏃‍♂️ Act fast - popular deals sell out quickly!"
            ],
            "navigation": "Find Flash Deals on the home screen or dedicated Flash Deals section"
        }

    # === ACHIEVEMENTS & RANKINGS ===
    @staticmethod
    def achievements_guide():
        """Guide users about achievements system"""
        return {
            "success": True,
            "message": "Earn achievements and climb the rankings! 🏆",
            "achievement_types": [
                "🍽️ Order milestones (1st order, 10th order, etc.)",
                "💚 Eco-warrior points for reducing food waste",
                "⭐ Review badges for rating restaurants",
                "🔥 Streak achievements for consecutive orders",
                "👑 VIP status for loyal customers"
            ],
            "navigation": "Check your progress in Profile → Achievements"
        }

    @staticmethod
    def rankings_explanation():
        """Explain the rankings system"""
        return {
            "success": True,
            "message": "See how you rank among FreshDeal users! 📊",
            "ranking_categories": [
                "🌱 Environmental impact (food waste saved)",
                "🏆 Total orders completed",
                "⭐ Reviews contributed",
                "💰 Money saved through deals"
            ],
            "navigation": "View rankings in the Rankings tab to see leaderboards"
        }

    # === NAVIGATION HELP ===
    @staticmethod
    def app_navigation_guide():
        """Comprehensive app navigation guide"""
        return {
            "success": True,
            "message": "FreshDeal App Navigation Guide 📱",
            "main_tabs": {
                "🏠 Home": "Browse restaurants, flash deals, and featured offers",
                "🔍 Search": "Find specific restaurants, cuisines, or deals",
                "❤️ Favorites": "Quick access to your saved restaurants and items",
                "🛒 Orders": "Track current orders and view order history",
                "👤 Account": "Profile settings, addresses, achievements, and app preferences"
            },
            "quick_actions": [
                "Pull down on home screen to refresh deals",
                "Use filter buttons to narrow search results",
                "Tap restaurant cards for menus and details",
                "Swipe on items for quick actions"
            ]
        }

    @staticmethod
    def checkout_help():
        """Guide users through checkout process"""
        return {
            "success": True,
            "message": "Checkout made simple! 🛒",
            "checkout_steps": [
                "1. Add items to cart from restaurant menus",
                "2. Review your cart and apply any discount codes",
                "3. Select delivery address (or add new one)",
                "4. Choose payment method",
                "5. Confirm order and track delivery"
            ],
            "tips": [
                "💡 Save addresses for faster future checkouts",
                "🎟️ Check for available coupons before paying",
                "📱 Track your order status in real-time"
            ]
        }

    # === UTILITY METHODS ===
    @staticmethod
    def _get_order_next_steps(status):
        """Get next steps based on order status"""
        status_guide = {
            "PENDING": "Your order is being prepared. You'll be notified when it's ready for pickup/delivery.",
            "CONFIRMED": "Great! Your order is confirmed and being prepared.",
            "IN_PROGRESS": "Your order is being prepared. Estimated completion time will be updated soon.",
            "READY": "Your order is ready! Check delivery details or head to pickup location.",
            "DELIVERED": "Enjoy your meal! Don't forget to rate and review the restaurant.",
            "COMPLETED": "Thank you for your order! Consider reordering from your favorites."
        }
        return status_guide.get(status, "Contact support if you need help with your order.")

    @staticmethod
    def get_help_options():
        """Show all available help topics"""
        return {
            "success": True,
            "message": "What do you need help with?",
            "help_topics": [
                "🛒 How to place an order",
                "📍 Managing delivery addresses",
                "❤️ Adding items to favorites",
                "🔍 Finding restaurants and deals",
                "💰 Using flash deals and discounts",
                "🏆 Understanding achievements and rankings",
                "📱 App navigation and features",
                "🛒 Checkout and payment process",
                "📞 Contact customer support"
            ]
        }

    @staticmethod
    def contact_support():
        """Provide contact information"""
        return {
            "success": True,
            "message": "Need human assistance? We're here to help! 👥",
            "contact_options": [
                "📧 Email: support@freshdeal.com",
                "📱 In-app chat: Account → Help & Support",
                "🕒 Support hours: 9 AM - 9 PM daily"
            ],
            "before_contacting": [
                "Check your order status in Orders tab",
                "Review FAQ in Account → Help section",
                "Try restarting the app if experiencing technical issues"
            ]
        }

    @staticmethod
    def handle_user_query(user_id, query_text):
        """Process natural language queries and route to appropriate methods"""
        query_lower = query_text.lower()

        # Order-related queries
        if any(word in query_lower for word in ['order', 'purchase', 'buy', 'cart']):
            if 'status' in query_lower or 'track' in query_lower:
                return ChatbotService.get_order_status(user_id)
            elif 'cancel' in query_lower:
                return ChatbotService.cancel_order(user_id)
            elif 'history' in query_lower:
                return ChatbotService.get_order_history(user_id)
            else:
                return ChatbotService.checkout_help()

        # Address-related queries
        elif any(word in query_lower for word in ['address', 'location', 'delivery']):
            return ChatbotService.get_user_addresses(user_id)

        # Favorites-related queries
        elif any(word in query_lower for word in ['favorite', 'saved', 'heart']):
            if 'how' in query_lower or 'add' in query_lower:
                return ChatbotService.add_to_favorites_guide()
            else:
                return ChatbotService.get_user_favorites(user_id)

        # Search-related queries
        elif any(word in query_lower for word in ['search', 'find', 'restaurant', 'food']):
            return ChatbotService.search_guidance()

        # Deals-related queries
        elif any(word in query_lower for word in ['deal', 'discount', 'flash', 'cheap']):
            return ChatbotService.flash_deals_guide()

        # Achievement-related queries
        elif any(word in query_lower for word in ['achievement', 'ranking', 'points', 'level']):
            if 'ranking' in query_lower or 'leaderboard' in query_lower:
                return ChatbotService.rankings_explanation()
            else:
                return ChatbotService.achievements_guide()

        # Navigation help
        elif any(word in query_lower for word in ['how', 'navigate', 'use', 'help']):
            return ChatbotService.app_navigation_guide()

        # Support queries
        elif any(word in query_lower for word in ['support', 'contact', 'problem', 'issue']):
            return ChatbotService.contact_support()

        # Default response
        else:
            return ChatbotService.get_help_options()