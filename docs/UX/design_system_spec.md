# AI News Archive - 디자인 시스템 명세서 (UI/UX Handoff)

프론트엔드 엔지니어(Liam)가 즉시 `frontend/css/style.css` 구조를 잡고 UI 컴포넌트를 개발할 수 있도록 크리스(UX)가 정의한 명세서입니다.

---

## 1. 글로벌 CSS 변수 (Design Tokens)

`frontend/css/style.css` 의 최상단 `:root` 에 복사해서 사용할 수 있는 색상 및 타이포그래피, 여백 토큰입니다. OS 테마 설정에 따라 다크/라이트 모드가 자동 적용되도록 미디어 쿼리를 구성하세요.

```css
/* 기본 (Light Mode) */
:root {
  /* Colors */
  --bg-primary: #F8FAFC;
  --bg-secondary: #FFFFFF;
  --bg-skeleton: #E2E8F0;
  
  --text-primary: #0F172A;
  --text-secondary: #64748B;
  
  --accent-blue: #3B82F6;
  --accent-blue-hover: #2563EB;
  --accent-purple: #8B5CF6;
  
  /* Tag Category Colors (Light Mode) */
  --tag-tech-bg: #E0E7FF;    /* Indigo - LLM/AI Tools */
  --tag-tech-text: #3730A3;
  --tag-edge-bg: #DCFCE7;    /* Green - Edge/Embedded */
  --tag-edge-text: #166534;
  --tag-biz-bg: #FFEDD5;     /* Orange - Business/Industry */
  --tag-biz-text: #9A3412;
  --tag-soc-bg: #FCE7F3;     /* Pink - Society/Culture */
  --tag-soc-text: #9D174D;
  --tag-default-bg: #F1F5F9; /* Slate - Default */
  --tag-default-text: #475569;
  
  --border-color: #E2E8F0;

  /* Typography */
  --font-family: Pretendard, -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', Arial, sans-serif;
  --text-xs: 0.75rem; /* 12px */
  --text-sm: 0.875rem; /* 14px */
  --text-base: 1rem; /* 16px */
  --text-lg: 1.125rem; /* 18px */
  --text-xl: 1.25rem; /* 20px */

  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;

  /* Radius & Shadow */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --shadow-card: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
}

/* 다크 모드 (Dark Mode) */
@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: #0B1120;
    --bg-secondary: #1E293B;
    --bg-skeleton: #334155;
    
    --text-primary: #F8FAFC;
    --text-secondary: #94A3B8;
    
    /* Tag Category Colors (Dark Mode) */
    --tag-tech-bg: rgba(99, 102, 241, 0.2);
    --tag-tech-text: #818CF8;
    --tag-edge-bg: rgba(34, 197, 94, 0.2);
    --tag-edge-text: #4ADE80;
    --tag-biz-bg: rgba(249, 115, 22, 0.2);
    --tag-biz-text: #FB923C;
    --tag-soc-bg: rgba(236, 72, 153, 0.2);
    --tag-soc-text: #F472B6;
    --tag-default-bg: rgba(255, 255, 255, 0.1);
    --tag-default-text: #E2E8F0;
    
    --border-color: #334155;
    
    --shadow-card: 0 4px 6px -1px rgba(0, 0, 0, 0.5), 0 2px 4px -1px rgba(0, 0, 0, 0.3);
  }
}
/* 토글 버튼으로 강제 제어하기 위한 data-theme 속성 활용 가능 */
[data-theme="dark"] {
    --bg-primary: #0B1120;
    --bg-secondary: #1E293B;
    /* (위 다크모드 변수와 동일하게 설정) */
}
```

---

## 2. 구체적인 UI 컴포넌트 스펙 (Component Spec)

*   **뉴스 카드 (Card Box)**
    *   `background-color`: `var(--bg-secondary)`
    *   `border-radius`: `var(--radius-lg)` (16px)
    *   `padding`: `var(--space-4)` (16px) 내외부 일관 유지 (모바일 환경 고려)
    *   `box-shadow`: `var(--shadow-card)`
    *   `border`: `1px solid var(--border-color)`
*   **태그 칩 (Tag Chip)**
    *   `display`: `inline-block`
    *   `padding`: `4px 10px`
    *   `border-radius`: `9999px` (완벽한 알약 모양 Pilled)
    *   `font-size`: `var(--text-xs)`
    *   `font-weight`: `500`
    *   *예외 처리*: `max-width: 150px`, `white-space: nowrap`, `overflow: hidden`, `text-overflow: ellipsis` (AI 긴 태그 방어)
    *   **컬러 베리에이션 (CSS 보조 클래스로 제어):**
        *   기본 (`.tag-default`): `background: var(--tag-default-bg)`, `color: var(--tag-default-text)`
        *   LLM/개발도구 (`.tag-tech`): `background: var(--tag-tech-bg)`, `color: var(--tag-tech-text)`
        *   임베디드/AI하드웨어 (`.tag-edge`): `background: var(--tag-edge-bg)`, `color: var(--tag-edge-text)`
        *   비즈니스/산업 (`.tag-biz`): `background: var(--tag-biz-bg)`, `color: var(--tag-biz-text)`
        *   사회/규제/윤리 (`.tag-soc`): `background: var(--tag-soc-bg)`, `color: var(--tag-soc-text)`
*   **주간 베스트 코너 뱃지 (Weekly Top 3 프리미엄 룩)**
    *   카드 `border` 대신 `box-shadow` 와 그라데이션을 사용해 프리미엄 네온 효과 부여.
    *   *예외 CSS:* `box-shadow: 0 0 0 1px transparent, 0 0 15px rgba(139, 92, 246, 0.3);` (보라색 네온 글로우)
    *   뱃지는 카드 우측 상단에 Absolute 띄움. `background: linear-gradient(135deg, #8B5CF6, #3B82F6); color: white;`

---

## 3. 인터랙션 및 상태 (Interaction & State) 효과

*   **Hover & Transition (터치/마우스오버 피드백)**
    *   **카드 호버:** `transition: transform 0.2s ease, box-shadow 0.2s ease;` `transform: translateY(-2px);`
    *   **아코디언 본문 (접힘/펼침):** JavaScript로 `max-height`를 토글하되, CSS로 부드럽게 열리게 처리. `transition: max-height 0.3s ease-out, opacity 0.3s ease;`
*   **로딩 상태: 쉬머 (Shimmer) 스켈레톤 애니메이션**
    *   회색 네모가 아닌 빛이 지나가는 효과 구현.
    ```css
    @keyframes shimmer {
      0% { background-position: -200% 0; }
      100% { background-position: 200% 0; }
    }
    .skeleton-box {
      background: linear-gradient(90deg, var(--bg-skeleton) 25%, rgba(255,255,255,0.1) 50%, var(--bg-skeleton) 75%);
      background-size: 200% 100%;
      animation: shimmer 1.5s infinite linear;
    }
    ```

---

## 4. 아이콘 에셋 (Icon Asset) 가이드

성능과 컬러 테마(다크/라이트) 대응을 위해 이미지 파일(PNG)이 아닌 **SVG 소스 코드**를 사용합니다. 
필요한 핵심 아이콘은 `docs/UX/Asset/` 폴더 내에 SVG 스니펫으로 제공됩니다. 모든 SVG는 CSS의 `color` 속성을 그대로 상속받도록 `fill="currentColor"` 또는 `stroke="currentColor"` 로 렌더링됩니다.

*   `icon-calendar.svg` : 상단 네비게이션 및 사이드바 날짜 선택용
*   `icon-sun.svg` : 테마 토글용 (라이트 모드로 전환 시)
*   `icon-moon.svg` : 테마 토글용 (다크 모드로 전환 시)
*   `icon-chevron-down.svg` : 아코디언 카드 접기/펼치기 화살표
*   `icon-share.svg` : 카드 하단 링크 복사 아이콘
*   `icon-crown.svg` : 주간 베스트 Top 1~3 배지용

> Frontend(Liam): HTML 내에 위 SVG 텍스트를 직접 `innerHTML` 로 박아 넣거나, SVG Symbol 방식으로 재사용하면 리퀘스트(네트워크 요청)를 아낄 수 있습니다.
