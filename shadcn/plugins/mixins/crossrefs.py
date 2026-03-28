import importlib
import re
from typing import Dict, List, Optional

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import get_plugin_logger
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page

from shadcn.plugins.mixins.base import Mixin

logger = get_plugin_logger("mixins/crossrefs")

# Matches backtick-quoted names that look like Python references
# (e.g. `foo`, `pkg.Class`, `pkg.mod.func`) but NOT already linked ones
# like [`foo`][bar].
BACKTICK_REF_RE = re.compile(r"(?<!\[)`([A-Za-z_][\w.]*)`(?!\])")


class CrossRefsMixin(Mixin):
    """Auto-link backtick references to mkdocstrings anchors.

    When mkdocstrings is configured, this mixin auto-converts backtick
    references like `SomeClass` into mkdocstrings cross-reference links
    [`SomeClass`][pkg.SomeClass].

    Configure via theme config:
        crossref_modules: list of dotted module names to search
            (default: auto-discovered top-level packages from mkdocstrings paths)
        crossref_aliases: dict mapping short names to fully qualified names
    """

    crossrefs_modules: List = []
    crossrefs_aliases: Dict[str, str] = {}
    crossrefs_activated: bool = False

    def on_config(self, config: MkDocsConfig):
        plugin = config["plugins"].get("mkdocstrings", None)
        if plugin is None:
            return super().on_config(config)

        self.crossrefs_aliases = config.theme.get("crossref_aliases", {})
        self.crossrefs_modules = []

        # If user specified explicit modules, use those
        explicit_modules = config.theme.get("crossref_modules", None)

        if explicit_modules is not None:
            for mod_name in explicit_modules:
                try:
                    mod = importlib.import_module(mod_name)
                    self.crossrefs_modules.append((mod_name, mod))
                    logger.info(f"Cross-refs: loaded module '{mod_name}'.")
                except Exception as e:
                    logger.warning(f"Cross-refs: could not import '{mod_name}': {e}")
        else:
            # Auto-discover top-level packages from mkdocstrings paths
            import os

            handler_config = plugin.config.get("handlers", {}).get("python", {})
            paths = handler_config.get("paths", [])

            for path in paths:
                if not os.path.isdir(path):
                    continue
                for entry in sorted(os.listdir(path)):
                    entry_path = os.path.join(path, entry)
                    if os.path.isdir(entry_path) and os.path.isfile(
                        os.path.join(entry_path, "__init__.py")
                    ):
                        try:
                            mod = importlib.import_module(entry)
                            self.crossrefs_modules.append((entry, mod))
                            logger.info(f"Cross-refs: loaded module '{entry}'.")
                        except Exception as e:
                            logger.debug(f"Cross-refs: could not import '{entry}': {e}")

        self.crossrefs_activated = len(self.crossrefs_modules) > 0

        if self.crossrefs_activated:
            logger.info(
                f"Cross-refs mixin activated for: "
                f"{[name for name, _ in self.crossrefs_modules]}"
            )

        return super().on_config(config)

    def _resolve_ref(self, name: str) -> Optional[str]:
        """Resolve a backtick name to its fully qualified mkdocstrings anchor."""
        *prefix, short = name.split(".")
        if prefix and prefix[0] not in {n for n, _ in self.crossrefs_modules}:
            return None

        # Check aliases first
        if short in self.crossrefs_aliases:
            return self.crossrefs_aliases[short]

        # Check each module directly — no recursion
        for mod_name, mod in self.crossrefs_modules:
            if hasattr(mod, short):
                return f"{mod_name}.{short}"

        return None

    def on_page_markdown(
        self,
        markdown: str,
        /,
        *,
        page: Page,
        config: MkDocsConfig,
        files: Files,
    ) -> str:
        if not self.crossrefs_activated:
            return super().on_page_markdown(
                markdown, page=page, config=config, files=files
            )

        # Split on code blocks to avoid processing fenced code
        blocks = markdown.split("```")
        for i, block in enumerate(blocks):
            if i % 2 == 0:
                blocks[i] = self._insert_cross_refs(block)
            else:
                blocks[i] = f"```{block}```"

        markdown = "".join(blocks)

        return super().on_page_markdown(
            markdown, page=page, config=config, files=files
        )

    def _insert_cross_refs(self, text: str) -> str:
        """Replace backtick references with mkdocstrings links."""
        replacements = {}
        for match in BACKTICK_REF_RE.finditer(text):
            name = match.group(1)
            full_match = match.group(0)
            if full_match in replacements:
                continue
            ref = self._resolve_ref(name)
            if ref is not None:
                replacements[full_match] = f"[`{name}`][{ref}]"

        for old, new in replacements.items():
            text = text.replace(old, new)

        return text
