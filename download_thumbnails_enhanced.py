#!/usr/bin/env python3
import json
import os
import requests
from urllib.parse import urlparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_image(item_id, url, influencer_type):
    """Download a single image and save it locally in type-specific folder"""
    try:
        # Determine the output directory based on influencer type
        if influencer_type == 'sales':
            output_dir = 'thumbnails_sales'
            relative_path = f"thumbnails_sales/{item_id}.jpg"
        else:
            output_dir = 'thumbnails_regular'
            relative_path = f"thumbnails_regular/{item_id}.jpg"
        
        # Create the output filename
        output_path = os.path.join(output_dir, f"{item_id}.jpg")
        
        # Skip if already downloaded
        if os.path.exists(output_path):
            print(f"✓ [{influencer_type}] Image {item_id} already exists, skipping")
            return item_id, relative_path, True, influencer_type
        
        # Download the image
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        # Save the image
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ [{influencer_type}] Downloaded image for ID {item_id}")
        return item_id, relative_path, True, influencer_type
        
    except Exception as e:
        print(f"✗ [{influencer_type}] Failed to download image for ID {item_id}: {str(e)}")
        return item_id, None, False, influencer_type

def main():
    # Load the combined data
    with open('data_combined.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create separate thumbnails directories if they don't exist
    os.makedirs('thumbnails_regular', exist_ok=True)
    os.makedirs('thumbnails_sales', exist_ok=True)
    
    # Prepare download tasks separated by type
    regular_tasks = []
    sales_tasks = []
    
    for item in data['data']:
        if item.get('thumbnail_url'):
            task = (item['id'], item['thumbnail_url'], item.get('influencer_type', 'unknown'))
            if item.get('influencer_type') == 'sales':
                sales_tasks.append(task)
            else:
                regular_tasks.append(task)
    
    print(f"Found {len(regular_tasks)} regular influencer images to download")
    print(f"Found {len(sales_tasks)} sales influencer images to download")
    print("=" * 50)
    
    # Download images in parallel (max 10 concurrent downloads)
    successful_regular = 0
    failed_regular = 0
    successful_sales = 0
    failed_sales = 0
    
    # Store the results
    download_results = {}
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit all download tasks
        future_to_id = {}
        
        # Add all tasks
        for task_id, url, inf_type in regular_tasks + sales_tasks:
            future = executor.submit(download_image, task_id, url, inf_type)
            future_to_id[future] = task_id
        
        # Process completed downloads
        for future in as_completed(future_to_id):
            item_id, local_path, success, inf_type = future.result()
            download_results[item_id] = local_path
            
            if success:
                if inf_type == 'sales':
                    successful_sales += 1
                else:
                    successful_regular += 1
            else:
                if inf_type == 'sales':
                    failed_sales += 1
                else:
                    failed_regular += 1
    
    print("=" * 50)
    print(f"Download complete!")
    print(f"Regular Influencers:")
    print(f"  ✓ Successful: {successful_regular}")
    print(f"  ✗ Failed: {failed_regular}")
    print(f"Sales Influencers:")
    print(f"  ✓ Successful: {successful_sales}")
    print(f"  ✗ Failed: {failed_sales}")
    print(f"Total:")
    print(f"  ✓ Successful: {successful_regular + successful_sales}")
    print(f"  ✗ Failed: {failed_regular + failed_sales}")
    
    # Update the data with local thumbnail paths
    for item in data['data']:
        item_id = item['id']
        if item_id in download_results and download_results[item_id]:
            item['local_thumbnail'] = download_results[item_id]
    
    # Save the updated data
    with open('data_combined.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Updated data_combined.json with local thumbnail paths")
    
    # Create a backup of the combined data
    with open('data_combined_backup.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("✓ Created backup at data_combined_backup.json")

if __name__ == "__main__":
    main()