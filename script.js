// Global variables
let allData = [];
let filteredData = [];
let currentPage = 1;
let itemsPerPage = 20;
let sortField = '';
let sortOrder = 'desc';
let currentView = 'card';
let currentTierFilter = '';

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
  await loadData();
  setupEventListeners();
  updateView();
});

// Load data from JSON file
async function loadData() {
  try {
    showLoading(true);
    const response = await fetch('data.json');
    const jsonData = await response.json();

    allData = jsonData.data;
    filteredData = [...allData];

    // Update summary
    updateSummary(jsonData.summary);

    showLoading(false);
  } catch (error) {
    console.error('Error loading data:', error);
    showLoading(false);
    alert('데이터를 불러오는 중 오류가 발생했습니다.');
  }
}

// Update summary cards
function updateSummary(summary) {
  document.getElementById('totalInfluencers').textContent =
    summary.total_influencers.toLocaleString();
  document.getElementById('totalViews').textContent = formatNumber(
    summary.total_views
  );
  document.getElementById('totalFollowers').textContent = formatNumber(
    summary.total_followers
  );
  document.getElementById('avgEngagement').textContent =
    (summary.avg_engagement_rate * 100).toFixed(2) + '%';
  document.getElementById('avgCPM').textContent =
    '$' + summary.avg_cpm.toFixed(2);
}

// Setup event listeners
function setupEventListeners() {
  // Search
  document.getElementById('searchBtn').addEventListener('click', performSearch);
  document.getElementById('searchInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') performSearch();
  });
  document.getElementById('clearBtn').addEventListener('click', clearSearch);

  // View toggle
  document.querySelectorAll('.view-btn').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      switchView(e.target.dataset.view);
    });
  });

  // Sorting
  document.getElementById('sortSelect').addEventListener('change', performSort);
  document
    .getElementById('sortOrderBtn')
    .addEventListener('click', toggleSortOrder);
  
  // Tier filter
  document.getElementById('tierFilter').addEventListener('change', (e) => {
    currentTierFilter = e.target.value;
    applyFilters();
  });

  // Table header sorting
  document.querySelectorAll('th.sortable').forEach((th) => {
    th.addEventListener('click', () => {
      sortField = th.dataset.field;
      performSort();
    });
  });

  // Items per page
  document.getElementById('itemsPerPage').addEventListener('change', (e) => {
    itemsPerPage =
      e.target.value === 'all' ? filteredData.length : parseInt(e.target.value);
    currentPage = 1;
    updateView();
  });

  // Modal close
  document.querySelector('.modal .close').addEventListener('click', closeModal);
  document.getElementById('detailModal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closeModal();
  });
  
  // Video modal close
  const videoClose = document.querySelector('.video-close');
  if (videoClose) {
    videoClose.addEventListener('click', closeVideoModal);
  }
  
  // Close video modal on background click
  const videoModal = document.getElementById('videoModal');
  if (videoModal) {
    videoModal.addEventListener('click', (e) => {
      if (e.target === videoModal) {
        closeVideoModal();
      }
    });
  }
}

// Apply all filters (search and tier)
function applyFilters() {
  const searchTerm = document
    .getElementById('searchInput')
    .value.toLowerCase()
    .trim();
  
  // Start with all data
  let filtered = [...allData];
  
  // Apply search filter
  if (searchTerm) {
    filtered = filtered.filter((item) => {
      return (
        (item.author_name &&
          item.author_name.toLowerCase().includes(searchTerm)) ||
        (item.account_id &&
          item.account_id.toLowerCase().includes(searchTerm)) ||
        (item.video_caption &&
          item.video_caption.toLowerCase().includes(searchTerm))
      );
    });
  }
  
  // Apply tier filter
  if (currentTierFilter) {
    filtered = filtered.filter((item) => {
      return item.follower_tier === currentTierFilter;
    });
  }
  
  filteredData = filtered;
  currentPage = 1;
  updateView();
}

// Search functionality
function performSearch() {
  applyFilters();
}

// Clear search
function clearSearch() {
  document.getElementById('searchInput').value = '';
  document.getElementById('tierFilter').value = '';
  currentTierFilter = '';
  filteredData = [...allData];
  currentPage = 1;
  updateView();
}

// Sort functionality
function performSort() {
  const field = document.getElementById('sortSelect').value || sortField;
  if (!field) return;

  sortField = field;

  filteredData.sort((a, b) => {
    let aVal = a[field];
    let bVal = b[field];

    // Handle null/undefined values
    if (aVal == null) return 1;
    if (bVal == null) return -1;

    // Numeric comparison
    if (typeof aVal === 'number' && typeof bVal === 'number') {
      return sortOrder === 'desc' ? bVal - aVal : aVal - bVal;
    }

    // String comparison
    aVal = String(aVal).toLowerCase();
    bVal = String(bVal).toLowerCase();

    if (sortOrder === 'desc') {
      return bVal.localeCompare(aVal);
    } else {
      return aVal.localeCompare(bVal);
    }
  });

  currentPage = 1;
  updateView();
}

// Toggle sort order
function toggleSortOrder() {
  sortOrder = sortOrder === 'desc' ? 'asc' : 'desc';
  document.getElementById('sortOrderBtn').textContent =
    sortOrder === 'desc' ? '↓' : '↑';
  if (sortField) performSort();
}

// Switch view
function switchView(view) {
  currentView = view;

  // Update buttons
  document.querySelectorAll('.view-btn').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.view === view);
  });

  // Update containers
  document
    .getElementById('cardView')
    .classList.toggle('active', view === 'card');
  document
    .getElementById('tableView')
    .classList.toggle('active', view === 'table');

  updateView();
}

// Update current view
function updateView() {
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const pageData = filteredData.slice(startIndex, endIndex);

  if (currentView === 'card') {
    renderCards(pageData);
  } else {
    renderTable(pageData);
  }

  updatePagination();
  updateShowingInfo(startIndex, endIndex);
}

// Render card view
function renderCards(data) {
  const container = document.getElementById('cardsContainer');
  container.innerHTML = '';

  data.forEach((item) => {
    const card = document.createElement('div');
    card.className = 'influencer-card';
    card.innerHTML = `
            <div class="card-image">
                ${
                  item.thumbnail_url
                    ? `<img src="${item.thumbnail_url}" alt="${item.author_name}" loading="lazy" onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2VlZSIvPjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjEwMCIgeT0iMTAwIiBzdHlsZT0iZmlsbDojYWFhO2ZvbnQtd2VpZ2h0OmJvbGQ7Zm9udC1zaXplOjEycHg7Zm9udC1mYW1pbHk6QXJpYWwsc2Fucy1zZXJpZjsiPk5vIEltYWdlPC90ZXh0Pjwvc3ZnPg=='">`
                    : `<div class="no-image">No Image</div>`
                }
            </div>
            <div class="card-content">
                <h3 class="card-title">${item.author_name || 'Unknown'}</h3>
                <p class="card-account">@${item.account_id || 'unknown'}</p>
                ${
                  item.email
                    ? `<div class="email-container">
                        <p class="card-email">${item.email}</p>
                        <button class="copy-email-btn" onclick="copyEmail('${item.email}', event)" title="이메일 복사">📋</button>
                    </div>`
                    : `<p class="card-email no-email">📧 이메일 없음</p>`
                }
                
                <div class="card-stats">
                    <div class="stat">
                        <span class="stat-label">팔로워</span>
                        <span class="stat-value">${
                          item.follower_count_formatted || '0'
                        }</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">조회수</span>
                        <span class="stat-value">${
                          item.views_count_formatted || '0'
                        }</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">참여율</span>
                        <span class="stat-value">${
                          item.engagement_rate
                            ? (item.engagement_rate * 100).toFixed(2) + '%'
                            : 'N/A'
                        }</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">CPM</span>
                        <span class="stat-value">${
                          item.estimated_cpm
                            ? '$' + item.estimated_cpm.toFixed(0)
                            : 'N/A'
                        }</span>
                    </div>
                </div>
                
                <div class="card-caption">${truncateText(
                  item.video_caption,
                  100
                )}</div>
                
                <div class="card-actions">
                    ${
                      item.video_url
                        ? `<button onclick="showVideo('${item.video_url}', event)" class="btn-link">동영상 보기</button>
                           <a href="${item.video_url}" target="_blank" class="btn-external">↗</a>`
                        : ''
                    }
                    <button class="btn-detail" onclick="showDetailById(${
                      item.id
                    })">상세 정보</button>
                </div>
            </div>
        `;
    container.appendChild(card);
  });
}

// Render table view
function renderTable(data) {
  const tbody = document.getElementById('tableBody');
  tbody.innerHTML = '';

  data.forEach((item) => {
    const row = document.createElement('tr');
    row.innerHTML = `
            <td>${item.id || '-'}</td>
            <td class="thumbnail-cell">
                ${
                  item.thumbnail_url
                    ? `<img src="${item.thumbnail_url}" alt="${item.author_name}" loading="lazy" onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTAiIGhlaWdodD0iNTAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjUwIiBoZWlnaHQ9IjUwIiBmaWxsPSIjZWVlIi8+PHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD9IjI1IiB5PSIyNSIgc3R5bGU9ImZpbGw6I2FhYTtmb250LXNpemU6OHB4O2ZvbnQtZmFtaWx5OkFyaWFsLHNhbnMtc2VyaWY7Ij5OQTwvdGV4dD48L3N2Zz4='">`
                    : '<span class="no-thumb">N/A</span>'
                }
            </td>
            <td>${item.author_name || '-'}</td>
            <td>@${item.account_id || '-'}</td>
            <td class="text-right">${item.follower_count_formatted || '0'}</td>
            <td class="text-right">${item.views_count_formatted || '0'}</td>
            <td class="text-right">${item.likes_count_formatted || '0'}</td>
            <td class="text-right">${
              item.engagement_rate
                ? (item.engagement_rate * 100).toFixed(2) + '%'
                : '-'
            }</td>
            <td class="text-right">${
              item.estimated_cpm ? '$' + item.estimated_cpm.toFixed(0) : '-'
            }</td>
            <td>
                ${
                  item.video_url
                    ? `<button class="btn-detail-small" onclick="showVideo('${item.video_url}', event)" title="동영상 보기">🎬</button>
                       <a href="${item.video_url}" target="_blank" class="link-icon" title="TikTok에서 열기">↗</a>`
                    : ''
                }
                <button class="btn-detail-small" onclick="showDetailById(${
                  item.id
                })" title="상세 정보">📋</button>
            </td>
        `;
    tbody.appendChild(row);
  });
}

// Pagination
function updatePagination() {
  const totalPages = Math.ceil(filteredData.length / itemsPerPage);
  const paginationDiv = document.getElementById('pagination');
  paginationDiv.innerHTML = '';

  if (totalPages <= 1) return;

  // Previous button
  const prevBtn = document.createElement('button');
  prevBtn.textContent = '이전';
  prevBtn.disabled = currentPage === 1;
  prevBtn.addEventListener('click', () => {
    if (currentPage > 1) {
      currentPage--;
      updateView();
    }
  });
  paginationDiv.appendChild(prevBtn);

  // Page numbers
  const maxButtons = 7;
  let startPage = Math.max(1, currentPage - Math.floor(maxButtons / 2));
  let endPage = Math.min(totalPages, startPage + maxButtons - 1);

  if (endPage - startPage < maxButtons - 1) {
    startPage = Math.max(1, endPage - maxButtons + 1);
  }

  if (startPage > 1) {
    addPageButton(1);
    if (startPage > 2) {
      const dots = document.createElement('span');
      dots.textContent = '...';
      dots.className = 'page-dots';
      paginationDiv.appendChild(dots);
    }
  }

  for (let i = startPage; i <= endPage; i++) {
    addPageButton(i);
  }

  if (endPage < totalPages) {
    if (endPage < totalPages - 1) {
      const dots = document.createElement('span');
      dots.textContent = '...';
      dots.className = 'page-dots';
      paginationDiv.appendChild(dots);
    }
    addPageButton(totalPages);
  }

  // Next button
  const nextBtn = document.createElement('button');
  nextBtn.textContent = '다음';
  nextBtn.disabled = currentPage === totalPages;
  nextBtn.addEventListener('click', () => {
    if (currentPage < totalPages) {
      currentPage++;
      updateView();
    }
  });
  paginationDiv.appendChild(nextBtn);

  function addPageButton(pageNum) {
    const btn = document.createElement('button');
    btn.textContent = pageNum;
    btn.className = pageNum === currentPage ? 'active' : '';
    btn.addEventListener('click', () => {
      currentPage = pageNum;
      updateView();
    });
    paginationDiv.appendChild(btn);
  }
}

// Update showing info
function updateShowingInfo(start, end) {
  const actualEnd = Math.min(end, filteredData.length);
  document.getElementById('showingInfo').textContent = `표시 중: ${
    start + 1
  }-${actualEnd} / ${filteredData.length}`;
}

// Show detail modal by ID
function showDetailById(id) {
  const item = filteredData.find((i) => i.id === id);
  if (!item) return;

  const modalBody = document.getElementById('modalBody');
  modalBody.innerHTML = `
        <div class="modal-header">
            <h2>${item.author_name || 'Unknown'}</h2>
            <p class="modal-account">@${item.account_id || 'unknown'}</p>
        </div>
        
        <div class="modal-image">
            ${
              item.thumbnail_url
                ? `<img src="${item.thumbnail_url}" alt="${item.author_name}">`
                : '<div class="no-image-large">No Image Available</div>'
            }
        </div>
        
        <div class="modal-info">
            <h3>프로필 소개</h3>
            <p>${item.profile_intro || 'N/A'}</p>
            
            <h3>영상 설명</h3>
            <p>${item.video_caption || 'N/A'}</p>
            
            <h3>상세 통계</h3>
            <div class="detail-stats">
                <div class="detail-stat">
                    <span>팔로워 수:</span>
                    <strong>${item.follower_count_formatted || '0'}</strong>
                </div>
                <div class="detail-stat">
                    <span>조회수:</span>
                    <strong>${item.views_count_formatted || '0'}</strong>
                </div>
                <div class="detail-stat">
                    <span>좋아요:</span>
                    <strong>${item.likes_count_formatted || '0'}</strong>
                </div>
                <div class="detail-stat">
                    <span>댓글:</span>
                    <strong>${item.comments_count_formatted || '0'}</strong>
                </div>
                <div class="detail-stat">
                    <span>공유:</span>
                    <strong>${item.shares_count_formatted || '0'}</strong>
                </div>
                <div class="detail-stat">
                    <span>참여율:</span>
                    <strong>${
                      item.engagement_rate
                        ? (item.engagement_rate * 100).toFixed(3) + '%'
                        : 'N/A'
                    }</strong>
                </div>
                <div class="detail-stat">
                    <span>조회수 비율:</span>
                    <strong>${item.view_ratio ? item.view_ratio.toFixed(2) + '%' : 'N/A'}</strong>
                </div>
                <div class="detail-stat">
                    <span>댓글 전환율:</span>
                    <strong>${
                      item.comment_conversion
                        ? (item.comment_conversion * 100).toFixed(3) + '%'
                        : 'N/A'
                    }</strong>
                </div>
                <div class="detail-stat">
                    <span>팔로워 품질:</span>
                    <strong>${
                      item.follower_quality
                        ? item.follower_quality.toFixed(2)
                        : 'N/A'
                    }</strong>
                </div>
                <div class="detail-stat">
                    <span>예상 CPM:</span>
                    <strong>${
                      item.estimated_cpm
                        ? '$' + item.estimated_cpm.toFixed(2)
                        : 'N/A'
                    }</strong>
                </div>
                <div class="detail-stat">
                    <span>비용 효율:</span>
                    <strong>${
                      item.cost_efficiency
                        ? item.cost_efficiency.toFixed(3)
                        : 'N/A'
                    }</strong>
                </div>
                <div class="detail-stat">
                    <span>업로드 영상 수:</span>
                    <strong>${item.upload_count || '0'}</strong>
                </div>
                <div class="detail-stat">
                    <span>영상 길이:</span>
                    <strong>${
                      item.video_duration ? item.video_duration + '초' : 'N/A'
                    }</strong>
                </div>
                <div class="detail-stat">
                    <span>음악:</span>
                    <strong>${item.music_title || 'N/A'} ${
    item.music_artist ? '- ' + item.music_artist : ''
  }</strong>
                </div>
                <div class="detail-stat">
                    <span>업로드 시간:</span>
                    <strong>${item.upload_time || 'N/A'}</strong>
                </div>
                <div class="detail-stat">
                    <span>팔로워 Tier:</span>
                    <strong>${item.follower_tier || 'N/A'}</strong>
                </div>
                <div class="detail-stat">
                    <span>이메일:</span>
                    <strong>
                        ${item.email || '이메일 없음'}
                        ${
                          item.email
                            ? `<button class="copy-email-btn-small" onclick="copyEmail('${item.email}', event)" title="이메일 복사">📋</button>`
                            : ''
                        }
                    </strong>
                </div>
            </div>
            
            ${
              item.video_url
                ? `<div class="modal-actions">
                    <button onclick="showVideo('${item.video_url}', event)" class="btn-primary">동영상 보기</button>
                    <a href="${item.video_url}" target="_blank" class="btn-primary btn-secondary">TikTok에서 열기</a>
                </div>`
                : ''
            }
        </div>
    `;

  document.getElementById('detailModal').style.display = 'block';
}

// Close modal
function closeModal() {
  document.getElementById('detailModal').style.display = 'none';
}

// Helper functions
function formatNumber(num) {
  if (!num) return '0';
  if (num >= 1000000000) return (num / 1000000000).toFixed(1) + 'B';
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
  return num.toString();
}

function truncateText(text, maxLength) {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

function showLoading(show) {
  document.getElementById('loadingIndicator').style.display = show
    ? 'flex'
    : 'none';
}

// Copy email to clipboard
function copyEmail(email, event) {
  event.stopPropagation();

  navigator.clipboard
    .writeText(email)
    .then(() => {
      // Show success feedback
      const button = event.target;
      const originalText = button.textContent;
      button.textContent = '✅';
      button.classList.add('copied');

      setTimeout(() => {
        button.textContent = originalText;
        button.classList.remove('copied');
      }, 2000);
    })
    .catch((err) => {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = email;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      document.body.appendChild(textArea);
      textArea.select();

      try {
        document.execCommand('copy');
        // Show success feedback
        const button = event.target;
        const originalText = button.textContent;
        button.textContent = '✅';
        button.classList.add('copied');

        setTimeout(() => {
          button.textContent = originalText;
          button.classList.remove('copied');
        }, 2000);
      } catch (err) {
        console.error('Failed to copy email:', err);
        alert('이메일 복사 실패');
      }

      document.body.removeChild(textArea);
    });
}

// Show TikTok video in modal
function showVideo(videoUrl, event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    // Extract video ID from URL
    const videoIdMatch = videoUrl.match(/video\/(\d+)/);
    if (!videoIdMatch) {
        alert('Invalid TikTok video URL');
        return;
    }
    
    const videoId = videoIdMatch[1];
    
    // Extract username from URL
    const usernameMatch = videoUrl.match(/@([^\/]+)/);
    const username = usernameMatch ? usernameMatch[1] : 'user';
    
    // Create TikTok embed
    const embedHtml = `
        <blockquote class="tiktok-embed" 
            cite="${videoUrl}"
            data-video-id="${videoId}"
            style="max-width: 605px; min-width: 325px; margin: 0 auto;">
            <section>
                <a target="_blank" title="@${username}" href="https://www.tiktok.com/@${username}">@${username}</a>
            </section>
        </blockquote>
    `;
    
    // Insert embed into modal
    document.getElementById('videoModalBody').innerHTML = embedHtml;
    
    // Show modal
    document.getElementById('videoModal').style.display = 'block';
    
    // Reload TikTok embed script to render the new video
    if (window.tiktok && window.tiktok.embed) {
        window.tiktok.embed.reload();
    } else {
        // Fallback: reload the script
        const script = document.createElement('script');
        script.src = 'https://www.tiktok.com/embed.js';
        script.async = true;
        document.body.appendChild(script);
    }
}

// Close video modal
function closeVideoModal() {
    document.getElementById('videoModal').style.display = 'none';
    document.getElementById('videoModalBody').innerHTML = '';
}
