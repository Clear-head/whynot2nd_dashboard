var map_container = document.getElementById('map'), // 지도를 표시할 div
    map_option = {
        center: new kakao.maps.LatLng(36.46201132199759, 127.8490946787158), // 지도의 중심좌표
        level: 13    // 지도의 확대 레벨
    };

var map = new kakao.maps.Map(map_container, map_option);

// 지도에 표시 될 마커 객체를 가지고 있을 배열
const detected_markers = [];
const detected_again_markers = [];
const killed_markers = [];

//  마커 종류별 이미지
const red_image = "https://maps.google.com/mapfiles/ms/icons/red-dot.png"
const yellow_image = "https://maps.google.com/mapfiles/ms/icons/yellow-dot.png"
const green_image = "https://maps.google.com/mapfiles/ms/icons/green-dot.png"

// 실제로 지도에 추가 될 마커 객체를 담을 배열
const marker_object_list = [];
//  마커 주변 영역
const circle_object_list = [];

//  지도에 추가된 마커 객체 지도 옆에 표시용
const current_displayed_markers = [];

// 데이터 받는 함수
function fetch_data() {
    fetch("http://localhost:4321/api/kakao/get-data")
        .then((response) => response.json())
        .then((data) => {
            // 배열 초기화
            detected_markers.length = 0;
            detected_again_markers.length = 0;
            killed_markers.length = 0;

            // 데이터 받아와서 배열에 넣기
            data.forEach(item => {
                const latlng = new kakao.maps.LatLng(item.latitude, item.longitude);
                const data_item = {
                    latlng: latlng,
                    content: item.contents,
                    status: item.status
                };

                //  status 별 따로 정보 담기
                if (item.status === 0) {
                    detected_markers.push(data_item);
                } else if (item.status === 1) {
                    detected_again_markers.push(data_item);
                } else if (item.status === 2) {
                    killed_markers.push(data_item);
                }
            });

            // 데이터 업데이트 후 마커 업데이트
            update_markers();
        })
        .catch(error => console.error('Error fetching data:', error));
}

// 5초마다 데이터 업데이트
setInterval(fetch_data, 5000);

// 스위치 확인
const checkbox1 = document.getElementById('switchDetected');
const checkbox2 = document.getElementById('switchDetectedAgain');
const checkbox3 = document.getElementById('switchKilled');

// 스위치에 이벤트 리스너 추가
checkbox1.addEventListener("change", update_markers);
checkbox2.addEventListener("change", update_markers);
checkbox3.addEventListener("change", update_markers);

function item_list() {
    const container = document.getElementById('marker-items');

    // 기존 내용 초기화
    container.innerHTML = '';

    // 현재 표시되는 마커들의 정보를 리스트로 표시
    current_displayed_markers.forEach((item, index) => {
        const div = document.createElement('div');
        div.className = `marker-item status-${item.status}`;

        const statusText = item.status === 0 ? '발견' : (item.status === 1 ? '재발견' : '사체 발견');
        div.innerHTML = `
            <strong>${statusText}</strong><br>
            ${item.content}
        `;

        container.appendChild(div);
    });

    // 총 개수 표시
    const countDiv = document.createElement('div');
    countDiv.className = 'alert alert-info mt-2';
    countDiv.innerHTML = `총 ${current_displayed_markers.length}개 마커`;
    container.appendChild(countDiv);
}

// 스위치 상태에 따라 마커를 업데이트하는 함수
function update_markers() {
    // 기존 마커 모두 제거
    marker_object_list.forEach(marker => marker.setMap(null));
    marker_object_list.length = 0; // 배열 초기화
    circle_object_list.forEach(marker => marker.setMap(null));
    circle_object_list.length = 0;
    current_displayed_markers.length = 0;

    if (checkbox1.checked) {
        add_markers(detected_markers);
    }
    if (checkbox2.checked) {
        add_markers(detected_again_markers);
    }
    if (checkbox3.checked) {
        add_markers(killed_markers);
    }

    item_list();
}

//  마우스 호버 액션리스너
function make_over_listener(map, marker, info_window) {
    return function() {
        info_window.open(map, marker);
    };
}

function make_out_listener(info_window) {
    return function() {
        info_window.close();
    };
}

// 마커를 추가하는 함수, 마커 주변에 원도 그리기
function add_markers(positions) {

    for (var i = 0; i < positions.length; i++) {
        var src = positions[i].status === 0 ? green_image : (positions[i].status === 1 ? yellow_image : red_image);
        var img = new kakao.maps.MarkerImage(
            src,
            new kakao.maps.Size(32, 34),
            {offset: new kakao.maps.Point(16, 17)}
        );

        var marker = new kakao.maps.Marker({
            map: map,
            position: positions[i].latlng,
            image: img
        });

        // 지도에 표시할 원을 생성합니다
        var circle = new kakao.maps.Circle({
            center : positions[i].latlng,
            radius: 5000,
            strokeWeight: 1,
            strokeColor: positions[i].status === 0 ? "#39DE2A" : (positions[i].status === 1 ? "#FEAB38" : "#FF3DE5"),
            strokeOpacity: 1,
            strokeStyle: 'longdash',
            fillColor: positions[i].status === 0 ? "#A2FF99" : (positions[i].status === 1 ? "#faae59" : "#FF8AEF"),
            fillOpacity: 0.3
        });
        circle.setMap(map);

        //  생성한 마커를 배열에 추가
        marker_object_list.push(marker);
        current_displayed_markers.push(positions[i]);
        circle_object_list.push(circle)


        var infowindow = new kakao.maps.InfoWindow({
            content: positions[i].content
        });

        kakao.maps.event.addListener(marker, 'mouseover', make_over_listener(map, marker, infowindow));
        kakao.maps.event.addListener(marker, 'mouseout', make_out_listener(infowindow));
    }
}

// 페이지 로드 시 초기 마커를 표시하기 위해 fetch_data 함수 호출
fetch_data();