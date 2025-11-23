/**
 * TreeNode component with visual differentiation and inline editing
 */

import { useState } from 'react';
import { InlineEditor } from './InlineEditor';
import type { L1Category, L2Branch, L3Leaf, NodeLevel } from '@/lib/types';

interface TreeNodeProps {
  level: NodeLevel;
  data: L1Category | L2Branch | L3Leaf;
  path: string[];
  onUpdate: (path: string[], data: any) => void;
  onDelete: (path: string[]) => void;
  onAdd: (path: string[], level: NodeLevel) => void;
}

export function TreeNode({ level, data, path, onUpdate, onDelete, onAdd }: TreeNodeProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Visual styles by level
  const levelStyles = {
    L1: 'bg-purple-900/30 border-l-4 border-purple-500 text-purple-100 text-lg font-bold',
    L2: 'bg-blue-900/30 border-l-4 border-blue-500 text-blue-100 text-base font-semibold ml-8',
    L3: 'bg-green-900/30 border-l-4 border-green-500 text-green-100 text-sm font-normal ml-16',
  };

  const levelIcon = {
    L1: '🟣',
    L2: '🔵',
    L3: '🟢',
  };

  const hasChildren =
    level === 'L1'
      ? Object.keys((data as L1Category).L2_branches || {}).length > 0
      : level === 'L2'
      ? ((data as L2Branch).L3_leaves || []).length > 0
      : false;

  function handleUpdate(newLabel: string) {
    onUpdate(path, { ...data, label: newLabel });
    setIsEditing(false);
  }

  function handleDelete() {
    if (showDeleteConfirm) {
      onDelete(path);
      setShowDeleteConfirm(false);
    } else {
      setShowDeleteConfirm(true);
      setTimeout(() => setShowDeleteConfirm(false), 3000);
    }
  }

  return (
    <div className="mb-2">
      {/* Node header */}
      <div className={`p-3 rounded ${levelStyles[level]}`}>
        <div className="flex items-center gap-2">
          {/* Collapse/Expand */}
          {hasChildren && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="hover:bg-white/10 px-1 rounded"
            >
              {isExpanded ? '[−]' : '[+]'}
            </button>
          )}
          {!hasChildren && <span className="w-6" />}

          {/* Level indicator */}
          <span className="opacity-60">{levelIcon[level]}</span>

          {/* Inline editor or label */}
          {isEditing ? (
            <InlineEditor
              value={data.label}
              onSave={handleUpdate}
              onCancel={() => setIsEditing(false)}
              placeholder="Enter label"
            />
          ) : (
            <span
              onDoubleClick={() => setIsEditing(true)}
              className="flex-1 cursor-text"
              title="Double-click to edit"
            >
              {data.label}:{' '}
              {level !== 'L3' ? (data as L1Category | L2Branch).question : (data as L3Leaf).question}
            </span>
          )}

          {/* Action buttons */}
          {!isEditing && (
            <div className="ml-auto flex gap-1">
              <button
                onClick={() => setIsEditing(true)}
                className="text-xs hover:bg-white/10 px-2 py-1 rounded"
                title="Edit"
              >
                ✏️
              </button>
              <button
                onClick={handleDelete}
                className={`text-xs px-2 py-1 rounded ${
                  showDeleteConfirm
                    ? 'bg-red-600 hover:bg-red-700'
                    : 'hover:bg-white/10'
                }`}
                title={showDeleteConfirm ? 'Click again to confirm' : 'Delete'}
              >
                🗑️
              </button>
            </div>
          )}
        </div>

        {/* L3 metadata */}
        {level === 'L3' && (
          <div className="mt-2 ml-8 text-xs opacity-75 flex gap-2">
            <span className="bg-gray-700 px-2 py-0.5 rounded">
              {(data as L3Leaf).metric_type}
            </span>
            <span>Target: {(data as L3Leaf).target}</span>
          </div>
        )}
      </div>

      {/* Children */}
      {isExpanded && hasChildren && (
        <div className="mt-2">
          {level === 'L1' &&
            Object.entries((data as L1Category).L2_branches).map(([key, l2]) => (
              <TreeNode
                key={key}
                level="L2"
                data={l2}
                path={[...path, key]}
                onUpdate={onUpdate}
                onDelete={onDelete}
                onAdd={onAdd}
              />
            ))}

          {level === 'L2' &&
            (data as L2Branch).L3_leaves.map((l3, i) => (
              <TreeNode
                key={i}
                level="L3"
                data={l3}
                path={[...path, String(i)]}
                onUpdate={onUpdate}
                onDelete={onDelete}
                onAdd={onAdd}
              />
            ))}
        </div>
      )}

      {/* Add child button */}
      {isExpanded && level !== 'L3' && (
        <button
          onClick={() => onAdd(path, level === 'L1' ? 'L2' : 'L3')}
          className={`mt-1 text-xs text-gray-400 hover:text-gray-200 ${
            level === 'L1' ? 'ml-12' : 'ml-20'
          }`}
        >
          [+ Add {level === 'L1' ? 'L2 Branch' : 'L3 Leaf'}]
        </button>
      )}
    </div>
  );
}
