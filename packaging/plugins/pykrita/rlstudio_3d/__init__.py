"""
RL Studio - 3D Models & Reference Plugin
Registers the 3D Reference Docker inside RL Studio / Krita.
"""

import krita
from .docker import RLStudio3DDocker

# Register Docker Widget Factory if running inside Krita
try:
    Application.addDockWidgetFactory(
        krita.DockWidgetFactory(
            "rlstudio_3d_docker",
            krita.DockWidgetFactoryBase.DockRight,
            RLStudio3DDocker
        )
    )
except (NameError, AttributeError):
    pass
