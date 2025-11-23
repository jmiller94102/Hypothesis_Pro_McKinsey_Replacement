'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Sidebar } from '@/components/layout/Sidebar';
import { MainTreeView } from '@/components/layout/MainTreeView';
import { DebugPanel } from '@/components/layout/DebugPanel';
import { api } from '@/lib/api-client';
import type { HypothesisTree, MECEValidationResult, DebugLog, ProjectVersion, NodeLevel } from '@/lib/types';

function EditorContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const projectName = searchParams.get('project') || '';

  const [tree, setTree] = useState<HypothesisTree | null>(null);
  const [debugLogs, setDebugLogs] = useState<DebugLog[]>([]);
  const [isDebugOpen, setIsDebugOpen] = useState(true);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [meceStatus, setMeceStatus] = useState<MECEValidationResult | null>(null);
  const [versions, setVersions] = useState<ProjectVersion[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (projectName) {
      loadProject();
    } else {
      setLoading(false);
      addDebugLog('No project specified', 'error');
    }
  }, [projectName]);

  function addDebugLog(message: string, type: DebugLog['type'] = 'info') {
    setDebugLogs((prev) => [
      ...prev,
      {
        timestamp: new Date().toISOString(),
        message,
        type,
      },
    ]);
  }

  async function loadProject() {
    try {
      addDebugLog(`Loading project: ${projectName}`, 'info');
      const [treeRes, versionsRes] = await Promise.all([
        api.loadTree(projectName),
        api.listVersions(projectName),
      ]);

      setTree(treeRes.data.content);
      setVersions(versionsRes.versions);
      setHasUnsavedChanges(false);
      addDebugLog(
        `Loaded ${projectName} v${treeRes.data.metadata.version}`,
        'success'
      );
    } catch (error) {
      addDebugLog(`Failed to load project: ${error}`, 'error');
      console.error('Failed to load project:', error);
    } finally {
      setLoading(false);
    }
  }

  async function handleSave() {
    if (!tree) return;

    try {
      addDebugLog('Saving project...', 'info');
      const result = await api.saveTree(
        projectName,
        tree,
        `Version ${versions.length + 1}`
      );

      setHasUnsavedChanges(false);
      setVersions([
        ...versions,
        {
          version: result.version,
          timestamp: result.timestamp,
          description: `Version ${result.version}`,
        },
      ]);
      addDebugLog(`Saved as v${result.version}`, 'success');
    } catch (error) {
      addDebugLog(`Save failed: ${error}`, 'error');
      console.error('Save failed:', error);
    }
  }

  async function handleValidate() {
    if (!tree) return;

    try {
      addDebugLog('Validating MECE compliance...', 'info');
      const result = await api.validateMECE(tree);
      setMeceStatus(result);

      if (result.is_mece) {
        addDebugLog('✅ MECE validation PASSED', 'success');
      } else {
        addDebugLog(
          `❌ MECE validation FAILED - ${result.issues.overlaps.length} overlaps, ${result.issues.gaps.length} gaps`,
          'error'
        );
        result.issues.overlaps.forEach((overlap) => {
          addDebugLog(`  Overlap: ${overlap}`, 'warning');
        });
        result.issues.gaps.forEach((gap) => {
          addDebugLog(`  Gap: ${gap}`, 'warning');
        });
      }
    } catch (error) {
      addDebugLog(`Validation failed: ${error}`, 'error');
      console.error('Validation failed:', error);
    }
  }

  function handleExport() {
    if (!tree) return;

    try {
      const dataStr = JSON.stringify(tree, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${projectName}_export.json`;
      link.click();
      URL.revokeObjectURL(url);
      addDebugLog(`Exported to ${projectName}_export.json`, 'success');
    } catch (error) {
      addDebugLog(`Export failed: ${error}`, 'error');
    }
  }

  async function handleLoadVersion(version: number) {
    try {
      addDebugLog(`Loading version ${version}...`, 'info');
      const result = await api.loadTree(projectName, version);
      setTree(result.data.content);
      setHasUnsavedChanges(false);
      addDebugLog(`Loaded v${version}`, 'success');
    } catch (error) {
      addDebugLog(`Failed to load version: ${error}`, 'error');
    }
  }

  async function handleUpdateNode(path: string[], data: any) {
    if (!tree) return;

    try {
      const result = await api.updateNode(tree, path, data);
      setTree(result.tree);
      setHasUnsavedChanges(true);
      addDebugLog(`Updated node: ${data.label}`, 'info');
    } catch (error) {
      addDebugLog(`Update failed: ${error}`, 'error');
    }
  }

  async function handleDeleteNode(path: string[]) {
    if (!tree) return;

    try {
      const result = await api.deleteNode(tree, path);
      setTree(result.tree);
      setHasUnsavedChanges(true);
      setMeceStatus(null); // Clear MECE status after deletion
      addDebugLog(`Deleted node at path: ${path.join(' > ')}`, 'warning');
    } catch (error) {
      addDebugLog(`Delete failed: ${error}`, 'error');
    }
  }

  async function handleAddNode(path: string[], level: NodeLevel) {
    if (!tree) return;

    try {
      // Create default node data
      const nodeData = {
        label: `New ${level}`,
        question: 'What is the question?',
        ...(level === 'L1' && { description: '' }),
        ...(level === 'L3' && {
          metric_type: 'qualitative',
          target: 'TBD',
          data_source: 'TBD',
          assessment_criteria: 'TBD',
        }),
      };

      const result = await api.addNode(tree, path, level, nodeData);
      setTree(result.tree);
      setHasUnsavedChanges(true);
      setMeceStatus(null); // Clear MECE status after addition
      addDebugLog(`Added ${level} node`, 'success');
    } catch (error) {
      addDebugLog(`Add node failed: ${error}`, 'error');
    }
  }

  function handleGoHome() {
    if (hasUnsavedChanges) {
      if (!confirm('You have unsaved changes. Leave anyway?')) {
        return;
      }
    }
    router.push('/');
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-950">
        <div className="text-lg text-gray-400">Loading project...</div>
      </div>
    );
  }

  if (!projectName) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-950">
        <div className="text-center">
          <div className="text-xl text-red-400 mb-4">No project specified</div>
          <button
            onClick={() => router.push('/')}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded"
          >
            Go to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex bg-gray-950 text-gray-100">
      {/* Left Sidebar - Fixed */}
      <Sidebar
        projectName={projectName}
        hasUnsavedChanges={hasUnsavedChanges}
        meceStatus={meceStatus}
        versions={versions}
        onSave={handleSave}
        onValidate={handleValidate}
        onExport={handleExport}
        onLoadVersion={handleLoadVersion}
        onGoHome={handleGoHome}
      />

      {/* Right Side - Main + Debug */}
      <div className="flex-1 flex flex-col">
        {/* Main Tree View - Scrollable X/Y */}
        <MainTreeView
          tree={tree}
          onUpdateNode={handleUpdateNode}
          onDeleteNode={handleDeleteNode}
          onAddNode={handleAddNode}
        />

        {/* Debug Panel - Collapsible bottom */}
        <DebugPanel
          logs={debugLogs}
          isOpen={isDebugOpen}
          onToggle={() => setIsDebugOpen(!isDebugOpen)}
        />
      </div>
    </div>
  );
}

export default function EditorPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center bg-gray-950"><div className="text-lg text-gray-400">Loading...</div></div>}>
      <EditorContent />
    </Suspense>
  );
}
