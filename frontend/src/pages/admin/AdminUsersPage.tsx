import React, { useState, useEffect } from 'react';
import {
  LuUsers,
  LuUserPlus,
  LuSearch,
  LuFilter,
  LuSquarePen,
  LuEye,
  LuUserCheck,
  LuUserX,
  LuCheck,
  LuX,
  LuShield,
  LuMail,
  LuKey,
  LuFlame,
  LuCalendar,
  LuActivity,
  LuTrash2,
  LuPhone,
} from 'react-icons/lu';
import { usersApi } from '../../api/users';
import {
  AdminUserCreatePayload,
  AdminUserDetail,
  AdminUserSummary,
  AdminUserUpdatePayload,
  UserRole,
} from '../../types';
import { EcoStageBadge } from '../../components/common/EcoStageBadge';
import { ConfirmModal } from '../../components/common/ConfirmModal';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';

export const AdminUsersPage: React.FC = () => {
  const [users, setUsers] = useState<AdminUserSummary[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState<string>('');
  const [roleFilter, setRoleFilter] = useState<string>('');
  const [activeFilter, setActiveFilter] = useState<string>('');

  // Modals & Drawers
  const [isCreateOpen, setIsCreateOpen] = useState<boolean>(false);
  const [editUser, setEditUser] = useState<AdminUserSummary | null>(null);
  const [detailUser, setDetailUser] = useState<AdminUserDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState<boolean>(false);
  const [toggleUser, setToggleUser] = useState<AdminUserSummary | null>(null);
  const [actionLoading, setActionLoading] = useState<boolean>(false);

  // Create Form State
  const [createForm, setCreateForm] = useState<AdminUserCreatePayload>({
    name: '',
    email: '',
    password: '',
    role: 'STUDENT',
    phone_number: '',
    is_active: true,
  });
  const [formError, setFormError] = useState<string | null>(null);

  // Edit Form State
  const [editForm, setEditForm] = useState<AdminUserUpdatePayload>({
    name: '',
    email: '',
    role: 'STUDENT',
    phone_number: '',
    is_active: true,
    password: '',
  });

  const loadUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await usersApi.listUsers({
        search: search.trim() || undefined,
        role: roleFilter || undefined,
        is_active: activeFilter === '' ? undefined : activeFilter === 'true',
        limit: 100,
      });
      setUsers(res.users);
      setTotalCount(res.total_count);
    } catch (err: any) {
      setError(err.message || 'Failed to load user accounts');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      loadUsers();
    }, 250);
    return () => clearTimeout(timer);
  }, [search, roleFilter, activeFilter]);

  const handleOpenDetail = async (user: AdminUserSummary) => {
    setDetailLoading(true);
    setDetailUser(null);
    try {
      const detail = await usersApi.getUserDetail(user.user_id);
      setDetailUser(detail);
    } catch (err: any) {
      alert(`Failed to load details: ${err.message}`);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    if (!createForm.name.trim() || !createForm.email.trim() || !createForm.password) {
      setFormError('Name, email, and password are required.');
      return;
    }
    if (createForm.password.length < 8) {
      setFormError('Password must be at least 8 characters.');
      return;
    }

    setActionLoading(true);
    try {
      await usersApi.createAdminUser({
        ...createForm,
        phone_number: createForm.phone_number?.trim() || null,
      });
      setIsCreateOpen(false);
      setCreateForm({ name: '', email: '', password: '', role: 'STUDENT', phone_number: '', is_active: true });
      loadUsers();
    } catch (err: any) {
      setFormError(err.message || 'Failed to create user');
    } finally {
      setActionLoading(false);
    }
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editUser) return;
    setFormError(null);

    setActionLoading(true);
    try {
      const payload: AdminUserUpdatePayload = {
        name: editForm.name,
        email: editForm.email,
        role: editForm.role,
        is_active: editForm.is_active,
        phone_number: editForm.phone_number?.trim() || null,
      };
      if (editForm.password && editForm.password.trim().length >= 8) {
        payload.password = editForm.password.trim();
      }

      await usersApi.updateAdminUser(editUser.user_id, payload);
      setEditUser(null);
      loadUsers();
    } catch (err: any) {
      setFormError(err.message || 'Failed to update user');
    } finally {
      setActionLoading(false);
    }
  };

  const handleConfirmToggleActive = async () => {
    if (!toggleUser) return;
    setActionLoading(true);
    try {
      await usersApi.updateAdminUser(toggleUser.user_id, {
        is_active: !toggleUser.is_active,
      });
      setToggleUser(null);
      loadUsers();
    } catch (err: any) {
      alert(`Status update failed: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-950 text-white rounded-3xl p-7 shadow-xl border-b-4 border-slate-950 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-indigo-300 flex items-center gap-1.5 mb-1">
            <LuShield className="w-4 h-4 text-emerald-400" />
            Platform Governance & RBAC
          </span>
          <h1 className="text-3xl sm:text-4xl font-black tracking-tight">User Management</h1>
          <p className="text-sm text-slate-300 max-w-xl mt-1 leading-relaxed">
            Manage student, staff, collector, and administrator accounts, roles, access permissions, and account statuses.
          </p>
        </div>

        <button
          onClick={() => {
            setFormError(null);
            setIsCreateOpen(true);
          }}
          className="inline-flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white font-bold px-6 py-3 rounded-2xl shadow-lg border-b-4 border-emerald-700 transition-all active:scale-95 self-start md:self-auto"
        >
          <LuUserPlus className="w-5 h-5" />
          <span>Add New User</span>
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-white rounded-2xl p-4 shadow-sm border border-slate-200 flex flex-col sm:flex-row items-center gap-4">
        {/* Search */}
        <div className="relative flex-1 w-full">
          <LuSearch className="w-5 h-5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by name or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium text-sm text-slate-800"
          />
        </div>

        {/* Role Filter */}
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="w-full sm:w-40 px-3 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-bold text-xs text-slate-700 bg-white"
          >
            <option value="">All Roles</option>
            <option value="STUDENT">Students</option>
            <option value="STAFF">Staff</option>
            <option value="COLLECTOR">Collectors</option>
            <option value="ADMIN">Admins</option>
          </select>

          {/* Status Filter */}
          <select
            value={activeFilter}
            onChange={(e) => setActiveFilter(e.target.value)}
            className="w-full sm:w-40 px-3 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-bold text-xs text-slate-700 bg-white"
          >
            <option value="">All Statuses</option>
            <option value="true">Active Accounts</option>
            <option value="false">Deactivated</option>
          </select>
        </div>
      </div>

      {/* Users Table */}
      {loading && <LoadingState message="Loading registered campus users..." />}
      {error && <ErrorState message={error} onRetry={loadUsers} />}

      {!loading && !error && (
        <div className="bg-white rounded-3xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="p-5 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <h3 className="font-bold text-slate-800 text-sm uppercase tracking-wider flex items-center gap-2">
              <LuUsers className="w-4 h-4 text-emerald-600" />
              Registered Accounts ({totalCount})
            </h3>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50/50 border-b border-slate-200 text-xs font-black uppercase text-slate-400">
                  <th className="py-3.5 px-6">User / Email</th>
                  <th className="py-3.5 px-4">Role</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4">Eco Stage</th>
                  <th className="py-3.5 px-4">Points</th>
                  <th className="py-3.5 px-4">Joined Date</th>
                  <th className="py-3.5 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-sm">
                {users.map((u) => {
                  const roleColors: Record<string, string> = {
                    STUDENT: 'bg-emerald-100 text-emerald-800 border-emerald-200',
                    STAFF: 'bg-blue-100 text-blue-800 border-blue-200',
                    COLLECTOR: 'bg-amber-100 text-amber-800 border-amber-200',
                    ADMIN: 'bg-purple-100 text-purple-800 border-purple-200',
                  };

                  return (
                    <tr key={u.user_id} className="hover:bg-slate-50/60 transition-colors">
                      <td className="py-4 px-6">
                        <div className="font-bold text-slate-900">{u.name}</div>
                        <div className="text-xs text-slate-500">{u.email}</div>
                        {u.phone_number && (
                          <div className="text-[11px] font-mono text-emerald-700 flex items-center gap-1 mt-0.5">
                            <LuPhone className="w-3 h-3" />
                            {u.phone_number}
                          </div>
                        )}
                      </td>

                      <td className="py-4 px-4">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-extrabold border ${roleColors[u.role] || 'bg-slate-100 text-slate-700'}`}>
                          {u.role}
                        </span>
                      </td>

                      <td className="py-4 px-4">
                        {u.is_active ? (
                          <span className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                            Active
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1.5 text-xs font-bold text-rose-700 bg-rose-50 px-2.5 py-1 rounded-full border border-rose-200">
                            <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
                            Blocked
                          </span>
                        )}
                      </td>

                      <td className="py-4 px-4">
                        {u.role === 'STUDENT' ? (
                          <EcoStageBadge stageName={u.stage_name} size="sm" />
                        ) : (
                          <span className="text-xs text-slate-400 font-medium">N/A</span>
                        )}
                      </td>

                      <td className="py-4 px-4 font-black text-slate-800">
                        {u.role === 'STUDENT' ? (
                          <span className="flex items-center gap-1">
                            <LuFlame className="w-4 h-4 text-emerald-500" />
                            {u.total_earned_points.toLocaleString()}
                          </span>
                        ) : (
                          <span className="text-xs text-slate-400 font-medium">—</span>
                        )}
                      </td>

                      <td className="py-4 px-4 text-xs text-slate-500">
                        {new Date(u.created_at).toLocaleDateString()}
                      </td>

                      <td className="py-4 px-6 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          {/* View Detail */}
                          <button
                            onClick={() => handleOpenDetail(u)}
                            className="p-2 rounded-xl text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
                            title="View Account Details"
                          >
                            <LuEye className="w-4 h-4" />
                          </button>

                          {/* Edit User */}
                          <button
                            onClick={() => {
                              setFormError(null);
                              setEditUser(u);
                              setEditForm({
                                name: u.name,
                                email: u.email,
                                role: u.role,
                                phone_number: u.phone_number || '',
                                is_active: u.is_active,
                                password: '',
                              });
                            }}
                            className="p-2 rounded-xl text-slate-500 hover:text-emerald-600 hover:bg-emerald-50 transition-colors"
                            title="Edit User"
                          >
                            <LuSquarePen className="w-4 h-4" />
                          </button>

                          {/* Toggle Active */}
                          <button
                            onClick={() => setToggleUser(u)}
                            className={`p-2 rounded-xl transition-colors ${
                              u.is_active
                                ? 'text-slate-500 hover:text-rose-600 hover:bg-rose-50'
                                : 'text-slate-500 hover:text-emerald-600 hover:bg-emerald-50'
                            }`}
                            title={u.is_active ? 'Deactivate User' : 'Activate User'}
                          >
                            {u.is_active ? <LuUserX className="w-4 h-4 text-rose-500" /> : <LuUserCheck className="w-4 h-4 text-emerald-600" />}
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}

                {users.length === 0 && (
                  <tr>
                    <td colSpan={7} className="text-center py-12 text-slate-400 font-medium">
                      No matching user accounts found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Create User Modal */}
      {isCreateOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
          <div className="relative w-full max-w-lg bg-white rounded-3xl p-7 shadow-2xl border border-slate-100">
            <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-100">
              <h3 className="text-xl font-black text-slate-900 flex items-center gap-2">
                <LuUserPlus className="w-5 h-5 text-emerald-600" />
                Add New Campus User
              </h3>
              <button onClick={() => setIsCreateOpen(false)} className="p-2 text-slate-400 hover:text-slate-600 rounded-full hover:bg-slate-100">
                <LuX className="w-5 h-5" />
              </button>
            </div>

            {formError && (
              <div className="p-3 mb-4 rounded-xl bg-rose-50 border border-rose-200 text-xs font-bold text-rose-700">
                {formError}
              </div>
            )}

            <form onSubmit={handleCreateSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">Full Name</label>
                <input
                  type="text"
                  required
                  value={createForm.name}
                  onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                  placeholder="e.g. John Doe"
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">Email Address</label>
                <input
                  type="email"
                  required
                  value={createForm.email}
                  onChange={(e) => setCreateForm({ ...createForm, email: e.target.value })}
                  placeholder="e.g. student@dbit.in"
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Phone Number (Optional - e.g. +919876543210)
                </label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <LuPhone className="w-4 h-4" />
                  </span>
                  <input
                    type="tel"
                    value={createForm.phone_number || ''}
                    onChange={(e) => setCreateForm({ ...createForm, phone_number: e.target.value })}
                    placeholder="+919876543210"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium text-sm font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">Password</label>
                <input
                  type="password"
                  required
                  minLength={8}
                  value={createForm.password}
                  onChange={(e) => setCreateForm({ ...createForm, password: e.target.value })}
                  placeholder="Min 8 characters"
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">Campus Role</label>
                  <select
                    value={createForm.role}
                    onChange={(e) => setCreateForm({ ...createForm, role: e.target.value as UserRole })}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-bold text-xs"
                  >
                    <option value="STUDENT">STUDENT</option>
                    <option value="STAFF">STAFF</option>
                    <option value="COLLECTOR">COLLECTOR</option>
                    <option value="ADMIN">ADMIN</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">Account Status</label>
                  <select
                    value={createForm.is_active ? 'true' : 'false'}
                    onChange={(e) => setCreateForm({ ...createForm, is_active: e.target.value === 'true' })}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-bold text-xs"
                  >
                    <option value="true">Active</option>
                    <option value="false">Deactivated</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setIsCreateOpen(false)}
                  className="px-4 py-2.5 rounded-xl text-sm font-bold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="px-6 py-2.5 rounded-xl text-sm font-bold bg-emerald-500 hover:bg-emerald-600 text-white border-b-2 border-emerald-700 shadow-md transition-all active:scale-95 disabled:opacity-50"
                >
                  {actionLoading ? 'Creating...' : 'Create Account'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit User Modal */}
      {editUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
          <div className="relative w-full max-w-lg bg-white rounded-3xl p-7 shadow-2xl border border-slate-100">
            <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-100">
              <h3 className="text-xl font-black text-slate-900 flex items-center gap-2">
                <LuSquarePen className="w-5 h-5 text-emerald-600" />
                Edit Account: {editUser.name}
              </h3>
              <button onClick={() => setEditUser(null)} className="p-2 text-slate-400 hover:text-slate-600 rounded-full hover:bg-slate-100">
                <LuX className="w-5 h-5" />
              </button>
            </div>

            {formError && (
              <div className="p-3 mb-4 rounded-xl bg-rose-50 border border-rose-200 text-xs font-bold text-rose-700">
                {formError}
              </div>
            )}

            <form onSubmit={handleEditSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">Full Name</label>
                <input
                  type="text"
                  required
                  value={editForm.name}
                  onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">Email Address</label>
                <input
                  type="email"
                  required
                  value={editForm.email}
                  onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Phone Number (Optional - e.g. +919876543210)
                </label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <LuPhone className="w-4 h-4" />
                  </span>
                  <input
                    type="tel"
                    value={editForm.phone_number || ''}
                    onChange={(e) => setEditForm({ ...editForm, phone_number: e.target.value })}
                    placeholder="+919876543210"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium text-sm font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">Reset Password (Optional)</label>
                <input
                  type="password"
                  placeholder="Leave blank to keep existing password"
                  value={editForm.password || ''}
                  onChange={(e) => setEditForm({ ...editForm, password: e.target.value })}
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">Role</label>
                  <select
                    value={editForm.role}
                    onChange={(e) => setEditForm({ ...editForm, role: e.target.value as UserRole })}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-bold text-xs"
                  >
                    <option value="STUDENT">STUDENT</option>
                    <option value="STAFF">STAFF</option>
                    <option value="COLLECTOR">COLLECTOR</option>
                    <option value="ADMIN">ADMIN</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">Account Status</label>
                  <select
                    value={editForm.is_active ? 'true' : 'false'}
                    onChange={(e) => setEditForm({ ...editForm, is_active: e.target.value === 'true' })}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-bold text-xs"
                  >
                    <option value="true">Active</option>
                    <option value="false">Deactivated</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setEditUser(null)}
                  className="px-4 py-2.5 rounded-xl text-sm font-bold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="px-6 py-2.5 rounded-xl text-sm font-bold bg-emerald-500 hover:bg-emerald-600 text-white border-b-2 border-emerald-700 shadow-md transition-all active:scale-95 disabled:opacity-50"
                >
                  {actionLoading ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* User Detail Drawer / Modal */}
      {detailUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
          <div className="relative w-full max-w-2xl bg-white rounded-3xl p-7 shadow-2xl border border-slate-100 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-100">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-2xl bg-indigo-50 text-indigo-700 flex items-center justify-center font-black text-xl shadow-inner">
                  {detailUser.name.charAt(0)}
                </div>
                <div>
                  <h3 className="text-xl font-black text-slate-900">{detailUser.name}</h3>
                  <span className="text-xs text-slate-500">{detailUser.email}</span>
                  {detailUser.phone_number && (
                    <div className="text-xs font-mono text-emerald-700 flex items-center gap-1 mt-0.5">
                      <LuPhone className="w-3.5 h-3.5" />
                      {detailUser.phone_number}
                    </div>
                  )}
                </div>
              </div>
              <button onClick={() => setDetailUser(null)} className="p-2 text-slate-400 hover:text-slate-600 rounded-full hover:bg-slate-100">
                <LuX className="w-5 h-5" />
              </button>
            </div>

            {/* Quick Metrics */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
              <div className="bg-slate-50 p-3.5 rounded-2xl border border-slate-100">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Role</span>
                <span className="font-extrabold text-slate-800 text-sm">{detailUser.role}</span>
              </div>
              <div className="bg-slate-50 p-3.5 rounded-2xl border border-slate-100">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Status</span>
                <span className={`font-extrabold text-xs ${detailUser.is_active ? 'text-emerald-600' : 'text-rose-600'}`}>
                  {detailUser.is_active ? 'Active' : 'Blocked'}
                </span>
              </div>
              <div className="bg-slate-50 p-3.5 rounded-2xl border border-slate-100">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Earned Pts</span>
                <span className="font-black text-slate-800 text-sm flex items-center gap-1">
                  <LuFlame className="w-3.5 h-3.5 text-emerald-500" />
                  {detailUser.total_earned_points.toLocaleString()}
                </span>
              </div>
              <div className="bg-slate-50 p-3.5 rounded-2xl border border-slate-100">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Net Balance</span>
                <span className="font-black text-slate-800 text-sm">
                  {detailUser.current_point_balance.toLocaleString()} pts
                </span>
              </div>
            </div>

            {/* Eco Stage Milestone */}
            {detailUser.role === 'STUDENT' && detailUser.stage && (
              <div className="mb-6 bg-emerald-50/60 p-4 rounded-2xl border border-emerald-100">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-black uppercase text-emerald-800">Current Eco Stage</span>
                  <EcoStageBadge stageName={detailUser.stage.stage_name} size="sm" />
                </div>
                <div className="w-full bg-emerald-200/60 rounded-full h-2">
                  <div
                    className="bg-emerald-500 h-2 rounded-full"
                    style={{ width: `${detailUser.stage.progress_percentage}%` }}
                  ></div>
                </div>
              </div>
            )}

            {/* Recent Point Ledger Transactions */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600 flex items-center gap-1.5">
                <LuActivity className="w-4 h-4 text-slate-400" />
                Recent Point Ledger Transactions
              </h4>
              <div className="bg-slate-50 rounded-2xl p-3 border border-slate-100 max-h-48 overflow-y-auto divide-y divide-slate-200/60 text-xs">
                {detailUser.recent_transactions.map((t) => (
                  <div key={t.transaction_id} className="py-2 flex items-center justify-between">
                    <div>
                      <span className="font-bold text-slate-800 block">{t.description || t.source_type}</span>
                      <span className="text-slate-400">{t.created_at ? new Date(t.created_at).toLocaleString() : ''}</span>
                    </div>
                    <span className={`font-black ${t.points > 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                      {t.points > 0 ? `+${t.points}` : t.points} pts
                    </span>
                  </div>
                ))}
                {detailUser.recent_transactions.length === 0 && (
                  <p className="text-slate-400 text-center py-4">No transactions recorded yet.</p>
                )}
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setDetailUser(null)}
                className="px-5 py-2 rounded-xl text-sm font-bold bg-slate-100 hover:bg-slate-200 text-slate-700"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Confirmation Modal for Toggle Active */}
      <ConfirmModal
        isOpen={toggleUser !== null}
        title={toggleUser?.is_active ? 'Deactivate User Account?' : 'Activate User Account?'}
        message={
          toggleUser?.is_active
            ? `Deactivating "${toggleUser?.name}" will immediately prevent this account from authenticating or performing campus operations.`
            : `Activating "${toggleUser?.name}" will restore full login and operational permissions.`
        }
        confirmLabel={toggleUser?.is_active ? 'Deactivate User' : 'Activate User'}
        confirmVariant={toggleUser?.is_active ? 'danger' : 'primary'}
        loading={actionLoading}
        onConfirm={handleConfirmToggleActive}
        onCancel={() => setToggleUser(null)}
      />
    </div>
  );
};
