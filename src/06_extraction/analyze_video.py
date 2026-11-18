"""Session 13: extract a transcript and key frames from a video with Content Understanding."""
import re
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import requests
from azure.identity import DefaultAzureCredential

from common.config import PROJECT_ENDPOINT

ENDPOINT = PROJECT_ENDPOINT.split("/api/projects/")[0] + "/contentunderstanding"
API = {"api-version": "2025-11-01"}
VIDEO_URL = (
    "https://media.githubusercontent.com/media/Azure-Samples/"
    "azure-ai-content-understanding-python/main/data/FlightSimulator.mp4"
)
CREDENTIAL = DefaultAzureCredential()


def headers() -> dict:
    return {"Authorization": "Bearer " + CREDENTIAL.get_token("https://cognitiveservices.azure.com/.default").token}


def analyze(analyzer: str, url: str) -> dict:
    """Submit the file, then poll the operation until it finishes (long-running operation)."""
    submit = requests.post(
        f"{ENDPOINT}/analyzers/{analyzer}:analyze", params=API, headers=headers(), json={"inputs": [{"url": url}]}, timeout=60
    )
    submit.raise_for_status()
    operation = submit.headers["Operation-Location"]
    while True:
        result = requests.get(operation, headers=headers(), timeout=60).json()
        status = result["status"].lower()
        if status in ("succeeded", "failed"):
            return result
        print(f"  {status}...")
        time.sleep(5)


def main() -> None:
    print("Analyzing the video (about a minute)...")
    result = analyze("prebuilt-video", VIDEO_URL)
    if result["status"].lower() != "succeeded":
        print("Failed:", result.get("error"))
        return
    content = result["result"]["contents"][0]
    markdown = content["markdown"]
    lines = re.findall(r"^(\d\d:\d\d\.\d{3}) --> \S+\n<(Speaker \d+)>(.*)$", markdown, flags=re.MULTILINE)
    speakers = sorted({speaker for _, speaker, _ in lines})
    print(f"Duration: {content['endTimeMs'] / 1000:.1f} s, {content['width']}x{content['height']}")
    print(f"Transcript lines: {len(lines)}, speakers: {', '.join(speakers)}, key frames: {markdown.count('keyFrame.')}")
    for start, speaker, text in lines:
        print(f"  [{start}] {speaker}: {text.strip()}")


if __name__ == "__main__":
    main()