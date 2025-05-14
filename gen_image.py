import requests
import json
import time
import base64
from io import BytesIO
from PIL import Image

def Image_Generation(prompt, hf_token):
    """
    Generate image using Hugging Face's Stable Diffusion API
    """
    # Using Stable Diffusion XL
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json"
    }

    # Enhanced payload with better parameters
    payload = {
        "inputs": prompt,
        "parameters": {
            "num_inference_steps": 50,
            "guidance_scale": 7.5,
            "width": 1024,
            "height": 1024
        }
    }

    print(f"Making request to {api_url}")
    print(f"With headers: {headers}")
    print(f"And payload: {json.dumps(payload, indent=2)}")

    # Maximum number of retries
    max_retries = 5
    retry_delay = 2  # seconds

    for attempt in range(max_retries):
        try:
            print(f"\nAttempt {attempt + 1}/{max_retries}")
            response = requests.post(api_url, headers=headers, json=payload)

            # Log response details for debugging
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")

            if response.status_code == 200:
                print("Successfully generated image!")
                return response.content

            # Handle model loading
            elif response.status_code == 503:
                try:
                    error_msg = response.json()
                    if "estimated_time" in error_msg:
                        wait_time = error_msg.get("estimated_time", retry_delay)
                        print(f"Model is loading. Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                except:
                    print("Could not parse 503 error message")

            # Print full response for debugging
            print(f"Response content: {response.text}")

            # Handle specific errors
            if response.status_code == 404:
                raise Exception("Model not found. Please check the model name and URL.")
            elif response.status_code == 401:
                raise Exception("Authentication failed. Please check your Hugging Face token.")
            else:
                raise Exception(f"Request failed with status code: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Network error: {str(e)}")
            if attempt == max_retries - 1:
                raise Exception(f"Network error after {max_retries} attempts: {str(e)}")
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

    raise Exception(f"Failed to generate image after {max_retries} attempts")

def upload_to_imgur(image_bytes, client_id):
    """
    Upload image to Imgur and return the URL
    """
    url = "https://api.imgur.com/3/image"
    headers = {"Authorization": f"Client-ID {client_id}"}

    # Convert image bytes to base64
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')

    payload = {
        'image': image_b64,
        'type': 'base64'
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()['data']['link']
    else:
        raise Exception(f"Imgur upload failed: {response.text}")

def prompt_to_image_url(prompt, hf_token, imgur_client_id):
    """
    Generate image from prompt and return public URL
    """
    try:
        # Generate image
        print(f"Generating image for prompt: '{prompt}'")
        image_bytes = Image_Generation(prompt, hf_token)

        # Verify image data
        try:
            img = Image.open(BytesIO(image_bytes))
            print(f"Image generated successfully. Size: {img.size}")
        except Exception as e:
            raise Exception(f"Invalid image data received: {str(e)}")

        # Upload to Imgur
        print("Uploading image to Imgur...")
        image_url = upload_to_imgur(image_bytes, imgur_client_id)
        print(f"Image uploaded successfully. URL: {image_url}")

        return image_url

    except Exception as e:
        print(f"Error in prompt_to_image_url: {str(e)}")
        raise

# Example usage
if __name__ == "__main__":
    # Your credentials
    hf_token = "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"
    imgur_client_id = "06d144c711be94d"

    # Test prompt
    prompt = "A futuristic cityscape at sunset with flying cars and neon lights"

    try:
        url = prompt_to_image_url(prompt, hf_token, imgur_client_id)
        print("\nSuccess!")
        print("Image URL:", url)
    except Exception as e:
        print("\nFailed!")
        print("Error:", str(e))