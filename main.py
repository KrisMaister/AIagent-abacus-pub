import requests
from datetime import datetime
import os
from pathlib import Path
<<<<<<< HEAD
import logging
from gen_image import prompt_to_image_url

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
=======
>>>>>>> c596bd843a3353c9a0e7c42ac4ed547e1b3d280b

class InstagramAPI:
    def __init__(self, access_token, instagram_account_id):
        self.access_token = access_token
        self.instagram_account_id = instagram_account_id
<<<<<<< HEAD
        self.base_url = "https://graph.facebook.com/v22.0"

    def validate_credentials(self):
=======
        self.base_url = "https://graph.facebook.com/v18.0"

    def post_photo(self, image_path, caption, hashtags=[]):
>>>>>>> c596bd843a3353c9a0e7c42ac4ed547e1b3d280b
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

<<<<<<< HEAD
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
=======
        Args:
            image_path (str): Local path to the image file
            caption (str): Main caption text
            hashtags (list): List of hashtags without the # symbol
>>>>>>> c596bd843a3353c9a0e7c42ac4ed547e1b3d280b
        """
        try:
            # Verify if image exists
            if not os.path.exists(image_path):
                return {
                    'status': 'error',
                    'message': f"Image not found at path: {image_path}",
                    'timestamp': datetime.now().isoformat()
                }

            # Format hashtags
            formatted_hashtags = " ".join([f"#{tag}" for tag in hashtags])
            full_caption = f"{caption}\n\n{formatted_hashtags}"

<<<<<<< HEAD
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

=======
            # Create a media container
            post_url = f"{self.base_url}/{self.instagram_account_id}/media"

            # Open the image file in binary mode
            with open(image_path, 'rb') as image_file:
                payload = {
                    'caption': full_caption,
                    'access_token': self.access_token
                }
                files = {
                    'image': image_file
                }

                # Create media container
                response = requests.post(post_url, data=payload, files=files)
                response.raise_for_status()
                creation_id = response.json()['id']

>>>>>>> c596bd843a3353c9a0e7c42ac4ed547e1b3d280b
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
    
    def post_photo(self, image_path, caption, hashtags=[]):
        """
        Post a photo to Instagram with caption and hashtags
        """
        # First validate credentials and account
        is_valid, message = self.validate_credentials()
        if not is_valid:
            return {
                'status': 'error',
                'message': f"Validation failed: {message}",
                'timestamp': datetime.now().isoformat()
            }

        # Check API limits
        has_limit, limit_message = self.check_api_limits()
        if not has_limit:
            return {
                'status': 'error',
                'message': f"API limit issue: {limit_message}",
                'timestamp': datetime.now().isoformat()
            }

        # Continue with the existing post_photo implementation...
        try:
            # Verify if image exists
            if not os.path.exists(image_path):
                return {
                    'status': 'error',
                    'message': f"Image not found at path: {image_path}",
                    'timestamp': datetime.now().isoformat()
                }

            # Format hashtags
            formatted_hashtags = " ".join([f"#{tag}" for tag in hashtags])
            full_caption = f"{caption}\n\n{formatted_hashtags}"

            # Upload the image
            with open(image_path, 'rb') as image_file:
                upload_url = f"{self.base_url}/{self.instagram_account_id}/media"
                payload = {
                    'access_token': self.access_token,
                    'caption': full_caption,
                    'media_type': 'IMAGE'
                }

                response = requests.post(
                    upload_url,
                    data=payload,
                    files={'file': ('photo.jpg', image_file, 'image/jpeg')}
                )

                logger.debug(f"Upload response status: {response.status_code}")
                logger.debug(f"Upload response content: {response.text}")

                if response.status_code != 200:
                    return {
                        'status': 'error',
                        'message': f"Upload failed: {response.text}",
                        'timestamp': datetime.now().isoformat()
                    }

                creation_id = response.json().get('id')

                # Publish the uploaded media
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
            logger.error(f"Error in post_photo: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

def main():
    # Replace these with your actual credentials
<<<<<<< HEAD
    ACCESS_TOKEN = "EAAbLmArAZCWsBOzRIENTzeIYccepzK9EKgaidlvwMrbCmmMy6XFRL2tileHsl9OWNpF9UMc8e4P0Az52R6Py4bEYZCO3CFtwJisO5M244MVvEzCu4f6u9jVu9as9WwX5Q1EmnZBD1g8vWzHZCVeoPLWy9ZBW1h41IMEipnD7jrMDxxegZB9TkSmYmn"
=======
    ACCESS_TOKEN = "IGAAJ2iZAYLdHhBZAE9rY0ktYjBDV0NnQjFDVlQ2c19tZAUJjWVNVcGZACQW96Um9pNzRWVlctYVZAnMFBodXJoXzluenphZAld4STJIVU5PamdyTXpqeTZAhQVhRZAVMzcVBVWFpmZAmh5Rjk0NG4zZATYxMVlsNDlpcDBtX1d6VTZAmWGtqSQZDZD"
>>>>>>> c596bd843a3353c9a0e7c42ac4ed547e1b3d280b
    INSTAGRAM_ACCOUNT_ID = "17841474045181795"

    # Initialize the API
    ig_api = InstagramAPI(ACCESS_TOKEN, INSTAGRAM_ACCOUNT_ID)

<<<<<<< HEAD
    # First, validate credentials and connection
    print("Validating credentials and Instagram connection...")
    is_valid, message = ig_api.validate_credentials()
    if not is_valid:
        print(f"Validation failed: {message}")
        return

    print(f"Validation successful: {message}")

    # Check API limits
    print("\nChecking API limits...")
    has_limit, limit_message = ig_api.check_api_limits()
    if not has_limit:
        print(f"API limit issue: {limit_message}")
        return

    print(f"API limits OK: {limit_message}")

    # Proceed with posting
    print("\nProceeding with post...")
    image_path = "/Users/kbuda/Documents/GitHub/AIagent-abacus-pub/test.jpg"  # Update this path
    image_url = "https://i.imgur.com/UHzHVew.jpeg"
    caption = "What a beautiful flower!"
    hashtags = ["nature", "photography", "instagood"]

    # Post the photo
    # result = ig_api.post_photo(image_path, caption, hashtags)
    result = ig_api.post_photo_with_url(image_url, caption, hashtags)
=======
    # Example post using local image
    # Specify the path to your local image
    image_path = "path/to/your/image.jpg"  # For example: "images/sunset.jpg"

    caption = "Beautiful sunset at the beach! 🌅"
    hashtags = ["sunset", "beach", "nature", "photography", "instagood"]

    # Post the photo
    result = ig_api.post_photo(image_path, caption, hashtags)
>>>>>>> c596bd843a3353c9a0e7c42ac4ed547e1b3d280b

    # Print result
    if result['status'] == 'success':
        print(f"\nSuccessfully posted to Instagram! Post ID: {result['post_id']}")
    else:
        print(f"\nError posting to Instagram: {result['message']}")

def main():
    # Replace these with your actual credentials
    ACCESS_TOKEN = "EAAbLmArAZCWsBOzRIENTzeIYccepzK9EKgaidlvwMrbCmmMy6XFRL2tileHsl9OWNpF9UMc8e4P0Az52R6Py4bEYZCO3CFtwJisO5M244MVvEzCu4f6u9jVu9as9WwX5Q1EmnZBD1g8vWzHZCVeoPLWy9ZBW1h41IMEipnD7jrMDxxegZB9TkSmYmn"
    INSTAGRAM_ACCOUNT_ID = "17841474045181795"

    # Initialize the API
    ig_api = InstagramAPI(ACCESS_TOKEN, INSTAGRAM_ACCOUNT_ID)

    # First, validate credentials and connection
    print("Validating credentials and Instagram connection...")
    is_valid, message = ig_api.validate_credentials()
    if not is_valid:
        print(f"Validation failed: {message}")
        return

    print(f"Validation successful: {message}")

    # Check API limits
    print("\nChecking API limits...")
    has_limit, limit_message = ig_api.check_api_limits()
    if not has_limit:
        print(f"API limit issue: {limit_message}")
        return

    print(f"API limits OK: {limit_message}")

    # Proceed with posting
    print("\nProceeding with post...")
    image_path = "/Users/kbuda/Documents/GitHub/AIagent-abacus-pub/test.jpg"  # Update this path
    image_url = "https://i.imgur.com/UHzHVew.jpeg"
    caption = "What a beautiful flower!"
    hashtags = ["nature", "photography", "instagood"]

    # Post the photo
    # result = ig_api.post_photo(image_path, caption, hashtags)
    result = ig_api.post_photo_with_url(image_url, caption, hashtags)

    # Print result
    if result['status'] == 'success':
        print(f"\nSuccessfully posted to Instagram! Post ID: {result['post_id']}")
    else:
        print(f"\nError posting to Instagram: {result['message']}")

# Helper function to validate image before posting
def validate_image(image_path):
    """
    Validates if the image meets Instagram's requirements
    """
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            return False, "Image file does not exist"

        # Check file extension
        valid_extensions = ['.jpg', '.jpeg', '.png']
        file_extension = Path(image_path).suffix.lower()
        if file_extension not in valid_extensions:
            return False, f"Invalid file format. Must be one of: {valid_extensions}"

        # Check file size (Instagram's limit is 8MB)
        file_size = os.path.getsize(image_path) / (1024 * 1024)  # Convert to MB
        if file_size > 8:
            return False, "Image file size must be less than 8MB"

        return True, "Image is valid"

    except Exception as e:
        return False, f"Error validating image: {str(e)}"

# Example usage with image validation
def post_with_validation():
    ACCESS_TOKEN = "your_access_token_here"
    INSTAGRAM_ACCOUNT_ID = "your_instagram_account_id_here"

    # Initialize the API
    ig_api = InstagramAPI(ACCESS_TOKEN, INSTAGRAM_ACCOUNT_ID)

    # Local image path
    image_path = "images/sunset.jpg"  # Update this path to your image location

    # Validate image first
    is_valid, message = validate_image(image_path)
    if not is_valid:
        print(f"Image validation failed: {message}")
        return

    # Prepare post content
    caption = "Enjoying this beautiful sunset! 🌅"
    hashtags = ["sunset", "beachlife", "nature", "photography", "instadaily"]

    # Make the post
    result = ig_api.post_photo(image_path, caption, hashtags)

    # Check result
    if result['status'] == 'success':
        print(f"Posted successfully! Post ID: {result['post_id']}")
    else:
        print(f"Error: {result['message']}")

if __name__ == "__main__":
<<<<<<< HEAD
    main()
=======
    post_with_validation()
>>>>>>> c596bd843a3353c9a0e7c42ac4ed547e1b3d280b
