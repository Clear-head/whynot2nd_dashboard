//  get grafana panel
async function fetch_panel_data(panelId, apiUrl, content) {
    try {

        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(content)
        });

        if (!response.ok) {
            throw new Error(`API 호출 실패: ${response.status}`);
        }

        const data = await response.json();
        const panelUrl = data.url;

        const panelDiv = document.getElementById(panelId.toString());
        const iframe = panelDiv.querySelector('iframe');
        if (iframe) {
            iframe.src = panelUrl;
        } else {
            console.error(`Panel ${panelId}에서 iframe을 찾을 수 없습니다.`);
        }

    } catch (error) {
        console.error(`API 호출 중 오류 발생 (${panelId}):`, error);
    }
}

// 패널들을 업데이트하는 함수
function get_panels() {

    const agg_interval = document.getElementById('agg_interval');
    const year_sel = document.getElementById('year_sel');
    const sel_period = document.getElementById('sel_period');


    if (!agg_interval || !year_sel || !sel_period) {
        return;
    }

    // sel_period가 비활성화되어 있으면 빈 값으로 처리
    const sel_period_value = sel_period.disabled ? "" : sel_period.value;

    // Panel 1 업데이트
    fetch_panel_data(1, "/api/dashboard/panel", {
        panel_id: 1,
        agg_interval: agg_interval.value,
        year_sel: year_sel.value,
        sel_period: sel_period_value
    });

    // Panel 2 업데이트
    fetch_panel_data(2, "/api/dashboard/panel", {
        panel_id: 2,
        agg_interval: agg_interval.value,
        year_sel: year_sel.value,
        sel_period: sel_period_value
    });
}

// DOM 로드 완료 후 실행
document.addEventListener('DOMContentLoaded', function() {

    // 잠시 기다린 후 요소들 확인
    setTimeout(() => {

        const agg_interval = document.getElementById('agg_interval');
        const sel_period = document.getElementById('sel_period');
        const year_sel = document.getElementById('year_sel');

        if (!agg_interval || !sel_period || !year_sel) {
            return;
        }

        // sel_period 옵션만 업데이트하는 함수
        function update_select3() {
            const value = agg_interval.value;
            sel_period.innerHTML = '';
            sel_period.disabled = false;

            let options = [];

            switch (value) {
                case '월':
                    for (let i = 1; i <= 12; i++) {
                        options.push(`<option value="${i}">${i}월</option>`);
                    }
                    break;
                case '분기':
                    options.push('<option value="Q1">1분기</option>');
                    options.push('<option value="Q2">2분기</option>');
                    options.push('<option value="Q3">3분기</option>');
                    options.push('<option value="Q4">4분기</option>');
                    break;
                case '반기':
                    options.push('<option value="H1">상반기</option>');
                    options.push('<option value="H2">하반기</option>');
                    break;
                case '일':
                case '년':
                default:
                    sel_period.disabled = true;
                    options.push('<option value="">선택불가</option>');
                    break;
            }

            sel_period.innerHTML = options.join('');
        }

        //  변경 시 옵션 업데이트 + 패널 새로고침
        agg_interval.addEventListener('change', function() {
            update_select3(); // 먼저 옵션 업데이트
            get_panels();     // 그 다음 패널 새로고침
        });

        year_sel.addEventListener('change', function() {
            get_panels();
        });

        sel_period.addEventListener('change', function() {
            get_panels();
        });


        update_select3();
        get_panels();

    }, 100); // 100ms 대기
});