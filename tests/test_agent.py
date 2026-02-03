from expert_finder.expert_finder.agent.expert_finder import ExpertFinderAgent
from expert_finder.expert_finder.llm.stub import DeterministicStubLLM
from expert_finder.expert_finder.tools.institution_search import InstitutionSearchTool
from expert_finder.expert_finder.tools.profile_retrieval import ProfileRetrievalTool


def test_agent_basic_flow():
    agent = ExpertFinderAgent(
        llm=DeterministicStubLLM(),
        institution_search=InstitutionSearchTool(),
        profile_retrieval=ProfileRetrievalTool(),
    )

    result = agent.run("People with previous experience at OpenAI in role Research Engineer")

    assert result.experts
    assert len(result.experts) <= 3
