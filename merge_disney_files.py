import pandas as pd

# Read both Excel files
print("Reading disney_profile.xlsx...")
df_profile = pd.read_excel('disney_profile.xlsx')
print(f"Profile data shape: {df_profile.shape}")
print(f"Profile columns: {list(df_profile.columns)}")

print("\nReading disney_filtered.xlsx...")
df_filtered = pd.read_excel('disney_filtered.xlsx')
print(f"Filtered data shape: {df_filtered.shape}")
print(f"Filtered columns: {list(df_filtered.columns)}")

# Check for username columns
if 'username' in df_profile.columns:
    print(f"\nFound 'username' column in disney_profile.xlsx")
    print(f"Sample usernames from profile: {df_profile['username'].head().tolist()}")
else:
    print("\nWarning: 'username' column not found in disney_profile.xlsx")
    print("Available columns:", list(df_profile.columns))

if 'ownerUsername' in df_filtered.columns:
    print(f"\nFound 'ownerUsername' column in disney_filtered.xlsx")
    print(f"Sample ownerUsernames from filtered: {df_filtered['ownerUsername'].head().tolist()}")
else:
    print("\nWarning: 'ownerUsername' column not found in disney_filtered.xlsx")
    print("Available columns:", list(df_filtered.columns))

# Perform the merge
if 'username' in df_profile.columns and 'ownerUsername' in df_filtered.columns:
    print("\n--- Performing merge ---")

    # Show unique counts before merge
    print(f"Unique usernames in profile: {df_profile['username'].nunique()}")
    print(f"Unique ownerUsernames in filtered: {df_filtered['ownerUsername'].nunique()}")

    # Merge the dataframes
    # Using left join to keep all posts from filtered data and add profile info where available
    merged_df = df_filtered.merge(
        df_profile,
        left_on='ownerUsername',
        right_on='username',
        how='left',
        suffixes=('_post', '_profile')
    )

    print(f"\nMerged data shape: {merged_df.shape}")
    print(f"Number of posts with matching profiles: {merged_df['username'].notna().sum()}")
    print(f"Number of posts without matching profiles: {merged_df['username'].isna().sum()}")

    # Save the merged data
    output_file = 'disney_merged.xlsx'
    merged_df.to_excel(output_file, index=False)
    print(f"\nMerged data saved to: {output_file}")

    # Show sample of merged data
    print("\n--- Sample of merged data ---")
    # Select key columns to display
    display_cols = []
    for col in ['url', 'ownerUsername', 'username', 'caption']:
        if col in merged_df.columns:
            display_cols.append(col)

    # Add some profile columns if they exist
    for col in df_profile.columns:
        if col not in ['username'] and col in merged_df.columns and len(display_cols) < 8:
            display_cols.append(col)

    if display_cols:
        print(merged_df[display_cols].head(3))
    else:
        print(merged_df.head(3))

    # Alternative merge using inner join to see only matching records
    print("\n--- Alternative: Inner join (only matching records) ---")
    inner_merged_df = df_filtered.merge(
        df_profile,
        left_on='ownerUsername',
        right_on='username',
        how='inner',
        suffixes=('_post', '_profile')
    )

    print(f"Inner join result shape: {inner_merged_df.shape}")

    # Save the inner join version as well
    inner_output_file = 'disney_merged_inner.xlsx'
    inner_merged_df.to_excel(inner_output_file, index=False)
    print(f"Inner join data saved to: {inner_output_file}")

else:
    print("\nError: Required columns not found for merge operation")