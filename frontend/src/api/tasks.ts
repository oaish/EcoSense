import { apiClient } from './client';
import {
  CollectionTask,
  TaskCreatePayload,
  ReportDelegationPayload,
  TaskStatusUpdatePayload,
  TaskReassignPayload,
  TaskCancelPayload,
  TaskStatus,
  TaskType,
  TaskPriority,
} from '../types';

export const tasksApi = {
  async createTask(data: TaskCreatePayload): Promise<CollectionTask> {
    return apiClient<CollectionTask>('/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async delegateReport(data: ReportDelegationPayload): Promise<CollectionTask> {
    return apiClient<CollectionTask>('/tasks/delegate-report', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async getTasks(params?: {
    collector_id?: string;
    status?: TaskStatus;
    task_type?: TaskType;
    priority?: TaskPriority;
    skip?: number;
    limit?: number;
  }): Promise<CollectionTask[]> {
    const res = await apiClient<any>('/tasks', { params });
    if (Array.isArray(res)) return res;
    if (res && Array.isArray(res.tasks)) return res.tasks;
    return [];
  },

  async getMyTasks(params?: {
    status?: TaskStatus;
    skip?: number;
    limit?: number;
  }): Promise<CollectionTask[]> {
    const res = await apiClient<any>('/tasks/me', { params });
    if (Array.isArray(res)) return res;
    if (res && Array.isArray(res.tasks)) return res.tasks;
    return [];
  },

  async getTaskById(taskId: number): Promise<CollectionTask> {
    return apiClient<CollectionTask>(`/tasks/${taskId}`);
  },

  async updateStatus(taskId: number, data: TaskStatusUpdatePayload): Promise<CollectionTask> {
    return apiClient<CollectionTask>(`/tasks/${taskId}/status`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  async reassignTask(taskId: number, data: TaskReassignPayload): Promise<CollectionTask> {
    return apiClient<CollectionTask>(`/tasks/${taskId}/reassign`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async cancelTask(taskId: number, data: TaskCancelPayload): Promise<CollectionTask> {
    return apiClient<CollectionTask>(`/tasks/${taskId}/cancel`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};
