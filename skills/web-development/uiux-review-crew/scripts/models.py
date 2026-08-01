from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class DimensionScore(BaseModel):
    name: str
    score: int = Field(ge=0, le=10)
    weight: float
    rationale: str

class UICriticOutput(BaseModel):
    overall_impression: str
    strengths: List[str]
    critical_issues: List[str]
    additional_improvements: List[str]
    top_priorities: List[str]
    dimension_scores: List[DimensionScore]
    images_analyzed: bool
    key_issues_count: int
    critical_priority: str
    target_audience: str

class DesignPlan(BaseModel):
    primary_goal: str
    target_user: str
    key_theme: str
    layout_changes: dict
    color_palette: dict
    typography: dict
    cta_optimization: dict
    accessibility: dict
    mobile_considerations: dict
    content_recommendations: dict
    improvement_categories: List[str]
    estimated_impact: Literal["High", "Medium", "Low"]
    implementation_complexity: Literal["Simple", "Moderate", "Complex"]

class VisualImplementerOutput(BaseModel):
    summary: str
    key_improvements: List[str]
    expected_impact: str

class ReviewResult(BaseModel):
    input_source: str
    timestamp: datetime
    screenshot_path: str
    ui_critic: UICriticOutput
    design_strategist: DesignPlan
    visual_implementer: VisualImplementerOutput
    composite_score: float
    passed: bool
    threshold: int
    report_path: str
    json_path: str