"""
Windows Wallpaper Changer
-------------------------
Change your desktop wallpaper from:
  1. A local image file, or
  2. An image downloaded from the web (any common format).

Requirements:
    Python 3.x
    pip install requests
"""

import os
import sys
import time
import ctypes
import requests
from urllib.parse import urlparse
import mimetypes


def get_user_choice():
    """Ask whether to use a local file or a web URL and return the details."""
    print("Processing your request...")
    choice = input("Enter your choice (local/web): ").strip()
    
    # Check if user entered a URL directly
    if choice.startswith(('http://', 'https://')):
        print(f"Detected URL input: {choice}")
        print("You chose: web")
        return "web", None, choice
    
    choice = choice.lower()
    print(f"You chose: {choice}")

    if choice == "local":
        image_path = input("Enter the full path to your image: ").strip()
        return choice, image_path, None
    elif choice == "web":
        image_url = input("Enter the direct image URL: ").strip()
        return choice, None, image_url
    else:
        print("Invalid choice. Please enter 'local', 'web', or paste a direct image URL.")
        sys.exit(1)


def download_web_image(image_url):
    """Download an image from a URL and return the local file path."""
    print("Downloading image from web...")
    try:
        response = requests.get(image_url, timeout=15)
        response.raise_for_status()  # stop if download fails

        # Determine filename and extension
        parsed = urlparse(image_url)
        file_name = os.path.basename(parsed.path)

        if not file_name or "." not in file_name:
            # Guess extension from the HTTP header if URL doesn't end with a file name
            content_type = response.headers.get("Content-Type", "")
            ext = mimetypes.guess_extension(content_type.split(";")[0].strip()) or ".jpg"
            file_name = f"downloaded_wallpaper{ext}"

        save_path = os.path.join(os.getcwd(), file_name)

        with open(save_path, "wb") as f:
            f.write(response.content)

        print(f"Image saved to {save_path}")
        return save_path
        
    except requests.RequestException as e:
        print(f"Error downloading image: {e}")
        raise
    except Exception as e:
        print(f"Error saving image: {e}")
        raise


def set_wallpaper(image_path):
    """Set the desktop wallpaper using Windows API."""
    abs_path = os.path.abspath(image_path)
    # SPI_SETDESKWALLPAPER = 20, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE = 3
    result = ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)
    if result:
        print(f"Wallpaper successfully changed to: {abs_path}")
    else:
        print("Failed to change wallpaper")
    return result


def main():
    """Main function to orchestrate the wallpaper changing process"""
    try:
        # Get user choice and inputs
        choice, local_path, web_url = get_user_choice()
        
        print("Got the input we needed")
        print(f"You want to set your background from {choice} source")
        
        # Wait for 1.5 seconds with user feedback (as requested)
        print("Processing request...")
        time.sleep(1.5)
        print("Processing complete.")
        
        # Handle web functionality or use local path
        if choice == "web":
            print(f"Attempting to download from: {web_url}")
            image_path = download_web_image(web_url)
            downloaded_file = True  # Track if we downloaded the file
        else:
            image_path = local_path
            downloaded_file = False  # Don't delete user's local files
            
        # Verify the image file exists
        if not os.path.exists(image_path):
            print(f"Error: Image file not found at {image_path}")
            return
            
        print(f"Attempting to set wallpaper: {image_path}")
        # Set the wallpaper
        success = set_wallpaper(image_path)
        
        # Delete downloaded image after setting wallpaper (only for web downloads)
        if success and downloaded_file:
            try:
                print(f"Deleting downloaded file: {image_path}")
                os.remove(image_path)
                print(f"Downloaded image deleted: {os.path.basename(image_path)}")
            except OSError as e:
                print(f"Warning: Could not delete downloaded image: {e}")
        elif not success:
            print("Wallpaper setting failed - keeping downloaded file for debugging")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except requests.RequestException as e:
        print(f"Error downloading image: {e}")
        print("Please check the URL and your internet connection.")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
