#!/usr/bin/env python3
import json
import os
import requests
from urllib.parse import urlparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_image(item_id, url, output_dir):
    """Download a single image and save it locally"""
    try:
        # Create the output filename
        output_path = os.path.join(output_dir, f"{item_id}.jpg")
        
        # Skip if already downloaded
        if os.path.exists(output_path):
            print(f"✓ Image {item_id} already exists, skipping")
            return item_id, f"thumbnails/{item_id}.jpg", True
        
        # Download the image
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        # Save the image
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ Downloaded image for ID {item_id}")
        return item_id, f"thumbnails/{item_id}.jpg", True
        
    except Exception as e:
        print(f"✗ Failed to download image for ID {item_id}: {str(e)}")
        return item_id, None, False

def main():
    # Load the data
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create thumbnails directory if it doesn't exist
    thumbnails_dir = 'thumbnails'
    os.makedirs(thumbnails_dir, exist_ok=True)
    
    # Prepare download tasks
    download_tasks = []
    for item in data['data']:
        if item.get('thumbnail_url'):
            download_tasks.append((item['id'], item['thumbnail_url']))
    
    print(f"Found {len(download_tasks)} images to download")
    print("=" * 50)
    
    # Download images in parallel (max 10 concurrent downloads)
    successful_downloads = 0
    failed_downloads = 0
    
    # Store the results
    download_results = {}
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit all download tasks
        future_to_id = {
            executor.submit(download_image, task_id, url, thumbnails_dir): task_id 
            for task_id, url in download_tasks
        }
        
        # Process completed downloads
        for future in as_completed(future_to_id):
            item_id, local_path, success = future.result()
            download_results[item_id] = local_path
            
            if success:
                successful_downloads += 1
            else:
                failed_downloads += 1
    
    print("=" * 50)
    print(f"Download complete!")
    print(f"✓ Successful: {successful_downloads}")
    print(f"✗ Failed: {failed_downloads}")
    
    # Update the data with local thumbnail paths
    for item in data['data']:
        item_id = item['id']
        if item_id in download_results and download_results[item_id]:
            item['local_thumbnail'] = download_results[item_id]
    
    # Save the updated data
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Updated data.json with local thumbnail paths")
    
    # Create a backup of the original data
    with open('data_backup.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("✓ Created backup at data_backup.json")

if __name__ == "__main__":
    main()