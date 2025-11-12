# KE Predictive Maintenance Dashboard - Wireframe Demo

## Quick Start Guide

### 1. Opening the Application
Start with the **login page**: `login.html`

**Demo Credentials:**
- Username: `admin`
- Password: `admin123`

### 2. Main Features to Demonstrate

#### A. Login & Authentication
- Professional split-screen design
- Secure admin-only access (no public signup)
- Clean branding and feature highlights

#### B. Dashboard Overview
- **4 Summary Cards**: Total (8,500), Healthy (8,341), Warning (117), Critical (42)
- **Interactive Map**: Click markers to see popup, then "View Details"
- **Transformer Table**: Shows 6 transformers with real-time filtering
- **Filters**: Region, Risk Level, Search

#### C. Transformer Details
Click any transformer to see:
- Health score and status badge
- Live IoT metrics (Load, Temperature, Oil Level)
- Historical trend charts
- System recommendations
- Action buttons (Assign Crew, View History)

**Try these transformers:**
- **T-2101**: Critical (22/100) - Replace Required
- **T-4091**: Critical (18/100) - Maintenance Required  
- **T-5500**: Warning (45/100) - Monitor Closely
- **T-6000**: Healthy (92/100) - Routine Maintenance

#### D. Active Faults Page
- Shows 5 critical/warning transformers
- Same transformers as main list (consistent data)
- Click any row to see details

#### E. Transformer List
- Complete inventory (7 shown, 8,500 total)
- Multiple filters (Region, Status, Capacity, Search)
- Pagination ready (170 pages)
- Export functionality

#### F. Settings Page
- Alert thresholds configuration
- Notification preferences (Email, SMS, Push)
- Maintenance scheduling options
- System information panel

#### G. Additional Features
- **Maintenance Assignment Form**: Assign crew with priority and scheduling
- **Maintenance History**: Past records and statistics
- **Logout**: Returns to login page

### 3. Navigation Flow

```
Login Page
    ↓
Dashboard (Main)
    ├→ Click Transformer → Detail View
    │                          ├→ Assign Crew → Form
    │                          └→ View History → History Page
    ├→ Sidebar: Active Faults
    ├→ Sidebar: Transformer List
    └→ Sidebar: Settings
```

### 4. Key Demonstration Points

1. **Data Consistency**: Same transformers appear across all pages
2. **Interactive Map**: Popup first, then navigate
3. **Real-time Filtering**: Type in search or change dropdowns
4. **Dynamic Details**: Each transformer shows unique data
5. **Professional UI**: Bootstrap 5, clean design, responsive
6. **Complete Workflow**: From alert → detail → assignment → history

### 5. Technologies Used

- **Frontend**: HTML5, CSS3, Bootstrap 5.3.3
- **Charts**: Chart.js
- **Maps**: Leaflet.js
- **Icons**: Bootstrap Icons
- **JavaScript**: Vanilla ES6+

### 6. Important Notes

✅ **All data is hardcoded** (perfect for wireframe demo)  
✅ **No backend required** (runs entirely in browser)  
✅ **No signup page** (admin manages users directly)  
✅ **Quick Actions removed from Settings** (not implemented)  
✅ **Map interaction improved** (popup → button → details)  
✅ **Active Faults shows transformers** (not separate fault IDs)  

### 7. Demo Script Suggestion

1. **Start**: Open `login.html`, login with admin/admin123
2. **Dashboard**: Show overview, map interaction, filters
3. **Click T-4091**: Show detail view, charts, recommendations
4. **Assign Crew**: Demonstrate maintenance form
5. **View History**: Show past maintenance records
6. **Back to Dashboard**: Click Active Faults
7. **Transformer List**: Show inventory and filtering
8. **Settings**: Show configuration options
9. **Logout**: Complete the workflow

### 8. Files Structure

```
FYP_KE/
├── login.html          ← START HERE
├── UI_Attempt2.html    ← Main dashboard
├── css/styles.css
├── js/
│   ├── dashboard.js    ← Navigation logic
│   ├── filters.js      ← Table filtering
│   ├── charts.js       ← Chart configurations
│   └── map.js          ← Map setup
├── WIREFRAME_SUMMARY.md
└── README.md           ← This file
```

### 9. Browser Compatibility

Works best in:
- Google Chrome
- Microsoft Edge
- Firefox
- Safari

### 10. Troubleshooting

**Issue**: Map doesn't load
- **Solution**: Check internet connection (uses CDN for Leaflet)

**Issue**: Charts not showing
- **Solution**: Refresh the page, ensure Chart.js CDN is accessible

**Issue**: Can't login
- **Solution**: Use exactly `admin` / `admin123` (case-sensitive)

---

## Ready to Present! 🎉

Your wireframe demonstrates a complete, professional, and functional predictive maintenance system. All screens are interconnected and demonstrate real-world workflows.

**Total Screens**: 8 (Login, Dashboard, Detail, Active Faults, Transformer List, Settings, Maintenance Form, History)

**Total Transformers**: 7 unique transformers with complete data

**Total Interactions**: 20+ clickable elements and workflows

Good luck with your submission! 🚀
