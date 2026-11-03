# EcoSense — QR Workflow, Public Bin Pages & UI Quality-of-Life Architecture

**Institution:** Don Bosco Institute of Technology (DBIT), Mumbai  
**Project:** EcoSense — AI-Based Zero Waste Campus Management Platform  
**Document Status:** Production Reference  

---

## 1. Overview & Objectives

This document details the architectural improvements introduced to transform EcoSense physical QR workflows into a production-grade campus system accessible from standard smartphone cameras, Google Lens, and QR scanner applications without requiring pre-authentication just to inspect physical bin telemetry.

---

## 2. Standard QR Payload Format & Resolution

### Physical QR Payload Structure
Every EcoSense waste bin QR code encodes a standard HTTPS/HTTP web URL pointing directly to the public bin resolution route:

```text
http://<ecosense-frontend-domain>/bin/<qr_token>
```

- **Example Local Dev:** `http://localhost:5173/bin/550e8400-e29b-41d4-a716-446655440000`
- **Example Campus Production:** `https://ecosense.dbit.mumbai/bin/550e8400-e29b-41d4-a716-446655440000`

### Security Boundary
- The QR payload contains only an **opaque UUID identifier (`qr_token`)**.
- The QR code contains **no database IDs, user credentials, authentication tokens, or internal secrets**.
- Compatible with all standard phone camera scanners (iOS Camera, Android Camera, Google Lens) and the built-in EcoSense QR scanner.
- Backward compatibility: EcoSense's built-in QR scanner seamlessly parses full URLs (`/bin/<token>`, `/qr/<token>`) as well as raw UUID strings.

---

## 3. Public Bin Information Page (`/bin/:qr_token`)

### Unauthenticated Access
Visiting `/bin/:qr_token` communicates with the backend endpoint:
```http
GET /api/v1/bins/public/{qr_token}
```
**No authentication headers or login cookies are required** to view public-safe physical bin telemetry:
- **Bin Code** (e.g. `CANTEEN-DRY-01`)
- **Designated Waste Stream** (e.g. `DRY RECYCLABLE`, `WET ORGANIC`, `E-WASTE`)
- **Campus Location** (Building, Floor, Room / Area)
- **Volume Capacity** (e.g. `80 Litres`)
- **Real-Time Fill Percentage & Status** (`ACTIVE`, `FULL`, `MAINTENANCE`)

### Role-Aware Action Flow
1. **Unauthenticated User:**
   - Displays full public bin specifications and real-time fill level.
   - Shows a prominent **"Log In to Record Disposal"** button.
   - Clicking redirects to `/login?returnUrl=/bin/<qr_token>`.
   - Post-authentication, the user is returned directly to the bin page without needing to re-scan.
2. **Authenticated Student (`STUDENT`):**
   - Displays bin specifications.
   - Displays inline disposal form (`Approximate Weight`, `Notes`).
   - Submitting executes `POST /api/v1/disposals` using the student's JWT token.
   - Triggers points celebration modal (`+10 Eco Points`).
   - Displays "Report Issue with this Bin" link (`/student/report?bin_id=...`).
3. **Authenticated Collector (`COLLECTOR`):**
   - Displays bin specifications.
   - Displays "Service This Bin" button navigating directly to the Collector Console.
4. **Authenticated Admin (`ADMIN` / `STAFF`):**
   - Displays bin specifications.
   - Displays "Manage Campus Bins" button navigating to Admin Bin Management.

### Error & Not Found Handling
- Non-existent, corrupted, or invalid UUID tokens render a friendly EcoSense **"Bin Not Found"** screen with options to return home or retry lookup, avoiding raw 404 or backend exception popups.

---

## 4. Bulk and Individual QR PDF / Print Placards

### One Bin Per Page Architecture
Both single-bin exports and bulk campus exports adhere strictly to the **ONE BIN PER PAGE** layout standard designed for physical asset placards:
- **Institution & Branding:** `ECOSENSE • Don Bosco Institute of Technology (DBIT), Mumbai`.
- **QR Matrix:** Centered, high-contrast, high-resolution SVG matrix (`level="H"`, 240px+) with ample quiet zones.
- **Physical Identifiers:** Large bin code, waste stream tag, campus location (Building & Floor), capacity, and status.
- **Scan Instructions:** User guidance and printed URL fallback.

### Print CSS Isolation
```css
@media print {
  .qr-print-sheet {
    page-break-after: always;
    break-after: page;
    min-height: 100vh;
  }
}
```
- Navigation bars, sidebars, headers, and UI buttons are hidden automatically via `print:hidden`.
- If zero bins exist when triggering bulk export, the system prevents generating blank sheets and alerts the administrator.

---

## 5. Global Null-Safety & Analytics Data Mapping

### Root Cause of `undefined` and `NaN%` Fixed
- Previously, frontend TypeScript interfaces flattened backend `AnalyticsSummary` metrics (`total_waste_collected_kg`, etc.), whereas the backend Phase 9 schema returned nested sub-objects (`summary`, `operations`, `participation`, `gamification`, `predictions`).
- Unmatched property accesses resolved to `undefined`, and arithmetic operations like `Math.round(undefined * 100)` produced `NaN%`.

### Centralized Formatters & Helper Utilities (`formatters.ts`)
1. `safePercentage(numerator, denominator, decimals, clamp)`:
   - Evaluates whether numerator or denominator is null, undefined, NaN, or non-finite.
   - Returns `0` if denominator $\le 0$.
   - Clamps outputs cleanly between `0%` and `100%`.
2. `formatWeight(kg)`: Converts valid numbers to `X.X kg` and null/undefined/0 to `0 kg`.
3. `formatNumber(val)`: Formats counts with locale comma separators and defaults to `0`.
4. `formatDate(dateStr)`: Formats dates cleanly and defaults to `—`.

### Waste Reports Empty State
In `AdminReportsPage`, distinct UI states are strictly enforced:
- **Loading:** `<LoadingState message="..." />`
- **API Error:** `<ErrorState message="..." onRetry={...} />`
- **Zero Records:** `<EmptyState icon={LuCircleCheck} title="No Waste Reports" description="There are currently no waste reports requiring attention. Everything looks good!" />`
