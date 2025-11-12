# KE Predictive Maintenance Dashboard - Wireframe Summary

## Overview
Complete functional wireframe implementation for the KE Predictive Maintenance Dashboard with all screens and interactions ready for demonstration.

## Implemented Screens

### 0. Login Page (login.html)
- **Professional gradient design** with split-screen layout
- **Left Panel**: Branding and feature highlights
  - KE logo and brand name
  - Key features with icons (Real-time monitoring, AI predictions, etc.)
- **Right Panel**: Login form
  - Username and password fields
  - Remember me checkbox
  - Forgot password link
  - Demo credentials displayed (admin/admin123)
  - Secure login messaging
- **Authentication**: Simple validation with redirect to dashboard
- **Note**: No signup page - admin manages user accounts directly

### 1. Dashboard (Main Page)
- **Grid Health Overview** with 4 key metrics cards:
  - Total Transformers: 8,500
  - Healthy: 8,341
  - Warning: 117
  - Critical: 42
- **Transformer Status Table** with filtering by:
  - Region (All, Johar, DHA, Nazimabad, Clifton)
  - Risk Level (All, Critical, Warning, Fault, Healthy)
  - Search functionality
- **Interactive Map** showing transformer locations
  - Color-coded markers (Red: Critical, Yellow: Warning, Green: Healthy, Blue: Active Fault)
  - **Click marker → Shows popup with basic info**
  - **Click "View Details" button in popup → Goes to detail view**
  - 7 transformers displayed on map (T-2101, T-4091, T-5500, F-102, T-6000, F-105, T-8822)
- **Navigation** between all pages
- **User Profile Dropdown** with logout option

### 2. Transformer Detail View
- **Dynamic Content** - Each transformer shows its own unique data:
  - T-2101 (Critical - Replace)
  - T-4091 (Critical - Maintenance)
  - T-5500 (Warning - Monitor)
  - F-102 (Active Fault - In Progress)
  - T-6000 (Healthy)
  - F-105 (Active Fault - Repair)
  - Plus 2 more (T-1205, T-3301)
- **Health Score Display** with color-coded status badges
- **Live IoT Metrics**: Load, Temperature, Ambient Temp, Oil Level
- **Recommendation System** with reasoning
- **Historical Charts**: 
  - Health Score & Load Trend (dual-axis line chart)
  - Temperature Trend (internal vs ambient)
- **Action Buttons**:
  - Assign Maintenance Crew (opens form)
  - View Maintenance History (opens history page)

### 3. Active Faults Page
- **Summary Cards**: 
  - Total Alerts: 5
  - Critical: 2
  - Warnings: 3
  - Avg Response Time: 2.4 hrs
- **Critical & Warning Transformers Table** with:
  - Transformer ID (not Fault ID - these are the same transformers from the main list)
  - Location
  - Status (Critical/Warning)
  - Detected time
  - Recommendation
  - Priority
  - Action buttons
- **Shows actual transformers**: T-2101, T-4091, T-5500, T-3301, T-8822
- **Clickable rows** to view transformer details

### 4. Transformer List Page
- **Summary Cards**: Total (8,500), Healthy (8,341), Warning (117), Critical (42)
- **Filter Options**:
  - Region dropdown
  - Status dropdown
  - Capacity dropdown
  - Search field
- **Comprehensive Table** showing:
  - Transformer ID
  - Location
  - Capacity (kVA)
  - Status
  - Health Score
  - Last Maintenance
  - Age (years)
- **7 transformers shown**: T-2101, T-4091, T-5500, T-6000, T-1205, T-3301, T-8822
- **Pagination** (UI ready, 170 pages shown)
- **Export Report** button

### 5. Settings Page
- **Alert Configuration**:
  - Critical Health Threshold
  - Warning Health Threshold
  - Temperature Alert Threshold
  - Load Alert Threshold
- **Notification Preferences**:
  - Email Notifications (toggle)
  - SMS Notifications (toggle)
  - Push Notifications (toggle)
  - Daily Summary Report (toggle)
- **Maintenance Scheduling**:
  - Auto-assign crew options
  - Maintenance interval configuration
- **System Information Panel**:
  - Version, Last Updated
  - Database status
  - Active IoT sensors count
  - ML Model version
- **Quick Actions removed** (not implemented, would be difficult to justify)

### 6. Maintenance Assignment Form
- **Auto-populated** from transformer detail view
- **Form Fields**:
  - Transformer ID (read-only)
  - Task Priority (Critical/High/Medium/Low)
  - Crew Selection (shows availability)
  - Scheduled Date & Time
  - Task Description (textarea)
  - Estimated Duration
- **Transformer Summary** sidebar
- **Submit Handler** with success confirmation

### 7. Maintenance History View
- **Historical Records Table**:
  - Date
  - Task Type
  - Crew
  - Duration
  - Status (Completed)
  - Notes
- **Statistics Card**:
  - Total maintenance tasks
  - Last maintenance date
  - Average downtime
  - Total cost
- **Next Scheduled Maintenance** card

### 8. Navigation Features
- **Login Page** as entry point
- **Sidebar Navigation** with active state indicators
- **Top Navbar** with:
  - Notification bell (with badge)
  - Clickable alerts dropdown
  - User profile dropdown with logout
- **Logout** returns to login page
- **Back buttons** on all sub-pages
- **Breadcrumb-style** navigation flow

### 9. Interactive Elements
- **Login form** with validation and demo credentials
- **Clickable Table Rows** - Navigate to transformer details
- **Notification Alerts** - Click to view transformer
- **Map Markers** - Click to show popup, then "View Details" to navigate
- **Filter Dropdowns** - Real-time table filtering
- **Status Badges** - Color-coded (Red/Yellow/Green/Blue/Primary)
- **Action Buttons** throughout
- **Logout functionality**

## Data Structure

### Transformer Data Array
8 transformer records with complete data (consistent across all pages):
- T-2101: Critical (Health: 22) - REPLACE
- T-4091: Critical (Health: 18) - MAINTENANCE
- T-5500: Warning (Health: 45) - MONITOR
- T-6000: Healthy (Health: 92) - ROUTINE
- T-1205: Healthy (Health: 88) - NO ACTION
- T-3301: Warning (Health: 52) - INSPECTION
- T-8822: Warning (Health: 48) - LOAD BALANCING
- F-102: Active Fault (Temporary outage)
- F-105: Active Fault (Temporary outage)

Each includes:
- Location (Region, Sub-region, Street)
- Health Score
- Status & Badge Color
- Recommendation & Reasoning
- Failure Probability
- Live Metrics (Load, Temperature, Oil Level)

## Technologies Used
- **Frontend**: HTML5, CSS3, Bootstrap 5.3.3
- **Icons**: Bootstrap Icons 1.11.3
- **Charts**: Chart.js (latest)
- **Maps**: Leaflet.js 1.9.4
- **JavaScript**: Vanilla ES6+

## File Structure
```
FYP_KE/
├── login.html (Login page - entry point)
├── UI_Attempt2.html (Main dashboard application)
├── css/
│   └── styles.css (Custom styles)
├── js/
│   ├── dashboard.js (Navigation & data logic)
│   ├── filters.js (Table filtering)
│   ├── charts.js (Chart.js configurations)
│   └── map.js (Leaflet map setup)
└── WIREFRAME_SUMMARY.md (This file)
```

## Key Interactions

0. **Login page** → Enter credentials (admin/admin123) → Dashboard
1. **Click any transformer in table** → Goes to detail view with that transformer's data
2. **Click notification alert** → Goes to that transformer's detail view
3. **Click map marker** → Shows popup with info → Click "View Details" button → Detail view
4. **Click "Assign Maintenance Crew"** → Opens assignment form
5. **Click "View Maintenance History"** → Opens history view
6. **Click sidebar navigation** → Switches between main pages
7. **Use filters** → Real-time table updates
8. **Click "Back" buttons** → Returns to previous view
9. **Click logout** → Returns to login page

## Important Fixes Made

1. **✅ Active Faults consistency**: Changed from separate fault IDs (F-102, F-105) to actual transformers (T-2101, T-4091, T-5500, T-3301, T-8822) - now matches the transformer list
2. **✅ Map interaction**: Clicking marker shows popup only, must click "View Details" button to navigate
3. **✅ Settings simplified**: Removed Quick Actions section (not implemented)
4. **✅ Login page added**: Professional mockup with admin-only access (no signup)
5. **✅ Logout functionality**: User can sign out and return to login
6. **✅ Data consistency**: All 7 transformers appear in Dashboard, Transformer List, and Active Faults (if critical/warning)

## Ready for Demonstration

All screens are fully functional and can be navigated through. The wireframe demonstrates:
- ✅ Complete user flow
- ✅ All major features
- ✅ Interactive elements
- ✅ Data visualization
- ✅ Form handling
- ✅ Multi-page navigation
- ✅ Responsive design
- ✅ Professional UI/UX

## Notes for Presentation
- All data is currently hardcoded (8 transformers)
- Perfect for wireframe demonstration
- Shows complete workflow from alert → assignment → history
- Professional color scheme and layout
- Bootstrap components ensure responsive design
- Ready for backend integration in future phases

---
**Created**: November 12, 2025
**Version**: 1.0