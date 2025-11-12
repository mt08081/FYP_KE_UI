// ===================================
// === Filter Table Logic ===
// ===================================
function filterTable() {
    // Get filter values
    const regionFilter = document.getElementById('filter-region') ? document.getElementById('filter-region').value : 'all';
    const riskFilter = document.getElementById('filter-risk') ? document.getElementById('filter-risk').value : 'all';
    const searchFilter = document.getElementById('filter-search') ? document.getElementById('filter-search').value.toLowerCase() : '';
    
    // Get table body and rows
    const tableBody = document.getElementById('transformer-table-body');
    if (!tableBody) return;
    
    const rows = tableBody.getElementsByTagName('tr');

    // Loop through all table rows
    for (let i = 0; i < rows.length; i++) {
        const row = rows[i];
        
        // Get row data
        const region = row.getAttribute('data-region') || '';
        const risk = row.getAttribute('data-risk') || '';
        const text = row.textContent || row.innerText;

        // Check for matches
        const regionMatch = (regionFilter === 'all' || region === regionFilter);
        const riskMatch = (riskFilter === 'all' || risk === riskFilter);
        const searchMatch = (text.toLowerCase().indexOf(searchFilter) > -1);

        // Show or hide the row
        if (regionMatch && riskMatch && searchMatch) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    }
}

// Apply filters function for transformer list page
function applyTransformerFilters() {
    // This can be expanded for the full transformer list page
    filterTable();
}
