from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class EcoStage:
    stage_id: int
    name: str
    min_points: int
    description: str
    flair_icon: str
    color_hex: str


ECO_STAGES: List[EcoStage] = [
    EcoStage(
        stage_id=1,
        name="Eco Seed",
        min_points=0,
        description="Starting your campus sustainability journey.",
        flair_icon="seed",
        color_hex="#10B981",
    ),
    EcoStage(
        stage_id=2,
        name="Green Sprout",
        min_points=100,
        description="Developing consistent waste segregation habits.",
        flair_icon="sprout",
        color_hex="#059669",
    ),
    EcoStage(
        stage_id=3,
        name="Eco Explorer",
        min_points=300,
        description="Active campus participant and waste classification advocate.",
        flair_icon="compass",
        color_hex="#0284C7",
    ),
    EcoStage(
        stage_id=4,
        name="Sustainability Champion",
        min_points=750,
        description="Leading by example with high-volume clean disposals.",
        flair_icon="medal",
        color_hex="#8B5CF6",
    ),
    EcoStage(
        stage_id=5,
        name="Eco Guardian",
        min_points=1500,
        description="Protecting DBIT campus environment through verified reporting.",
        flair_icon="shield",
        color_hex="#F59E0B",
    ),
    EcoStage(
        stage_id=6,
        name="Campus Earth Hero",
        min_points=3000,
        description="Top-tier environmental stewardship and campus zero-waste leadership.",
        flair_icon="trophy",
        color_hex="#EF4444",
    ),
]


def calculate_eco_stage(total_earned_points: int) -> dict:
    """Calculate the user's current stage, progress, and next milestone from cumulative EARN points.
    
    Cumulative lifetime EARN points are used so spending points on rewards never degrades stage.
    """
    total_earned = max(0, int(total_earned_points or 0))
    current_stage = ECO_STAGES[0]
    next_stage: Optional[EcoStage] = None

    for i, stage in enumerate(ECO_STAGES):
        if total_earned >= stage.min_points:
            current_stage = stage
            if i + 1 < len(ECO_STAGES):
                next_stage = ECO_STAGES[i + 1]
            else:
                next_stage = None

    if next_stage:
        points_in_stage = total_earned - current_stage.min_points
        stage_span = next_stage.min_points - current_stage.min_points
        progress_percentage = min(100.0, max(0.0, (points_in_stage / stage_span) * 100.0))
        points_to_next = max(0, next_stage.min_points - total_earned)
    else:
        progress_percentage = 100.0
        points_to_next = 0

    return {
        "stage_id": current_stage.stage_id,
        "stage_name": current_stage.name,
        "description": current_stage.description,
        "flair_icon": current_stage.flair_icon,
        "color_hex": current_stage.color_hex,
        "min_points": current_stage.min_points,
        "lifetime_earned_points": total_earned,
        "next_stage_name": next_stage.name if next_stage else None,
        "next_stage_min_points": next_stage.min_points if next_stage else None,
        "points_to_next_stage": points_to_next,
        "progress_percentage": round(progress_percentage, 2),
        "is_max_stage": next_stage is None,
    }
