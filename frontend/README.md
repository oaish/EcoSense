# EcoSense Frontend & Admin Dashboard (Phase 10)

EcoSense — AI-Based Zero Waste Campus Management Platform  
**Institution:** Don Bosco Institute of Technology (DBIT), Mumbai  

---

## 🌿 Overview

The EcoSense frontend is a modern, responsive web application inspired by the playful, gamified, and approachable design language of Duolingo. It connects directly to the FastAPI backend (Phases 1–9) with role-based user experiences for **Students**, **Staff**, **Collectors**, and **Administrators**.

### Role Personalities & Experiences:
- **🎓 Student Experience (`/student/*`):** Gamified eco-dashboard, live QR bin scanning & disposal recording, confetti reward animations, real-time ledger point balances, streaks, AI waste classification helper (`/classify`), and campus perks store (`/rewards`).
- **🏢 Staff Portal (`/staff/*`):** Campus cleanliness issue monitoring, waste report tracking, and physical bin inspection.
- **🚛 Collector Field Hub (`/collector/*`):** High-fill bin alerts, QR scanning for fill telemetry readings & collection logging, recycling/composting processing records, and AI fill predictions.
- **⚡ Admin Control Center (`/admin/*`):** Real-time campus zero-waste dashboard with landfill diversion tracking, comprehensive suite for all 13 Phase 9 analytics endpoints, bin & location management, issue resolution with points rewards, rewards store inventory, and financial ledger adjustments.

---

## 🛠️ Technology Stack

- **Framework:** React 18 + TypeScript + Vite
- **Styling:** Tailwind CSS + PostCSS (Custom EcoSense soft-3D design system tokens)
- **Routing:** React Router v6 with Auth & Role-Based Route Guards
- **Icons & Visuals:** Lucide React + Canvas Confetti
- **QR Scanner:** HTML5-QRCode with camera detection & manual token fallback
- **Testing:** Vitest + React Testing Library + jsdom

---

## 🚀 Getting Started

### 1. Prerequisites
- Node.js v18+ (tested on Node v24)
- Running EcoSense FastAPI backend (default: `http://localhost:8000`)

### 2. Environment Configuration
Copy `.env.example` to `.env`:
```bash
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Install Dependencies
```bash
cd frontend
npm install
```

### 4. Development Server
```bash
npm run dev
```
The application will be accessible at `http://localhost:5173`.

### 5. Run Tests
```bash
npm test
```

### 6. Production Build
```bash
npm run build
```

---

## 🔑 Demo Credentials (from Backend Seed / DBIT)

| Role | Email | Password | Default Path |
| :--- | :--- | :--- | :--- |
| **Student** | `student@dbit.in` | `studentpassword` | `/student/dashboard` |
| **Staff** | `staff@dbit.in` | `staffpassword` | `/staff/dashboard` |
| **Collector** | `collector@dbit.in` | `collectorpassword` | `/collector/dashboard` |
| **Admin** | `admin@dbit.in` | `adminpassword` | `/admin/dashboard` |

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── api/             # Central API client & domain modules (auth, bins, reports, analytics...)
│   ├── components/      # Reusable design system components (StatCard, PointsCard, QRScanner...)
│   ├── context/         # AuthContext & JWT session store
│   ├── layouts/         # AppShell, Header, Sidebar, MobileNav
│   ├── pages/           # Role-tailored pages (Student, Staff, Collector, Admin)
│   ├── routes/          # ProtectedRoute, RoleRoute, AppRoutes
│   ├── tests/           # Vitest unit & integration test suites
│   ├── types/           # TypeScript interfaces aligned with Backend Schemas
│   ├── App.tsx          # App root
│   ├── main.tsx         # Entrypoint
│   └── index.css        # EcoSense 3D design system styles
├── public/              # Static assets & brand favicon
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```
