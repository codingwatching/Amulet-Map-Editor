from typing import TYPE_CHECKING, Tuple
import wx

from amulet.api.data_types import PointCoordinatesAny

from amulet_map_editor.api.opengl.mesh.selection import RenderSelection
from amulet_map_editor.api.opengl.camera import Projection

from .raycast_behaviour import RaycastBehaviour
from ..events import EVT_PRE_DRAW, EVT_CAMERA_MOVED

if TYPE_CHECKING:
    from amulet_map_editor.programs.edit.api.canvas import EditCanvas


class PointerBehaviour(RaycastBehaviour):
    """Adds the behaviour of the selection pointer."""

    def __init__(self, canvas: "EditCanvas"):
        super().__init__(canvas)

        # has the pointer moved
        self._pointer_moved = True

        # the distance between the camera and the pointer
        self._pointer_distance = 10

        # the pointer
        self._pointer = RenderSelection(
            self.canvas.context_identifier,
            self.canvas.renderer.opengl_resource_pack,
        )

    def bind_events(self):
        super().bind_events()
        self.canvas.Bind(EVT_PRE_DRAW, self._move_pointer)
        self.canvas.Bind(EVT_CAMERA_MOVED, self._invalidate_pointer)
        self.canvas.Bind(wx.EVT_MOTION, self._invalidate_pointer)

    def _invalidate_pointer(self, evt):
        self._pointer_moved = True
        evt.Skip()

    def _move_pointer(self, evt):
        if self._pointer_moved:
            self._pointer.point1, self._pointer.point2 = self._get_pointer_location()
            self._pointer_moved = False
        evt.Skip()

    def _get_pointer_location(self) -> Tuple[PointCoordinatesAny, PointCoordinatesAny]:
        if self.canvas.camera.projection_mode == Projection.TOP_DOWN:
            location = self.closest_block_2d()[0]
        else:
            location = self.closest_block_3d()[0]
        return location, location + 1

    def draw(self):
        self._pointer.draw(self.canvas.camera.transformation_matrix)
