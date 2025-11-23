/**
 * Collapsible debug panel with independent scrolling
 */

import { DebugLog } from '@/lib/types';

interface DebugPanelProps {
  logs: DebugLog[];
  isOpen: boolean;
  onToggle: () => void;
}

export function DebugPanel({ logs, isOpen, onToggle }: DebugPanelProps) {
  const getLogColor = (type: DebugLog['type']) => {
    switch (type) {
      case 'error':
        return 'text-red-400';
      case 'success':
        return 'text-green-400';
      case 'warning':
        return 'text-yellow-400';
      default:
        return 'text-gray-300';
    }
  };

  return (
    <div
      className={`border-t border-gray-700 bg-gray-950 transition-all duration-200 ${
        isOpen ? 'h-64' : 'h-10'
      }`}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-4 h-10 cursor-pointer hover:bg-gray-900"
        onClick={onToggle}
      >
        <span className="text-sm font-medium flex items-center gap-2">
          <span className="text-gray-400">{isOpen ? '▼' : '▶'}</span>
          DEBUG PANEL
        </span>
        <span className="text-xs text-gray-500">{logs.length} events</span>
      </div>

      {/* Logs - Independent scroll */}
      {isOpen && (
        <div className="overflow-y-auto h-[calc(100%-2.5rem)] px-4 pb-4 font-mono text-xs">
          {logs.length === 0 ? (
            <div className="text-gray-500 italic py-2">No events yet</div>
          ) : (
            logs.map((log, i) => (
              <div key={i} className={`py-1 ${getLogColor(log.type)}`}>
                <span className="text-gray-500">
                  [{new Date(log.timestamp).toLocaleTimeString()}]
                </span>{' '}
                {log.message}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
