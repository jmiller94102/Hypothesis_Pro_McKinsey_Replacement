'use client';

import React, { useState } from 'react';
import { PriorityMatrix } from '@/lib/types';

interface Matrix2x2EditorProps {
  projectId: string;
  matrixData: PriorityMatrix;
  onMatrixUpdate: (updatedMatrix: PriorityMatrix) => void;
  onAddItem: (quadrant: 'Q1' | 'Q2' | 'Q3' | 'Q4', item: string) => Promise<void>;
  onDeleteItem: (quadrant: 'Q1' | 'Q2' | 'Q3' | 'Q4', itemIndex: number) => Promise<void>;
  onEditItem: (quadrant: 'Q1' | 'Q2' | 'Q3' | 'Q4', itemIndex: number, newText: string) => Promise<void>;
  onMoveItem: (fromQuadrant: 'Q1' | 'Q2' | 'Q3' | 'Q4', toQuadrant: 'Q1' | 'Q2' | 'Q3' | 'Q4', itemIndex: number) => Promise<void>;
}

export function Matrix2x2Editor({
  projectId,
  matrixData,
  onMatrixUpdate,
  onAddItem,
  onDeleteItem,
  onEditItem,
  onMoveItem,
}: Matrix2x2EditorProps) {
  const { quadrants, placements, x_axis, y_axis, recommendations } = matrixData;

  const [editingItem, setEditingItem] = useState<{ quadrant: string; index: number } | null>(null);
  const [editText, setEditText] = useState('');
  const [addingTo, setAddingTo] = useState<string | null>(null);
  const [newItemText, setNewItemText] = useState('');
  const [draggedItem, setDraggedItem] = useState<{ quadrant: string; index: number } | null>(null);

  const handleStartEdit = (quadrant: string, index: number, currentText: string) => {
    setEditingItem({ quadrant, index });
    setEditText(currentText);
  };

  const handleSaveEdit = async () => {
    if (!editingItem || !editText.trim()) return;

    try {
      await onEditItem(editingItem.quadrant as any, editingItem.index, editText.trim());
      setEditingItem(null);
      setEditText('');
    } catch (error) {
      console.error('Failed to edit item:', error);
      alert('Failed to edit item');
    }
  };

  const handleCancelEdit = () => {
    setEditingItem(null);
    setEditText('');
  };

  const handleDelete = async (quadrant: string, index: number) => {
    if (!confirm('Delete this item?')) return;

    try {
      await onDeleteItem(quadrant as any, index);
    } catch (error) {
      console.error('Failed to delete item:', error);
      alert('Failed to delete item');
    }
  };

  const handleStartAdd = (quadrant: string) => {
    setAddingTo(quadrant);
    setNewItemText('');
  };

  const handleSaveAdd = async () => {
    if (!addingTo || !newItemText.trim()) return;

    try {
      await onAddItem(addingTo as any, newItemText.trim());
      setAddingTo(null);
      setNewItemText('');
    } catch (error) {
      console.error('Failed to add item:', error);
      alert('Failed to add item');
    }
  };

  const handleCancelAdd = () => {
    setAddingTo(null);
    setNewItemText('');
  };

  // Drag and drop handlers
  const handleDragStart = (quadrant: string, index: number) => {
    setDraggedItem({ quadrant, index });
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault(); // Allow drop
  };

  const handleDrop = async (e: React.DragEvent, toQuadrant: string) => {
    e.preventDefault();

    if (!draggedItem) return;

    const fromQuadrant = draggedItem.quadrant;
    const itemIndex = draggedItem.index;

    if (fromQuadrant === toQuadrant) {
      // Same quadrant, no action needed
      setDraggedItem(null);
      return;
    }

    try {
      await onMoveItem(fromQuadrant as any, toQuadrant as any, itemIndex);
      setDraggedItem(null);
    } catch (error) {
      console.error('Failed to move item:', error);
      alert('Failed to move item');
      setDraggedItem(null);
    }
  };

  const renderQuadrant = (
    quadrantKey: string,
    name: string,
    position: string,
    description: string,
    items: string[],
    colorClass: string,
    borderClass: string
  ) => (
    <div
      className={`${colorClass} ${borderClass} rounded-lg p-3 transition-all flex flex-col ${
        draggedItem && draggedItem.quadrant !== quadrantKey ? 'ring-2 ring-blue-400' : ''
      }`}
      onDragOver={handleDragOver}
      onDrop={(e) => handleDrop(e, quadrantKey)}
    >
      {/* Compact header with title, position, and add button on same line */}
      <div className="flex justify-between items-center mb-2 leading-tight">
        <div className="flex items-baseline gap-2">
          <span className="text-base font-bold">{name}</span>
          <span className="text-xs text-gray-400">({position})</span>
        </div>
        <button
          onClick={() => handleStartAdd(quadrantKey)}
          className="text-xs px-2 py-0.5 bg-gray-700 hover:bg-gray-600 rounded transition-colors flex-shrink-0"
          title="Add item"
        >
          + Add
        </button>
      </div>
      <div className="text-xs text-gray-500 mb-2 leading-tight">{description}</div>

      <ul className="space-y-1.5 flex-1 overflow-auto">
        {items.length === 0 && addingTo !== quadrantKey && (
          <li className="text-gray-600 text-sm italic">No items</li>
        )}

        {items.map((item, idx) => (
          <li
            key={idx}
            draggable
            onDragStart={() => handleDragStart(quadrantKey, idx)}
            className={`text-xs bg-gray-800 rounded px-2 py-1.5 cursor-move hover:bg-gray-700 transition-colors leading-tight ${
              draggedItem?.quadrant === quadrantKey && draggedItem?.index === idx
                ? 'opacity-50'
                : ''
            }`}
          >
            {editingItem?.quadrant === quadrantKey && editingItem?.index === idx ? (
              <div className="space-y-1.5">
                <input
                  type="text"
                  value={editText}
                  onChange={(e) => setEditText(e.target.value)}
                  className="w-full bg-gray-900 border border-gray-600 rounded px-2 py-1 text-xs focus:outline-none focus:border-blue-500"
                  autoFocus
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleSaveEdit();
                    if (e.key === 'Escape') handleCancelEdit();
                  }}
                />
                <div className="flex gap-1.5">
                  <button
                    onClick={handleSaveEdit}
                    className="text-xs px-1.5 py-0.5 bg-blue-600 hover:bg-blue-700 rounded"
                  >
                    Save
                  </button>
                  <button
                    onClick={handleCancelEdit}
                    className="text-xs px-1.5 py-0.5 bg-gray-600 hover:bg-gray-700 rounded"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex justify-between items-center group">
                <span className="flex-1">{item}</span>
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity ml-2">
                  <button
                    onClick={() => handleStartEdit(quadrantKey, idx, item)}
                    className="text-xs px-1.5 py-0.5 bg-blue-600 hover:bg-blue-700 rounded"
                    title="Edit"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(quadrantKey, idx)}
                    className="text-xs px-1.5 py-0.5 bg-red-600 hover:bg-red-700 rounded"
                    title="Delete"
                  >
                    Del
                  </button>
                </div>
              </div>
            )}
          </li>
        ))}

        {addingTo === quadrantKey && (
          <li className="text-xs bg-gray-800 rounded px-2 py-1.5">
            <div className="space-y-1.5">
              <input
                type="text"
                value={newItemText}
                onChange={(e) => setNewItemText(e.target.value)}
                placeholder="Enter new item..."
                className="w-full bg-gray-900 border border-gray-600 rounded px-2 py-1 text-xs focus:outline-none focus:border-blue-500"
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSaveAdd();
                  if (e.key === 'Escape') handleCancelAdd();
                }}
              />
              <div className="flex gap-1.5">
                <button
                  onClick={handleSaveAdd}
                  className="text-xs px-1.5 py-0.5 bg-green-600 hover:bg-green-700 rounded"
                >
                  Add
                </button>
                <button
                  onClick={handleCancelAdd}
                  className="text-xs px-1.5 py-0.5 bg-gray-600 hover:bg-gray-700 rounded"
                >
                  Cancel
                </button>
              </div>
            </div>
          </li>
        )}
      </ul>
    </div>
  );

  return (
    <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
      {/* Compact inline header */}
      <div className="flex items-baseline gap-3 mb-3 flex-wrap leading-tight">
        <h2 className="text-xl font-bold">Priority Matrix (Editable)</h2>
        <span className="text-sm text-gray-400">{y_axis} vs. {x_axis}</span>
        <span className="text-xs text-gray-500">
          Drag items to move between quadrants, or use Edit/Delete buttons
        </span>
      </div>

      {/* 2x2 Grid */}
      <div className="grid grid-cols-2 grid-rows-2 gap-3 mb-4">
        {/* Q1: Top-Left (High Y, Low X) - Quick Wins */}
        {renderQuadrant(
          'Q1',
          quadrants.Q1.name,
          quadrants.Q1.position,
          quadrants.Q1.description,
          placements.Q1 || [],
          'bg-green-900/20',
          'border-2 border-green-600'
        )}

        {/* Q2: Top-Right (High Y, High X) - Strategic Bets */}
        {renderQuadrant(
          'Q2',
          quadrants.Q2.name,
          quadrants.Q2.position,
          quadrants.Q2.description,
          placements.Q2 || [],
          'bg-yellow-900/20',
          'border-2 border-yellow-600'
        )}

        {/* Q3: Bottom-Left (Low Y, Low X) - Fill Later */}
        {renderQuadrant(
          'Q3',
          quadrants.Q3.name,
          quadrants.Q3.position,
          quadrants.Q3.description,
          placements.Q3 || [],
          'bg-gray-700/20',
          'border-2 border-gray-600'
        )}

        {/* Q4: Bottom-Right (Low Y, High X) - Hard Slogs */}
        {renderQuadrant(
          'Q4',
          quadrants.Q4.name,
          quadrants.Q4.position,
          quadrants.Q4.description,
          placements.Q4 || [],
          'bg-red-900/20',
          'border-2 border-red-600'
        )}
      </div>

      {/* Axis Labels */}
      <div className="grid grid-cols-2 gap-3 mb-3">
        <div className="text-center text-xs text-gray-500 leading-tight">← Low {x_axis}</div>
        <div className="text-center text-xs text-gray-500 leading-tight">High {x_axis} →</div>
      </div>

      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-3">
          <h3 className="text-sm text-blue-400 font-semibold mb-2">Recommendations</h3>
          <ul className="space-y-1">
            {recommendations.map((rec, idx) => (
              <li key={idx} className="text-xs text-gray-300 flex items-start leading-tight">
                <span className="text-blue-500 mr-2">•</span>
                <span className="flex-1">{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
