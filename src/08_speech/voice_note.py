"""Session 12: voice note -> transcript (phrase list) -> translation (dictionary) -> spoken translation."""
import json
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.append(str(Path(__file__).resolve().parents[1]))

import requests
from azure.identity import DefaultAzureCredential

from common.config import AZURE_REGION, FOUNDRY_RESOURCE_ID, PROJECT_ENDPOINT

ENDPOINT = PROJECT_ENDPOINT.split("/api/projects/")[0].replace("services.ai.azure.com", "cognitiveservices.azure.com")
AUDIO = Path(__file__).resolve().parents[2] / "data" / "audio"
CREDENTIAL = DefaultAzureCredential()

NOTE = (
    "Voice note for pump one-oh-one. Alarm E one-oh-three is active and the pump sounds like gravel. "
    "I think we need two B R G sixty-two oh five bearings."
)
PHRASES = ["we need two BRG 6205 bearings", "E103"]
PART_CODE = re.compile(r"\b[A-Z]{1,4}[- ]?\d{3,4}(?:-\w+)?\b")  # E103, BRG 6205, BRG-6205-2RS


def headers() -> dict:
    token = CREDENTIAL.get_token("https://cognitiveservices.azure.com/.default").token
    return {"Authorization": f"Bearer {token}"}


def speak(text: str, voice: str, language: str, path: Path) -> None:
    ssml = f'<speak version="1.0" xml:lang="{language}"><voice name="{voice}">{escape(text)}</voice></speak>'
    response = requests.post(
        f"{ENDPOINT}/tts/cognitiveservices/v1",
        headers={**headers(), "Content-Type": "application/ssml+xml", "X-Microsoft-OutputFormat": "riff-16khz-16bit-mono-pcm"},
        data=ssml.encode("utf-8"),
        timeout=60,
    )
    response.raise_for_status()
    path.write_bytes(response.content)
    print(f"  saved {path.name}")


def transcribe(path: Path, phrases: list[str] | None = None) -> str:
    definition = {"locales": ["en-US"]}
    if phrases:
        definition["phraseList"] = {"phrases": phrases}
    response = requests.post(
        f"{ENDPOINT}/speechtotext/transcriptions:transcribe",
        params={"api-version": "2025-10-15"},
        headers=headers(),
        files={"audio": (path.name, path.read_bytes(), "audio/wav"), "definition": (None, json.dumps(definition), "application/json")},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["combinedPhrases"][0]["text"]


def translate(text: str, to: str) -> str:
    protected = PART_CODE.sub(lambda m: f'<mstrans:dictionary translation="{m.group(0)}">{m.group(0)}</mstrans:dictionary>', text)
    response = requests.post(
        f"{ENDPOINT}/translator/text/v3.0/translate",
        params={"api-version": "3.0", "to": to},
        headers={**headers(), "Ocp-Apim-ResourceId": FOUNDRY_RESOURCE_ID, "Ocp-Apim-Subscription-Region": AZURE_REGION},
        json=[{"text": protected}],
        timeout=60,
    )
    response.raise_for_status()
    return response.json()[0]["translations"][0]["text"]


def main() -> None:
    print("1. Technician records a voice note (simulated with text-to-speech)")
    note = AUDIO / "voice_note.wav"
    speak(NOTE, "en-US-AndrewMultilingualNeural", "en-US", note)

    print("\n2. Speech-to-text")
    print(f"  without phrase list: {transcribe(note)}")
    transcript = transcribe(note, PHRASES)
    print(f"  with phrase list:    {transcript}")

    print("\n3. Translate for the German site (part codes protected)")
    german = translate(transcript, "de")
    print(f"  {german}")

    print("\n4. Speak the German version")
    speak(german, "de-DE-KatjaNeural", "de-DE", AUDIO / "voice_note_de.wav")


if __name__ == "__main__":
    main()