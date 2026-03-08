// script.js - Client interactions and dynamic data fetching

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initTabs();
    initTagListeners();
    initCalendarListeners();
    initLogoListener(); // Added logo click listener
    loadLatestNews().then(() => {
        handleAnchorScroll();
    });
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

// 1-1. Logo Event Logic
function initLogoListener() {
    const logo = document.getElementById('home-logo');
    if (logo) {
        logo.addEventListener('click', () => {
            // Hard refresh / navigate back to the base URL
            window.location.href = window.location.pathname;
        });
    }
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

            if (targetId === 'view-weekly') {
                loadWeeklyNews();
            } else if (targetId === 'view-daily') {
                document.getElementById('view-title').textContent = window.latestDailyTitle || "Latest AI News";
            }
        });
    });
}

function initTagListeners() {
    // Add click event to all tags in the UI
    document.querySelectorAll('.tag-cloud .tag, .mobile-tags .tag').forEach(tagEl => {
        tagEl.style.cursor = 'pointer';
        tagEl.addEventListener('click', (e) => {
            e.stopPropagation(); // prevent card toggling if tag is inside a card
            const rawTag = tagEl.textContent.trim().replace('#', '');
            loadTagNews(rawTag);
        });
    });
}

function initCalendarListeners() {
    // Simple POC for calendar clicks (assuming Mar 2026)
    document.querySelectorAll('.calendar-grid .date:not(.empty)').forEach(dateEl => {
        dateEl.style.cursor = 'pointer';
        dateEl.addEventListener('click', () => {
            document.querySelectorAll('.calendar-grid .date').forEach(d => d.classList.remove('current'));
            dateEl.classList.add('current');

            const dayNum = dateEl.textContent.trim().padStart(2, '0');
            const targetDate = `2026-03-${dayNum}`;
            loadDailyNewsByDate(targetDate);
        });
    });
}

function handleAnchorScroll() {
    const hash = window.location.hash;
    if (hash && hash.length > 1) {
        // e.g., #article-1234
        const targetEl = document.querySelector(hash);
        if (targetEl) {
            targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
            targetEl.classList.add('expanded'); // Auto expand
            targetEl.style.boxShadow = '0 0 0 2px var(--accent-light)'; // Highlight
        }
    }
}

function setLoadingState(isLoading) {
    const activeTarget = document.querySelector('.nav-btn.active').getAttribute('data-target');
    const loadingView = document.getElementById('loading-view');

    if (isLoading) {
        document.querySelectorAll('.news-list').forEach(list => list.classList.add('hidden'));
        loadingView.classList.remove('hidden');
    } else {
        loadingView.classList.add('hidden');
        document.getElementById(activeTarget).classList.remove('hidden');
    }
}

async function loadLatestNews() {
    setLoadingState(true);
    try {
        // Switch tab to daily just in case
        document.querySelector('[data-target="view-daily"]').click();

        const indexRes = await fetch('data/index.json');
        if (!indexRes.ok) throw new Error('Failed to load indices');
        const indexData = await indexRes.json();

        // Render Popular Tags if provided in index.json
        if (indexData.top_tags && indexData.top_tags.length > 0) {
            renderPopularTags(indexData.top_tags);
        }

        if (indexData.available_dates && indexData.available_dates.length > 0) {
            const latestDate = indexData.available_dates[0];
            window.latestDailyTitle = `Latest AI News (${latestDate})`;
            document.getElementById('view-title').textContent = window.latestDailyTitle;

            const dailyRes = await fetch(`data/daily/${latestDate}.json`);
            if (dailyRes.ok) {
                const articles = await dailyRes.json();
                renderNews(articles, 'view-daily');
                return;
            }
        }
        renderEmptyState('view-daily', '오늘의 수집된 뉴스가 없습니다.');
    } catch (error) {
        console.error('Data Fetch Error:', error);
        renderEmptyState('view-daily', '데이터를 불러오는 중 오류가 발생했습니다.');
    } finally {
        setLoadingState(false);
    }
}

async function loadDailyNewsByDate(dateStr) {
    setLoadingState(true);
    document.querySelector('[data-target="view-daily"]').click();
    try {
        window.latestDailyTitle = `Archive: ${dateStr}`;
        document.getElementById('view-title').textContent = window.latestDailyTitle;

        const res = await fetch(`data/daily/${dateStr}.json`);
        if (res.ok) {
            const articles = await res.json();
            renderNews(articles, 'view-daily');
        } else {
            renderEmptyState('view-daily', `${dateStr}에는 수집된 기사가 없습니다.`);
        }
    } catch (error) {
        renderEmptyState('view-daily', '해당 날짜의データを 불러오지 못했습니다.');
    } finally {
        setLoadingState(false);
    }
}

async function loadTagNews(rawTag) {
    setLoadingState(true);
    // Force switch to daily view for tags
    document.querySelector('[data-target="view-daily"]').click();

    // Normalize string to match safe_tag from python
    let safeTag = rawTag.trim().toLowerCase().replace(/[^a-z0-9가-힣 \-_]/g, '').replace(/ /g, '_');

    try {
        const titleEl = document.getElementById('view-title');
        titleEl.innerHTML = `Tag: #${rawTag} <button onclick="loadLatestNews()" class="action-btn" style="margin-left: 10px; font-size: 0.8em; padding: 4px 8px; border: 1px solid var(--accent-color);">✕ 필터 초기화</button>`;
        window.latestDailyTitle = titleEl.textContent.trim(); // store plaintext fallback

        const res = await fetch(`data/tags/${safeTag}.json`);
        if (res.ok) {
            const articles = await res.json();
            renderNews(articles, 'view-daily');
        } else {
            renderEmptyState('view-daily', `최근 30일 내 #${rawTag} 관련 기사를 찾을 수 없습니다.`);
        }
    } catch (error) {
        console.error(error);
        renderEmptyState('view-daily', '태그별 기사를 불러오지 못했습니다.');
    } finally {
        setLoadingState(false);
    }
}

async function loadWeeklyNews() {
    setLoadingState(true);
    try {
        document.getElementById('view-title').textContent = `Weekly Top News`;

        // Compute current ISO week string as fallback
        const now = new Date();
        now.setDate(now.getDate() + 4 - (now.getDay() || 7));
        const yearStart = new Date(now.getFullYear(), 0, 1);
        const weekNo = Math.ceil((((now - yearStart) / 86400000) + 1) / 7);
        const currentYear = now.getFullYear();
        const weeklyFile = `${currentYear}_W${weekNo}.json`;

        const res = await fetch(`data/weekly/${weeklyFile}`);
        if (res.ok) {
            const articles = await res.json();
            renderWeeklyHeader(weekNo);
            renderWeeklyNewsList(articles);
        } else {
            renderEmptyState('view-weekly', `아직 이번 주 주간 베스트가 집계되지 않았습니다. (토요일 자정 전송)`);
        }
    } catch (error) {
        console.error(error);
        renderEmptyState('view-weekly', '위클리 기사를 불러오지 못했습니다.');
    } finally {
        setLoadingState(false);
    }
}

function renderNews(articles, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';

    if (!articles || articles.length === 0) {
        renderEmptyState(containerId, '수집된 기사가 없습니다.');
        return;
    }

    articles.forEach((a, i) => {
        let tagsHtml = '';
        if (a.ai_tags && a.ai_tags.length > 0) {
            a.ai_tags.forEach(t => {
                tagsHtml += `<span class="tag tag-tech" onclick="event.stopPropagation(); loadTagNews('${t}')">#${t}</span>`;
            });
        }

        let dateStr = a.published_date ? a.published_date.split('T')[0] : '';
        const articleId = a.id ? a.id : `article-${Date.now()}-${i}`;

        const articleHtml = `
            <article class="news-card" id="${articleId}">
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
        container.insertAdjacentHTML('beforeend', articleHtml);
    });
}

function renderWeeklyHeader(weekNo) {
    const list = document.getElementById('view-weekly');
    list.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-4); background-color: var(--bg-secondary); padding: 8px 16px; border-radius: 8px; border: 1px solid var(--border-color);">
            <button class="cal-nav" style="font-weight: bold;">&larr; 이전 주 (Week ${weekNo - 1})</button>
            <span style="font-size: var(--text-sm); font-weight: bold;">Week ${weekNo}</span>
            <button class="cal-nav" style="opacity: 0.3; cursor: default;">다음 주 &rarr;</button>
        </div>
    `;
}

function renderWeeklyNewsList(articles) {
    const container = document.getElementById('view-weekly');

    if (!articles || articles.length === 0) {
        container.insertAdjacentHTML('beforeend', `<div>위클리 데이터가 비어있습니다.</div>`);
        return;
    }

    articles.forEach((a, index) => {
        let tagsHtml = '';
        if (a.ai_tags && a.ai_tags.length > 0) {
            a.ai_tags.forEach(t => {
                tagsHtml += `<span class="tag tag-tech" onclick="event.stopPropagation(); loadTagNews('${t}')">#${t}</span>`;
            });
        }

        let dateStr = a.published_date ? a.published_date.split('T')[0] : '';
        const articleId = a.id ? a.id : `article-${Date.now()}-${index}`;

        // Top 1 vs Top 2,3 styling
        let premiumClass = '';
        let badgeStyle = '';
        let outlineStyle = '';

        if (a.rank === 1) {
            premiumClass = 'premium-card';
        } else {
            premiumClass = 'premium-card';
            outlineStyle = `style="box-shadow: 0 0 0 1px transparent, 0 0 10px rgba(59, 130, 246, 0.2);"`;
            badgeStyle = `style="background: linear-gradient(135deg, #3B82F6, #14B8A6);"`;
        }

        const articleHtml = `
            <article class="news-card ${premiumClass}" id="${articleId}" ${outlineStyle}>
                <div class="rank-badge" ${badgeStyle}>
                    <svg width="12" height="12"><use href="#icon-crown"></use></svg> Top ${a.rank || (index + 1)}
                </div>
                <div class="card-header" onclick="toggleAccordion(this)">
                    <h3>${escapeHtml(a.title)}</h3>
                    <div class="card-meta">${escapeHtml(a.source)} • ${a.category} • ${escapeHtml(dateStr)}</div>
                    <div class="card-tags">${tagsHtml}</div>
                    <svg class="expand-icon" width="20" height="20">
                        <use href="#icon-chevron-down"></use>
                    </svg>
                </div>
                <div class="card-body">
                    <div style="margin-bottom: 8px; font-weight: bold; color: var(--accent-color);">🏆 이번 주 핫 토픽: #${a.weekly_hot_tag || a.ai_tags[0]}</div>
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
        container.insertAdjacentHTML('beforeend', articleHtml);
    });
}

function renderEmptyState(containerId, message) {
    const list = document.getElementById(containerId);
    list.innerHTML = `
        <div style="text-align: center; padding: 40px; color: var(--text-secondary);">
            <svg width="48" height="48" fill="none" stroke="currentColor" stroke-width="2" style="opacity: 0.5; margin-bottom: 16px;">
                <use href="#icon-calendar"></use>
            </svg>
            <p>${message}</p>
        </div>
    `;
}

function renderPopularTags(tagsArray) {
    // Generate HTML for the sidebar and mobile tags arrays
    let html = '';
    // Let's use alternating colors for visual variety like the mockup
    const styles = ['tag-tech', 'tag-edge', 'tag-biz', 'tag-soc'];

    tagsArray.forEach((tag, idx) => {
        const styleClass = styles[idx % styles.length];
        html += `<span class="tag ${styleClass}" onclick="loadTagNews('${tag}')" style="cursor: pointer;">#${tag}</span>`;
    });

    const sidebarCloud = document.querySelector('.tag-cloud');
    const mobileCloud = document.querySelector('.mobile-tags');

    if (sidebarCloud) sidebarCloud.innerHTML = html;
    if (mobileCloud) mobileCloud.innerHTML = html;
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
window.copyUrl = function (url) {
    navigator.clipboard.writeText(url).then(() => {
        alert("URL이 클립보드에 복사되었습니다.");
    }).catch(err => {
        console.error('Copy failed', err);
    });
};
