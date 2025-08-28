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
        const panelFrame = document.getElementById(panelId);
        panelFrame.src = panelUrl


    } catch (error) {
        console.error(`API 호출 중 오류 발생 (${panelId}):`, error);
    }
}

//  content: {"url":"https://"}
function get_panels() {
    const add_interval = document.getElementById('add_interval');
    const year_sel = document.getElementById('year_sel');
    const sel_period = document.getElementById('sel_period');

    fetch_panel_data(1, "/api/dashboard/panel", {
        panel_id: 1,
        add_interval:add_interval.value,
        year_sel:year_sel.value,
        sel_period:sel_period.value
    });
    fetch_panel_data(2, "/api/dashboard/panel", {
        panel_id: 2,
        add_interval:add_interval.value,
        year_sel:year_sel.value,
        sel_period:sel_period.value
    });
}

get_panels();


//  selector
document.addEventListener('DOMContentLoaded', function() {
    const add_interval = document.getElementById('add_interval');
    const sel_period = document.getElementById('sel_period');

    function update_select3() {
        const value = add_interval.value;
        sel_period.innerHTML = ''; // 기존 옵션 제거
        sel_period.disabled = false; // 기본적으로 활성화

        let options = [];

        switch (value) {
            case '월':
                for (let i = 1; i <= 12; i++) {
                    options.push(`<option value="${i}">${i}</option>`);
                }
                break;
            case '분기':
                options.push('<option value="1">1</option>', '<option value="2">2</option>', '<option value="3">3</option>', '<option value="4">4</option>');
                break;
            case '반기':
                options.push('<option value="1">1</option>', '<option value="2">2</option>');
                break;
            case '일':
            case '년':
            default:
                sel_period.disabled = true; // '일' 또는 '년'일 때 비활성화
                options.push('<option value="">선택불가</option>');
                break;
        }

        sel_period.innerHTML = options.join('');
    }

    // add_interval 값이 변경될 때마다 update_select3 함수 실행
    add_interval.addEventListener('change', update_select3);

    // 페이지 로드 시 초기 상태 설정
    update_select3();
});


