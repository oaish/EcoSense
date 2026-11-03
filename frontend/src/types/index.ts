// EcoSense Frontend Types - Strict Alignment with Backend Models & OpenAPI

export type UserRole = 'ADMIN' | 'STAFF' | 'COLLECTOR' | 'STUDENT';

export interface Role {
  role_id: number;
  role_name: UserRole;
  description?: string;
}

export interface User {
  user_id: string;
  name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  phone_number?: string | null;
  created_at?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface Location {
  location_id: number;
  name: string;
  code: string;
  building?: string;
  floor?: string;
  description?: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface LocationCreate {
  name: string;
  code: string;
  building?: string;
  floor?: string;
  description?: string;
  is_active?: boolean;
}

export interface LocationUpdate {
  name?: string;
  code?: string;
  building?: string;
  floor?: string;
  description?: string;
  is_active?: boolean;
}

export interface WasteType {
  waste_type_id: number;
  name: string;
  code: string;
  description?: string;
  color_code?: string;
  icon_name?: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface WasteTypeCreate {
  name: string;
  code: string;
  description?: string;
  color_code?: string;
  icon_name?: string;
  is_active?: boolean;
}

export interface WasteTypeUpdate {
  name?: string;
  code?: string;
  description?: string;
  color_code?: string;
  icon_name?: string;
  is_active?: boolean;
}

export type BinStatus = 'ACTIVE' | 'INACTIVE' | 'MAINTENANCE' | 'FULL' | 'OFFLINE' | 'DAMAGED';

export interface Bin {
  bin_id: string;
  bin_code: string;
  location_id: number;
  waste_type_id: number;
  status: BinStatus;
  capacity_liters: number;
  current_fill_percentage: number;
  last_collection_date?: string | null;
  qr_token: string;
  location?: Location;
  waste_type?: WasteType;
  created_at?: string;
  updated_at?: string;
}

export interface BinCreate {
  bin_code: string;
  location_id: number;
  waste_type_id: number;
  capacity_liters: number;
  status?: BinStatus;
}

export interface BinUpdate {
  bin_code?: string;
  location_id?: number;
  waste_type_id?: number;
  capacity_liters?: number;
  status?: BinStatus;
  current_fill_percentage?: number;
}

export interface BinQRRead {
  bin_id: string;
  bin_code: string;
  qr_token?: string;
  status: BinStatus;
  capacity_liters?: number;
  capacity_litres?: number;
  current_fill_percentage: number;
  location?: {
    location_id: number;
    name: string;
    building?: string;
    floor?: string;
  };
  waste_type?: {
    waste_type_id: number;
    name: string;
  };
  location_id?: number;
  location_name?: string;
  building?: string;
  floor?: string;
  waste_type_id?: number;
  waste_type_name?: string;
  waste_type_code?: string;
  color_code?: string;
  icon_name?: string;
}

export interface Disposal {
  disposal_id: number;
  user_id: string;
  bin_id: string;
  quantity_kg?: number | null;
  disposal_timestamp: string;
  notes?: string | null;
  points_awarded?: number;
  created_at?: string;
  bin?: Bin;
}

export interface DisposalCreate {
  bin_id: string;
  quantity_kg?: number;
  notes?: string;
}

export type ReportType = 'OVERFLOWING' | 'DAMAGED_BIN' | 'MISSING_BIN' | 'WRONG_SEGREGATION' | 'OTHER';
export type ReportStatus = 'PENDING' | 'IN_PROGRESS' | 'RESOLVED' | 'REJECTED';

export interface WasteReport {
  report_id: number;
  user_id: string;
  bin_id?: string | null;
  bin_code?: string | null;
  report_type: ReportType;
  description?: string;
  status: ReportStatus;
  image_url?: string | null;
  created_at: string;
  updated_at?: string;
  resolved_at?: string | null;
  resolved_by?: string | null;
  resolution_notes?: string | null;
  user?: {
    user_id: string;
    email: string;
    name: string;
  };
  bin?: Bin;
}

export interface ReportCreate {
  report_type: ReportType;
  bin_id?: string;
  description?: string;
  image_url?: string;
}

export interface ReportUpdate {
  status: ReportStatus;
  resolution_notes?: string;
}

export type ReadingSource = 'MANUAL' | 'SENSOR' | 'ESTIMATED';

export interface FillReading {
  reading_id: number;
  bin_id: string;
  fill_percentage: number;
  reading_timestamp: string;
  source: ReadingSource;
  confidence?: number;
  created_at?: string;
}

export interface FillReadingCreate {
  fill_percentage: number;
  source?: ReadingSource;
  reading_timestamp?: string;
  confidence?: number;
}

export interface Collection {
  collection_id: number;
  bin_id: string;
  collector_id: string;
  collection_timestamp: string;
  fill_level_before: number;
  fill_level_after: number;
  collected_quantity_kg?: number | null;
  notes?: string | null;
  bin?: Bin;
  collector?: {
    user_id: string;
    name: string;
    email: string;
  };
  created_at?: string;
}

export interface CollectionCreate {
  bin_id: string;
  fill_level_before: number;
  fill_level_after: number;
  collected_quantity_kg?: number;
  notes?: string;
}

export interface WasteClassification {
  classification_id: number;
  user_id?: string;
  image_url: string;
  predicted_waste_type?: {
    waste_type_id: number;
    name: string;
  } | null;
  predicted_category?: string;
  confidence_score?: number | null;
  model_version?: string | null;
  low_confidence?: boolean;
  is_low_confidence?: boolean;
  raw_model_output?: Record<string, any>;
  disposal_id?: number | null;
  created_at: string;
}

export interface ClassificationCreate {
  image_url: string;
  disposal_id?: number;
}

export interface FillPrediction {
  prediction_id: number;
  bin_id: string;
  target_timestamp: string;
  predicted_fill_percentage: number;
  confidence_score: number;
  model_name: string;
  features_used?: Record<string, any>;
  created_at: string;
}

export interface PredictionRequest {
  horizon_minutes?: number;
}

export type ProcessingType = 'RECYCLING' | 'COMPOSTING';

export interface ProcessingRecord {
  processing_id: number;
  collection_id: number;
  processor_id: string;
  processing_type: ProcessingType;
  quantity_kg: number;
  facility_name?: string;
  batch_number?: string;
  notes?: string;
  created_at: string;
  collection?: Collection;
}

export interface ProcessingCreate {
  collection_id: number;
  processing_type: ProcessingType;
  quantity_kg: number;
  facility_name?: string;
  batch_number?: string;
  notes?: string;
}

export type TransactionType = 'EARN' | 'REDEEM' | 'ADJUSTMENT';

export interface PointTransaction {
  transaction_id: number;
  user_id: string;
  points: number;
  transaction_type: TransactionType;
  reason?: string;
  reference_type?: string;
  reference_id?: string;
  created_at: string;
}

export interface PointBalanceRead {
  user_id: string;
  current_balance: number;
  total_earned: number;
  total_redeemed: number;
}

export interface PointAdjustmentCreate {
  points: number;
  reason: string;
}

export interface Reward {
  reward_id: number;
  name: string;
  description: string;
  points_cost: number;
  is_active: boolean;
  stock_quantity?: number | null;
  icon_name?: string;
  created_at: string;
  updated_at?: string;
}

export interface RewardCreate {
  name: string;
  description: string;
  points_cost: number;
  is_active?: boolean;
  stock_quantity?: number | null;
  icon_name?: string;
}

export interface RewardUpdate {
  name?: string;
  description?: string;
  points_cost?: number;
  is_active?: boolean;
  stock_quantity?: number | null;
  icon_name?: string;
}

export type RedemptionStatus = 'PENDING' | 'APPROVED' | 'FULFILLED' | 'CANCELLED';

export interface RewardRedemption {
  redemption_id: number;
  user_id: string;
  reward_id: number;
  points_spent: number;
  status: RedemptionStatus;
  redeemed_at: string;
  fulfilled_at?: string | null;
  notes?: string;
  reward_name?: string;
  reward?: Reward;
}

// ----------------- ANALYTICS TYPES (Phase 9) -----------------

export interface SummaryMetrics {
  disposal_count: number;
  total_collected_quantity_kg?: number | null;
  total_processed_quantity_kg?: number | null;
  total_recycled_quantity_kg?: number | null;
  total_composted_quantity_kg?: number | null;
  diversion_rate?: number | null;
}

export interface OperationalMetrics {
  total_bins: number;
  active_bins: number;
  high_fill_bins: number;
  damaged_bins: number;
  missing_bins: number;
  pending_reports: number;
  in_progress_reports: number;
  resolved_reports: number;
}

export interface ParticipationMetrics {
  total_active_students: number;
  participating_students: number;
  participation_rate?: number | null;
}

export interface GamificationMetrics {
  total_points_earned: number;
  total_points_redeemed: number;
  reward_redemptions_count: number;
}

export interface PredictionMetrics {
  prediction_count: number;
  high_fill_predictions: number;
}

export interface AnalyticsSummary {
  period_start: string;
  period_end: string;
  summary: SummaryMetrics;
  operations: OperationalMetrics;
  participation: ParticipationMetrics;
  gamification: GamificationMetrics;
  predictions: PredictionMetrics;
}

export interface WasteTypeMetric {
  waste_type_id: number;
  waste_type_name: string;
  disposal_count: number;
  collected_quantity_kg?: number | null;
  processed_quantity_kg?: number | null;
  recycled_quantity_kg?: number | null;
  composted_quantity_kg?: number | null;
}

export interface LocationMetric {
  location_id: number;
  location_name: string;
  location_type: string;
  building: string;
  floor: string;
  active_bin_count: number;
  disposal_count: number;
  collected_quantity_kg?: number | null;
  processed_quantity_kg?: number | null;
  recycled_quantity_kg?: number | null;
  composted_quantity_kg?: number | null;
  average_fill_percentage?: number | null;
}

export interface TrendPoint {
  period: string;
  disposal_count: number;
  collected_quantity_kg?: number | null;
  processed_quantity_kg?: number | null;
  recycled_quantity_kg?: number | null;
  composted_quantity_kg?: number | null;
}

export interface TrendAnalytics {
  granularity: string;
  data_points: TrendPoint[];
}

export interface CollectionAnalytics {
  total_collections: number;
  total_collected_quantity_kg?: number | null;
  average_collected_quantity_kg?: number | null;
  average_fill_before?: number | null;
  average_fill_after?: number | null;
  collections_by_day: Array<Record<string, any>>;
  frequently_collected_bins: Array<{
    bin_id: string;
    bin_code: string;
    location_name: string;
    collection_count: number;
    total_kg: number;
  }>;
}

export interface BinDetailSummary {
  bin_id: string;
  bin_code: string;
  location_name: string;
  waste_type: string;
  current_fill_percentage?: number | null;
  status: string;
}

export interface BinFillAnalytics {
  average_fill_percentage?: number | null;
  max_fill_percentage?: number | null;
  min_fill_percentage?: number | null;
  total_readings: number;
  high_fill_reading_count: number;
  high_fill_threshold: number;
  high_fill_bins: BinDetailSummary[];
}

export interface AlertItem {
  alert_type: string;
  severity: string;
  title: string;
  description: string;
  bin_id?: string;
  bin_code?: string;
  location_name?: string;
  waste_type_name?: string;
  related_id?: string;
  observed_at: string;
}

export interface ReportAnalytics {
  total_reports: number;
  pending_reports: number;
  in_progress_reports: number;
  resolved_reports: number;
  rejected_reports: number;
  reports_by_type: Record<string, number>;
  reports_by_location: Array<Record<string, any>>;
  average_resolution_time_hours?: number | null;
}

export interface ProcessingAnalytics {
  total_processing_records: number;
  total_processed_quantity_kg?: number | null;
  total_recycled_quantity_kg?: number | null;
  total_composted_quantity_kg?: number | null;
  diversion_rate?: number | null;
  processing_by_waste_type: Array<Record<string, any>>;
  processing_by_location: Array<Record<string, any>>;
}

export interface ParticipationAnalytics {
  total_active_students: number;
  students_with_at_least_one_disposal: number;
  unique_participating_students: number;
  disposal_records_count: number;
  reports_submitted_count: number;
  reports_resolved_count: number;
  participation_rate?: number | null;
}

export interface GamificationAnalytics {
  total_points_earned: number;
  total_points_redeemed: number;
  earning_transactions_count: number;
  reward_redemptions_count: number;
  unique_participating_students: number;
  points_earned_by_action: Record<string, number>;
  most_redeemed_rewards: Array<{
    reward_id: number;
    name: string;
    redemptions_count: number;
    total_points_spent: number;
  }>;
}

export interface PredictionAnalytics {
  total_predictions: number;
  average_predicted_fill?: number | null;
  max_predicted_fill?: number | null;
  high_fill_predictions_count: number;
  predictions_by_model_version: Record<string, number>;
  predictions_by_bin: Array<Record<string, any>>;
}

export interface ClassificationAnalytics {
  total_classifications: number;
  average_confidence?: number | null;
  low_confidence_count: number;
  classifications_by_waste_type: Record<string, number>;
  classifications_by_model_version: Record<string, number>;
}

// Phase 12 Gamification & Eco Stage Types
export interface EcoStage {
  stage_id: number;
  stage_name: string;
  description: string;
  flair_icon: string;
  color_hex: string;
  min_points: number;
  lifetime_earned_points: number;
  next_stage_name?: string | null;
  next_stage_min_points?: number | null;
  points_to_next_stage: number;
  progress_percentage: number;
  is_max_stage: boolean;
}

export interface LeaderboardEntry {
  rank: number;
  user_id: string;
  display_name: string;
  earned_points: number;
  stage_name: string;
  flair_icon: string;
  color_hex: string;
  is_current_user?: boolean;
}

export interface UserRank {
  rank: number;
  user_id: string;
  display_name: string;
  earned_points: number;
  stage_name: string;
  flair_icon: string;
  color_hex: string;
}

export interface LeaderboardResponse {
  period: string;
  total_participants: number;
  leaderboard: LeaderboardEntry[];
  current_user_rank?: UserRank | null;
}

// Phase 12 Admin User Management Types
export interface AdminUserSummary {
  user_id: string;
  name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  phone_number?: string | null;
  total_earned_points: number;
  current_point_balance: number;
  stage_name: string;
  flair_icon: string;
  color_hex: string;
  created_at: string;
}

export interface AdminUserCreatePayload {
  name: string;
  email: string;
  password: string;
  role: UserRole;
  phone_number?: string | null;
  is_active?: boolean;
}

export interface AdminUserUpdatePayload {
  name?: string;
  email?: string;
  role?: UserRole;
  phone_number?: string | null;
  is_active?: boolean;
  password?: string;
}

export interface CollectorPhoneUpdatePayload {
  phone_number?: string | null;
}

export interface AdminUserDetail {
  user_id: string;
  name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  phone_number?: string | null;
  created_at: string;
  total_earned_points: number;
  total_redeemed_points: number;
  current_point_balance: number;
  stage: EcoStage;
  recent_transactions: Array<{
    transaction_id: number;
    transaction_type: string;
    points: number;
    source_type: string;
    description?: string;
    created_at?: string;
  }>;
  recent_redemptions: Array<{
    redemption_id: number;
    reward_name: string;
    points_spent: number;
    status: string;
    redeemed_at?: string;
  }>;
  total_disposals: number;
  total_reports: number;
}

export interface AdminUserListResponse {
  total_count: number;
  users: AdminUserSummary[];
}

// ==========================================
// Collector Attendance & Task Types
// ==========================================

export type AttendanceStatus = 'ON_SHIFT' | 'CHECKED_OUT' | 'NOT_CHECKED_IN';

export interface AttendanceRecord {
  attendance_id: number;
  collector_id: string;
  attendance_date: string;
  check_in_at: string;
  check_out_at?: string | null;
  status: AttendanceStatus;
  notes?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface CollectorShiftSummary {
  collector_id: string;
  collector_name: string;
  name?: string;
  collector_email: string;
  email?: string;
  phone_number?: string | null;
  has_sms_configured?: boolean;
  has_phone_configured?: boolean;
  is_active: boolean;
  status: AttendanceStatus;
  attendance_status?: string;
  active_session?: AttendanceRecord | null;
  last_session?: AttendanceRecord | null;
  active_task_count: number;
  active_tasks_count?: number;
  check_in_at?: string | null;
  check_out_at?: string | null;
}

export interface AdminAttendanceOverview {
  total_collectors: number;
  on_shift_count: number;
  on_shift_collectors?: number;
  not_checked_in_count: number;
  not_checked_in_collectors?: number;
  with_active_tasks_count: number;
  collectors_with_active_tasks?: number;
  overdue_tasks_count: number;
  collectors: CollectorShiftSummary[];
  campus_date: string;
}

export type TaskType = 'COLLECTION' | 'INSPECTION' | 'ISSUE_RESPONSE';
export type TaskPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
export type TaskStatus = 'ASSIGNED' | 'ACCEPTED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';

export interface CollectionTask {
  task_id: number;
  task_type: TaskType;
  collector_id: string;
  bin_id?: string | null;
  location_id?: number | null;
  report_id?: number | null;
  priority: TaskPriority;
  title: string;
  instructions?: string | null;
  due_date?: string | null;
  status: TaskStatus;
  created_by: string;
  assigned_at: string;
  started_at?: string | null;
  completed_at?: string | null;
  completion_notes?: string | null;
  cancelled_at?: string | null;
  cancellation_reason?: string | null;
  collection_id?: number | null;
  collector_name?: string | null;
  collector_email?: string | null;
  bin_code?: string | null;
  location_name?: string | null;
  report_title?: string | null;
  report_type?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface TaskCreatePayload {
  task_type: TaskType;
  collector_id: string;
  bin_id?: string | null;
  location_id?: number | null;
  report_id?: number | null;
  priority: TaskPriority;
  title: string;
  instructions?: string | null;
  due_date?: string | null;
}

export interface ReportDelegationPayload {
  report_id: number;
  collector_id: string;
  priority: TaskPriority;
  instructions?: string | null;
  due_date?: string | null;
}

export interface TaskStatusUpdatePayload {
  status: TaskStatus;
  completion_notes?: string | null;
  collection_id?: number | null;
}

export interface TaskReassignPayload {
  collector_id: string;
  notes?: string | null;
}

export interface TaskCancelPayload {
  reason: string;
}

