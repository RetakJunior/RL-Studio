"""
RL Studio - Hardware Accelerated 3D Viewport
Uses QOpenGLWidget, QOpenGLShaderProgram, and QMatrix4x4.
Provides orbit camera, interactive light direction, wireframe/clay/silhouette modes,
and high-resolution canvas snapshot rendering.
"""

import math
import ctypes
from array import array
from PyQt5 import sip
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import (
    QMatrix4x4, QVector3D, QColor, QImage, QPainter,
    QOpenGLBuffer, QOpenGLShader, QOpenGLShaderProgram, QSurfaceFormat, QPalette
)

VERTEX_SHADER_SRC = """#version 120
attribute vec3 a_position;
attribute vec3 a_normal;

uniform mat4 u_mvp;
uniform mat4 u_modelview;
uniform mat3 u_normalmat;

varying vec3 v_normal;
varying vec3 v_viewpos;

void main() {
    v_normal = normalize(u_normalmat * a_normal);
    vec4 view_pos = u_modelview * vec4(a_position, 1.0);
    v_viewpos = view_pos.xyz;
    gl_Position = u_mvp * vec4(a_position, 1.0);
}
"""

FRAGMENT_SHADER_SRC = """#version 120
varying vec3 v_normal;
varying vec3 v_viewpos;

uniform vec3 u_lightdir;
uniform int u_rendermode; // 0: Clay, 1: Wireframe/Edge, 2: Silhouette
uniform vec3 u_basecolor;

void main() {
    if (u_rendermode == 2) {
        // Flat Silhouette for shape study
        gl_FragColor = vec4(0.12, 0.14, 0.18, 1.0);
        return;
    }

    if (u_rendermode == 1) {
        // Wireframe / Edge line
        gl_FragColor = vec4(0.0, 0.68, 0.71, 1.0); // RL Teal
        return;
    }

    // Studio Clay shading
    vec3 N = normalize(v_normal);
    vec3 L = normalize(u_lightdir);
    vec3 V = normalize(-v_viewpos);
    vec3 H = normalize(L + V);

    float diff = max(dot(N, L), 0.0);
    float spec = pow(max(dot(N, H), 0.0), 24.0) * 0.15;
    
    // Hemispheric ambient lighting (Soft sky & ground bounce)
    vec3 ambient = mix(vec3(0.2, 0.22, 0.26), vec3(0.35, 0.38, 0.42), N.y * 0.5 + 0.5);
    vec3 diffuse = u_basecolor * diff;
    vec3 final_color = ambient + diffuse + vec3(spec);

    gl_FragColor = vec4(final_color, 1.0);
}
"""


class _OpenGLFunctions:
    """Resolve the small set of GL calls needed by this widget through Qt.

    PyQt5 intentionally does not expose ``QOpenGLContext.functions()``. Qt's
    ``getProcAddress()`` is available in Krita's bundled PyQt and keeps these
    calls tied to the active context without requiring PyOpenGL.
    """

    _SIGNATURES = {
        "glEnable": (ctypes.c_uint,),
        "glDepthFunc": (ctypes.c_uint,),
        "glBlendFunc": (ctypes.c_uint, ctypes.c_uint),
        "glViewport": (ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int),
        "glClearColor": (ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float),
        "glClear": (ctypes.c_uint,),
        "glLineWidth": (ctypes.c_float,),
        "glDrawArrays": (ctypes.c_uint, ctypes.c_int, ctypes.c_int),
    }

    def __init__(self, context):
        for name, argtypes in self._SIGNATURES.items():
            pointer = context.getProcAddress(name.encode("ascii"))
            if not pointer:
                raise RuntimeError("OpenGL function is unavailable: {}".format(name))

            function_type = ctypes.CFUNCTYPE(None, *argtypes)
            setattr(self, name, function_type(int(pointer)))


class GLViewport3D(QOpenGLWidget):
    camera_updated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mesh = None
        self._mesh_buffer_dirty = False
        self._mesh_vertex_bytes = 0
        self._transparent_background = False

        # Camera parameters
        self.distance = 3.5
        self.yaw = 30.0
        self.pitch = 20.0
        self.pan_x = 0.0
        self.pan_y = 0.0

        # Light parameters (spherical coords)
        self.light_yaw = 45.0
        self.light_pitch = 45.0

        # Render mode: 0: Clay Shaded, 1: Wireframe, 2: Silhouette
        self.render_mode = 0
        self.base_color = QVector3D(0.78, 0.80, 0.82) # Clean clay gray

        # Mouse tracking
        self.last_pos = QPoint()
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

        # GL shader program
        self._gl = None
        self.vertex_buffer = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.program = None
        self.loc_mvp = -1
        self.loc_mv = -1
        self.loc_norm = -1
        self.loc_light = -1
        self.loc_mode = -1
        self.loc_color = -1

    def set_mesh(self, mesh):
        self.mesh = mesh
        self._mesh_buffer_dirty = mesh is not None
        self.update()

    def set_render_mode(self, mode):
        self.render_mode = mode
        self.update()

    def set_light_angle(self, yaw, pitch):
        self.light_yaw = yaw
        self.light_pitch = pitch
        self.update()

    def reset_camera(self):
        self.distance = 3.5
        self.yaw = 30.0
        self.pitch = 20.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.update()

    def initializeGL(self):
        # Setup GL parameters
        self._gl = _OpenGLFunctions(self.context())
        gl = self._gl
        if not self.vertex_buffer.create():
            self.program = None
            return
        self.vertex_buffer.setUsagePattern(QOpenGLBuffer.StaticDraw)

        gl.glEnable(0x0B71) # GL_DEPTH_TEST
        gl.glDepthFunc(0x0203) # GL_LEQUAL
        gl.glEnable(0x0BE2) # GL_BLEND
        gl.glBlendFunc(0x0302, 0x0303) # GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA

        # Compile Shader Program
        self.program = QOpenGLShaderProgram()
        if not self.program.addShaderFromSourceCode(QOpenGLShader.Vertex, VERTEX_SHADER_SRC):
            print("[RL Studio 3D] Vertex shader error: {}".format(self.program.log()))
            self.program = None
            return
        if not self.program.addShaderFromSourceCode(QOpenGLShader.Fragment, FRAGMENT_SHADER_SRC):
            print("[RL Studio 3D] Fragment shader error: {}".format(self.program.log()))
            self.program = None
            return

        # Attribute indexes must match the VBO layout on every OpenGL driver.
        self.program.bindAttributeLocation("a_position", 0)
        self.program.bindAttributeLocation("a_normal", 1)
        if not self.program.link():
            print("[RL Studio 3D] Shader link error: {}".format(self.program.log()))
            self.program = None
            return

        self.loc_mvp = self.program.uniformLocation("u_mvp")
        self.loc_mv = self.program.uniformLocation("u_modelview")
        self.loc_norm = self.program.uniformLocation("u_normalmat")
        self.loc_light = self.program.uniformLocation("u_lightdir")
        self.loc_mode = self.program.uniformLocation("u_rendermode")
        self.loc_color = self.program.uniformLocation("u_basecolor")

    def resizeGL(self, w, h):
        gl = self._gl
        if gl is None:
            return
        gl.glViewport(0, 0, w, h)

    def _get_light_dir(self):
        rad_y = math.radians(self.light_yaw)
        rad_p = math.radians(self.light_pitch)
        x = math.cos(rad_p) * math.sin(rad_y)
        y = math.sin(rad_p)
        z = math.cos(rad_p) * math.cos(rad_y)
        return QVector3D(x, y, z).normalized()

    def _upload_mesh(self):
        """Upload position and normal data once through Qt's supported VBO API."""
        if not self.mesh or not self.mesh.vertices or not self.mesh.normals:
            return False

        data = array("f", self.mesh.vertices)
        self._mesh_vertex_bytes = len(data) * data.itemsize
        data.extend(self.mesh.normals)
        pointer, count = data.buffer_info()

        if not self.vertex_buffer.bind():
            return False
        self.vertex_buffer.allocate(sip.voidptr(pointer), count * data.itemsize)
        self.vertex_buffer.release()
        self._mesh_buffer_dirty = False
        return True

    def paintGL(self):
        gl = self._gl
        if gl is None:
            return
        # Match the host application's workspace instead of drawing a separate dark panel.
        background = self.palette().color(QPalette.Window)
        alpha = 0.0 if self._transparent_background else 1.0
        gl.glClearColor(background.redF(), background.greenF(), background.blueF(), alpha)
        gl.glClear(0x00004000 | 0x00000100) # GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT

        if not self.mesh or not self.program:
            return

        w = max(self.width(), 1)
        h = max(self.height(), 1)
        aspect = w / h

        # Projection Matrix
        proj = QMatrix4x4()
        proj.perspective(45.0, aspect, 0.1, 100.0)

        # View Matrix (Orbit Camera)
        view = QMatrix4x4()
        view.translate(self.pan_x, self.pan_y, -self.distance)
        view.rotate(self.pitch, 1.0, 0.0, 0.0)
        view.rotate(self.yaw, 0.0, 1.0, 0.0)

        model = QMatrix4x4()
        mv = view * model
        mvp = proj * mv
        norm_mat = mv.normalMatrix()

        self.program.bind()
        self.program.setUniformValue(self.loc_mvp, mvp)
        self.program.setUniformValue(self.loc_mv, mv)
        self.program.setUniformValue(self.loc_norm, norm_mat)
        self.program.setUniformValue(self.loc_light, self._get_light_dir())
        self.program.setUniformValue(self.loc_mode, self.render_mode)
        self.program.setUniformValue(self.loc_color, self.base_color)

        if self._mesh_buffer_dirty and not self._upload_mesh():
            self.program.release()
            return
        if not self.vertex_buffer.bind():
            self.program.release()
            return

        self.program.enableAttributeArray(0)
        self.program.enableAttributeArray(1)

        # Position and normal attributes are separate blocks in the VBO.
        self.program.setAttributeBuffer(0, 0x1406, 0, 3, 0)
        self.program.setAttributeBuffer(1, 0x1406, self._mesh_vertex_bytes, 3, 0)

        if self.render_mode == 1:
            # Wireframe drawing
            gl.glLineWidth(1.5)
            # Draw triangle elements as wire lines
            gl.glDrawArrays(0x0004, 0, self.mesh.vertex_count) # GL_TRIANGLES
        else:
            # Solid Triangles
            gl.glDrawArrays(0x0004, 0, self.mesh.vertex_count) # GL_TRIANGLES

        self.program.disableAttributeArray(0)
        self.program.disableAttributeArray(1)
        self.vertex_buffer.release()
        self.program.release()

    def mousePressEvent(self, event):
        self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.last_pos.x()
        dy = event.y() - self.last_pos.y()

        if event.buttons() & Qt.LeftButton:
            # Orbit rotation
            self.yaw += dx * 0.6
            self.pitch += dy * 0.6
            self.pitch = max(-89.0, min(89.0, self.pitch))
            self.update()
            self.camera_updated.emit()
        elif event.buttons() & Qt.RightButton or event.buttons() & Qt.MiddleButton:
            # Pan
            factor = self.distance * 0.002
            self.pan_x += dx * factor
            self.pan_y -= dy * factor
            self.update()
            self.camera_updated.emit()

        self.last_pos = event.pos()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        zoom_speed = 0.003 * self.distance
        self.distance -= delta * zoom_speed
        self.distance = max(0.5, min(30.0, self.distance))
        self.update()
        self.camera_updated.emit()

    def capture_snapshot(self, transparent_bg=True):
        """Renders the current 3D view to a transparent QImage for Krita canvas."""
        previous_background = self._transparent_background
        self._transparent_background = transparent_bg
        try:
            img = self.grabFramebuffer()
        finally:
            self._transparent_background = previous_background
            self.update()
        if transparent_bg:
            # Preserve the alpha channel cleared by paintGL for a clean canvas overlay.
            img = img.convertToFormat(QImage.Format_ARGB32_Premultiplied)
        return img
