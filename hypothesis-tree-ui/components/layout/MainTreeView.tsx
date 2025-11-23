/**
 * Main tree visualization with independent X/Y scrolling and zoom
 */

import { useRef, useEffect } from 'react';
import { TreeNode } from '../tree/TreeNode';
import type { HypothesisTree, NodeLevel } from '@/lib/types';

interface MainTreeViewProps {
  tree: HypothesisTree | null;
  onUpdateNode: (path: string[], data: any) => void;
  onDeleteNode: (path: string[]) => void;
  onAddNode: (path: string[], level: NodeLevel) => void;
  zoom: number;
  onZoomChange: (zoom: number) => void;
  expandedNodes: Set<string>;
}

export function MainTreeView({
  tree,
  onUpdateNode,
  onDeleteNode,
  onAddNode,
  zoom,
  onZoomChange,
  expandedNodes,
}: MainTreeViewProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  // Mouse wheel zoom
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleWheel = (e: WheelEvent) => {
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();
        const delta = e.deltaY > 0 ? -0.1 : 0.1;
        const newZoom = Math.max(0.5, Math.min(2, zoom + delta));
        onZoomChange(newZoom);
      }
    };

    container.addEventListener('wheel', handleWheel, { passive: false });
    return () => container.removeEventListener('wheel', handleWheel);
  }, [zoom, onZoomChange]);

  if (!tree) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-900 text-gray-500">
        <div className="text-center">
          <div className="text-4xl mb-4">📊</div>
          <div className="text-lg">No tree loaded</div>
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="flex-1 overflow-auto bg-gray-900">
      {/* Scrollable container with zoom - independent X/Y scroll */}
      <div
        className="p-8 min-w-max origin-top-left transition-transform"
        style={{ transform: `scale(${zoom})` }}
      >
        <div className="mb-6">
          <h1 className="text-2xl font-bold mb-2">{tree.problem}</h1>
          <p className="text-sm text-gray-400">
            Framework: {tree.framework_name}
          </p>
          {tree.description && (
            <p className="text-sm text-gray-500 mt-1">{tree.description}</p>
          )}
        </div>

        {/* Render L1 categories */}
        <div className="space-y-3">
          {Object.entries(tree.tree).map(([key, l1]) => (
            <TreeNode
              key={key}
              level="L1"
              data={l1}
              path={[key]}
              onUpdate={onUpdateNode}
              onDelete={onDeleteNode}
              onAdd={onAddNode}
              expandedNodes={expandedNodes}
            />
          ))}
        </div>

        {/* Add L1 button */}
        <button
          onClick={() => onAddNode([], 'L1')}
          className="mt-4 text-sm text-blue-400 hover:text-blue-300"
        >
          [+ Add L1 Category]
        </button>
      </div>
    </div>
  );
}
