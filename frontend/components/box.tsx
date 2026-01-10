import React from "react";

export default function Box({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative bg-gradient-to-br from-gray-900 to-black rounded-3xl border border-gray-800 overflow-hidden">
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 px-6 py-3 border-b border-gray-700 flex justify-between">
        <span className="text-xs text-gray-400">AI Response System</span>
      </div>

      <div className="h-[70vh] overflow-y-auto p-6 space-y-6 custom-scrollbar">
        {children}
      </div>

      <div className="bg-gradient-to-r from-gray-800 to-gray-900 px-6 py-3 border-t border-gray-700 flex justify-between">
        <span className="text-xs text-gray-400">Ready</span>
        <span className="text-xs text-gray-500">Powered by AI</span>
      </div>
    </div>
  );
}
