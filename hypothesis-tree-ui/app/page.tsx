'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api-client';
import type { Framework, Project } from '@/lib/types';

export default function HomePage() {
  const router = useRouter();
  const [frameworks, setFrameworks] = useState<Framework[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [newProjectProblem, setNewProjectProblem] = useState('');
  const [selectedFramework, setSelectedFramework] = useState('');

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

    try {
      const { tree } = await api.generateTree(newProjectProblem, selectedFramework);
      const projectName = newProjectProblem.toLowerCase().replace(/[^a-z0-9]+/g, '_').substring(0, 50);

      // Save initial version
      await api.saveTree(projectName, tree, 'Initial version');

      // Navigate to editor
      router.push(`/editor?project=${projectName}`);
    } catch (error) {
      console.error('Failed to create project:', error);
      alert('Failed to create project. Please try again.');
    }
  }

  function loadProject(projectName: string) {
    router.push(`/editor?project=${projectName}`);
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
                className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md font-medium transition-colors"
              >
                Create Project
              </button>
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
