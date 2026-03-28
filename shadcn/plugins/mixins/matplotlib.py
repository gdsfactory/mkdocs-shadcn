from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import get_plugin_logger

from shadcn.plugins.mixins.base import Mixin

logger = get_plugin_logger("mixins/matplotlib")

# Sensible defaults for matplotlib figures in docs:
# transparent backgrounds and grey axes/text so plots look good on both
# light and dark themes.
MATPLOTLIB_RCPARAMS = {
    "figure.figsize": (6, 2.5),
    "axes.grid": True,
    "lines.color": "grey",
    "patch.edgecolor": "grey",
    "text.color": "grey",
    "axes.facecolor": "ffffff00",
    "axes.edgecolor": "grey",
    "axes.labelcolor": "grey",
    "xtick.color": "grey",
    "ytick.color": "grey",
    "grid.color": "grey",
    "figure.facecolor": "ffffff00",
    "figure.edgecolor": "ffffff00",
    "savefig.facecolor": "ffffff00",
    "savefig.edgecolor": "ffffff00",
}


class MatplotlibMixin(Mixin):
    """Set matplotlib rcParams so plots render well on light and dark themes.

    Applies transparent backgrounds and grey axes/text/grid by default.
    Only activates if matplotlib is installed.
    """

    def on_config(self, config: MkDocsConfig):
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            logger.debug("matplotlib not installed, skipping rcParams setup.")
            return super().on_config(config)

        plt.rcParams.update(MATPLOTLIB_RCPARAMS)
        logger.info("Matplotlib rcParams configured for docs.")
        return super().on_config(config)
