'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Sidebar } from '@/components/layout/Sidebar';
import { MainTreeView } from '@/components/layout/MainTreeView';
import { DebugPanel } from '@/components/layout/DebugPanel';
import { TreeControls } from '@/components/layout/TreeControls';
import { api } from '@/lib/api-client';
import type { HypothesisTree, MECEValidationResult, DebugLog, ProjectVersion, NodeLevel } from '@/lib/types';

function EditorContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const projectId = searchParams.get('id') || '';  // Use 'id' param for project UUID

  const [tree, setTree] = useState<HypothesisTree | null>(null);
  const [debugLogs, setDebugLogs] = useState<DebugLog[]>([]);
  const [isDebugOpen, setIsDebugOpen] = useState(true);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [meceStatus, setMeceStatus] = useState<MECEValidationResult | null>(null);
  const [versions, setVersions] = useState<ProjectVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [zoom, setZoom] = useState(1);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (projectId) {
      loadProject();
    } else {
      setLoading(false);
      addDebugLog('No project specified', 'error');
    }
  }, [projectId]);

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
      addDebugLog(`Loading project: ${projectId}`, 'info');
      const [treeRes, versionsRes] = await Promise.all([
        api.loadTree(projectId),
        api.listVersions(projectId),
      ]);

      setTree(treeRes.data.content);
      setVersions(versionsRes.versions);
      setHasUnsavedChanges(false);
      addDebugLog(
        `Loaded project ${projectId} v${treeRes.data.metadata.version}`,
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
        projectId,
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
      link.download = `${projectId}_export.json`;
      link.click();
      URL.revokeObjectURL(url);
      addDebugLog(`Exported to ${projectId}_export.json`, 'success');
    } catch (error) {
      addDebugLog(`Export failed: ${error}`, 'error');
    }
  }

  async function handleLoadVersion(version: number) {
    try {
      addDebugLog(`Loading version ${version}...`, 'info');
      const result = await api.loadTree(projectId, version);
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

  // Collapse/Expand all nodes at a level
  function handleCollapseAll(level: 'L1' | 'L2' | 'L3') {
    if (!tree) return;
    const newExpanded = new Set<string>();

    // Keep nodes expanded if they're above the target level
    if (level === 'L3' || level === 'L2') {
      Object.keys(tree.tree).forEach((l1Key) => {
        newExpanded.add(l1Key); // Keep L1 expanded
        if (level === 'L3') {
          Object.keys(tree.tree[l1Key].L2_branches || {}).forEach((l2Key) => {
            newExpanded.add(`${l1Key}-${l2Key}`); // Keep L2 expanded when collapsing L3
          });
        }
      });
    }

    setExpandedNodes(newExpanded);
    addDebugLog(`Collapsed all ${level} nodes`, 'info');
  }

  function handleExpandAll(level: 'L1' | 'L2' | 'L3') {
    if (!tree) return;
    const newExpanded = new Set<string>();

    Object.entries(tree.tree).forEach(([l1Key, l1]) => {
      newExpanded.add(l1Key); // Expand all L1

      if (level === 'L2' || level === 'L3') {
        Object.keys(l1.L2_branches || {}).forEach((l2Key) => {
          newExpanded.add(`${l1Key}-${l2Key}`); // Expand all L2
        });
      }
    });

    setExpandedNodes(newExpanded);
    addDebugLog(`Expanded all ${level} nodes`, 'info');
  }

  // Zoom controls
  function handleZoomIn() {
    setZoom((prev) => Math.min(2, prev + 0.1));
  }

  function handleZoomOut() {
    setZoom((prev) => Math.max(0.5, prev - 0.1));
  }

  function handleZoomReset() {
    setZoom(1);
    addDebugLog('Reset zoom to 100%', 'info');
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-950">
        <div className="text-lg text-gray-400">Loading project...</div>
      </div>
    );
  }

  if (!projectId) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-950">
        <div className="text-center">
          <div className="text-xl text-red-400 mb-4">No project ID specified</div>
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
        projectName={projectId}  // Pass project ID (will display as ID for now)
        hasUnsavedChanges={hasUnsavedChanges}
        meceStatus={meceStatus}
        versions={versions}
        onSave={handleSave}
        onValidate={handleValidate}
        onExport={handleExport}
        onLoadVersion={handleLoadVersion}
        onGoHome={handleGoHome}
      />

      {/* Right Side - Controls + Main + Debug */}
      <div className="flex-1 flex flex-col">
        {/* Tree Controls - Collapse/Expand and Zoom */}
        <TreeControls
          onCollapseAll={handleCollapseAll}
          onExpandAll={handleExpandAll}
          zoom={zoom}
          onZoomIn={handleZoomIn}
          onZoomOut={handleZoomOut}
          onZoomReset={handleZoomReset}
        />

        {/* Main Tree View - Scrollable X/Y with Zoom */}
        <MainTreeView
          tree={tree}
          onUpdateNode={handleUpdateNode}
          onDeleteNode={handleDeleteNode}
          onAddNode={handleAddNode}
          zoom={zoom}
          onZoomChange={setZoom}
          expandedNodes={expandedNodes}
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
