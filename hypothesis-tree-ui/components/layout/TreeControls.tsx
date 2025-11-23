/**
 * Tree view controls for collapse/expand and zoom
 */

interface TreeControlsProps {
  onCollapseAll: (level: 'L1' | 'L2' | 'L3') => void;
  onExpandAll: (level: 'L1' | 'L2' | 'L3') => void;
  zoom: number;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onZoomReset: () => void;
}

export function TreeControls({
  onCollapseAll,
  onExpandAll,
  zoom,
  onZoomIn,
  onZoomOut,
  onZoomReset,
}: TreeControlsProps) {
  return (
    <div className="bg-gray-800 border-b border-gray-700 px-4 py-3 flex items-center justify-between">
      {/* Collapse/Expand Controls */}
      <div className="flex items-center gap-4">
        <span className="text-sm font-medium text-gray-400">Collapse/Expand:</span>

        <div className="flex gap-2">
          <button
            onClick={() => onCollapseAll('L1')}
            className="px-2 py-1 text-xs bg-purple-600 hover:bg-purple-700 rounded"
            title="Collapse all L1"
          >
            🟣 All
          </button>
          <button
            onClick={() => onExpandAll('L1')}
            className="px-2 py-1 text-xs bg-purple-600/50 hover:bg-purple-600/70 rounded"
            title="Expand all L1"
          >
            🟣 Expand
          </button>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => onCollapseAll('L2')}
            className="px-2 py-1 text-xs bg-blue-600 hover:bg-blue-700 rounded"
            title="Collapse all L2"
          >
            🔵 All
          </button>
          <button
            onClick={() => onExpandAll('L2')}
            className="px-2 py-1 text-xs bg-blue-600/50 hover:bg-blue-600/70 rounded"
            title="Expand all L2"
          >
            🔵 Expand
          </button>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => onCollapseAll('L3')}
            className="px-2 py-1 text-xs bg-green-600 hover:bg-green-700 rounded"
            title="Collapse all L3"
          >
            🟢 All
          </button>
          <button
            onClick={() => onExpandAll('L3')}
            className="px-2 py-1 text-xs bg-green-600/50 hover:bg-green-600/70 rounded"
            title="Expand all L3"
          >
            🟢 Expand
          </button>
        </div>
      </div>

      {/* Zoom Controls */}
      <div className="flex items-center gap-4">
        <span className="text-sm font-medium text-gray-400">Zoom:</span>

        <div className="flex items-center gap-2">
          <button
            onClick={onZoomOut}
            disabled={zoom <= 0.5}
            className="px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded disabled:opacity-50 disabled:cursor-not-allowed"
            title="Zoom out"
          >
            −
          </button>

          <span className="text-sm w-12 text-center">{Math.round(zoom * 100)}%</span>

          <button
            onClick={onZoomIn}
            disabled={zoom >= 2}
            className="px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded disabled:opacity-50 disabled:cursor-not-allowed"
            title="Zoom in"
          >
            +
          </button>

          <button
            onClick={onZoomReset}
            className="px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded ml-2"
            title="Reset zoom (100%)"
          >
            Reset
          </button>
        </div>

        <div className="text-xs text-gray-500">
          (Mouse wheel to zoom)
        </div>
      </div>
    </div>
  );
}
