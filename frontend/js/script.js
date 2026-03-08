// script.js - Client interactions and dynamic data fetching

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initTabs();
    loadLatestNews(); // Fetch real JSON instead of mockups
});

// 1. Theme Toggle Logic
function initTheme() {
    const toggleBtn = document.getElementById('theme-toggle');
    const htmlEl = document.documentElement;
    const svgIcon = toggleBtn.querySelector('use');

    if (!htmlEl.getAttribute('data-theme')) {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        htmlEl.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    }

    const updateIcon = () => {
        if (htmlEl.getAttribute('data-theme') === 'dark') {
            svgIcon.setAttribute('href', '#icon-sun');
        } else {
            svgIcon.setAttribute('href', '#icon-moon');
        }
    };
    
    updateIcon();

    toggleBtn.addEventListener('click', () => {
        const currentTheme = htmlEl.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        htmlEl.setAttribute('data-theme', newTheme);
        updateIcon();
    });
}

// 2. Accordion Card Toggle Logic
function toggleAccordion(headerElement) {
    const card = headerElement.parentElement;
    const isExpanded = card.classList.contains('expanded');
    
    if (isExpanded) {
        card.classList.remove('expanded');
    } else {
        card.classList.add('expanded');
    }
}

// 3. Tab Navigation Logic
function initTabs() {
    const navBtns = document.querySelectorAll('.nav-btn');

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            navBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const targetId = btn.getAttribute('data-target');
            document.querySelectorAll('.news-list').forEach(list => {
                list.classList.add('hidden');
            });
            document.getElementById(targetId).classList.remove('hidden');
        });
    });
}

// 4. Dynamic Data Fetching (Wiring)
function setLoadingState(isLoading) {
    const viewDaily = document.getElementById('view-daily');
    const loadingView = document.getElementById('loading-view');

    if (isLoading) {
        viewDaily.classList.add('hidden');
        loadingView.classList.remove('hidden');
    } else {
        loadingView.classList.add('hidden');
        if (document.querySelector('.nav-btn.active').getAttribute('data-target') === 'view-daily') {
            viewDaily.classList.remove('hidden');
        }
    }
}

async function loadLatestNews() {
    setLoadingState(true);
    try {
        const indexRes = await fetch('data/index.json');
        if (!indexRes.ok) throw new Error('Failed to load indices');
        const indexData = await indexRes.json();
        
        if (indexData.available_dates && indexData.available_dates.length > 0) {
            const latestDate = indexData.available_dates[0];
            document.getElementById('view-title').textContent = `Latest AI News (${latestDate})`;
            
            const dailyRes = await fetch(`data/daily/${latestDate}.json`);
            if (dailyRes.ok) {
                const articles = await dailyRes.json();
                renderDailyNews(articles);
                return;
            }
        }
        renderEmptyState();
    } catch (error) {
        console.error('Data Fetch Error:', error);
        renderEmptyState();
    } finally {
        setLoadingState(false);
    }
}

function renderDailyNews(articles) {
    const list = document.getElementById('view-daily');
    list.innerHTML = ''; // Selectively clear mockup data entirely
    
    if (!articles || articles.length === 0) {
        renderEmptyState();
        return;
    }
    
    articles.forEach(a => {
        let tagsHtml = '';
        if (a.ai_tags && a.ai_tags.length > 0) {
            a.ai_tags.forEach(t => {
                tagsHtml += `<span class="tag tag-tech">#${t}</span>`;
            });
        }
        
        // Use regex strictly to parse or format date if needed, fallback to raw DB text
        let dateStr = a.published_date.split('T')[0] || a.published_date;

        const articleHtml = `
            <article class="news-card">
                <div class="card-header" onclick="toggleAccordion(this)">
                    <h3>${escapeHtml(a.title)}</h3>
                    <div class="card-meta">${escapeHtml(a.source)} • ${escapeHtml(dateStr)}</div>
                    <div class="card-tags">${tagsHtml}</div>
                    <svg class="expand-icon" width="20" height="20">
                        <use href="#icon-chevron-down"></use>
                    </svg>
                </div>
                <div class="card-body">
                    <p>${escapeHtml(a.ai_summary)}</p>
                    <div class="card-actions">
                        <button class="action-btn" onclick="copyUrl('${a.link}')">
                            <svg width="14" height="14"><use href="#icon-share"></use></svg> URL 복사
                        </button>
                        <a href="${a.link}" target="_blank" class="action-btn">원문 보기</a>
                    </div>
                </div>
            </article>
        `;
        list.insertAdjacentHTML('beforeend', articleHtml);
    });
}

function renderEmptyState() {
    const list = document.getElementById('view-daily');
    list.innerHTML = `
        <div style="text-align: center; padding: 40px; color: var(--text-secondary);">
            <svg width="48" height="48" fill="none" stroke="currentColor" stroke-width="2" style="opacity: 0.5; margin-bottom: 16px;">
                <use href="#icon-calendar"></use>
            </svg>
            <p>오늘의 수집된 뉴스가 없습니다.</p>
        </div>
    `;
    document.getElementById('view-title').textContent = `Latest AI News (No Data)`;
}

// 5. Utilities
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

// Define copyUrl in global scope for inline onclick usage
window.copyUrl = function(url) {
    navigator.clipboard.writeText(url).then(() => {
        alert("URL이 클립보드에 복사되었습니다.");
    }).catch(err => {
        console.error('Copy failed', err);
    });
};
