from typing import Dict, List, Any, Optional
import models
import schemas
from .prompt_template_engine import PromptTemplateEngine

class PromptBuilder:
    """エージェントのパーソナリティを反映したプロンプトを構築"""

    def __init__(self, template_engine: PromptTemplateEngine):
        self.template_engine = template_engine

    async def build(
        self,
        message: str,
        agent: Optional[models.Agent] = None,
        context: Optional[List[Dict[str, str]]] = None,
        template_name: Optional[str] = None,
        r18_mode_chat: bool = False,
        **kwargs: Any
    ) -> str:
        """プロンプトを構築"""
        
        # 1. Determine the template name
        if template_name is None:
            if agent:
                personality_info = self._extract_personality_info(agent)
                # Simple logic to select a template based on roles
                if "customer_support" in personality_info["roles"]:
                    final_template_name = "customer_support.j2"
                else:
                    final_template_name = "default.j2"
            else:
                # Default template if no agent and no specific template is requested
                final_template_name = "default.j2"
        else:
            final_template_name = template_name

        # 2. Prepare rendering context
        render_context = {
            "user_message": message,
            "conversation_history": context or [],
            "r18_mode_enabled": r18_mode_chat,
            **kwargs
        }

        if agent:
            # This ensures personality_info is calculated if not already done
            if 'personality_info' not in locals():
                personality_info = self._extract_personality_info(agent)
            
            render_context.update({
                "agent_name": agent.name,
                "agent_description": agent.description,
                "agent_background": agent.background,
                "personalities": personality_info["personalities"],
                "roles": personality_info["roles"],
                "tones": personality_info["tones"],
                "gender": agent.gender,
                "first_person": agent.first_person,
                "second_person": agent.second_person,
                "relationship": agent.relationship_status,
            })

        # 3. Get template and render
        template = self.template_engine.get_template(final_template_name)
        prompt = template.render(render_context)
        
        return prompt

    def _extract_personality_info(self, agent: models.Agent) -> Dict[str, List[str]]:
        """エージェントのパーソナリティ情報を抽出・整形"""
        return {
            "personalities": [p.name for p in agent.personalities],
            "roles": [r.name for r in agent.roles],
            "tones": [t.name for t in agent.tones]
        }