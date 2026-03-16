import { Users, Calendar, CheckCircle, AlertCircle } from 'lucide-react';

interface DashboardProps {
  stats: {
    totalEmployees: number;
    lastUploadDate: string;
    payslipsSentToday: number;
    errors: number;
  };
}

export function Dashboard({ stats }: DashboardProps) {
  const cards = [
    {
      title: 'Total Employees',
      value: stats.totalEmployees,
      icon: Users,
      color: 'bg-blue-50 text-blue-600',
    },
    {
      title: 'Last Upload Date',
      value: stats.lastUploadDate,
      icon: Calendar,
      color: 'bg-gray-50 text-gray-600',
    },
    {
      title: 'Payslips Sent Today',
      value: stats.payslipsSentToday,
      icon: CheckCircle,
      color: 'bg-green-50 text-green-600',
    },
    {
      title: 'Errors',
      value: stats.errors,
      icon: AlertCircle,
      color: stats.errors > 0 ? 'bg-red-50 text-red-600' : 'bg-gray-50 text-gray-600',
    },
  ];

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-3">Dashboard</h1>
        <p className="text-gray-600 text-lg">
          Welcome to the Payslip Management System. Here you can view an overview of your payslip operations.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <div
              key={card.title}
              className="bg-white rounded-lg shadow-md p-6 border border-gray-200"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-lg ${card.color}`}>
                  <Icon className="w-6 h-6" />
                </div>
              </div>
              <h3 className="text-gray-600 text-sm font-medium mb-1">{card.title}</h3>
              <p className="text-3xl font-bold text-gray-900">{card.value}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
