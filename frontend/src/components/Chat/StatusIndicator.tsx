/**
 * Real-time status indicator for agent processing
 */

interface StatusIndicatorProps {
  status: string;
}

export function StatusIndicator({ status }: StatusIndicatorProps) {
  if (!status) return null;

  return (
    <div className="flex items-start mb-4">
      <div className="max-w-[70%] bg-gray-50 border border-gray-200 rounded-lg px-4 py-2">
        <div className="flex items-center gap-2">
          <div className="flex gap-1">
            <span className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></span>
            <span className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style={{ animationDelay: "0.2s" }}></span>
            <span className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style={{ animationDelay: "0.4s" }}></span>
          </div>
          <span className="text-sm text-gray-600">{status}</span>
        </div>
      </div>
    </div>
  );
}
