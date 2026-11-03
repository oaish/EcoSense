import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ProtectedRoute } from './ProtectedRoute';
import { RoleRoute, getRoleDefaultPath } from './RoleRoute';
import { AppShell } from '../layouts/AppShell';

// Pages
import { LoginPage } from '../pages/auth/LoginPage';
import { PublicBinPage } from '../pages/public/PublicBinPage';

// Student Pages
import { StudentDashboard } from '../pages/student/StudentDashboard';
import { ScanBinPage } from '../pages/student/ScanBinPage';
import { AIClassificationPage } from '../pages/student/AIClassificationPage';
import { StudentReportPage } from '../pages/student/StudentReportPage';
import { StudentReportsHistoryPage } from '../pages/student/StudentReportsHistoryPage';
import { RewardsCatalogPage } from '../pages/student/RewardsCatalogPage';
import { RewardsHistoryPage } from '../pages/student/RewardsHistoryPage';
import { StudentActivityPage } from '../pages/student/StudentActivityPage';
import { StudentLeaderboardPage } from '../pages/student/StudentLeaderboardPage';

// Staff Pages
import { StaffDashboard } from '../pages/staff/StaffDashboard';
import { StaffReportsPage } from '../pages/staff/StaffReportsPage';
import { StaffBinsPage } from '../pages/staff/StaffBinsPage';

// Collector Pages
import { CollectorDashboard } from '../pages/collector/CollectorDashboard';
import { CollectorScanPage } from '../pages/collector/CollectorScanPage';
import { CollectorCollectionsPage } from '../pages/collector/CollectorCollectionsPage';
import { CollectorProcessingPage } from '../pages/collector/CollectorProcessingPage';
import { CollectorPredictionsPage } from '../pages/collector/CollectorPredictionsPage';
import { CollectorTasksPage } from '../pages/collector/CollectorTasksPage';

// Admin Pages
import { AdminDashboard } from '../pages/admin/AdminDashboard';
import { AdminAnalyticsPage } from '../pages/admin/AdminAnalyticsPage';
import { AdminBinsPage } from '../pages/admin/AdminBinsPage';
import { AdminLocationsPage } from '../pages/admin/AdminLocationsPage';
import { AdminReportsPage } from '../pages/admin/AdminReportsPage';
import { AdminCollectionsPage } from '../pages/admin/AdminCollectionsPage';
import { AdminProcessingPage } from '../pages/admin/AdminProcessingPage';
import { AdminRewardsPage } from '../pages/admin/AdminRewardsPage';
import { AdminPointsPage } from '../pages/admin/AdminPointsPage';
import { AdminUsersPage } from '../pages/admin/AdminUsersPage';
import { AdminCollectorOperationsPage } from '../pages/admin/AdminCollectorOperationsPage';

export const AppRoutes: React.FC = () => {
  const { user } = useAuth();

  return (
    <Routes>
      {/* Public Routes */}
      <Route
        path="/login"
        element={user ? <Navigate to={getRoleDefaultPath(user.role)} replace /> : <LoginPage />}
      />
      <Route path="/bin/:qr_token" element={<PublicBinPage />} />

      {/* Authenticated Root */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        {/* Default Redirect to Role Dashboard */}
        <Route
          index
          element={<Navigate to={getRoleDefaultPath(user?.role)} replace />}
        />

        {/* Universal Actions */}
        <Route path="scan" element={<ScanBinPage />} />
        <Route path="classify" element={<AIClassificationPage />} />
        <Route path="leaderboard" element={<StudentLeaderboardPage />} />

        {/* Student Experience */}
        <Route
          path="student/dashboard"
          element={
            <RoleRoute allowedRoles={['STUDENT', 'ADMIN']}>
              <StudentDashboard />
            </RoleRoute>
          }
        />
        <Route
          path="student/leaderboard"
          element={
            <RoleRoute allowedRoles={['STUDENT', 'ADMIN']}>
              <StudentLeaderboardPage />
            </RoleRoute>
          }
        />
        <Route
          path="student/report"
          element={
            <RoleRoute allowedRoles={['STUDENT', 'STAFF', 'ADMIN']}>
              <StudentReportPage />
            </RoleRoute>
          }
        />
        <Route
          path="student/reports"
          element={
            <RoleRoute allowedRoles={['STUDENT', 'STAFF', 'ADMIN']}>
              <StudentReportsHistoryPage />
            </RoleRoute>
          }
        />
        <Route
          path="rewards"
          element={
            <RoleRoute allowedRoles={['STUDENT', 'ADMIN']}>
              <RewardsCatalogPage />
            </RoleRoute>
          }
        />
        <Route
          path="rewards/history"
          element={
            <RoleRoute allowedRoles={['STUDENT', 'ADMIN']}>
              <RewardsHistoryPage />
            </RoleRoute>
          }
        />
        <Route
          path="student/activity"
          element={
            <RoleRoute allowedRoles={['STUDENT', 'ADMIN']}>
              <StudentActivityPage />
            </RoleRoute>
          }
        />

        {/* Staff Experience */}
        <Route
          path="staff/dashboard"
          element={
            <RoleRoute allowedRoles={['STAFF', 'ADMIN']}>
              <StaffDashboard />
            </RoleRoute>
          }
        />
        <Route
          path="staff/reports"
          element={
            <RoleRoute allowedRoles={['STAFF', 'ADMIN']}>
              <StaffReportsPage />
            </RoleRoute>
          }
        />
        <Route
          path="staff/bins"
          element={
            <RoleRoute allowedRoles={['STAFF', 'ADMIN']}>
              <StaffBinsPage />
            </RoleRoute>
          }
        />

        {/* Collector Experience */}
        <Route
          path="collector/dashboard"
          element={
            <RoleRoute allowedRoles={['COLLECTOR', 'ADMIN']}>
              <CollectorDashboard />
            </RoleRoute>
          }
        />
        <Route
          path="collector/scan"
          element={
            <RoleRoute allowedRoles={['COLLECTOR', 'ADMIN']}>
              <CollectorScanPage />
            </RoleRoute>
          }
        />
        <Route
          path="collector/collections"
          element={
            <RoleRoute allowedRoles={['COLLECTOR', 'ADMIN']}>
              <CollectorCollectionsPage />
            </RoleRoute>
          }
        />
        <Route
          path="collector/processing"
          element={
            <RoleRoute allowedRoles={['COLLECTOR', 'ADMIN', 'STAFF']}>
              <CollectorProcessingPage />
            </RoleRoute>
          }
        />
        <Route
          path="collector/predictions"
          element={
            <RoleRoute allowedRoles={['COLLECTOR', 'ADMIN']}>
              <CollectorPredictionsPage />
            </RoleRoute>
          }
        />
        <Route
          path="collector/tasks"
          element={
            <RoleRoute allowedRoles={['COLLECTOR', 'ADMIN']}>
              <CollectorTasksPage />
            </RoleRoute>
          }
        />

        {/* Admin Dashboard & Management */}
        <Route
          path="admin/dashboard"
          element={
            <RoleRoute allowedRoles={['ADMIN']}>
              <AdminDashboard />
            </RoleRoute>
          }
        />
        <Route
          path="admin/collector-operations"
          element={
            <RoleRoute allowedRoles={['ADMIN']}>
              <AdminCollectorOperationsPage />
            </RoleRoute>
          }
        />
        <Route
          path="admin/analytics"
          element={
            <RoleRoute allowedRoles={['ADMIN']}>
              <AdminAnalyticsPage />
            </RoleRoute>
          }
        />
        <Route
          path="admin/bins"
          element={
            <RoleRoute allowedRoles={['ADMIN']}>
              <AdminBinsPage />
            </RoleRoute>
          }
        />
        <Route
          path="admin/locations"
          element={
            <RoleRoute allowedRoles={['ADMIN']}>
              <AdminLocationsPage />
            </RoleRoute>
          }
        />
        <Route
          path="admin/reports"
          element={
            <RoleRoute allowedRoles={['ADMIN']}>
              <AdminReportsPage />
            </RoleRoute>
          }
        />
        <Route
          path="admin/collections"
          element={
            <RoleRoute allowedRoles={['ADMIN']}>
              <AdminCollectionsPage />
            </RoleRoute>
          }
        />
        <Route
          path="admin/processing"
          element={
            <RoleRoute allowedRoles={['ADMIN']}>
              <AdminProcessingPage />
            </RoleRoute>
          }
        />
        <Route
          path="admin/rewards"
          element={
            <RoleRoute allowedRoles={['ADMIN']}>
              <AdminRewardsPage />
            </RoleRoute>
          }
        />
        <Route
          path="admin/points"
          element={
            <RoleRoute allowedRoles={['ADMIN']}>
              <AdminPointsPage />
            </RoleRoute>
          }
        />
        <Route
          path="admin/users"
          element={
            <RoleRoute allowedRoles={['ADMIN']}>
              <AdminUsersPage />
            </RoleRoute>
          }
        />
      </Route>

      {/* Catch-all fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};
