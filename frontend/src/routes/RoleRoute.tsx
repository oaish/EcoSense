import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { UserRole } from '../types';

interface RoleRouteProps {
  allowedRoles: UserRole[];
  children: React.ReactNode;
}

export const getRoleDefaultPath = (role?: UserRole): string => {
  switch (role) {
    case 'ADMIN':
      return '/admin/dashboard';
    case 'STAFF':
      return '/staff/dashboard';
    case 'COLLECTOR':
      return '/collector/dashboard';
    case 'STUDENT':
    default:
      return '/student/dashboard';
  }
};

export const RoleRoute: React.FC<RoleRouteProps> = ({ allowedRoles, children }) => {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const userRole = user.role as UserRole;
  if (!allowedRoles.includes(userRole)) {
    // Redirect to the user's default role dashboard
    return <Navigate to={getRoleDefaultPath(userRole)} replace />;
  }

  return <>{children}</>;
};
