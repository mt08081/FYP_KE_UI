/**
 * K-Electric Dashboard v3
 * =======================
 * Clean, intuitive, data-driven dashboard
 */

const API_BASE = 'http://localhost:8000';

// State
let dashboardData = null;
let plantsData = null;
let map = null;
let faultChart = null;
let areaChart = null;

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 K-Electric Dashboard v3 starting...');
    
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(t => new bootstrap.Tooltip(t));
    
    try {
        // Load all data
        const [dashboard, plants] = await Promise.all([
            fetchAPI('/dashboard'),
            fetchAPI('/plants')
        ]);
        
        dashboardData = dashboard;
        plantsData = plants;
        
        // Update UI
        updateStats(dashboard.summary);
        updateFaultsTable(dashboard.recent_faults);
        initMap(dashboard.map_markers);
        initCharts(dashboard.summary);
        populateFilters(plants);
        setupPredictionForm(plants);
        
        // Update timestamp
        document.getElementById('lastUpdate').textContent = 
            `Updated: ${new Date().toLocaleTimeString()}`;
        
        console.log('✅ Dashboard loaded');
    } catch (error) {
        console.error('❌ Load error:', error);
        showError('Could not connect to API server. Make sure it\'s running on port 8000.');
    } finally {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
});

// ============================================
// API
// ============================================
async function fetchAPI(endpoint, params = {}) {
    const url = new URL(API_BASE + endpoint);
    Object.entries(params).forEach(([k, v]) => {
        if (v != null) url.searchParams.append(k, v);
    });
    
    const res = await fetch(url);
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
}

function showError(msg) {
    alert(msg);
}

// ============================================
// UPDATE FUNCTIONS
// ============================================
function updateStats(summary) {
    document.getElementById('statTotal').textContent = summary.total_faults;
    
    // Find status counts
    const statuses = {};
    summary.statuses.forEach(s => {
        statuses[s.status] = s.count;
    });
    
    document.getElementById('statInProgress').textContent = statuses['IN_PROGRESS'] || 0;
    document.getElementById('statCompleted').textContent = statuses['COMPLETED'] || 0;
    document.getElementById('statNew').textContent = statuses['NEW'] || 0;
}

function updateFaultsTable(faults) {
    const tbody = document.getElementById('faultsTable');
    tbody.innerHTML = '';
    
    if (!faults || faults.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">No faults found</td></tr>';
        return;
    }
    
    faults.forEach(f => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${f.id}</strong></td>
            <td>
                <div class="fw-semibold">${f.plant_name}</div>
                <small class="text-muted">${f.area}</small>
            </td>
            <td>
                <i class="bi bi-${f.fault_icon} me-1" style="color: ${f.color};"></i>
                ${f.fault_type}
            </td>
            <td>${getRiskBadge(f.risk_level)}</td>
            <td>${getStatusBadge(f.status, f.status_info)}</td>
            <td>${f.duration || 'N/A'}</td>
        `;
        tbody.appendChild(row);
    });
}

function getRiskBadge(risk) {
    const classes = {
        'Extreme': 'risk-extreme',
        'High': 'risk-high',
        'Medium': 'risk-medium',
        'Secure': 'risk-secure'
    };
    return `<span class="risk-badge ${classes[risk] || ''}">${risk}</span>`;
}

function getStatusBadge(status, info) {
    if (!info) info = { label: status, color: 'secondary', icon: 'circle' };
    return `<span class="badge bg-${info.color}">
        <i class="bi bi-${info.icon} me-1"></i>${info.label}
    </span>`;
}

// ============================================
// MAP
// ============================================
function initMap(markers) {
    map = L.map('plantMap').setView([24.87, 67.05], 11);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap'
    }).addTo(map);
    
    markers.forEach(m => {
        const marker = L.circleMarker([m.lat, m.lng], {
            radius: 12 + Math.min(m.fault_count / 30, 8),
            fillColor: m.color,
            color: '#fff',
            weight: 3,
            fillOpacity: 0.8
        });
        
        marker.bindPopup(`
            <div style="min-width: 180px;">
                <h6 class="mb-2"><i class="bi bi-building"></i> ${m.plant_name}</h6>
                <p class="mb-1"><strong>Area:</strong> ${m.area}</p>
                <p class="mb-1"><strong>Risk Level:</strong> ${getRiskBadge(m.risk_level)}</p>
                <p class="mb-0"><strong>Fault Records:</strong> ${m.fault_count}</p>
            </div>
        `);
        
        marker.addTo(map);
    });
}

// ============================================
// CHARTS
// ============================================
function initCharts(summary) {
    // Fault Type Chart
    const faultCtx = document.getElementById('faultChart');
    if (faultCtx) {
        const faultLabels = Object.keys(summary.by_fault_type);
        const faultValues = Object.values(summary.by_fault_type);
        
        faultChart = new Chart(faultCtx, {
            type: 'doughnut',
            data: {
                labels: faultLabels,
                datasets: [{
                    data: faultValues,
                    backgroundColor: ['#dc3545', '#fd7e14', '#ffc107', '#28a745']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { boxWidth: 12, padding: 10 }
                    }
                }
            }
        });
    }
    
    // Area Chart
    const areaCtx = document.getElementById('areaChart');
    if (areaCtx) {
        const areaLabels = Object.keys(summary.by_area);
        const areaValues = Object.values(summary.by_area);
        const areaColors = {
            'Korangi': '#dc3545',
            'Surjani': '#fd7e14',
            'Nazimabad': '#ffc107',
            'Clifton': '#28a745'
        };
        
        areaChart = new Chart(areaCtx, {
            type: 'bar',
            data: {
                labels: areaLabels,
                datasets: [{
                    label: 'Faults',
                    data: areaValues,
                    backgroundColor: areaLabels.map(a => areaColors[a] || '#6c757d')
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }
}

// ============================================
// FILTERS
// ============================================
function populateFilters(plants) {
    const plantFilter = document.getElementById('filterPlant');
    plants.forEach(p => {
        plantFilter.innerHTML += `<option value="${p.id}">${p.name}</option>`;
    });
    
    // Filter event listeners
    document.getElementById('filterStatus').addEventListener('change', applyFilters);
    document.getElementById('filterPlant').addEventListener('change', applyFilters);
    document.getElementById('filterRisk').addEventListener('change', applyFilters);
    document.getElementById('filterFault').addEventListener('change', applyFilters);
}

async function applyFilters() {
    const status = document.getElementById('filterStatus').value;
    const plant = document.getElementById('filterPlant').value;
    const risk = document.getElementById('filterRisk').value;
    const fault = document.getElementById('filterFault').value;
    
    // Filter client-side from loaded data
    let filtered = dashboardData.recent_faults;
    
    if (status) {
        filtered = filtered.filter(f => f.status === status);
    }
    if (plant) {
        filtered = filtered.filter(f => f.plant_id === plant);
    }
    if (risk) {
        filtered = filtered.filter(f => f.risk_level === risk);
    }
    if (fault) {
        filtered = filtered.filter(f => f.fault_type === fault);
    }
    
    updateFaultsTable(filtered);
}

// ============================================
// PREDICTION FORM
// ============================================
function setupPredictionForm(plants) {
    const predPlant = document.getElementById('predPlant');
    const plantInfo = document.getElementById('plantAreaInfo');
    
    // Populate plant dropdown with area info
    plants.forEach(p => {
        predPlant.innerHTML += `<option value="${p.id}" data-area="${p.area}" data-risk="${p.risk_level}">
            ${p.name}
        </option>`;
    });
    
    // Show area when plant selected
    predPlant.addEventListener('change', function() {
        const selected = this.options[this.selectedIndex];
        if (selected.value) {
            const area = selected.dataset.area;
            const risk = selected.dataset.risk;
            plantInfo.innerHTML = `<span style="color: ${getRiskColor(risk)};">
                <i class="bi bi-geo-alt-fill"></i> ${area} Area - ${risk} Risk
            </span>`;
        } else {
            plantInfo.innerHTML = '';
        }
    });
    
    // Form submit
    document.getElementById('predictionForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const plant = predPlant.value;
        const temp = parseFloat(document.getElementById('predTemp').value);
        const wind = parseFloat(document.getElementById('predWind').value);
        
        if (!plant) {
            alert('Please select a plant');
            return;
        }
        
        const resultDiv = document.getElementById('predictionResult');
        resultDiv.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary"></div></div>';
        
        try {
            const result = await fetchAPI('/predict', { plant, temp, wind });
            displayPrediction(result);
        } catch (error) {
            resultDiv.innerHTML = `<div class="alert alert-danger mt-3">${error.message}</div>`;
        }
    });
}

function getRiskColor(risk) {
    return {
        'Extreme': '#dc3545',
        'High': '#fd7e14',
        'Medium': '#f57c00',
        'Secure': '#28a745'
    }[risk] || '#6c757d';
}

function displayPrediction(result) {
    const div = document.getElementById('predictionResult');
    
    div.innerHTML = `
        <div class="prediction-result mt-3">
            <div class="row text-center mb-3">
                <div class="col-6 border-end">
                    <div class="text-muted small">Predicted Fault</div>
                    <div class="prediction-value">
                        <i class="bi bi-${result.predictions.fault_icon}"></i>
                    </div>
                    <div class="fw-semibold">${result.predictions.fault_type}</div>
                </div>
                <div class="col-6">
                    <div class="text-muted small">Est. Repair Time</div>
                    <div class="prediction-value">${result.predictions.restoration_formatted}</div>
                    <div class="text-muted small">${result.predictions.restoration_hours} hours</div>
                </div>
            </div>
            
            <hr>
            
            <div class="small">
                <div class="d-flex justify-content-between mb-2">
                    <span class="text-muted">Nearest Service Center:</span>
                    <span class="fw-semibold">${result.response.nearest_center}</span>
                </div>
                <div class="d-flex justify-content-between mb-2">
                    <span class="text-muted">Travel Time:</span>
                    <span>${result.response.travel_time_min} min (${result.response.distance_km} km)</span>
                </div>
                <div class="d-flex justify-content-between mb-2">
                    <span class="text-muted">Total ETA:</span>
                    <span class="fw-semibold text-primary">${result.response.total_eta_formatted}</span>
                </div>
            </div>
            
            <div class="mt-3 p-2 rounded small" style="background: ${getRiskColor(result.plant.risk_level)}15;">
                <i class="bi bi-shield-exclamation"></i>
                <strong>${result.plant.area}</strong> is a <strong>${result.plant.risk_level}</strong> kunda risk area
            </div>
        </div>
    `;
}
