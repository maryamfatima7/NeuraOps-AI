export type Severity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type IncidentStatus = 'OPEN' | 'INVESTIGATING' | 'MITIGATED' | 'RESOLVED';

export type HealthSummary = {
  overall_health: string;
  active_incidents: number;
  error_rate: number;
  average_latency: number;
  requests_per_minute: number;
  services_monitored: number;
  recent_alerts: Array<{ rule: string; service: string; severity: string; status: string; created_at: string }>;
  recent_incidents: Array<{ id: number; title: string; severity: string; status: string; detected_time: string }>;
  ai_detected_anomalies: Array<{ metric: string; service: string; severity: string; deviation: number; timestamp: string }>;
  logs: Array<{ service: string; level: string; message: string; timestamp: string }>;
};

export type ServiceSummary = {
  id: number;
  name: string;
  status: string;
  uptime: number;
  request_rate: number;
  error_rate: number;
  latency_ms: number;
  description?: string;
  dependencies?: string;
  owner?: string;
};

export type IncidentDetail = {
  id: number;
  title: string;
  description: string;
  severity: string;
  status: string;
  affected_services: string[];
  detected_time: string;
  updated_time: string;
  root_cause?: string;
  ai_analysis?: string;
  recommendations?: string;
  ai_summary?: string;
  related_logs: LogEntry[];
  anomalies: Anomaly[];
};

export type Incident = IncidentDetail;

export type LogEntry = {
  id: number;
  service: string;
  level: string;
  message: string;
  summary?: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
  correlation_id?: string;
};

export type Anomaly = {
  metric: string;
  observed_value: number;
  expected_baseline: number;
  deviation?: number;
};

export type Alert = {
  id: number;
  rule: string;
  service: string;
  severity: string;
  status: string;
  current_value: number;
  threshold: number;
  created_at?: string;
};

export type AIAnalysis = {
  summary: string;
  suspected_root_cause: string;
  confidence: number;
  evidence?: string[];
  affected_components?: string[];
  recommended_actions?: string[];
  investigation_steps?: string[];
};

export type HealthStatus = {
  status: string;
  database: string;
  redis: string;
  telemetry: string;
  ai_service: string;
};
