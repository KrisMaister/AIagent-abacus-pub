import requests
from datetime import datetime
import os
from pathlib import Path

class InstagramAPI:
    def __init__(self, access_token, instagram_account_id):
        self.access_token = access_token
        self.instagram_account_id = instagram_account_id
        self.base_url = "https://graph.facebook.com/v18.0"

    def post_photo(self, image_path, caption, hashtags=[]):
        """
        Post a photo to Instagram with caption and hashtags

        Args:
            image_path (str): Local path to the image file
            caption (str): Main caption text
            hashtags (list): List of hashtags without the # symbol
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

            # Publish the container
            publish_url = f"{self.base_url}/{self.instagram_account_id}/media_publish"
            publish_payload = {
                'creation_id': creation_id,
                'access_token': self.access_token
            }

            publish_response = requests.post(publish_url, data=publish_payload)
            publish_response.raise_for_status()

            return {
                'status': 'success',
                'post_id': publish_response.json()['id'],
                'timestamp': datetime.now().isoformat()
            }

        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

def main():
    # Replace these with your actual credentials
    ACCESS_TOKEN = "IGAAJ2iZAYLdHhBZAE9rY0ktYjBDV0NnQjFDVlQ2c19tZAUJjWVNVcGZACQW96Um9pNzRWVlctYVZAnMFBodXJoXzluenphZAld4STJIVU5PamdyTXpqeTZAhQVhRZAVMzcVBVWFpmZAmh5Rjk0NG4zZATYxMVlsNDlpcDBtX1d6VTZAmWGtqSQZDZD"
    INSTAGRAM_ACCOUNT_ID = "17841474045181795"

    # Initialize the API
    ig_api = InstagramAPI(ACCESS_TOKEN, INSTAGRAM_ACCOUNT_ID)

    # Example post using local image
    # Specify the path to your local image
    image_path = "path/to/your/image.jpg"  # For example: "images/sunset.jpg"

    caption = "Beautiful sunset at the beach! 🌅"
    hashtags = ["sunset", "beach", "nature", "photography", "instagood"]

    # Post the photo
    result = ig_api.post_photo(image_path, caption, hashtags)

    # Print result
    if result['status'] == 'success':
        print(f"Successfully posted to Instagram! Post ID: {result['post_id']}")
    else:
        print(f"Error posting to Instagram: {result['message']}")

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
    post_with_validation()
