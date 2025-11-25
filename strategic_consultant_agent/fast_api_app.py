# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""FastAPI application for Cloud Run deployment using ADK web server."""

import os

from google.adk.cli.fast_api import get_fast_api_app

# Get the directory containing agent modules (parent of this file's directory)
AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Allow CORS for all origins in Cloud Run
allow_origins = ["*"]

# Create the FastAPI app using ADK's built-in function
# This automatically discovers agents in the AGENT_DIR
app = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,  # Enable the dev-ui web interface
    allow_origins=allow_origins,
)

app.title = "HypothesisTree Pro - Strategic Consultant Agent"
app.description = "AI-powered strategic decision support using MECE hypothesis trees"


# Health check endpoint for Cloud Run
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Main execution
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
