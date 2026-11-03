import { describe, it, expect, beforeEach } from 'vitest';
import { setStoredToken, apiClient, ApiError } from '../api/client';
import { getRoleDefaultPath } from '../routes/RoleRoute';

describe('Authentication & RBAC Logic', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('stores and clears JWT in localStorage', () => {
    setStoredToken('test-jwt-token-xyz');
    expect(localStorage.getItem('ecosense_token')).toBe('test-jwt-token-xyz');

    setStoredToken(null);
    expect(localStorage.getItem('ecosense_token')).toBeNull();
  });

  it('correctly maps roles to their respective default home routes', () => {
    expect(getRoleDefaultPath('STUDENT')).toBe('/student/dashboard');
    expect(getRoleDefaultPath('STAFF')).toBe('/staff/dashboard');
    expect(getRoleDefaultPath('COLLECTOR')).toBe('/collector/dashboard');
    expect(getRoleDefaultPath('ADMIN')).toBe('/admin/dashboard');
  });

  it('ApiError carries status code and error details', () => {
    const error = new ApiError(401, 'Incorrect email or password', { detail: 'Incorrect email or password' });
    expect(error.status).toBe(401);
    expect(error.message).toBe('Incorrect email or password');
    expect(error.data.detail).toBe('Incorrect email or password');
  });
});
