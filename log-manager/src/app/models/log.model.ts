export interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  source: string;
  [key: string]: any;
}

export interface LogFilter {
  startDate?: string;
  endDate?: string;
  level?: string;
  source?: string;
  platform?: string | null;
  keyword?: string;
  [key: string]: any;
}
