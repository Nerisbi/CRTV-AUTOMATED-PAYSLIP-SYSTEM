import { LayoutDashboard, Upload, Send, ScrollText, LogOut } from 'lucide-react';

interface SidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
  onExitClick: () => void;
}

export function Sidebar({ activeSection, onSectionChange, onExitClick }: SidebarProps) {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'upload', label: 'Upload PDF', icon: Upload },
    { id: 'send', label: 'Send Payslips', icon: Send },
    { id: 'logs', label: 'Logs', icon: ScrollText },
  ];

  return (
    <div className="w-64 bg-blue-900 h-screen flex flex-col text-white">
      <div className="p-6 border-b border-blue-800">
        <h1 className="text-2xl font-bold">Payslip Manager</h1>
      </div>
      
      <nav className="flex-1 p-4">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeSection === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => onSectionChange(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-colors ${
                isActive 
                  ? 'bg-blue-700 text-white' 
                  : 'text-blue-100 hover:bg-blue-800'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="p-4 border-t border-blue-800">
        <button
          onClick={onExitClick}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-blue-100 hover:bg-blue-800 transition-colors"
        >
          <LogOut className="w-5 h-5" />
          <span>Exit</span>
        </button>
      </div>
    </div>
  );
}
