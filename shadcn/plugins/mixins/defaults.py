from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import get_plugin_logger

from shadcn.plugins.mixins.base import Mixin

logger = get_plugin_logger("mixins/defaults")

# Standard markdown extensions that the shadcn theme expects/recommends.
# Only injected if the user hasn't configured them.
DEFAULT_MARKDOWN_EXTENSIONS = {
    "attr_list": {},
    "toc": {"permalink": True},
    "pymdownx.highlight": {
        "anchor_linenums": True,
        "line_spans": "__span",
        "pygments_lang_class": True,
    },
    "pymdownx.inlinehilite": {},
    "pymdownx.snippets": {},
    "pymdownx.magiclink": {},
    "pymdownx.tabbed": {"alternate_style": True},
    "admonition": {},
    "pymdownx.details": {},
    "pymdownx.arithmatex": {"generic": True},
    "pymdownx.superfences": {},
}

# Default mkdocstrings handler options for Python.
DEFAULT_MKDOCSTRINGS_OPTIONS = {
    "allow_inspection": True,
    "docstring_style": "google",
    "docstring_options": {"ignore_init_summary": True},
    "docstring_section_style": "table",
    "filters": ["!^_"],
    "heading_level": 1,
    "inherited_members": True,
    "merge_init_into_class": True,
    "separate_signature": True,
    "show_root_heading": True,
    "show_root_full_path": False,
    "show_signature_annotations": True,
    "show_source": True,
    "show_symbol_type_heading": True,
    "show_symbol_type_toc": True,
    "signature_crossrefs": True,
    "summary": True,
}


class DefaultsMixin(Mixin):
    """Inject sensible default markdown extensions and mkdocstrings config.

    - Adds standard markdown extensions if not already configured by the user.
    - Sets default mkdocstrings Python handler options, merging with any
      user-provided overrides (user values take precedence).
    """

    def on_config(self, config: MkDocsConfig):
        self._inject_markdown_extensions(config)
        self._inject_mkdocstrings_defaults(config)
        return super().on_config(config)

    def _inject_markdown_extensions(self, config: MkDocsConfig):
        """Add default markdown extensions if not already present."""
        # Build a set of already-configured extension names
        existing = set()
        for ext in config.markdown_extensions:
            if isinstance(ext, str):
                existing.add(ext)

        # mdx_configs holds extension options
        mdx_configs = config.get("mdx_configs", {})

        for ext_name, ext_defaults in DEFAULT_MARKDOWN_EXTENSIONS.items():
            if ext_name not in existing:
                config.markdown_extensions.append(ext_name)
                if ext_defaults and ext_name not in mdx_configs:
                    mdx_configs[ext_name] = ext_defaults
                logger.debug(f"Added default markdown extension: {ext_name}")

    def _inject_mkdocstrings_defaults(self, config: MkDocsConfig):
        """Set default mkdocstrings options, letting user overrides win."""
        plugin = config["plugins"].get("mkdocstrings", None)
        if plugin is None:
            return

        handlers = plugin.config.get("handlers", {})
        python = handlers.get("python", {})
        user_options = python.get("options", {})

        # Merge: defaults first, then user overrides on top
        merged = {**DEFAULT_MKDOCSTRINGS_OPTIONS, **user_options}
        python.setdefault("options", {}).update(merged)

        # Ensure the nested dicts are wired up
        handlers["python"] = python
        plugin.config["handlers"] = handlers

        logger.debug("Applied default mkdocstrings options.")
