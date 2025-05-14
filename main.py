import requests
from datetime import datetime
import os
from pathlib import Path
import logging
import base64
from gen_image import prompt_to_image_url
from news_analyzer import generate_news_enhanced_prompt

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InstagramAPI:
    def __init__(self, access_token, instagram_account_id):
        self.access_token = access_token
        self.instagram_account_id = instagram_account_id
        self.base_url = "https://graph.facebook.com/v18.0"

    def validate_credentials(self):
        """
        Validates the access token and Instagram account ID
        Returns tuple (bool, str) - (is_valid, message)
        """
        try:
            # First, verify the access token
            token_info_url = f"{self.base_url}/debug_token"
            params = {
                'input_token': self.access_token,
                'access_token': self.access_token
            }

            response = requests.get(token_info_url, params=params)
            if response.status_code != 200:
                return False, f"Invalid access token. Status code: {response.status_code}"

            token_data = response.json().get('data', {})

            # Check if token is valid
            if not token_data.get('is_valid'):
                return False, "Access token is invalid or expired"

            # Check token permissions
            required_permissions = ['instagram_basic', 'instagram_content_publish', 'pages_read_engagement']
            scopes = token_data.get('scopes', [])
            missing_permissions = [perm for perm in required_permissions if perm not in scopes]

            if missing_permissions:
                return False, f"Missing required permissions: {', '.join(missing_permissions)}"

            # Verify Instagram account
            return self.verify_instagram_account()

        except requests.exceptions.RequestException as e:
            return False, f"Network error during validation: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error during validation: {str(e)}"

    def verify_instagram_account(self):
        """
        Verifies if the Instagram account is valid and accessible
        Returns tuple (bool, str) - (is_valid, message)
        """
        try:
            # Get Instagram Business Account info
            account_url = f"{self.base_url}/{self.instagram_account_id}"
            params = {
                'fields': 'id,username',
                'access_token': self.access_token
            }

            response = requests.get(account_url, params=params)
            if response.status_code != 200:
                return False, f"Unable to access Instagram account. Status code: {response.status_code}. Response: {response.text}"

            account_data = response.json()
            logger.debug(f"Account data received: {account_data}")

            # Check if we can access the account
            if 'id' not in account_data:
                return False, "Unable to verify Instagram account ID"

            # Try to get more detailed Instagram account information
            ig_account_url = f"{self.base_url}/{self.instagram_account_id}?fields=biography,id,username,website&access_token={self.access_token}"
            ig_response = requests.get(ig_account_url)

            if ig_response.status_code != 200:
                return False, f"Unable to fetch Instagram account details. Status: {ig_response.status_code}"

            ig_data = ig_response.json()
            logger.debug(f"Instagram data received: {ig_data}")

            username = ig_data.get('username', 'Unknown')
            return True, f"Successfully verified Instagram account: {username}"

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during account verification: {str(e)}")
            return False, f"Network error during account verification: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error during account verification: {str(e)}")
            return False, f"Unexpected error during account verification: {str(e)}"

    def check_api_limits(self):
        """
        Checks current API usage limits
        Returns tuple (bool, str) - (has_available_calls, message)
        """
        try:
            usage_url = f"{self.base_url}/{self.instagram_account_id}/content_publishing_limit"
            params = {
                'fields': 'config,quota_usage',
                'access_token': self.access_token
            }

            response = requests.get(usage_url, params=params)
            if response.status_code != 200:
                return False, "Unable to check API limits"

            usage_data = response.json().get('data', [])[0] if response.json().get('data') else {}
            quota_usage = usage_data.get('quota_usage', 0)
            config = usage_data.get('config', {})
            quota_total = config.get('quota_total', 0)

            if quota_usage >= quota_total:
                return False, f"API limit reached: {quota_usage}/{quota_total} posts"

            return True, f"API calls available: {quota_total - quota_usage}/{quota_total}"

        except requests.exceptions.RequestException as e:
            return False, f"Network error checking API limits: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error checking API limits: {str(e)}"

    def post_photo_with_url(self, image_url, caption, hashtags=[]):
        """
        Post a photo to Instagram using an image URL
        """
        try:
            # Format hashtags
            formatted_hashtags = " ".join([f"#{tag}" for tag in hashtags])
            full_caption = f"{caption}\n\n{formatted_hashtags}"

            # Create media container
            media_url = f"{self.base_url}/{self.instagram_account_id}/media"
            payload = {
                'image_url': image_url,
                'caption': full_caption,
                'access_token': self.access_token
            }

            # Create container
            response = requests.post(media_url, data=payload)
            logger.debug(f"Container creation response status: {response.status_code}")
            logger.debug(f"Container creation response content: {response.text}")

            if response.status_code != 200:
                return {
                    'status': 'error',
                    'message': f"Container creation failed: {response.text}",
                    'timestamp': datetime.now().isoformat()
                }

            creation_id = response.json().get('id')

            # Publish the container
            publish_url = f"{self.base_url}/{self.instagram_account_id}/media_publish"
            publish_payload = {
                'creation_id': creation_id,
                'access_token': self.access_token
            }

            publish_response = requests.post(publish_url, data=publish_payload)
            logger.debug(f"Publish response status: {publish_response.status_code}")
            logger.debug(f"Publish response content: {publish_response.text}")

            if publish_response.status_code != 200:
                return {
                    'status': 'error',
                    'message': f"Publishing failed: {publish_response.text}",
                    'timestamp': datetime.now().isoformat()
                }

            return {
                'status': 'success',
                'post_id': publish_response.json().get('id'),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error in post_photo_with_url: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def generate_and_post(self, prompt, hashtags=None):
        """
        Generates an image from a prompt and posts it to Instagram
        """
        try:
            # Get secrets for image generation
            secrets = read_secrets()
            hf_token = secrets.get('HUGGINGFACE_TOKEN')
            imgur_client_id = secrets.get('IMGUR_CLIENT_ID')

            # Generate image URL
            image_url = prompt_to_image_url(prompt, hf_token, imgur_client_id)
            if not image_url:
                return {
                    'status': 'error',
                    'message': 'Failed to generate image URL',
                    'timestamp': datetime.now().isoformat()
                }

            # Post to Instagram
            return self.post_photo_with_url(image_url, prompt, hashtags or [])

        except Exception as e:
            logger.error(f"Error in generate_and_post: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

def generate_detailed_prompt(topic_description):
    """
    Generate a detailed image prompt based on a high-level description and current news.
    Returns a tuple of (detailed_prompt, hashtags)
    """
    # Get news-enhanced description and hashtags directly
    # Since news_analyzer.py now handles all the prompt generation
    return generate_news_enhanced_prompt(topic_description)

def read_secrets():
    """Read secrets from tokens_secret.txt file"""
    try:
        with open('tokens_secret.txt', 'r') as f:
            content = f.read()
            # Decode base64 content
            decoded = base64.b64decode(content).decode('utf-8')
            secrets = {}
            for line in decoded.splitlines():
                if line.startswith('export '):
                    key, value = line.replace('export ', '').split('=', 1)
                    secrets[key] = value.strip('"')
            return secrets
    except Exception as e:
        logger.error(f"Error reading secrets file: {str(e)}")
        return {}

def main():
    # Get credentials from secrets file
    secrets = read_secrets()
    access_token = secrets.get('INSTAGRAM_ACCESS_TOKEN')
    instagram_account_id = secrets.get('INSTAGRAM_ACCOUNT_ID')

    if not access_token or not instagram_account_id:
        logger.error("Missing required credentials in secrets file")
        return

    # Initialize API
    api = InstagramAPI(access_token, instagram_account_id)

    # Validate credentials
    is_valid, message = api.validate_credentials()
    if not is_valid:
        logger.error(f"Credential validation failed: {message}")
        return

    logger.info(f"Credentials validated: {message}")

    # Check API limits
    has_calls, limit_message = api.check_api_limits()
    if not has_calls:
        logger.error(f"API limit check failed: {limit_message}")
        return

    logger.info(f"API limits checked: {limit_message}")

    # Get user input for the image description
    description = input("Please describe what kind of image you want to create: ")
    
    # Generate detailed prompt and hashtags
    detailed_prompt, hashtags = generate_detailed_prompt(description)
    
    # Log the generated prompt
    logger.info(f"Generated prompt: {detailed_prompt}")
    logger.info(f"Generated hashtags: {hashtags}")
    
    # Confirm with user
    print("\nGenerated image prompt:")
    print(detailed_prompt)
    print("\nHashtags:")
    print(" ".join([f"#{tag}" for tag in hashtags]))
    
    proceed = input("\nWould you like to proceed with this prompt? (yes/no): ")
    if proceed.lower() != 'yes':
        logger.info("User cancelled the operation")
        return

    # Generate and post the image
    result = api.generate_and_post(detailed_prompt, hashtags)
    logger.info(f"Post result: {result}")

if __name__ == "__main__":
    main()