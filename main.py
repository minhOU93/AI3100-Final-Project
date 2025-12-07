from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
from direct.task import Task

class Viewer(ShowBase):
    def __init__(self):
        super().__init__()

        self.disableMouse()

        self.accept("p", self.print_position)

        # --- Lock mouse to window + hide ---
        props = WindowProperties()
        props.setMouseMode(WindowProperties.M_relative)  # true FPS mode
        props.setCursorHidden(True)
        self.win.requestProperties(props)

        # Center pointer (for older Panda versions needing fallback)
        self.center_x = int(self.win.getXSize() / 2)
        self.center_y = int(self.win.getYSize() / 2)
        self.win.movePointer(0, self.center_x, self.center_y)

        self.last_mouse_x = self.center_x
        self.last_mouse_y = self.center_y

        # Camera setup
        self.camera.setPos(0.831, -0.627, 0.3)
        self.pitch = 0
        self.yaw = 0
        self.mouse_sensitivity = 0.15
        self.move_speed = 10

        # Load model
        model = self.loader.loadModel("model/mesh.obj")
        model.reparentTo(self.render)
        model.setScale(1)

        # Key inputs
        self.keys = {"w": False, "s": False, "a": False, "d": False}
        for key in self.keys:
            self.accept(key, self.set_key, [key, True])
            self.accept(key+"-up", self.set_key, [key, False])

        self.taskMgr.add(self.update, "update")

    def set_key(self, key, state):
        self.keys[key] = state

    def update(self, task):
        dt = globalClock.getDt()

        # --- RAW mouse look ---
        pointer = self.win.getPointer(0)
        dx = pointer.getX() - self.last_mouse_x
        dy = pointer.getY() - self.last_mouse_y

        self.last_mouse_x = pointer.getX()
        self.last_mouse_y = pointer.getY()

        self.yaw -= dx * self.mouse_sensitivity
        self.pitch -= dy * self.mouse_sensitivity
        self.pitch = max(-89, min(89, self.pitch))

        self.camera.setH(self.yaw)
        self.camera.setP(self.pitch)

        # --- Movement ---
        forward = self.camera.getQuat().getForward()
        right = self.camera.getQuat().getRight()
        forward.setZ(0); forward.normalize()
        right.setZ(0); right.normalize()

        if self.keys["w"]:
            self.camera.setPos(self.camera.getPos() + forward * self.move_speed * dt)
        if self.keys["s"]:
            self.camera.setPos(self.camera.getPos() - forward * self.move_speed * dt)
        if self.keys["a"]:
            self.camera.setPos(self.camera.getPos() - right * self.move_speed * dt)
        if self.keys["d"]:
            self.camera.setPos(self.camera.getPos() + right * self.move_speed * dt)

        return Task.cont

    def print_position(self):
        pos = self.camera.getPos()
        hpr = self.camera.getHpr()
        print(f"Camera Position: {pos}, Rotation (HPR): {hpr}")

app = Viewer()
app.run()
