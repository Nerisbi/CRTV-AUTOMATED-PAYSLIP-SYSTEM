import { useState } from 'react';
import { Sidebar } from '@/app/components/Sidebar';
import { Dashboard } from '@/app/components/Dashboard';
import { UploadPDF } from '@/app/components/UploadPDF';
import { SendPayslips } from '@/app/components/SendPayslips';
import { Logs } from '@/app/components/Logs';

export default function App() {
  const [activeSection, setActiveSection] = useState('dashboard');
  const [showExitConfirmation, setShowExitConfirmation] = useState(false);
  const [payslipsLoaded, setPayslipsLoaded] = useState(true); // Mock data
  const [employeeListLoaded] = useState(true); // Mock data

  // Dashboard stats
  const [dashboardStats, setDashboardStats] = useState({
    totalEmployees: 45,
    lastUploadDate: '2026-01-28',
    payslipsSentToday: 45,
    errors: 0,
  });

  const handleExitClick = () => {
    setShowExitConfirmation(true);
  };

  const handleConfirmExit = () => {
    // In a real application, this would close the window or redirect
    alert('Application would close here. In a web app, you might redirect to a logout page.');
    setShowExitConfirmation(false);
  };

  const handleCancelExit = () => {
    setShowExitConfirmation(false);
  };

  const handleUploadSuccess = (fileName: string) => {
    setPayslipsLoaded(true);
    setDashboardStats(prev => ({
      ...prev,
      lastUploadDate: new Date().toISOString().split('T')[0],
    }));
    console.log('Uploaded:', fileName);
  };

  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return <Dashboard stats={dashboardStats} />;
      case 'upload':
        return <UploadPDF onUploadSuccess={handleUploadSuccess} />;
      case 'send':
        return (
          <SendPayslips
            payslipsLoaded={payslipsLoaded}
            employeeListLoaded={employeeListLoaded}
          />
        );
      case 'logs':
        return <Logs />;
      default:
        return <Dashboard stats={dashboardStats} />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar
        activeSection={activeSection}
        onSectionChange={setActiveSection}
        onExitClick={handleExitClick}
      />
      
      <div className="flex-1 overflow-y-auto">
        {renderContent()}
      </div>

      {showExitConfirmation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold text-gray-900 mb-4">
              Exit System
            </h3>
            <p className="text-gray-600 mb-6">
              Do you want to exit the system? Any unsaved changes will be lost.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={handleCancelExit}
                className="px-6 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmExit}
                className="px-6 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700 transition-colors"
              >
                Exit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
