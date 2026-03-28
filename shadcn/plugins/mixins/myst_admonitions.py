import re

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import get_plugin_logger
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page

from shadcn.plugins.mixins.base import Mixin

logger = get_plugin_logger("mixins/myst_admonitions")

# Maps MyST admonition types to standard mkdocs admonition types
ADMONITION_ALIASES = {
    "hint": "info",
    "seealso": "tip",
    "important": "warning",
    "versionadded": "note",
    "versionchanged": "note",
    "deprecated": "warning",
}

# Pattern matching ```{type}\n...\n``` blocks
MYST_BLOCK_RE = re.compile(
    r"```\{(\w+)\}\s*\n(.*?)```",
    re.DOTALL,
)


def _convert_block(match: re.Match) -> str:
    """Convert a MyST-style fenced admonition to a standard mkdocs admonition."""
    admonition_type = match.group(1)
    content = match.group(2)
    admonition_type = ADMONITION_ALIASES.get(admonition_type, admonition_type)
    lines = content.strip().split("\n")
    indented = "\n".join(f"    {line.strip()}" for line in lines)
    return f"!!! {admonition_type}\n\n{indented}\n"


class MystAdmonitionsMixin(Mixin):
    """Convert MyST-style fenced admonitions to standard mkdocs admonitions.

    Converts syntax like:

        ```{hint}
        Some content here.
        ```

    Into:

        !!! info

            Some content here.
    """

    def on_page_markdown(
        self,
        markdown: str,
        /,
        *,
        page: Page,
        config: MkDocsConfig,
        files: Files,
    ) -> str:
        markdown = MYST_BLOCK_RE.sub(_convert_block, markdown)
        return super().on_page_markdown(
            markdown,
            page=page,
            config=config,
            files=files,
        )
