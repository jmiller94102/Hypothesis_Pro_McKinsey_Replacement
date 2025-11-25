'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Sidebar } from '@/components/layout/Sidebar';
import { MainTreeView } from '@/components/layout/MainTreeView';
import { DebugPanel } from '@/components/layout/DebugPanel';
import { TreeControls } from '@/components/layout/TreeControls';
import { MatrixControls } from '@/components/layout/MatrixControls';
import { Matrix2x2 } from '@/components/prioritization/Matrix2x2';
import { Matrix2x2Editor } from '@/components/prioritization/Matrix2x2Editor';
import { api } from '@/lib/api-client';
import type { HypothesisTree, MECEValidationResult, DebugLog, ProjectVersion, NodeLevel, PriorityMatrix, MatrixType, MatrixData } from '@/lib/types';

// Tab configuration for navigation
const TABS = [
  { id: 'tree', label: 'Hypothesis Tree', matrixType: null },
  { id: 'hypothesis', label: 'Hypothesis Priority', matrixType: 'hypothesis_prioritization' as MatrixType },
  { id: 'risks', label: 'Risk Register', matrixType: 'risk_register' as MatrixType },
  { id: 'tasks', label: 'Task Priority', matrixType: 'task_prioritization' as MatrixType },
  { id: 'measurements', label: 'Measurement Priority', matrixType: 'measurement_priorities' as MatrixType },
] as const;

type TabId = typeof TABS[number]['id'];

// API base URL for backend calls
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function EditorContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const projectId = searchParams.get('id') || '';  // Use 'id' param for project UUID

  const [tree, setTree] = useState<HypothesisTree | null>(null);
  const [priorityMatrix, setPriorityMatrix] = useState<PriorityMatrix | null>(null);
  const [activeTab, setActiveTab] = useState<TabId>('tree');
  const [matrices, setMatrices] = useState<Record<MatrixType, MatrixData | null>>({
    hypothesis_prioritization: null,
    risk_register: null,
    task_prioritization: null,
    measurement_priorities: null,
  });
  const [loadingMatrices, setLoadingMatrices] = useState<Set<MatrixType>>(new Set());
  const [debugLogs, setDebugLogs] = useState<DebugLog[]>([]);
  const [isDebugOpen, setIsDebugOpen] = useState(true);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [meceStatus, setMeceStatus] = useState<MECEValidationResult | null>(null);
  const [versions, setVersions] = useState<ProjectVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [zoom, setZoom] = useState(1);
  const [matrixZoom, setMatrixZoom] = useState(1);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (projectId) {
      loadProject();
      loadPriorityMatrix();
      loadAllMatrices();
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

      // Load tree and versions, but handle 404 errors gracefully
      const [treeRes, versionsRes] = await Promise.all([
        api.loadTree(projectId).catch((err) => {
          // If tree doesn't exist yet (404), that's okay - might be brand new project
          if (err.status === 404) {
            addDebugLog('Project not saved yet - will be created on first save', 'warning');
            return null;
          }
          throw err;
        }),
        api.listVersions(projectId).catch((err) => {
          // If no versions yet, return empty array
          if (err.status === 404) {
            return { versions: [] };
          }
          throw err;
        }),
      ]);

      if (treeRes) {
        setTree(treeRes.data.content);
        setVersions(versionsRes.versions);
        setHasUnsavedChanges(false);
        addDebugLog(
          `Loaded project ${projectId} v${treeRes.data.metadata.version}`,
          'success'
        );
      } else {
        // Project doesn't exist yet - this shouldn't happen in normal flow
        // User might have navigated directly to /editor?id=invalid-id
        addDebugLog('Project not found - please generate a new tree from home page', 'error');
        setVersions([]);
      }
    } catch (error) {
      addDebugLog(`Failed to load project: ${error}`, 'error');
      console.error('Failed to load project:', error);
    } finally {
      setLoading(false);
    }
  }

  async function loadPriorityMatrix() {
    try {
      const result = await api.loadPriorityMatrix(projectId);
      setPriorityMatrix(result.data.content);
      addDebugLog('Priority matrix loaded', 'success');
    } catch (error: any) {
      // Matrix might not exist for this project yet - that's okay
      if (error.status === 404) {
        addDebugLog('No priority matrix found for this project', 'warning');
      } else {
        addDebugLog(`Failed to load priority matrix: ${error}`, 'error');
        console.error('Failed to load priority matrix:', error);
      }
    }
  }

  async function loadAllMatrices() {
    // Load all 4 matrix types
    for (const tab of TABS) {
      if (tab.matrixType) {
        try {
          const response = await fetch(`${API_BASE_URL}/api/projects/${projectId}/matrices/${tab.matrixType}`);
          if (response.ok) {
            const data = await response.json();
            setMatrices(prev => ({ ...prev, [tab.matrixType!]: data.data.content }));
            addDebugLog(`Loaded ${tab.label}`, 'success');
          }
        } catch (error) {
          // Matrix doesn't exist yet - that's OK
          addDebugLog(`${tab.label} not found (not yet generated)`, 'info');
        }
      }
    }
  }

  async function handleGenerateMatrix(matrixType: MatrixType) {
    setLoadingMatrices(prev => new Set(prev).add(matrixType));

    try {
      addDebugLog(`Generating ${matrixType} matrix...`, 'info');
      const response = await fetch(`${API_BASE_URL}/api/projects/${projectId}/matrices/${matrixType}`, {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        setMatrices(prev => ({ ...prev, [matrixType]: data.matrix }));
        addDebugLog(`Successfully generated ${matrixType} matrix`, 'success');
      } else {
        // Safely parse error response (may be HTML or JSON)
        const errorData = await response.json().catch(() => ({
          detail: `HTTP ${response.status}: ${response.statusText}`
        }));
        addDebugLog(`Failed to generate matrix: ${errorData.detail || 'Unknown error'}`, 'error');
        alert(`Failed to generate matrix. ${errorData.detail || 'Please check the console for details.'}`);
      }
    } catch (error) {
      console.error('Matrix generation error:', error);
      addDebugLog(`Matrix generation error: ${error}`, 'error');
      alert('Failed to generate matrix');
    } finally {
      setLoadingMatrices(prev => {
        const next = new Set(prev);
        next.delete(matrixType);
        return next;
      });
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

  // Matrix CRUD operations
  async function handleAddMatrixItem(quadrant: 'Q1' | 'Q2' | 'Q3' | 'Q4', item: string) {
    try {
      const result = await api.addMatrixItem(projectId, quadrant, item);
      setPriorityMatrix(result.matrix);
      addDebugLog(`Added item to ${quadrant}`, 'success');
    } catch (error) {
      addDebugLog(`Failed to add matrix item: ${error}`, 'error');
      throw error;
    }
  }

  async function handleDeleteMatrixItem(quadrant: 'Q1' | 'Q2' | 'Q3' | 'Q4', itemIndex: number) {
    try {
      const result = await api.deleteMatrixItem(projectId, quadrant, itemIndex);
      setPriorityMatrix(result.matrix);
      addDebugLog(`Deleted item from ${quadrant}`, 'success');
    } catch (error) {
      addDebugLog(`Failed to delete matrix item: ${error}`, 'error');
      throw error;
    }
  }

  async function handleEditMatrixItem(quadrant: 'Q1' | 'Q2' | 'Q3' | 'Q4', itemIndex: number, newText: string) {
    try {
      const result = await api.editMatrixItem(projectId, quadrant, itemIndex, newText);
      setPriorityMatrix(result.matrix);
      addDebugLog(`Edited item in ${quadrant}`, 'success');
    } catch (error) {
      addDebugLog(`Failed to edit matrix item: ${error}`, 'error');
      throw error;
    }
  }

  async function handleMoveMatrixItem(fromQuadrant: 'Q1' | 'Q2' | 'Q3' | 'Q4', toQuadrant: 'Q1' | 'Q2' | 'Q3' | 'Q4', itemIndex: number) {
    try {
      const result = await api.moveMatrixItem(projectId, fromQuadrant, toQuadrant, itemIndex);
      setPriorityMatrix(result.matrix);
      addDebugLog(`Moved item from ${fromQuadrant} to ${toQuadrant}`, 'success');
    } catch (error) {
      addDebugLog(`Failed to move matrix item: ${error}`, 'error');
      throw error;
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

  // Matrix zoom controls
  function handleMatrixZoomIn() {
    setMatrixZoom((prev) => Math.min(2, prev + 0.1));
  }

  function handleMatrixZoomOut() {
    setMatrixZoom((prev) => Math.max(0.5, prev - 0.1));
  }

  function handleMatrixZoomReset() {
    setMatrixZoom(1);
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
        {/* Tab Switcher */}
        <div className="flex border-b border-gray-800 bg-gray-900">
          {TABS.map(tab => (
            <button
              key={tab.id}
              className={`px-4 py-3 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'border-b-2 border-blue-500 text-blue-400 bg-gray-800'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
              }`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab === 'tree' && (
          <>
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
          </>
        )}

        {activeTab !== 'tree' && (() => {
          const tab = TABS.find(t => t.id === activeTab);
          if (!tab || !tab.matrixType) return null;

          const matrixType = tab.matrixType;
          const matrixData = matrices[matrixType];
          const isLoading = loadingMatrices.has(matrixType);

          return (
            <>
              <MatrixControls
                zoom={matrixZoom}
                onZoomIn={handleMatrixZoomIn}
                onZoomOut={handleMatrixZoomOut}
                onZoomReset={handleMatrixZoomReset}
              />
              <div
                className="flex-1 overflow-auto p-6"
                style={{
                  transform: `scale(${matrixZoom})`,
                  transformOrigin: 'top left',
                  width: `${100 / matrixZoom}%`,
                  height: `${100 / matrixZoom}%`
                }}
              >
                {matrixData ? (
                  <Matrix2x2Editor
                    projectId={projectId}
                    matrixType={matrixType}
                    matrixData={matrixData}
                    onMatrixUpdate={(updated) => {
                      setMatrices(prev => ({ ...prev, [matrixType]: updated }));
                    }}
                    onAddItem={async (quadrant, item) => {
                      // Placeholder - would need to implement proper API calls
                      addDebugLog(`Added item to ${quadrant} in ${matrixType}`, 'success');
                    }}
                    onDeleteItem={async (quadrant, itemIndex) => {
                      addDebugLog(`Deleted item from ${quadrant} in ${matrixType}`, 'success');
                    }}
                    onEditItem={async (quadrant, itemIndex, newText) => {
                      addDebugLog(`Edited item in ${quadrant} in ${matrixType}`, 'success');
                    }}
                    onMoveItem={async (fromQuadrant, toQuadrant, itemIndex) => {
                      addDebugLog(`Moved item from ${fromQuadrant} to ${toQuadrant} in ${matrixType}`, 'success');
                    }}
                  />
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center text-gray-500">
                      <p className="text-lg mb-4">{tab.label} Not Generated</p>
                      <p className="text-sm mb-4">Generate this matrix from your hypothesis tree</p>
                      <button
                        onClick={() => handleGenerateMatrix(matrixType)}
                        disabled={isLoading}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded disabled:bg-gray-600 disabled:cursor-not-allowed"
                      >
                        {isLoading ? 'Generating...' : `Generate ${tab.label}`}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </>
          );
        })()}

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
