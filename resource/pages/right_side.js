
const panelConfigs = [
            { id: 'panel1', panelId: 1, baseUrl: 'http://localhost:3000/d-solo/38eedacf-2392-420d-8c4f-83a81cc1c579/graph' },
            { id: 'panel2', panelId: 2, baseUrl: 'http://localhost:3000/d-solo/38eedacf-2392-420d-8c4f-83a81cc1c579/graph' }
        ];

// 글로벌 변수들
let currentTimeUnit = 'year';
let currentYear = new Date().getFullYear();
let currentPeriod = null;

// 시간 단위 선택
function selectTimeUnit(value, text) {
    currentTimeUnit = value;
    document.getElementById('timeUnitBtn').textContent = text;
    updateTimeUnit();
}

// 년도 선택
function selectYear(value, text) {
    currentYear = value;
    document.getElementById('yearBtn').textContent = text;
    updatePanels();
}

// 기간 선택
function selectPeriod(value, text) {
    currentPeriod = value;
    document.getElementById('periodBtn').textContent = text;
    updatePanels();
}

// 년도 드롭다운 초기화 (기존 함수 수정)
function initializeYears() {
    const yearDropdown = document.getElementById('yearDropdown');
    const currentYear = new Date().getFullYear();

    yearDropdown.innerHTML = '';
    for (let year = currentYear - 5; year <= currentYear + 2; year++) {
        const li = document.createElement('li');
        li.innerHTML = `<a class="dropdown-item" href="#" onclick="selectYear(${year}, '${year}년')">${year}년</a>`;
        yearDropdown.appendChild(li);
    }

    // 기본값 설정
    document.getElementById('yearBtn').textContent = `${currentYear}년`;
    this.currentYear = currentYear;
}

// updateTimeUnit 함수 수정
function updateTimeUnit() {
    const periodDropdown = document.getElementById('periodDropdown');
    const periodBtn = document.getElementById('periodBtn');
    const periodLabel = document.getElementById('periodLabel');

    periodDropdown.innerHTML = '';

    switch (currentTimeUnit) {
        case 'year':
        case 'day':
            // 년, 일은 기간 선택 비활성화
            periodBtn.disabled = true;
            periodBtn.textContent = '해당 없음';
            periodLabel.textContent = '기간 (비활성화)';
            currentPeriod = null;
            break;

        case 'month':
            // 1~12월
            periodBtn.disabled = false;
            periodLabel.textContent = '월';
            for (let i = 1; i <= 12; i++) {
                const li = document.createElement('li');
                li.innerHTML = `<a class="dropdown-item" href="#" onclick="selectPeriod(${i}, '${i}월')">${i}월</a>`;
                periodDropdown.appendChild(li);
            }
            // 현재 월로 기본 설정
            const currentMonth = new Date().getMonth() + 1;
            periodBtn.textContent = `${currentMonth}월`;
            currentPeriod = currentMonth;
            break;

        case 'quarter':
            // 1~4분기
            periodBtn.disabled = false;
            periodLabel.textContent = '분기';
            for (let i = 1; i <= 4; i++) {
                const li = document.createElement('li');
                li.innerHTML = `<a class="dropdown-item" href="#" onclick="selectPeriod(${i}, '${i}분기')">${i}분기</a>`;
                periodDropdown.appendChild(li);
            }
            // 현재 분기로 기본 설정
            const currentQuarter = Math.floor((new Date().getMonth() + 3) / 3);
            periodBtn.textContent = `${currentQuarter}분기`;
            currentPeriod = currentQuarter;
            break;

        case 'half':
            // 1~2반기
            periodBtn.disabled = false;
            periodLabel.textContent = '반기';
            for (let i = 1; i <= 2; i++) {
                const li = document.createElement('li');
                li.innerHTML = `<a class="dropdown-item" href="#" onclick="selectPeriod(${i}, '${i}반기')">${i}반기</a>`;
                periodDropdown.appendChild(li);
            }
            // 현재 반기로 기본 설정
            const currentHalf = new Date().getMonth() < 6 ? 1 : 2;
            periodBtn.textContent = `${currentHalf}반기`;
            currentPeriod = currentHalf;
            break;
    }

    updatePanels();
}

// updatePanels 함수도 글로벌 변수 사용하도록 수정
function updatePanels() {
    // 기존 getElementById 대신 글로벌 변수 사용
    const timeUnit = currentTimeUnit;
    const year = currentYear;
    const period = currentPeriod;

    // 나머지 로직은 동일...
    panelConfigs.forEach(config => {
        const iframe = document.querySelector(`.grafana-panel iframe[src*="panelId=${config.panelId}"]`);
        if (!iframe) return;

        const params = new URLSearchParams();

        params.set('orgId', '1');
        params.set('panelId', config.panelId);
        params.set('timezone', 'browser');
        params.set('refresh', '1m');
        params.set('__feature.dashboardSceneSolo', 'true');

        params.set('var-timeUnit', timeUnit);
        params.set('var-year', year);

        if (timeUnit === 'month' || timeUnit === 'quarter' || timeUnit === 'half') {
            params.set('var-period', period);
        }

        const timeRange = calculateTimeRange(timeUnit, year, period);
        if (timeRange.from && timeRange.to) {
            params.set('from', timeRange.from);
            params.set('to', timeRange.to);
        }

        iframe.src = `${config.baseUrl}?${params.toString()}`;
    });
}
initializeYears();
updateTimeUnit();
// 페이지 로드시 실행
document.addEventListener('DOMContentLoaded', function() {
    initializeYears();
    updateTimeUnit();
});