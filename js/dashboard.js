// === Show/Hide Logic ===
const mainDashboard = document.getElementById('main-dashboard');
const detailView = document.getElementById('detail-view');
const activeFaultsView = document.getElementById('active-faults-view');
const transformerListView = document.getElementById('transformer-list-view');
const settingsView = document.getElementById('settings-view');
const maintenanceFormView = document.getElementById('maintenance-form-view');
const maintenanceHistoryView = document.getElementById('maintenance-history-view');
let mapInitialized = false;

// Transformer data
const transformerData = {
    'T-2101': {
        id: 'T-2101',
        location: 'Region Johar, Sub-region Johar Chowrangi, Street Main Road',
        health: 22,
        status: 'Critical',
        statusBadge: 'bg-danger',
        recommendation: 'REPLACE TRANSFORMER',
        reason: 'Severe degradation detected. Transformer nearing end-of-life.',
        failureProb: 'Very High (95%) probability of failure within 48 hours.',
        metrics: {
            load: '92%',
            temperature: '98°C',
            ambient: '36°C',
            oilLevel: '95%'
        }
    },
    'T-4091': {
        id: 'T-4091',
        location: 'Region Nazimabad, Sub-region Nadra Mega Center, Street X',
        health: 18,
        status: 'Critical',
        statusBadge: 'bg-danger',
        recommendation: 'SCHEDULE MAINTENANCE',
        reason: 'Sustained high load stress & temperature anomalies detected.',
        failureProb: 'High (88%) probability of failure within 72 hours.',
        metrics: {
            load: '85%',
            temperature: '92°C',
            ambient: '34°C',
            oilLevel: '98%'
        }
    },
    'T-5500': {
        id: 'T-5500',
        location: 'Region DHA, Sub-region Phase 2, Street Khayaban-e-Seher',
        health: 45,
        status: 'Warning',
        statusBadge: 'bg-warning text-dark',
        recommendation: 'MONITOR CLOSELY',
        reason: 'Load patterns indicate stress. Schedule inspection within 7 days.',
        failureProb: 'Medium (35%) probability of issues within next month.',
        metrics: {
            load: '78%',
            temperature: '82°C',
            ambient: '32°C',
            oilLevel: '100%'
        }
    },
    'F-102': {
        id: 'F-102',
        location: 'Region Johar, Sub-region Habib University, Street Main Campus Road',
        health: '--',
        status: 'Active Fault',
        statusBadge: 'bg-primary',
        recommendation: 'CREW DISPATCHED',
        reason: 'Circuit breaker tripped. Crew currently on-site.',
        failureProb: 'Estimated recovery time: ~45 minutes.',
        metrics: {
            load: 'N/A',
            temperature: 'N/A',
            ambient: '33°C',
            oilLevel: 'N/A'
        }
    },
    'T-6000': {
        id: 'T-6000',
        location: 'Region Clifton, Sub-region Boat Basin, Street Main Boulevard',
        health: 92,
        status: 'Healthy',
        statusBadge: 'bg-success',
        recommendation: 'ROUTINE MAINTENANCE',
        reason: 'All parameters within optimal range.',
        failureProb: 'Low risk. Next inspection due in 60 days.',
        metrics: {
            load: '45%',
            temperature: '65°C',
            ambient: '30°C',
            oilLevel: '100%'
        }
    },
    'F-105': {
        id: 'F-105',
        location: 'Region DHA, Sub-region Phase 5, Street Khayaban-e-Bukhari',
        health: '--',
        status: 'Active Fault',
        statusBadge: 'bg-primary',
        recommendation: 'REPAIR IN PROGRESS',
        reason: 'Cable damage detected. Repair work ongoing.',
        failureProb: 'Estimated recovery time: ~2.5 hours.',
        metrics: {
            load: 'N/A',
            temperature: 'N/A',
            ambient: '31°C',
            oilLevel: 'N/A'
        }
    },
    'T-1205': {
        id: 'T-1205',
        location: 'Region Gulshan, Sub-region Block 13, Street Main Road',
        health: 88,
        status: 'Healthy',
        statusBadge: 'bg-success',
        recommendation: 'NO ACTION REQUIRED',
        reason: 'Excellent operating condition.',
        failureProb: 'Very low risk. Next inspection due in 90 days.',
        metrics: {
            load: '52%',
            temperature: '68°C',
            ambient: '31°C',
            oilLevel: '99%'
        }
    },
    'T-3301': {
        id: 'T-3301',
        location: 'Region Korangi, Sub-region Industrial Area, Street Factory Road',
        health: 52,
        status: 'Warning',
        statusBadge: 'bg-warning text-dark',
        recommendation: 'SCHEDULE INSPECTION',
        reason: 'Industrial load patterns causing stress.',
        failureProb: 'Medium (42%) probability of issues within 2 weeks.',
        metrics: {
            load: '82%',
            temperature: '86°C',
            ambient: '35°C',
            oilLevel: '97%'
        }
    },
    'T-8822': {
        id: 'T-8822',
        location: 'Region Gulshan, Sub-region Block 13, Street Main Road',
        health: 48,
        status: 'Warning',
        statusBadge: 'bg-warning text-dark',
        recommendation: 'LOAD BALANCING REQUIRED',
        reason: 'Uneven load distribution detected. Immediate balancing recommended.',
        failureProb: 'Medium (40%) probability of issues within 10 days.',
        metrics: {
            load: '88%',
            temperature: '84°C',
            ambient: '33°C',
            oilLevel: '99%'
        }
    }
};

function hideAllViews() {
    mainDashboard.style.display = 'none';
    detailView.style.display = 'none';
    activeFaultsView.style.display = 'none';
    transformerListView.style.display = 'none';
    settingsView.style.display = 'none';
    maintenanceFormView.style.display = 'none';
    maintenanceHistoryView.style.display = 'none';
    
    // Reset nav links
    document.querySelectorAll('.sidebar .nav-link').forEach(link => {
        link.classList.remove('active');
    });
}

function showDashboard() {
    hideAllViews();
    mainDashboard.style.display = 'block';
    document.getElementById('nav-dashboard').classList.add('active');
    
    if (!mapInitialized) {
        initMap();
        mapInitialized = true;
    }
}

function showDetail(transformerId) {
    hideAllViews();
    detailView.style.display = 'block';
    
    // Get transformer data
    const data = transformerData[transformerId] || transformerData['T-4091']; // Default to T-4091 if not found
    
    // Update detail view
    document.getElementById('detail-transformer-id').textContent = 'Transformer ID: ' + data.id;
    document.getElementById('detail-location').textContent = 'Location: ' + data.location;
    document.getElementById('detail-status-badge').textContent = 'STATUS: ' + data.status.toUpperCase();
    document.getElementById('detail-status-badge').className = 'badge fs-4 ' + data.statusBadge;
    
    // Health score
    const healthScoreElement = document.getElementById('detail-health-score');
    healthScoreElement.innerHTML = data.health + ' <span class="fs-3 text-muted">/ 100</span>';
    
    // Failure probability
    document.getElementById('detail-failure-prob').textContent = data.failureProb;
    document.getElementById('detail-failure-prob').className = data.health < 30 ? 'text-danger' : (data.health < 60 ? 'text-warning' : 'text-success');
    
    // Recommendation
    const recommendationAlert = document.getElementById('detail-recommendation-alert');
    recommendationAlert.className = 'alert ' + (data.health < 30 ? 'alert-danger' : (data.health < 60 ? 'alert-warning' : 'alert-info'));
    document.getElementById('detail-recommendation').textContent = data.recommendation;
    document.getElementById('detail-reason').textContent = 'Reason: ' + data.reason;
    
    // Update metrics
    const metricsHTML = `
        <li class="list-group-item d-flex justify-content-between"><strong>Current Load:</strong> <span>${data.metrics.load}</span></li>
        <li class="list-group-item d-flex justify-content-between"><strong>Current Temperature:</strong> <span>${data.metrics.temperature}</span></li>
        <li class="list-group-item d-flex justify-content-between"><strong>Ambient Temperature:</strong> <span>${data.metrics.ambient}</span></li>
        <li class="list-group-item d-flex justify-content-between"><strong>Oil Level:</strong> <span>${data.metrics.oilLevel}</span></li>
    `;
    document.getElementById('detail-metrics').innerHTML = metricsHTML;
}

function showActiveFaults() {
    hideAllViews();
    activeFaultsView.style.display = 'block';
    document.getElementById('nav-faults').classList.add('active');
}

function showTransformerList() {
    hideAllViews();
    transformerListView.style.display = 'block';
    document.getElementById('nav-transformers').classList.add('active');
}

function showSettings() {
    hideAllViews();
    settingsView.style.display = 'block';
    document.getElementById('nav-settings').classList.add('active');
}

function showMaintenanceForm() {
    // Get current transformer ID from detail view
    const transformerId = document.getElementById('detail-transformer-id').textContent.replace('Transformer ID: ', '');
    const data = transformerData[transformerId] || transformerData['T-4091'];
    
    detailView.style.display = 'none';
    maintenanceFormView.style.display = 'block';
    
    // Populate form
    document.getElementById('form-transformer-id').value = data.id;
    document.getElementById('form-location').textContent = data.location;
    document.getElementById('form-health').textContent = data.health + ' / 100';
    document.getElementById('form-status').textContent = data.status;
    document.getElementById('form-recommendation').textContent = data.recommendation;
    
    // Set default datetime to now
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    document.getElementById('form-datetime').value = now.toISOString().slice(0, 16);
}

function hideMaintenanceForm() {
    maintenanceFormView.style.display = 'none';
    detailView.style.display = 'block';
}

function submitMaintenanceForm() {
    // Show success message
    alert('Maintenance crew assigned successfully! The crew will be notified via SMS and email.');
    hideMaintenanceForm();
}

function showMaintenanceHistory() {
    const transformerId = document.getElementById('detail-transformer-id').textContent.replace('Transformer ID: ', '');
    
    detailView.style.display = 'none';
    maintenanceHistoryView.style.display = 'block';
    
    document.getElementById('history-transformer-id').textContent = transformerId;
}

function hideMaintenanceHistory() {
    maintenanceHistoryView.style.display = 'none';
    detailView.style.display = 'block';
}

function viewFaultDetail(faultId) {
    showDetail(faultId);
}

document.addEventListener("DOMContentLoaded", function() {
    initMap();
    mapInitialized = true;
    
    // Call filterTable on load to ensure table is correctly displayed
    if (typeof filterTable === 'function') {
        filterTable();
    }
});
