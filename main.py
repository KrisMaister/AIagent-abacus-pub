import requests
from datetime import datetime

class InstagramAPI:
    def __init__(self, access_token, instagram_account_id):
        self.access_token = access_token
        self.instagram_account_id = instagram_account_id
        self.base_url = "https://graph.facebook.com/v18.0"  # Using latest API version

    def post_photo(self, image_url, caption, hashtags=[]):
        """
        Post a photo to Instagram with caption and hashtags

        Args:
            image_url (str): URL of the image to post
            caption (str): Main caption text
            hashtags (list): List of hashtags without the # symbol
        """
        try:
            # Format hashtags
            formatted_hashtags = " ".join([f"#{tag}" for tag in hashtags])
            full_caption = f"{caption}\n\n{formatted_hashtags}"

            # First, create a media container
            post_url = f"{self.base_url}/{self.instagram_account_id}/media"

            payload = {
                'image_url': image_url,
                'caption': full_caption,
                'access_token': self.access_token
            }

            # Create media container
            response = requests.post(post_url, data=payload)
            response.raise_for_status()
            creation_id = response.json()['id']

            # Second, publish the container
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

# Example usage
def main():
    # Replace these with your actual credentials
    ACCESS_TOKEN = "your_access_token_here"
    INSTAGRAM_ACCOUNT_ID = "your_instagram_account_id_here"

    # Initialize the API
    ig_api = InstagramAPI(ACCESS_TOKEN, INSTAGRAM_ACCOUNT_ID)

    # Example post
    image_url = "https://example.com/your-image.jpg"
    caption = "Beautiful sunset at the beach! 🌅"
    hashtags = ["sunset", "beach", "nature", "photography", "instagood"]

    # Post the photo
    result = ig_api.post_photo(image_url, caption, hashtags)

    # Print result
    if result['status'] == 'success':
        print(f"Successfully posted to Instagram! Post ID: {result['post_id']}")
    else:
        print(f"Error posting to Instagram: {result['message']}")

if __name__ == "__main__":
    main()
