# Influencer Data Visualization Dashboard

An interactive web application for visualizing and analyzing influencer data from TikTok.

## Features

- 📊 **Dual View Modes**: Switch between card gallery and table views
- 🖼️ **Thumbnail Display**: Video thumbnails with automatic fallback
- 🔍 **Search & Filter**: Find influencers by name, account, or caption
- 📈 **Sorting**: Sort by followers, views, engagement rate, CPM, and more
- 📧 **Email Management**: Copy emails to clipboard with visual feedback
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile
- 🇰🇷 **Korean Language Support**: Full Korean interface

## Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Data Processing**: Python (pandas)
- **Deployment**: Vercel
- **Data Format**: JSON (converted from Excel)

## Local Development

1. Install Python 3.x
2. Install pandas: `pip install pandas openpyxl`
3. Run the converter: `python3 convert_data.py`
4. Start local server: `python3 -m http.server 8000`
5. Open browser: `http://localhost:8000`

## Data Structure

The application processes Excel files with the following columns:
- Influencer profile information
- Engagement metrics (views, likes, comments, shares)
- Financial metrics (CPM, cost efficiency)
- Content details (video URL, thumbnail, caption)
- Contact information (email)

## Deployment

This project is configured for easy deployment on Vercel:

1. Push to GitHub
2. Connect repository to Vercel
3. Deploy with zero configuration

## File Structure

```
├── index.html          # Main HTML page
├── styles.css          # Styling
├── script.js           # Interactive functionality
├── convert_data.py     # Excel to JSON converter
├── data.json           # Processed data
├── vercel.json         # Vercel configuration
└── package.json        # Project metadata
```

## Statistics

- **Total Influencers**: 265
- **Total Views**: 244.4M
- **Total Followers**: 187.7M
- **Average Engagement**: 5.89%

## License

MIT