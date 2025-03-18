from typing import TypedDict


class JobFields(TypedDict):
    title: str
    company: str
    description: str
    url: str
    apply_url: str
    applicants: str
    locations: str
    salary_range: str
    sources: list[str]
    score: str
    comment: str
    ai_model: str
    applied: bool
    interview_status: str  # New field: pending/scheduled/completed
    slug: str

    # Internal tracking
    added_date: str
