"""In-memory data for the POC tools."""

from __future__ import annotations

from datetime import date

from expert_finder.expert_finder.types.schemas import Candidate, CV, InstitutionRecord


CANDIDATES = [
    Candidate(
        name="Avery Chen",
        current_title="Principal ML Engineer",
        institution_records=[
            InstitutionRecord(
                institution="OpenAI",
                role="Research Engineer",
                start_date=date(2019, 1, 1),
                end_date=date(2022, 6, 1),
            )
        ],
    ),
    Candidate(
        name="Diego Morales",
        current_title="Data Science Lead",
        institution_records=[
            InstitutionRecord(
                institution="Google",
                role="Senior Data Scientist",
                start_date=date(2017, 5, 1),
                end_date=date(2021, 12, 1),
            )
        ],
    ),
    Candidate(
        name="Priya Patel",
        current_title="AI Product Manager",
        institution_records=[
            InstitutionRecord(
                institution="OpenAI",
                role="Product Manager",
                start_date=date(2020, 3, 1),
                end_date=date(2023, 8, 1),
            )
        ],
    ),
    Candidate(
        name="Samir Khan",
        current_title="Applied Scientist",
        institution_records=[
            InstitutionRecord(
                institution="Amazon",
                role="Applied Scientist",
                start_date=date(2018, 2, 1),
                end_date=date(2022, 2, 1),
            ),
            InstitutionRecord(
                institution="OpenAI",
                role="Research Scientist",
                start_date=date(2022, 3, 1),
                end_date=None,
            ),
        ],
    ),
    Candidate(
        name="Maya Rodriguez",
        current_title="ML Researcher",
        institution_records=[
            InstitutionRecord(
                institution="Stanford University",
                role="PhD Researcher",
                start_date=date(2016, 9, 1),
                end_date=date(2021, 6, 1),
            )
        ],
    ),
    Candidate(
        name="Elena Fischer",
        current_title="Senior NLP Engineer",
        institution_records=[
            InstitutionRecord(
                institution="OpenAI",
                role="NLP Engineer",
                start_date=date(2018, 4, 1),
                end_date=date(2021, 9, 1),
            ),
            InstitutionRecord(
                institution="Meta",
                role="Senior NLP Engineer",
                start_date=date(2021, 10, 1),
                end_date=None,
            ),
        ],
    ),
    Candidate(
        name="Jordan Lee",
        current_title="Security Engineer",
        institution_records=[
            InstitutionRecord(
                institution="OpenAI",
                role="Security Engineer",
                start_date=date(2019, 7, 1),
                end_date=date(2022, 11, 1),
            )
        ],
    ),
    Candidate(
        name="Nadia Ivanova",
        current_title="Research Scientist",
        institution_records=[
            InstitutionRecord(
                institution="OpenAI",
                role="Research Scientist",
                start_date=date(2017, 2, 1),
                end_date=date(2020, 12, 1),
            )
        ],
    ),
]

CVS = {
    "Avery Chen": CV(
        name="Avery Chen",
        summary="Research engineer focused on model optimization and infra.",
        experience=[
            "Built model evaluation pipelines for large-scale training.",
            "Led deployment of distributed training infrastructure.",
        ],
        skills=["model evaluation", "distributed systems", "Python"],
        education=["MS Computer Science, UC Berkeley"],
        publications=["Efficient Scaling of Transformer Training"],
    ),
    "Diego Morales": CV(
        name="Diego Morales",
        summary="Data science lead with experimentation and forecasting focus.",
        experience=[
            "Owned experimentation platform and causal analysis.",
            "Built forecasting models for supply chain optimization.",
        ],
        skills=["causal inference", "forecasting", "SQL"],
        education=["PhD Statistics, University of Michigan"],
        publications=["Robust Causal Experiments in Production"],
    ),
    "Priya Patel": CV(
        name="Priya Patel",
        summary="AI product manager with model-driven product launches.",
        experience=[
            "Launched AI-assisted developer tooling product.",
            "Defined evaluation metrics for LLM product readiness.",
        ],
        skills=["product strategy", "LLM evaluation", "roadmapping"],
        education=["MBA, Wharton"],
        publications=["Measuring LLM Product Impact"],
    ),
    "Samir Khan": CV(
        name="Samir Khan",
        summary="Applied scientist focused on recommendation and ranking.",
        experience=[
            "Improved ranking models with deep learning features.",
            "Published on large-scale recommender systems.",
        ],
        skills=["ranking", "deep learning", "Python"],
        education=["PhD Computer Science, UIUC"],
        publications=["Neural Ranking at Scale"],
    ),
    "Maya Rodriguez": CV(
        name="Maya Rodriguez",
        summary="ML researcher with academic and industry collaboration.",
        experience=[
            "Researched interpretability methods for neural networks.",
            "Collaborated with industry lab on safety benchmarks.",
        ],
        skills=["interpretability", "ML safety", "PyTorch"],
        education=["PhD Computer Science, Stanford"],
        publications=["Interpretability Benchmarks for NLP"],
    ),
    "Elena Fischer": CV(
        name="Elena Fischer",
        summary="NLP engineer with productionization of language models.",
        experience=[
            "Deployed multilingual NLP pipelines in production.",
            "Optimized inference for transformer-based services.",
        ],
        skills=["NLP", "model serving", "Python"],
        education=["MS Computational Linguistics, University of Washington"],
        publications=["Latency-Aware Transformer Serving"],
    ),
    "Jordan Lee": CV(
        name="Jordan Lee",
        summary="Security engineer specializing in AI infrastructure security.",
        experience=[
            "Built threat modeling program for AI systems.",
            "Implemented security controls for model training clusters.",
        ],
        skills=["threat modeling", "cloud security", "Python"],
        education=["BS Computer Engineering, Purdue"],
        publications=["Securing AI Training Infrastructure"],
    ),
    "Nadia Ivanova": CV(
        name="Nadia Ivanova",
        summary="Research scientist with focus on alignment and evaluation.",
        experience=[
            "Designed alignment evaluation suites for LLMs.",
            "Led research on reward modeling techniques.",
        ],
        skills=["alignment", "reward modeling", "Python"],
        education=["PhD Computer Science, CMU"],
        publications=["Reward Modeling for Aligned LLMs"],
    ),
}
