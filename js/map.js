// === Map Logic ===
function initMap() {
    var container = L.DomUtil.get('map');
    if(container != null){
        container._leaflet_id = null;
    }

    var map = L.map('map').setView([24.8607, 67.0011], 11);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
    }).addTo(map);
    
    // Define Icons
    var redIcon = new L.Icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
        iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41]
    });
    var yellowIcon = new L.Icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-gold.png',
        iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41]
    });
    var greenIcon = new L.Icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
        iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41]
    });
    var blueIcon = new L.Icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
        iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41]
    });

    // Add Markers with popups only (no direct navigation on click)
    var marker1 = L.marker([24.9341, 67.0922], {icon: redIcon})
        .addTo(map)
        .bindPopup('<div style="text-align: center;"><b>ID: T-2101</b><br>Status: Critical<br>Health: 22/100<br>Rec: REPLACE<br><br><button onclick="showDetail(\'T-2101\')" class="btn btn-sm btn-primary" style="margin-top: 5px;">View Details</button></div>');

    var marker2 = L.marker([24.9138, 67.0322], {icon: redIcon})
        .addTo(map)
        .bindPopup('<div style="text-align: center;"><b>ID: T-4091</b><br>Status: Critical<br>Health: 18/100<br>Rec: Maintenance<br><br><button onclick="showDetail(\'T-4091\')" class="btn btn-sm btn-primary" style="margin-top: 5px;">View Details</button></div>');

    var marker3 = L.marker([24.8118, 67.0327], {icon: yellowIcon})
        .addTo(map)
        .bindPopup('<div style="text-align: center;"><b>ID: T-5500</b><br>Status: Warning<br>Health: 45/100<br>Rec: Monitor<br><br><button onclick="showDetail(\'T-5500\')" class="btn btn-sm btn-primary" style="margin-top: 5px;">View Details</button></div>');

    var marker4 = L.marker([24.9200, 67.1143], {icon: blueIcon})
        .addTo(map)
        .bindPopup('<div style="text-align: center;"><b>ID: F-102</b><br>Status: Active Fault<br>Est. Recovery: ~45 mins<br><br><button onclick="showDetail(\'F-102\')" class="btn btn-sm btn-primary" style="margin-top: 5px;">View Details</button></div>');

    var marker5 = L.marker([24.7969, 67.0384], {icon: greenIcon})
        .addTo(map)
        .bindPopup('<div style="text-align: center;"><b>ID: T-6000</b><br>Status: Healthy<br>Health: 92/100<br><br><button onclick="showDetail(\'T-6000\')" class="btn btn-sm btn-primary" style="margin-top: 5px;">View Details</button></div>');
    
    var marker6 = L.marker([24.8080, 67.0504], {icon: blueIcon})
        .addTo(map)
        .bindPopup('<div style="text-align: center;"><b>ID: F-105</b><br>Status: Active Fault<br>Est. Recovery: ~2.5 hours<br><br><button onclick="showDetail(\'F-105\')" class="btn btn-sm btn-primary" style="margin-top: 5px;">View Details</button></div>');
    
    var marker7 = L.marker([24.8848, 67.0631], {icon: yellowIcon})
        .addTo(map)
        .bindPopup('<div style="text-align: center;"><b>ID: T-8822</b><br>Status: Warning<br>Health: 48/100<br>Rec: Load Balancing<br><br><button onclick="showDetail(\'T-8822\')" class="btn btn-sm btn-primary" style="margin-top: 5px;">View Details</button></div>');
}
