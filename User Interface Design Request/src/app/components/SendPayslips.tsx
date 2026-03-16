import { useState } from 'react';
import { CheckCircle, AlertCircle, FileText, Users } from 'lucide-react';

interface SendPayslipsProps {
  payslipsLoaded: boolean;
  employeeListLoaded: boolean;
}

export function SendPayslips({ payslipsLoaded, employeeListLoaded }: SendPayslipsProps) {
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [sendSuccess, setSendSuccess] = useState(false);

  const canSend = payslipsLoaded && employeeListLoaded;

  const handleSendClick = () => {
    if (canSend) {
      setShowConfirmation(true);
    }
  };

  const handleConfirmSend = () => {
    setShowConfirmation(false);
    // Simulate sending
    setTimeout(() => {
      setSendSuccess(true);
      setTimeout(() => {
        setSendSuccess(false);
      }, 3000);
    }, 500);
  };

  const handleCancelSend = () => {
    setShowConfirmation(false);
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-3">Send Payslips</h1>
        <p className="text-gray-600 text-lg">
          Send payslips to all employees in the system.
        </p>
      </div>

      <div className="max-w-2xl">
        <div className="bg-white rounded-lg shadow-md p-8 border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            System Requirements
          </h2>

          <div className="space-y-4 mb-8">
            <div className={`p-4 rounded-lg border-2 ${
              payslipsLoaded 
                ? 'bg-green-50 border-green-200' 
                : 'bg-gray-50 border-gray-200'
            }`}>
              <div className="flex items-center gap-3">
                {payslipsLoaded ? (
                  <CheckCircle className="w-6 h-6 text-green-600" />
                ) : (
                  <AlertCircle className="w-6 h-6 text-gray-400" />
                )}
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4" />
                    <p className="font-medium text-gray-900">Payslips File Loaded</p>
                  </div>
                  <p className={`text-sm ${
                    payslipsLoaded ? 'text-green-700' : 'text-gray-500'
                  }`}>
                    {payslipsLoaded ? 'Ready to send' : 'Please upload payslips first'}
                  </p>
                </div>
              </div>
            </div>

            <div className={`p-4 rounded-lg border-2 ${
              employeeListLoaded 
                ? 'bg-green-50 border-green-200' 
                : 'bg-gray-50 border-gray-200'
            }`}>
              <div className="flex items-center gap-3">
                {employeeListLoaded ? (
                  <CheckCircle className="w-6 h-6 text-green-600" />
                ) : (
                  <AlertCircle className="w-6 h-6 text-gray-400" />
                )}
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <Users className="w-4 h-4" />
                    <p className="font-medium text-gray-900">Employee List Loaded</p>
                  </div>
                  <p className={`text-sm ${
                    employeeListLoaded ? 'text-green-700' : 'text-gray-500'
                  }`}>
                    {employeeListLoaded ? 'Ready to send' : 'Employee list not available'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <button
            onClick={handleSendClick}
            disabled={!canSend}
            className={`w-full px-6 py-4 rounded-lg font-semibold text-white transition-colors ${
              canSend
                ? 'bg-blue-600 hover:bg-blue-700 cursor-pointer'
                : 'bg-gray-300 cursor-not-allowed'
            }`}
          >
            {canSend ? 'Send Payslips to All Employees' : 'Requirements Not Met'}
          </button>

          {!canSend && (
            <p className="mt-4 text-sm text-gray-500 text-center">
              Please ensure both payslips file and employee list are loaded before sending.
            </p>
          )}

          {sendSuccess && (
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3">
              <CheckCircle className="w-6 h-6 text-green-600" />
              <div className="flex-1">
                <p className="font-semibold text-green-900">Payslips Sent Successfully!</p>
                <p className="text-sm text-green-700">
                  All payslips have been sent to employees.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {showConfirmation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold text-gray-900 mb-4">
              Confirm Send Payslips
            </h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to send payslips to all employees? This action cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={handleCancelSend}
                className="px-6 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmSend}
                className="px-6 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors"
              >
                Confirm Send
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
