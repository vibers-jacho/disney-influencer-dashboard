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
df = pd.read_excel('disney_scraped.xlsx')
print(f"\nOriginal Excel file shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# Check which column contains URLs
url_columns = []
for col in df.columns:
    if df[col].dtype == 'object':
        sample = df[col].dropna().head(5).astype(str)
        if sample.str.contains('instagram.com', case=False).any():
            url_columns.append(col)
            print(f"\nFound URL column: '{col}'")
            print(f"Sample values:")
            print(sample.tolist())

if not url_columns:
    print("\nNo URL column found. Checking all columns for Instagram URLs...")
    print("\nFirst few rows of the dataframe:")
    print(df.head())
else:
    # Use the 'url' column which contains the Instagram post URLs
    url_column = 'url' if 'url' in url_columns else url_columns[0]
    print(f"\nUsing column '{url_column}' for filtering")

    # Show sample of reel URLs for debugging
    print(f"\nSample of URLs from reels.txt (first 5):")
    for i, url in enumerate(reel_urls[:5]):
        print(f"  {i+1}. {url}")

    # Show sample of Excel URLs for debugging
    print(f"\nSample of URLs from Excel file (first 5):")
    excel_urls = df[url_column].dropna().head(5)
    for i, url in enumerate(excel_urls):
        print(f"  {i+1}. {url}")

    # Create a set for faster lookup
    reel_urls_set = set(reel_urls)

    # Filter the dataframe
    filtered_df = df[df[url_column].isin(reel_urls_set)]

    print(f"\nFiltered dataframe shape: {filtered_df.shape}")
    print(f"Kept {len(filtered_df)} rows out of {len(df)} total rows")

    # If no exact matches, try checking for partial matches
    if filtered_df.empty:
        print("\nNo exact matches found. Checking for partial matches...")
        # Extract the post ID from URLs (the part between /p/ and /)
        reel_post_ids = set()
        for url in reel_urls:
            if '/p/' in url:
                post_id = url.split('/p/')[1].rstrip('/')
                reel_post_ids.add(post_id)

        print(f"Found {len(reel_post_ids)} post IDs from reels.txt")

        # Filter by post IDs
        mask = df[url_column].apply(lambda x: any(post_id in str(x) for post_id in reel_post_ids) if pd.notna(x) else False)
        filtered_df = df[mask]

        print(f"Filtered dataframe shape after partial match: {filtered_df.shape}")

    # Save the filtered dataframe to a new Excel file
    output_file = 'disney_filtered.xlsx'
    filtered_df.to_excel(output_file, index=False)
    print(f"\nFiltered data saved to: {output_file}")

    # Show a sample of the filtered data
    if not filtered_df.empty:
        print(f"\nSample of filtered data (first 5 rows):")
        print(filtered_df[['url', 'ownerUsername', 'caption']].head() if 'caption' in filtered_df.columns else filtered_df.head())