//  get grafana panel
async function fetchPanelData(panelId, apiUrl, content) {
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


    } catch (error) {
        console.error(`API 호출 중 오류 발생 (${panelId}):`, error);
    }
}

//  content: {"url":"https://"}
function getPanels(content) {

    fetchPanelData("panel_1", "/api/dashboard/panel-1", content);
    fetchPanelData("panel_2", "/api/dashboard/panel-2", content);
}

getPanels();
setInterval(get_panels, 5000);