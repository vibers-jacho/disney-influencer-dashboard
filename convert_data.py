#!/usr/bin/env python3
import pandas as pd
import json
import math

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

def main():
    # Read Excel file - check for enhanced version first
    import os
    if os.path.exists('verish_enhanced.xlsx'):
        df = pd.read_excel('verish_enhanced.xlsx', header=1)
        print("Using verish_enhanced.xlsx")
    else:
        df = pd.read_excel('verish.xlsx', header=1)
        print("Using verish.xlsx")
    
    # Convert DataFrame to list of dictionaries
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
            'shares_count': safe_value(row['공유 수']),
            'shares_count_formatted': format_number(row['공유 수']),
            'comments_count': safe_value(row['댓글 수']),
            'comments_count_formatted': format_number(row['댓글 수']),
            'views_count': safe_value(row['조회수']),
            'views_count_formatted': format_number(row['조회수']),
            'video_duration': safe_value(row['영상 길이(초)']),
            'music_title': safe_value(row['음악 제목']),
            'music_artist': safe_value(row['음악 아티스트']),
            'upload_time': str(row['업로드 시간']) if pd.notna(row['업로드 시간']) else None,
            'video_url': safe_value(row['영상 URL']),
            'author_id': safe_value(row['작성자 고유 ID']),
            'thumbnail_url': safe_value(row['영상 썸네일 URL']),
            'follower_tier': safe_value(row['팔로워 Tier'])
        }
        
        # Add email if enhanced file is used
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
        'total_shares': int(df['공유 수'].sum()) if not pd.isna(df['공유 수'].sum()) else 0
    }
    
    # Create final JSON structure
    result = {
        'summary': summary,
        'data': data
    }
    
    # Write to JSON file
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"Successfully converted {len(data)} records to data.json")
    print(f"Total views: {format_number(summary['total_views'])}")
    print(f"Total followers: {format_number(summary['total_followers'])}")
    print(f"Average engagement rate: {summary['avg_engagement_rate']:.2%}")

if __name__ == "__main__":
    main()