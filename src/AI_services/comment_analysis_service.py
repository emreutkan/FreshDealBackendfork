import os
import requests
import json
import datetime
import re
from typing import List, Dict, Any
from dotenv import load_dotenv
import logging

from src.models import RestaurantComment, Restaurant

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_restaurant_comments(restaurant_id: int) -> List[Dict[str, Any]]:
    """
    Fetch comments for a specific restaurant from the last 3 months

    Args:
        restaurant_id: ID of the restaurant

    Returns:
        List of comment dictionaries with text and other metadata
    """
    # Calculate date 3 months ago
    current_date = datetime.datetime.now()
    three_months_ago = current_date - datetime.timedelta(days=90)

    # Query for comments from the last 3 months
    recent_comments = RestaurantComment.query.filter(
        RestaurantComment.restaurant_id == restaurant_id,
        RestaurantComment.timestamp >= three_months_ago
    ).all()

    # Format comments for analysis
    comments_data = []
    for comment in recent_comments:
        if comment.comment:  # Make sure comment text exists
            comments_data.append({
                "text": comment.comment,
                "rating": float(comment.rating) if comment.rating else None,
                "timestamp": comment.timestamp.isoformat() if comment.timestamp else None,
                "user_id": comment.user_id
            })

    return comments_data


class CommentAnalysisService:
    """Service for analyzing restaurant comments using Groq API"""

    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Get API key from environment variables
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            logger.error("GROQ_API_KEY not found in environment variables")
            raise ValueError("GROQ_API_KEY not found in environment variables")

        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def analyze_comments(self, restaurant_id: int) -> Dict[str, Any]:
        """
        Analyze comments for a specific restaurant using Groq API

        Args:
            restaurant_id: ID of the restaurant

        Returns:
            Dictionary containing categorized good and bad feedback summaries
        """
        # Check if restaurant exists
        restaurant = Restaurant.query.get(restaurant_id)
        if not restaurant:
            logger.error(f"Restaurant with ID {restaurant_id} not found")
            return {
                "error": f"Restaurant with ID {restaurant_id} not found"
            }

        # Get restaurant comments
        comments_data = get_restaurant_comments(restaurant_id)

        if not comments_data:
            logger.info(f"No comments found for restaurant {restaurant_id} in the last 3 months")
            return {
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant.restaurantName,
                "message": "No comments found from the last 3 months",
                "good_aspects": [],
                "bad_aspects": []
            }

        # Extract just the comment text for analysis
        comment_texts = [comment["text"] for comment in comments_data]

        # Limit the number of comments to analyze if there are too many
        # This helps avoid potential token limit issues with the API
        max_comments = 50
        if len(comment_texts) > max_comments:
            logger.info(f"Limiting analysis to {max_comments} comments out of {len(comment_texts)}")
            comment_texts = comment_texts[:max_comments]

        prompt = f"""
        Lütfen bu restoranla ilgili son 3 ayda yapılan {len(comment_texts)} müşteri yorumunu analiz ediniz:

        {json.dumps(comment_texts)}


        Önemli kurallar:
        1. Tek harfleri ve anlamsız karakterleri göz ardı et
        2. Sadece restoran hakkında net fikir belirten yorumları dikkate al
        3. Birden fazla yorumda tekrarlanan ortak noktalara odaklan
        4. Olumsuz bir özellik ancak birden fazla yorumda geçiyorsa veya çok önemli bir sorun ise dahil edilmeli
        5. Kısa veya belirsiz yorumları aşırı yorumlama, ancak "taze", "lezzetli" gibi olumlu yorumlar ile "soğuk", "bayat" gibi olumsuz yorumlar kabul edilebilir
        6. Benzer anlamları tek bir kategoride birleştir (örneğin "lezzetli yemek" ve "harika yemek" aynı kategori olmalı: "lezzetli yemek")


        Yorumları şu kategorilerde sınıflandır:
        1. Müşterilerin restoran/satıcı hakkında belirttiği genel olumlu özellikler
        2. Müşterilerin restoran/satıcı hakkında belirttiği genel olumsuz özellikler

        Yanıtını aşağıdaki anahtar kelimelerle bir JSON nesnesi formatında ver:
        - "good_aspects": [bu restoranın genel olarak iyi özellikleri (kısa ifadelerle, sadece Türkçe ve tekrar etmeyen kategoriler)]
        - "bad_aspects": [bu restoranın genel olarak kötü özellikleri (kısa ifadelerle, sadece Türkçe ve tekrar etmeyen kategoriler)]
        - "reasoning:" [analizin arkasındaki mantığın kısa açıklaması (sadece Türkçe)]


        YALNIZCA JSON nesnesini döndür, başka metin ekleme.
        """

        payload = {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }

        try:
            logger.info(f"Sending API request to Groq for restaurant {restaurant_id}")
            response = requests.post(self.base_url, headers=self.headers, json=payload)

            # Log the response for debugging
            logger.info(f"Groq API response status: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"Groq API error: {response.text}")

            response.raise_for_status()

            result = response.json()

            # Extract the content safely
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                print(f"Raw Groq response content:\n{content}")  # <-- ADD THIS LINE

                # Extract JSON from content (which may be wrapped in markdown code blocks)
                json_content = self._extract_json_from_markdown(content)

                if json_content:
                    try:
                        analysis_result = json.loads(json_content)
                    except json.JSONDecodeError:
                        # If JSON parsing fails, try the backup parser
                        analysis_result = self._extract_aspects_from_text(content)
                else:
                    # If no JSON was found, use the backup parser
                    analysis_result = self._extract_aspects_from_text(content)
            else:
                logger.error(f"Unexpected API response format: {result}")
                analysis_result = {
                    "good_aspects": [],
                    "bad_aspects": []
                }

            return {
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant.restaurantName,
                "comment_count": len(comment_texts),
                "analysis_date": datetime.datetime.now().isoformat(),
                "good_aspects": analysis_result.get("good_aspects", []),
                "bad_aspects": analysis_result.get("bad_aspects", [])
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            # Add more detailed error information
            error_details = ""
            if hasattr(e, 'response') and e.response is not None:
                error_details = f" - Response: {e.response.text}"

            return {
                "error": f"API request failed: {str(e)}{error_details}",
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant.restaurantName
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse API response: {str(e)}")
            return {
                "error": f"Failed to parse API response: {str(e)}",
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant.restaurantName
            }
        except Exception as e:
            logger.error(f"Unexpected error during comment analysis: {str(e)}")
            return {
                "error": f"Unexpected error during comment analysis: {str(e)}",
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant.restaurantName
            }

    def _extract_json_from_markdown(self, content: str) -> str:
        """Extract JSON from markdown code blocks"""
        # Pattern to match JSON code blocks (both with and without language specifier)
        json_pattern = r"```(?:json)?\s*\n([\s\S]*?)\n\s*```"
        matches = re.findall(json_pattern, content)

        # Return the first JSON block found
        if matches:
            return matches[0].strip()
        return ""

    def _extract_aspects_from_text(self, content: str) -> Dict[str, List[str]]:
        """Extract good and bad aspects from text content when JSON parsing fails"""
        good_aspects = []
        bad_aspects = []

        lines = content.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect sections
            if 'good aspects' in line.lower() or 'positive aspects' in line.lower():
                current_section = 'good'
            elif 'bad aspects' in line.lower() or 'negative aspects' in line.lower():
                current_section = 'bad'
            # Detect list items
            elif line.startswith('- ') or line.startswith('* ') or line.startswith('•'):
                item = re.sub(r'^[-*•]\s+', '', line).strip()
                if current_section == 'good' and item:
                    good_aspects.append(item)
                elif current_section == 'bad' and item:
                    bad_aspects.append(item)
            # Detect numbered lists
            elif re.match(r'^\d+\.', line):
                item = re.sub(r'^\d+\.\s*', '', line).strip()
                if current_section == 'good' and item:
                    good_aspects.append(item)
                elif current_section == 'bad' and item:
                    bad_aspects.append(item)

        return {
            "good_aspects": good_aspects,
            "bad_aspects": bad_aspects
        }

