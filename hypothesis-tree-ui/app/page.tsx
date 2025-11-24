'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api-client';
import type { Framework, Project } from '@/lib/types';

interface ProgressEvent {
  stage: string;
  message: string;
  progress: number;
  timestamp: string;
}

export default function HomePage() {
  const router = useRouter();
  const [frameworks, setFrameworks] = useState<Framework[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [newProjectProblem, setNewProjectProblem] = useState('');
  const [selectedFramework, setSelectedFramework] = useState('');

  // Progress tracking
  const [isGenerating, setIsGenerating] = useState(false);
  const [progressEvents, setProgressEvents] = useState<ProgressEvent[]>([]);
  const [currentProgress, setCurrentProgress] = useState(0);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const [fwRes, projRes] = await Promise.all([
        api.listFrameworks(),
        api.listProjects(),
      ]);
      setFrameworks(fwRes.frameworks);
      setProjects(projRes.projects);
      if (fwRes.frameworks.length > 0) {
        setSelectedFramework(fwRes.frameworks[0].name);
      }
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  }

  async function createNewProject() {
    if (!newProjectProblem.trim() || !selectedFramework) {
      alert('Please enter a problem statement and select a framework');
      return;
    }

    setIsGenerating(true);
    setProgressEvents([]);
    setCurrentProgress(0);

    try {
      // Use EventSource for Server-Sent Events
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const eventSource = new EventSource(
        `${API_BASE}/api/tree/generate-stream?` +
        new URLSearchParams({
          problem: newProjectProblem,
          framework: selectedFramework,
        })
      );

      let finalResult: any = null;

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.stage === 'complete') {
            // Final result received
            finalResult = data.result;
            eventSource.close();

            // Backend auto-saves during generation, so we can navigate directly
            const projectId = finalResult.project_id;
            router.push(`/editor?id=${projectId}`);
          } else if (data.stage === 'error') {
            // Error occurred
            console.error('Generation error:', data.message);
            alert(`Error: ${data.message}`);
            eventSource.close();
            setIsGenerating(false);
          } else {
            // Progress update
            setProgressEvents((prev) => [...prev, data]);
            setCurrentProgress(data.progress);
          }
        } catch (err) {
          console.error('Failed to parse SSE data:', err);
        }
      };

      eventSource.onerror = (error) => {
        console.error('SSE Error:', error);
        eventSource.close();

        // Fallback to non-streaming API
        if (!finalResult) {
          console.log('Falling back to non-streaming API...');
          api.generateTree(newProjectProblem, selectedFramework)
            .then(({ tree, project_id }) => {
              return api.saveTree(project_id, tree, 'Initial version').then(() => project_id);
            })
            .then((projectId) => {
              router.push(`/editor?id=${projectId}`);
            })
            .catch((err) => {
              console.error('Fallback failed:', err);
              alert('Failed to create project. Please try again.');
              setIsGenerating(false);
            });
        }
      };
    } catch (error) {
      console.error('Failed to create project:', error);
      alert('Failed to create project. Please try again.');
      setIsGenerating(false);
    }
  }

  function loadProject(projectName: string) {
    router.push(`/editor?id=${projectName}`);
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <div className="max-w-6xl mx-auto px-6 py-12">
        <header className="mb-12">
          <h1 className="text-4xl font-bold mb-2">HypothesisTree Pro</h1>
          <p className="text-gray-400">Strategic Decision Support with MECE Hypothesis Trees</p>
        </header>

        <div className="grid md:grid-cols-2 gap-8">
          {/* New Project */}
          <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
            <h2 className="text-2xl font-semibold mb-4">Create New Project</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Problem Statement</label>
                <textarea
                  value={newProjectProblem}
                  onChange={(e) => setNewProjectProblem(e.target.value)}
                  placeholder="e.g., Should we scale deployment of fall detection in senior living?"
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 h-24 resize-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Framework</label>
                <select
                  value={selectedFramework}
                  onChange={(e) => setSelectedFramework(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {frameworks.map((fw) => (
                    <option key={fw.name} value={fw.name}>
                      {fw.display_name}
                    </option>
                  ))}
                </select>
                {selectedFramework && (
                  <p className="mt-2 text-sm text-gray-400">
                    {frameworks.find(f => f.name === selectedFramework)?.description}
                  </p>
                )}
              </div>

              <button
                onClick={createNewProject}
                disabled={isGenerating}
                className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-md font-medium transition-colors"
              >
                {isGenerating ? 'Generating...' : 'Create Project'}
              </button>

              {/* Progress Panel */}
              {isGenerating && (
                <div className="mt-4 p-4 bg-gray-800 border border-gray-700 rounded-md">
                  <div className="mb-2">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium">Progress</span>
                      <span className="text-gray-400">{currentProgress}%</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${currentProgress}%` }}
                      />
                    </div>
                  </div>

                  {/* Event Log */}
                  <div className="mt-3 max-h-32 overflow-y-auto space-y-1">
                    {progressEvents.map((event, idx) => (
                      <div key={idx} className="text-xs text-gray-400 font-mono">
                        <span className="text-gray-500">{new Date(event.timestamp).toLocaleTimeString()}</span>
                        {' '}
                        <span className="text-gray-300">{event.message}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Existing Projects */}
          <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
            <h2 className="text-2xl font-semibold mb-4">Recent Projects</h2>

            {projects.length === 0 ? (
              <p className="text-gray-500 italic">No projects yet. Create your first project!</p>
            ) : (
              <div className="space-y-3">
                {projects.map((project) => (
                  <button
                    key={project.name}
                    onClick={() => loadProject(project.name)}
                    className="w-full text-left px-4 py-3 bg-gray-800 hover:bg-gray-750 rounded-md border border-gray-700 hover:border-gray-600 transition-colors"
                  >
                    <div className="font-medium">{project.problem}</div>
                    <div className="text-sm text-gray-400 mt-1">
                      v{project.latest_version} • {new Date(project.last_updated).toLocaleDateString()}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
