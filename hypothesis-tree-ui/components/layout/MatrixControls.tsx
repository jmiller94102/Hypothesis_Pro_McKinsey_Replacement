/**
 * Matrix view controls for zoom
 */

interface MatrixControlsProps {
  zoom: number;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onZoomReset: () => void;
}

export function MatrixControls({
  zoom,
  onZoomIn,
  onZoomOut,
  onZoomReset,
}: MatrixControlsProps) {
  return (
    <div className="bg-gray-800 border-b border-gray-700 px-4 py-3 flex items-center justify-between">
      {/* Empty left side for visual balance */}
      <div></div>

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
