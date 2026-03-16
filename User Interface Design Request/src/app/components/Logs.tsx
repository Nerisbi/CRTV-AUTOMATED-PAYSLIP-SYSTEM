import { ScrollText } from 'lucide-react';

interface LogEntry {
  timestamp: string;
  type: 'info' | 'success' | 'error';
  message: string;
}

export function Logs() {
  // Mock log entries
  const logs: LogEntry[] = [
    {
      timestamp: '2026-01-28 14:32:15',
      type: 'success',
      message: 'Payslips sent successfully to 45 employees',
    },
    {
      timestamp: '2026-01-28 14:31:50',
      type: 'info',
      message: 'User admin initiated payslip distribution',
    },
    {
      timestamp: '2026-01-28 14:30:22',
      type: 'success',
      message: 'PDF file uploaded: January_2026_Payslips.pdf',
    },
    {
      timestamp: '2026-01-28 14:15:08',
      type: 'info',
      message: 'Employee list loaded: 45 employees',
    },
    {
      timestamp: '2026-01-28 10:45:33',
      type: 'success',
      message: 'System startup completed',
    },
    {
      timestamp: '2026-01-27 16:22:11',
      type: 'success',
      message: 'Payslips sent successfully to 45 employees',
    },
    {
      timestamp: '2026-01-27 16:20:05',
      type: 'info',
      message: 'User admin initiated payslip distribution',
    },
    {
      timestamp: '2026-01-27 16:18:44',
      type: 'success',
      message: 'PDF file uploaded: December_2025_Payslips.pdf',
    },
    {
      timestamp: '2026-01-27 15:55:12',
      type: 'error',
      message: 'Failed to upload file: Invalid PDF format',
    },
    {
      timestamp: '2026-01-27 15:50:30',
      type: 'info',
      message: 'User admin logged in',
    },
  ];

  const getLogColor = (type: LogEntry['type']) => {
    switch (type) {
      case 'success':
        return 'text-green-700 bg-green-50';
      case 'error':
        return 'text-red-700 bg-red-50';
      default:
        return 'text-gray-700 bg-gray-50';
    }
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-3">System Logs</h1>
        <p className="text-gray-600 text-lg">
          View system activity logs for administrative verification. Read-only access.
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
        <div className="bg-gray-50 border-b border-gray-200 p-4 flex items-center gap-3">
          <ScrollText className="w-5 h-5 text-gray-600" />
          <h2 className="font-semibold text-gray-900">Activity Log</h2>
        </div>
        
        <div className="h-[calc(100vh-300px)] overflow-y-auto">
          <div className="p-4 space-y-2">
            {logs.map((log, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg border ${getLogColor(log.type)}`}
              >
                <div className="flex items-start gap-3">
                  <span className="text-sm font-mono font-medium whitespace-nowrap">
                    {log.timestamp}
                  </span>
                  <span className="text-sm flex-1">{log.message}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-800">
          <strong>Note:</strong> This log is read-only and intended for administrative verification purposes.
        </p>
      </div>
    </div>
  );
}
