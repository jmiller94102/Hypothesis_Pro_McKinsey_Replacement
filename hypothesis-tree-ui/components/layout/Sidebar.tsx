/**
 * Fixed left sidebar with project controls
 */

import { useState } from 'react';
import type { MECEValidationResult, ProjectVersion } from '@/lib/types';

interface SidebarProps {
  projectName: string;
  hasUnsavedChanges: boolean;
  meceStatus: MECEValidationResult | null;
  versions: ProjectVersion[];
  onSave: () => void;
  onValidate: () => void;
  onExport: () => void;
  onLoadVersion: (version: number) => void;
  onGoHome: () => void;
}

export function Sidebar({
  projectName,
  hasUnsavedChanges,
  meceStatus,
  versions,
  onSave,
  onValidate,
  onExport,
  onLoadVersion,
  onGoHome,
}: SidebarProps) {
  const [showVersions, setShowVersions] = useState(false);

  return (
    <div className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col overflow-y-auto">
      <div className="p-4 border-b border-gray-800">
        <button
          onClick={onGoHome}
          className="text-sm text-blue-400 hover:text-blue-300 mb-2"
        >
          ← Back to Home
        </button>
        <h1 className="text-lg font-bold truncate" title={projectName}>
          {projectName}
        </h1>
      </div>

      {/* Project Actions */}
      <div className="p-4 border-b border-gray-800">
        <h2 className="text-sm font-semibold text-gray-400 mb-3">PROJECT</h2>
        <div className="space-y-2">
          <button
            onClick={onSave}
            className={`w-full px-3 py-2 rounded text-sm font-medium transition-colors ${
              hasUnsavedChanges
                ? 'bg-blue-600 hover:bg-blue-700 text-white'
                : 'bg-gray-800 hover:bg-gray-750 text-gray-300'
            }`}
          >
            Save {hasUnsavedChanges && '*'}
          </button>
        </div>
      </div>

      {/* MECE Status */}
      <div className="p-4 border-b border-gray-800">
        <h2 className="text-sm font-semibold text-gray-400 mb-3">STATUS</h2>
        {meceStatus ? (
          <div className="space-y-2">
            <div
              className={`px-3 py-2 rounded text-sm ${
                meceStatus.is_mece
                  ? 'bg-green-900/30 border border-green-700 text-green-100'
                  : 'bg-red-900/30 border border-red-700 text-red-100'
              }`}
            >
              {meceStatus.is_mece ? '✅ MECE Valid' : '❌ MECE Invalid'}
            </div>
            {!meceStatus.is_mece && (
              <div className="text-xs space-y-1">
                {meceStatus.issues.overlaps.length > 0 && (
                  <div className="text-red-300">
                    {meceStatus.issues.overlaps.length} overlap(s)
                  </div>
                )}
                {meceStatus.issues.gaps.length > 0 && (
                  <div className="text-yellow-300">
                    {meceStatus.issues.gaps.length} gap(s)
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="text-sm text-gray-500 italic">
            Not validated yet
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="p-4 border-b border-gray-800">
        <h2 className="text-sm font-semibold text-gray-400 mb-3">ACTIONS</h2>
        <div className="space-y-2">
          <button
            onClick={onValidate}
            className="w-full px-3 py-2 bg-purple-600 hover:bg-purple-700 rounded text-sm font-medium transition-colors"
          >
            Validate MECE
          </button>
          <button
            onClick={onExport}
            className="w-full px-3 py-2 bg-gray-800 hover:bg-gray-750 rounded text-sm font-medium transition-colors"
          >
            Export JSON
          </button>
        </div>
      </div>

      {/* Version History */}
      <div className="p-4">
        <h2 className="text-sm font-semibold text-gray-400 mb-3">HISTORY</h2>
        <button
          onClick={() => setShowVersions(!showVersions)}
          className="w-full px-3 py-2 bg-gray-800 hover:bg-gray-750 rounded text-sm font-medium transition-colors mb-2"
        >
          {showVersions ? '▼' : '▶'} {versions.length} Version(s)
        </button>
        {showVersions && (
          <div className="space-y-1 max-h-48 overflow-y-auto">
            {versions.map((v) => (
              <button
                key={v.version}
                onClick={() => onLoadVersion(v.version)}
                className="w-full text-left px-2 py-1 text-xs hover:bg-gray-800 rounded"
              >
                <div className="font-medium">v{v.version}</div>
                <div className="text-gray-500 text-[10px]">
                  {new Date(v.timestamp).toLocaleString()}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
