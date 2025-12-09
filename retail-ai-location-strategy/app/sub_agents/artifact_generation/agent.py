# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Artifact Generation Pipeline - Parallel execution of output artifacts.

This module creates a ParallelAgent that runs the three artifact generators
concurrently: HTML report, infographic image, and audio podcast overview.

Using ParallelAgent instead of sequential execution provides:
- Faster overall pipeline completion (~40% faster)
- Better resource utilization
- Independent failure handling
"""

from google.adk.agents import ParallelAgent

from ..report_generator import report_generator_agent
from ..infographic_generator import infographic_generator_agent
from ..audio_overview import audio_overview_agent


artifact_generation_pipeline = ParallelAgent(
    name="ArtifactGenerationPipeline",
    description="""Generates all output artifacts in parallel:
    - 4A: HTML executive report (McKinsey/BCG style)
    - 4B: Visual infographic (Gemini image generation)
    - 4C: Audio podcast overview (Gemini multi-speaker TTS)

    All three agents run concurrently and share the same session state,
    reading from strategic_report and writing their respective outputs.
    """,
    sub_agents=[
        report_generator_agent,
        infographic_generator_agent,
        audio_overview_agent,
    ],
)
