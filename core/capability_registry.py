from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentCapability:
    name: str
    description: str
    examples: list[str] = field(default_factory=list)


@dataclass
class AgentRegistration:
    name: str
    description: str
    capabilities: list[AgentCapability]
    agent: Any = None


class CapabilityRegistry:

    def __init__(self):
        self._agents: dict[str, AgentRegistration] = {}


    def register_agent(
        self,
        name: str,
        description: str,
        capabilities: list[AgentCapability],
        agent=None,
    ):
        if name in self._agents:
            raise ValueError(
                f"Agent '{name}' is already registered."
            )

        self._agents[name] = AgentRegistration(
            name=name,
            description=description,
            capabilities=capabilities,
            agent=agent,
        )


    def get_agent(self, agent_name: str):
        registration = self._agents.get(agent_name)

        if registration is None:
            return None

        return registration.agent


    def has_agent(self, agent_name: str) -> bool:
        return agent_name in self._agents


    def get_agent_names(self) -> list[str]:
        return list(self._agents.keys())


    def get_capability_map(self) -> dict:

        return {
            name: {
                "description": registration.description,

                "capabilities": [
                    {
                        "name": capability.name,
                        "description": capability.description,
                        "examples": capability.examples,
                    }

                    for capability
                    in registration.capabilities
                ],
            }

            for name, registration
            in self._agents.items()
        }


    def get_planner_context(self) -> str:
        """
        Produce a readable capability description for the Planner.
        """

        sections = []

        for registration in self._agents.values():

            lines = [
                f"Agent: {registration.name}",
                f"Description: {registration.description}",
                "Capabilities:",
            ]

            for capability in registration.capabilities:

                lines.append(
                    f"- {capability.name}: "
                    f"{capability.description}"
                )

                if capability.examples:
                    lines.append(
                        "  Examples: "
                        + "; ".join(capability.examples)
                    )

            sections.append("\n".join(lines))

        return "\n\n".join(sections)