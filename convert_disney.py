#!/usr/bin/env python3
import pandas as pd
import json
import math
import os

def safe_value(val):
    """Convert NaN and inf values to None for JSON serialization"""
    if pd.isna(val) or (isinstance(val, float) and math.isinf(val)):
        return None
    return val

def format_number(num):
    """Format large numbers for display"""
    if pd.isna(num):
        return None
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(int(num))

def process_disney_data():
    """Process Disney Excel file and return structured data"""
    print(f"Processing disney.xlsx...")

    df = pd.read_excel('disney.xlsx', header=1)
    data = []

    for index, row in df.iterrows():
        record = {
            'id': safe_value(row['번호']),
            'author_name': safe_value(row['작성자 이름']),
            'account_id': safe_value(row['아이디(@계정)']),
            'profile_intro': safe_value(row['프로필 소개글']),
            'video_caption': safe_value(row['영상 설명(캡션)']),
            'engagement_rate': safe_value(row['참여율']),
            'view_ratio': safe_value(row['조회수 비율']),
            'comment_conversion': safe_value(row['댓글 전환율']),
            'follower_quality': safe_value(row['팔로워 품질']),
            'estimated_cpm': safe_value(row['예상 CPM($)']),
            'cost_efficiency': safe_value(row['비용 효율']),
            'follower_count': safe_value(row['팔로워 수']),
            'follower_count_formatted': format_number(row['팔로워 수']),
            'upload_count': safe_value(row['업로드 영상 수']),
            'likes_count': safe_value(row['좋아요 수']),
            'likes_count_formatted': format_number(row['좋아요 수']),
            'comments_count': safe_value(row['댓글 수']),
            'comments_count_formatted': format_number(row['댓글 수']),
            'views_count': safe_value(row['조회수']),
            'views_count_formatted': format_number(row['조회수']),
            'video_duration': safe_value(row['영상 길이(초)']),
            'video_url': safe_value(row['영상 URL']),
            'author_id': safe_value(row['작성자 고유 ID']),
            'thumbnail_url': safe_value(row['영상 썸네일 URL']),
            'follower_tier': safe_value(row['팔로워 Tier']),
            # Fields that don't exist in Disney data - set to None
            'shares_count': None,
            'shares_count_formatted': None,
            'music_title': None,
            'music_artist': None,
            'upload_time': None
        }

        # Add email if available
        if '이메일 추출' in row.index:
            email_val = safe_value(row['이메일 추출'])
            # Check if email is "2.이메일 없음" and convert to None
            if email_val == '2.이메일 없음':
                record['email'] = None
            else:
                record['email'] = email_val
        else:
            record['email'] = None

        # Add priority if available
        if '우선순위' in row.index:
            record['priority'] = safe_value(row['우선순위'])

        # Add profile entry if available
        if '프로필 진입' in row.index:
            record['profile_entry'] = safe_value(row['프로필 진입'])

        data.append(record)

    # Calculate summary statistics
    summary = {
        'total_influencers': len(data),
        'total_views': int(df['조회수'].sum()) if not pd.isna(df['조회수'].sum()) else 0,
        'total_followers': int(df['팔로워 수'].sum()) if not pd.isna(df['팔로워 수'].sum()) else 0,
        'avg_engagement_rate': float(df['참여율'].mean()) if not pd.isna(df['참여율'].mean()) else 0,
        'avg_cpm': float(df['예상 CPM($)'].mean()) if not pd.isna(df['예상 CPM($)'].mean()) else 0,
        'total_likes': int(df['좋아요 수'].sum()) if not pd.isna(df['좋아요 수'].sum()) else 0,
        'total_comments': int(df['댓글 수'].sum()) if not pd.isna(df['댓글 수'].sum()) else 0,
        'total_shares': 0  # Disney data doesn't have shares
    }

    return data, summary

def main():
    # Process Disney data
    disney_data, disney_summary = process_disney_data()
    print(f"Processed {len(disney_data)} Disney influencers")

    # Create final JSON structure with single summary (no types)
    result = {
        'summary': disney_summary,  # Single summary, no type breakdown
        'data': disney_data
    }

    # Write to JSON file
    with open('data_combined.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    print(f"\nSuccessfully converted {len(disney_data)} records to data_combined.json")
    print(f"Total views: {format_number(disney_summary['total_views'])}")
    print(f"Total followers: {format_number(disney_summary['total_followers'])}")
    print(f"Average engagement rate: {disney_summary['avg_engagement_rate']:.2%}")
    print(f"Average CPM: ${disney_summary['avg_cpm']:.2f}")

if __name__ == "__main__":
    main()