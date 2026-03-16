import { useState, useRef } from 'react';
import { Upload, CheckCircle, FileText } from 'lucide-react';

interface UploadPDFProps {
  onUploadSuccess: (fileName: string) => void;
}

export function UploadPDF({ onUploadSuccess }: UploadPDFProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setUploadSuccess(false);
    } else {
      alert('Please select a valid PDF file');
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleUpload = () => {
    if (selectedFile) {
      // Simulate upload
      setTimeout(() => {
        setUploadSuccess(true);
        onUploadSuccess(selectedFile.name);
        setTimeout(() => {
          setUploadSuccess(false);
          setSelectedFile(null);
          if (fileInputRef.current) {
            fileInputRef.current.value = '';
          }
        }, 3000);
      }, 500);
    }
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-3">Upload PDF</h1>
        <p className="text-gray-600 text-lg">
          Select and upload payslip PDF files to the system.
        </p>
      </div>

      <div className="max-w-2xl">
        <div className="bg-white rounded-lg shadow-md p-8 border border-gray-200">
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
            <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-700 mb-2">
              Select PDF File
            </h3>
            <p className="text-gray-500 mb-6">
              Click below to select a payslip PDF file to upload
            </p>
            
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleFileSelect}
              className="hidden"
              id="pdf-upload"
            />
            
            <label
              htmlFor="pdf-upload"
              className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg cursor-pointer hover:bg-blue-700 transition-colors"
            >
              Choose PDF File
            </label>
          </div>

          {selectedFile && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3 mb-4">
                <FileText className="w-5 h-5 text-blue-600" />
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{selectedFile.name}</p>
                  <p className="text-sm text-gray-500">
                    {(selectedFile.size / 1024).toFixed(2)} KB
                  </p>
                </div>
              </div>
              
              <button
                onClick={handleUpload}
                className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Upload Payslip
              </button>
            </div>
          )}

          {uploadSuccess && (
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3">
              <CheckCircle className="w-6 h-6 text-green-600" />
              <div className="flex-1">
                <p className="font-semibold text-green-900">Upload Successful!</p>
                <p className="text-sm text-green-700">
                  Your payslip file has been uploaded successfully.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
