import requests

def Image_Generation(prompt, hf_token):
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {"inputs": prompt}
    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.content  # This is the image bytes
    else:
        raise Exception(f"Image generation failed: {response.text}")

def upload_to_imgur(image_bytes, client_id):
    url = "https://api.imgur.com/3/image"
    headers = {"Authorization": f"Client-ID {client_id}"}
    files = {'image': image_bytes}
    response = requests.post(url, headers=headers, files=files)
    if response.status_code == 200:
        return response.json()['data']['link']
    else:
        raise Exception(f"Imgur upload failed: {response.text}")

def prompt_to_image_url(prompt, hf_token, imgur_client_id):
    # Step 1: Generate image
    image_bytes = Image_Generation(prompt, hf_token)
    # Step 2: Upload to Imgur
    image_url = upload_to_imgur(image_bytes, imgur_client_id)
    return image_url

# Example usage:
if __name__ == "__main__":
    print("TEST")
    prompt = "A futuristic cityscape at sunset, vibrant colors"
    hf_token = "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"
    imgur_client_id = "KrisMaister"
    url = prompt_to_image_url(prompt, hf_token, imgur_client_id)
    print("Image URL:", url)