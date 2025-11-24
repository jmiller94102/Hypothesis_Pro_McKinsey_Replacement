import React from 'react';

interface QuadrantData {
  name: string;
  position: string;
  description: string;
  action: string;
}

interface MatrixData {
  matrix_type: string;
  x_axis: string;
  y_axis: string;
  quadrants: {
    Q1: QuadrantData;
    Q2: QuadrantData;
    Q3: QuadrantData;
    Q4: QuadrantData;
  };
  placements: {
    Q1: string[];
    Q2: string[];
    Q3: string[];
    Q4: string[];
  };
  recommendations: string[];
}

interface Matrix2x2Props {
  matrixData: MatrixData;
}

export function Matrix2x2({ matrixData }: Matrix2x2Props) {
  const { quadrants, placements, x_axis, y_axis, recommendations } = matrixData;

  return (
    <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
      <h2 className="text-2xl font-bold mb-4">Prioritization Matrix</h2>
      <p className="text-gray-400 mb-6">
        {y_axis} vs. {x_axis}
      </p>

      {/* 2x2 Grid */}
      <div className="grid grid-cols-2 gap-4 mb-6" style={{ minHeight: '500px' }}>
        {/* Q1: Top-Left (High Y, Low X) - Quick Wins */}
        <div className="bg-green-900/20 border-2 border-green-600 rounded-lg p-4">
          <div className="text-green-400 font-bold text-lg mb-2">{quadrants.Q1.name}</div>
          <div className="text-sm text-gray-400 mb-3">{quadrants.Q1.position}</div>
          <div className="text-xs text-gray-500 mb-4">{quadrants.Q1.description}</div>

          {placements.Q1.length > 0 ? (
            <ul className="space-y-2">
              {placements.Q1.map((item, idx) => (
                <li key={idx} className="text-sm bg-gray-800 rounded px-3 py-2">
                  {item}
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-gray-600 text-sm italic">No items</div>
          )}
        </div>

        {/* Q2: Top-Right (High Y, High X) - Strategic Bets */}
        <div className="bg-yellow-900/20 border-2 border-yellow-600 rounded-lg p-4">
          <div className="text-yellow-400 font-bold text-lg mb-2">{quadrants.Q2.name}</div>
          <div className="text-sm text-gray-400 mb-3">{quadrants.Q2.position}</div>
          <div className="text-xs text-gray-500 mb-4">{quadrants.Q2.description}</div>

          {placements.Q2.length > 0 ? (
            <ul className="space-y-2">
              {placements.Q2.map((item, idx) => (
                <li key={idx} className="text-sm bg-gray-800 rounded px-3 py-2">
                  {item}
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-gray-600 text-sm italic">No items</div>
          )}
        </div>

        {/* Q3: Bottom-Left (Low Y, Low X) - Fill Later */}
        <div className="bg-gray-700/20 border-2 border-gray-600 rounded-lg p-4">
          <div className="text-gray-400 font-bold text-lg mb-2">{quadrants.Q3.name}</div>
          <div className="text-sm text-gray-400 mb-3">{quadrants.Q3.position}</div>
          <div className="text-xs text-gray-500 mb-4">{quadrants.Q3.description}</div>

          {placements.Q3.length > 0 ? (
            <ul className="space-y-2">
              {placements.Q3.map((item, idx) => (
                <li key={idx} className="text-sm bg-gray-800 rounded px-3 py-2">
                  {item}
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-gray-600 text-sm italic">No items</div>
          )}
        </div>

        {/* Q4: Bottom-Right (Low Y, High X) - Hard Slogs */}
        <div className="bg-red-900/20 border-2 border-red-600 rounded-lg p-4">
          <div className="text-red-400 font-bold text-lg mb-2">{quadrants.Q4.name}</div>
          <div className="text-sm text-gray-400 mb-3">{quadrants.Q4.position}</div>
          <div className="text-xs text-gray-500 mb-4">{quadrants.Q4.description}</div>

          {placements.Q4.length > 0 ? (
            <ul className="space-y-2">
              {placements.Q4.map((item, idx) => (
                <li key={idx} className="text-sm bg-gray-800 rounded px-3 py-2">
                  {item}
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-gray-600 text-sm italic">No items</div>
          )}
        </div>
      </div>

      {/* Axis Labels */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="text-center text-sm text-gray-500">
          ← Low {x_axis}
        </div>
        <div className="text-center text-sm text-gray-500">
          High {x_axis} →
        </div>
      </div>

      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4 mt-4">
          <h3 className="text-blue-400 font-semibold mb-3">Recommendations</h3>
          <ul className="space-y-2">
            {recommendations.map((rec, idx) => (
              <li key={idx} className="text-sm text-gray-300 flex items-start">
                <span className="text-blue-500 mr-2">•</span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
