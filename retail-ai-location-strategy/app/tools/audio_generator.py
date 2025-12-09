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

"""Gemini TTS audio generation tool for creating podcast-style audio overviews.

Uses Gemini 2.5 Flash Preview TTS model with multi-speaker configuration
to generate a conversational podcast-style audio summary of the location
intelligence report.

Saves the generated audio as an artifact using tool_context.save_artifact()
so it's accessible in adk web UI.
"""

import base64
import io
import logging
import wave
from google.adk.tools import ToolContext
from google.genai import types
from google.genai.errors import ServerError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ..config import TTS_MODEL, USE_VERTEX_AI

logger = logging.getLogger("LocationStrategyPipeline")


def _wrap_pcm_in_wav(pcm_data: bytes, sample_rate: int = 24000, channels: int = 1, sample_width: int = 2) -> bytes:
    """Wrap raw PCM audio data in a proper WAV container with headers.

    Gemini TTS returns raw PCM data (audio/L16) without WAV headers.
    This function adds the necessary RIFF/WAV headers so the audio
    can be played in browsers and media players.

    Args:
        pcm_data: Raw PCM audio bytes from Gemini TTS
        sample_rate: Sample rate in Hz (default 24000 for Gemini TTS)
        channels: Number of audio channels (default 1 for mono)
        sample_width: Bytes per sample (default 2 for 16-bit audio)

    Returns:
        Complete WAV file bytes with proper RIFF headers
    """
    wav_buffer = io.BytesIO()

    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)

    return wav_buffer.getvalue()


def _parse_sample_rate_from_mime(mime_type: str) -> int:
    """Extract sample rate from MIME type string.

    Gemini returns MIME like: audio/L16;codec=pcm;rate=24000

    Args:
        mime_type: MIME type string from Gemini response

    Returns:
        Sample rate in Hz (default 24000 if not found)
    """
    if "rate=" in mime_type:
        try:
            rate_str = mime_type.split("rate=")[1].split(";")[0]
            return int(rate_str)
        except (ValueError, IndexError):
            pass
    return 24000  # Default Gemini TTS sample rate


async def generate_audio_overview(podcast_script: str, tool_context: ToolContext) -> dict:
    """Generate a podcast-style audio overview using Gemini's TTS.

    This tool creates an audio summary of the location intelligence report.

    **AI Studio mode**: Uses multi-speaker TTS with two hosts (Host A and Host B)
    in a NotebookLM-style podcast format.

    **Vertex AI mode**: Uses single-speaker TTS with a narrator voice (Kore),
    as multi_speaker_voice_config is not supported in Vertex AI.

    The generated audio is automatically saved as an artifact named "audio_overview.wav"
    which can be viewed in the adk web UI.

    Args:
        podcast_script: A formatted script for audio generation.
                       For AI Studio: Use speaker labels like "Host A:", "Host B:"
                       For Vertex AI: Use plain narrative text (single narrator)
        tool_context: ADK ToolContext for saving artifacts and accessing state.

    Returns:
        dict: A dictionary containing:
            - status: "success" or "error"
            - message: Status message
            - artifact_saved: True if artifact was saved successfully
            - duration_estimate: Estimated audio duration
            - error_message: Error details (if failed)
    """
    try:
        from google import genai

        # Initialize Gemini client
        client = genai.Client()

        # Configure TTS based on authentication mode
        if USE_VERTEX_AI:
            # Vertex AI: Single-speaker mode only
            # multi_speaker_voice_config is NOT supported in Vertex AI
            speech_config = types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Kore"  # Professional narrator voice
                    )
                )
            )
            logger.info("Using single-speaker TTS (Vertex AI mode)")
        else:
            # AI Studio: Multi-speaker mode supported
            # Configure with two distinct voices for podcast-style dialogue
            # Kore: Professional, authoritative voice (Host A - main narrator)
            # Puck: Friendly, conversational voice (Host B - analyst)
            speech_config = types.SpeechConfig(
                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                    speaker_voice_configs=[
                        types.SpeakerVoiceConfig(
                            speaker="Host A",
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name="Kore"
                                )
                            ),
                        ),
                        types.SpeakerVoiceConfig(
                            speaker="Host B",
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name="Puck"
                                )
                            ),
                        ),
                    ]
                )
            )
            logger.info("Using multi-speaker TTS (AI Studio mode)")

        # Retry wrapper for handling model overload errors
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=2, min=2, max=30),
            retry=retry_if_exception_type(ServerError),
            before_sleep=lambda retry_state: logger.warning(
                f"Gemini TTS API error, retrying in {retry_state.next_action.sleep} seconds... "
                f"(attempt {retry_state.attempt_number}/3)"
            ),
        )
        def generate_with_retry():
            return client.models.generate_content(
                model=TTS_MODEL,
                contents=podcast_script,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=speech_config,
                ),
            )

        # Generate the audio using Gemini TTS model
        logger.info(f"Generating audio with {'single-speaker' if USE_VERTEX_AI else 'multi-speaker'} TTS...")
        response = generate_with_retry()

        # Check for successful generation
        if response.candidates and len(response.candidates) > 0:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    raw_audio_bytes = part.inline_data.data
                    raw_mime_type = part.inline_data.mime_type or "audio/L16"

                    # Parse sample rate from MIME type (e.g., "audio/L16;codec=pcm;rate=24000")
                    sample_rate = _parse_sample_rate_from_mime(raw_mime_type)

                    # Wrap raw PCM in WAV container with proper headers
                    # Gemini returns raw PCM without headers, which won't play in browsers/VLC
                    audio_bytes = _wrap_pcm_in_wav(raw_audio_bytes, sample_rate=sample_rate)
                    mime_type = "audio/wav"
                    logger.info(f"Wrapped raw PCM ({len(raw_audio_bytes)} bytes) in WAV container ({len(audio_bytes)} bytes)")

                    # Calculate duration from raw PCM size (16-bit mono = 2 bytes per sample)
                    duration_seconds = len(raw_audio_bytes) / (sample_rate * 2)
                    duration_str = f"{int(duration_seconds // 60)}:{int(duration_seconds % 60):02d}"

                    # Save the audio directly as an artifact using tool_context
                    try:
                        audio_artifact = types.Part.from_bytes(
                            data=audio_bytes,
                            mime_type=mime_type
                        )
                        artifact_filename = "audio_overview.wav"
                        version = await tool_context.save_artifact(
                            filename=artifact_filename,
                            artifact=audio_artifact
                        )
                        logger.info(
                            f"Saved audio artifact: {artifact_filename} "
                            f"(version {version}, ~{duration_str})"
                        )

                        # Also store base64 in state for AG-UI frontend display
                        b64_audio = base64.b64encode(audio_bytes).decode('utf-8')
                        tool_context.state["audio_overview_base64"] = f"data:{mime_type};base64,{b64_audio}"
                        tool_context.state["audio_overview_duration"] = duration_str

                        return {
                            "status": "success",
                            "message": f"Audio overview generated and saved as artifact '{artifact_filename}'",
                            "artifact_saved": True,
                            "artifact_filename": artifact_filename,
                            "artifact_version": version,
                            "mime_type": mime_type,
                            "duration_estimate": duration_str,
                            "size_bytes": len(audio_bytes),
                        }
                    except Exception as save_error:
                        logger.warning(f"Failed to save audio artifact: {save_error}")
                        # Still return success with base64 data as fallback
                        return {
                            "status": "success",
                            "message": "Audio overview generated but artifact save failed",
                            "artifact_saved": False,
                            "audio_data": base64.b64encode(audio_bytes).decode("utf-8"),
                            "mime_type": mime_type,
                            "duration_estimate": duration_str,
                            "save_error": str(save_error),
                        }

        # No audio found in response
        return {
            "status": "error",
            "error_message": "No audio was generated in the response. The model may have encountered an issue.",
        }

    except Exception as e:
        logger.error(f"Failed to generate audio overview: {e}")
        return {
            "status": "error",
            "error_message": f"Failed to generate audio overview: {str(e)}",
        }
