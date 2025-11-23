/**
 * Inline editor component for node labels/questions
 */

import { useState, useRef, useEffect } from 'react';

interface InlineEditorProps {
  value: string;
  onSave: (newValue: string) => void;
  onCancel: () => void;
  placeholder?: string;
}

export function InlineEditor({ value, onSave, onCancel, placeholder }: InlineEditorProps) {
  const [editValue, setEditValue] = useState(value);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
    inputRef.current?.select();
  }, []);

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSave();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      onCancel();
    }
  }

  function handleSave() {
    if (editValue.trim() && editValue !== value) {
      onSave(editValue.trim());
    } else {
      onCancel();
    }
  }

  return (
    <div className="flex items-center gap-2 flex-1">
      <input
        ref={inputRef}
        type="text"
        value={editValue}
        onChange={(e) => setEditValue(e.target.value)}
        onKeyDown={handleKeyDown}
        onBlur={handleSave}
        placeholder={placeholder}
        className="flex-1 px-2 py-1 bg-gray-800 border border-blue-500 rounded focus:outline-none focus:ring-1 focus:ring-blue-400"
      />
      <button
        onClick={handleSave}
        className="px-2 py-1 bg-green-600 hover:bg-green-700 rounded text-xs"
      >
        ✓
      </button>
      <button
        onClick={onCancel}
        className="px-2 py-1 bg-red-600 hover:bg-red-700 rounded text-xs"
      >
        ✗
      </button>
    </div>
  );
}
