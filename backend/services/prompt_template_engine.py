from jinja2 import Environment, FileSystemLoader, Template
from typing import List

# This is a simplified version based on the architecture document.
# In a real application, you might have more complex logic
# to select templates based on agent properties.

class PromptTemplateEngine:
    """プロンプトテンプレートの管理と選択"""

    def __init__(self, template_dir: str = "templates/prompts"):
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def get_template(self, template_name: str) -> Template:
        """指定された名前のテンプレートを取得"""
        return self.env.get_template(template_name)