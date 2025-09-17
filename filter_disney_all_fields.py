import pandas as pd

# Read the URLs from reels.txt
reel_urls = []
with open('reels.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if line and 'instagram.com' in line:
            # Extract the URL part (after the tab character)
            parts = line.split('\t')
            if len(parts) > 1:
                reel_urls.append(parts[1])
            else:
                # If no tab, try to extract the URL directly
                if 'https://' in line:
                    url_start = line.find('https://')
                    reel_urls.append(line[url_start:])

print(f"Found {len(reel_urls)} URLs in reels.txt")

# Read the Excel file
df = pd.read_excel('disney_all_fields.xlsx')
print(f"\nOriginal Excel file shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# Check which column contains URLs - try multiple possible column names
possible_url_columns = ['url', 'URL', 'link', 'Link', 'post_url', 'postUrl', 'instagram_url', 'ig_url']
url_column = None

# First check for exact column name matches
for col_name in possible_url_columns:
    if col_name in df.columns:
        url_column = col_name
        print(f"\nFound URL column by name: '{url_column}'")
        break

# If no exact match, check columns that contain Instagram URLs
if url_column is None:
    for col in df.columns:
        if df[col].dtype == 'object':
            sample = df[col].dropna().head(5).astype(str)
            if sample.str.contains('instagram.com/p/', case=False).any():
                url_column = col
                print(f"\nFound URL column by content: '{url_column}'")
                break

if url_column is None:
    print("\nNo URL column found. Here are all columns:")
    for col in df.columns:
        print(f"  - {col}")
    print("\nFirst few rows of the dataframe:")
    print(df.head())
else:
    print(f"\nUsing column '{url_column}' for filtering")

    # Show sample of URLs from Excel
    print(f"\nSample of URLs from Excel file (first 5):")
    excel_urls = df[url_column].dropna().head(5)
    for i, url in enumerate(excel_urls):
        print(f"  {i+1}. {url}")

    # Show sample of URLs from reels.txt
    print(f"\nSample of URLs from reels.txt (first 5):")
    for i, url in enumerate(reel_urls[:5]):
        print(f"  {i+1}. {url}")

    # Create a set for faster lookup
    reel_urls_set = set(reel_urls)

    # Filter the dataframe - first try exact match
    filtered_df = df[df[url_column].isin(reel_urls_set)]

    print(f"\nFiltered dataframe shape (exact match): {filtered_df.shape}")
    print(f"Kept {len(filtered_df)} rows out of {len(df)} total rows")

    # If no exact matches, try partial matching with post IDs
    if filtered_df.empty:
        print("\nNo exact matches found. Checking for partial matches...")

        # Extract post IDs from reels.txt URLs
        reel_post_ids = set()
        for url in reel_urls:
            if '/p/' in url:
                post_id = url.split('/p/')[1].rstrip('/')
                reel_post_ids.add(post_id)

        print(f"Found {len(reel_post_ids)} post IDs from reels.txt")
        print(f"Sample post IDs: {list(reel_post_ids)[:5]}")

        # Filter by post IDs
        mask = df[url_column].apply(lambda x: any(post_id in str(x) for post_id in reel_post_ids) if pd.notna(x) else False)
        filtered_df = df[mask]

        print(f"Filtered dataframe shape (partial match): {filtered_df.shape}")

    # Save the filtered dataframe to a new Excel file
    output_file = 'disney_all_fields_filtered.xlsx'
    filtered_df.to_excel(output_file, index=False)
    print(f"\nFiltered data saved to: {output_file}")

    # Show column names and sample of filtered data
    if not filtered_df.empty:
        print(f"\nColumns in filtered data: {list(filtered_df.columns)}")
        print(f"\nSample of filtered data (first 3 rows):")
        # Show just a few key columns if they exist
        key_cols = [url_column]
        for col in ['ownerUsername', 'username', 'caption', 'description', 'text']:
            if col in filtered_df.columns:
                key_cols.append(col)

        if len(key_cols) > 1:
            print(filtered_df[key_cols].head(3))
        else:
            print(filtered_df.head(3))