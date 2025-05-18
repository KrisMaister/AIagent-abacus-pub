import requests
import json
import time
import base64
from io import BytesIO
from PIL import Image

def Image_Generation(prompt, api_keys, max_retries=3, initial_delay=1):
    """
    Generate image using Hugging Face's Stable Diffusion API
    
    Args:
        prompt (str): The image generation prompt
        api_keys (dict): Dictionary of API keys
        max_retries (int): Maximum number of retries
        initial_delay (int): Initial delay in seconds between retries
    """
    cartoon_style = "cartoon style, vibrant colors, clean lines, illustration art, animated movie style: "
    enhanced_prompt = f"{cartoon_style} {prompt}"
    
    if not api_keys.get('HUGGINGFACE_TOKEN'):
        raise Exception("Hugging Face token not found in api_keys")

    url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {
        "Authorization": f"Bearer {api_keys['HUGGINGFACE_TOKEN']}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": enhanced_prompt,
        "parameters": {
            "num_inference_steps": 50,
            "guidance_scale": 7.5,
            "width": 1024,
            "height": 1024
        }
    }
    
    retry_count = 0
    delay = initial_delay
    
    while retry_count < max_retries:
        try:
            print(f"Generating image with Abacus.ai (attempt {retry_count + 1}/{max_retries})")
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                print("Successfully generated image!")
                return response.content
            
            elif response.status_code == 401:
                raise Exception("Hugging Face token invalid or expired")
            
            elif response.status_code == 503:
                # Model is loading
                try:
                    error_msg = response.json()
                    if "estimated_time" in error_msg:
                        wait_time = error_msg.get("estimated_time", delay)
                        print(f"Model is loading. Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                        retry_count += 1
                        continue
                except:
                    print("Could not parse 503 error message")
            
            elif response.status_code in [403, 429]:
                print("Request blocked or rate limited")
                time.sleep(delay)
                delay *= 2
                retry_count += 1
                continue
            
            else:
                print(f"API failed with status {response.status_code}")
                print(f"Response: {response.text}")
                time.sleep(delay)
                delay *= 2
                retry_count += 1
                continue

        except requests.exceptions.Timeout:
            print("Request timed out")
            time.sleep(delay)
            delay *= 2
            retry_count += 1
            continue
            
        except Exception as e:
            print(f"Error: {str(e)}")
            time.sleep(delay)
            delay *= 2
            retry_count += 1
            continue
    
    raise Exception(f"Image generation failed after {max_retries} attempts")

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

def prompt_to_image_url(prompt, api_keys, imgur_client_id):
    """
    Generate image from prompt using Abacus.ai and return public URL
    """
    try:
        # Generate image
        print(f"Generating image for prompt: '{prompt}'")
        image_bytes = Image_Generation(prompt, api_keys)

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

def read_secrets():
    """Read secrets from tokens.txt file"""
    try:
        with open('tokens.txt', 'r') as f:
            secrets = {}
            for line in f:
                if '=' in line:
                    key, value = line.split('=', 1)
                    # Remove any quotes
                    key = key.strip()
                    value = value.strip().strip('"')
                    secrets[key] = value
            return secrets
    except Exception as e:
        print(f"Error reading secrets file: {str(e)}")
        return {}

# Example usage
if __name__ == "__main__":
    # Get credentials from secrets file
    secrets = read_secrets()
    api_keys = {
        'HUGGINGFACE_TOKEN': secrets.get('HUGGINGFACE_TOKEN')
    }
    imgur_client_id = secrets.get('IMGUR_CLIENT_ID')

    if not api_keys['HUGGINGFACE_TOKEN'] or not imgur_client_id:
        print("Missing required credentials in secrets file")
        exit(1)

    # Test prompt
    prompt = "A futuristic cityscape at sunset with flying cars and neon lights"

    try:
        url = prompt_to_image_url(prompt, api_keys, imgur_client_id)
        print("\nSuccess!")
        print("Image URL:", url)
    except Exception as e:
        print("\nFailed!")
        print("Error:", str(e))