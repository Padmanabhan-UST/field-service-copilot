"""Session 11: generate a damaged-part photo, assess it with a multimodal model, and edit it."""
import base64
import sys
from pathlib import Path
from typing import Literal

sys.path.append(str(Path(__file__).resolve().parents[1]))

from pydantic import BaseModel

from common.clients import image_client, openai_client
from common.config import CHAT_DEPLOYMENT, IMAGE_DEPLOYMENT

IMAGES = Path(__file__).resolve().parents[2] / "data" / "images"
DAMAGED = IMAGES / "damaged_bearing.png"
REPAIRED = IMAGES / "repaired_bearing.png"


class DamageReport(BaseModel):
    part: str
    damage_type: Literal["corrosion", "pitting", "cracking", "wear", "overheating", "none"]
    severity: Literal["low", "medium", "high"]
    replace: bool
    evidence: str


def generate_photo() -> None:
    if DAMAGED.exists():
        print(f"Using existing {DAMAGED.name} (saves an image call)")
        return
    result = image_client().images.generate(
        model=IMAGE_DEPLOYMENT,
        prompt="Close-up photo of a corroded, pitted ball bearing removed from an industrial centrifugal pump, "
        "lying on a workshop bench, realistic",
        size="1024x1024",
    )
    DAMAGED.write_bytes(base64.b64decode(result.data[0].b64_json))
    print(f"Generated {DAMAGED.name}")


def assess_damage() -> DamageReport:
    image_b64 = base64.b64encode(DAMAGED.read_bytes()).decode()
    response = openai_client().responses.parse(
        model=CHAT_DEPLOYMENT,
        instructions="You inspect photos of industrial pump parts for a maintenance team.",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Assess the damage on this part."},
                    {"type": "input_image", "image_url": f"data:image/png;base64,{image_b64}"},
                ],
            }
        ],
        text_format=DamageReport,
    )
    return response.output_parsed


def show_repaired() -> None:
    result = image_client().images.edit(
        model=IMAGE_DEPLOYMENT,
        image=open(DAMAGED, "rb"),
        prompt="Replace the corroded bearing with a brand-new, clean ball bearing; keep everything else unchanged",
        size="1024x1024",
    )
    REPAIRED.write_bytes(base64.b64decode(result.data[0].b64_json))
    print(f"Saved {REPAIRED.name}")


def main() -> None:
    generate_photo()
    report = assess_damage()
    print(report.model_dump_json(indent=2))
    if report.replace:
        show_repaired()


if __name__ == "__main__":
    main()