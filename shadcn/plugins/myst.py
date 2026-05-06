from mkdocs.plugins import BasePlugin

from shadcn.plugins.mixins.myst_admonitions import MystAdmonitionsMixin


class MystPlugin(MystAdmonitionsMixin, BasePlugin):
    """Standalone plugin that converts MyST-style fenced admonitions.

    Converts ``{note}``, ``{warning}``, etc. to standard mkdocs admonitions.
    Use this when not using ``shadcn/search``.
    """
