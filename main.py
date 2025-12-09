from direct.showbase.ShowBase import ShowBase

from panda3d.core import (
    WindowProperties,
    Vec3,
    BitMask32,
    CollisionNode,
    CollisionSphere,
    CollisionTraverser,
    CollisionHandlerPusher
)

from direct.task import Task
import math

class Viewer(ShowBase):
    def __init__(self):
        super().__init__()

        self.disableMouse()

        # Hide cursor only
        props = WindowProperties()
        props.setCursorHidden(True)
        self.win.requestProperties(props)

        # Mouse center
        self.winX = self.win.getProperties().getXSize()
        self.winY = self.win.getProperties().getYSize()
        self.center_x = int(self.winX / 2)
        self.center_y = int(self.winY / 2)
        self.win.movePointer(0, self.center_x, self.center_y)

        self.floor_pos = 0.15

        # Camera rotation
        self.pitch = 0
        self.yaw = 0
        self.mouse_sensitivity = 0.15

        # Movement + physics
        self.move_speed = 1.5
        self.jump_force = 3
        self.gravity = -13
        self.y_velocity = 0
        self.is_on_ground = True

        self.camLens.setNear(0.1)
        self.camLens.setFov(90)

        # LOAD MODEL
        model = self.loader.loadModel("model/mesh.obj")
        tex = self.loader.loadTexture("model/material_0.png")
        model.setTexture(tex, 1)

        model.reparentTo(self.render)
        
        # Treat all geometry as a collision surface
        for node in model.findAllMatches("**/+GeomNode"):
            node.node().setIntoCollideMask(BitMask32.bit(1))

        # CAMERA COLLISION SPHERE
        cnode = CollisionNode("camSphere")
        cnode.addSolid(CollisionSphere(0, 0, 0, 0.2))  # personal space

        self.camCollider = self.camera.attachNewNode(cnode)

        # Collision traverser + pusher
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()
        self.pusher.addCollider(self.camCollider, self.camera)
        self.cTrav.addCollider(self.camCollider, self.pusher)

        # KEY INPUT
        self.keys = {"w": False, "s": False, "a": False, "d": False, "space": False}
        for key in self.keys:
            self.accept(key, self.set_key, [key, True])
            self.accept(key + "-up", self.set_key, [key, False])

        # Debug "P" prints position
        self.accept("p", self.print_position)

        # Initial camera position
        self.camera.setPos(0.8, -0.6, self.floor_pos)

        # BACKGROUND MUSIC
        self.music = self.loader.loadSfx("audio/bgm2.ogg")
        self.music.setLoop(True)
        self.music.setVolume(0.2) 
        self.music.play()

        # JUMP SFX
        self.jump_sfx = self.loader.loadSfx("audio/jump.ogg")
        self.jump_sfx.setVolume(0.9)

        self.mouse_locked = True
        self.accept("escape", self.toggle_mouse_lock)

        self.taskMgr.add(self.update, "update")

    def set_key(self, key, state):
        self.keys[key] = state

    def print_position(self):
        print("Camera Pos:", self.camera.getPos(), "HPR:", self.camera.getHpr())

    def update(self, task):
        dt = globalClock.getDt()

        # MOUSE LOOK
        if(self.mouse_locked):
            pointer = self.win.getPointer(0)
            dx = pointer.getX() - self.center_x
            dy = pointer.getY() - self.center_y
            self.win.movePointer(0, self.center_x, self.center_y)

            self.yaw -= dx * self.mouse_sensitivity
            self.pitch -= dy * self.mouse_sensitivity
            self.pitch = max(-89, min(89, self.pitch))
            self.camera.setHpr(self.yaw, self.pitch, 0)

        # MOVEMENT
        move_vec = Vec3(0, 0, 0)

        forward = self.camera.getQuat().getForward()
        right = self.camera.getQuat().getRight()
        forward.setZ(0); forward.normalize()
        right.setZ(0); right.normalize()

        if self.keys["w"]: move_vec += forward
        if self.keys["s"]: move_vec -= forward
        if self.keys["a"]: move_vec -= right
        if self.keys["d"]: move_vec += right

        if move_vec.length() > 0:
            move_vec.normalize()
            move_vec *= self.move_speed * dt

        # GRAVITY
        self.y_velocity += self.gravity * dt   # gravity always applies

        # But prevent downward drift if grounded
        if self.camera.getZ() <= self.floor_pos + 1e-6:   # tiny epsilon to detect ground
            if self.y_velocity < 0:
                self.y_velocity = 0            # cancel downward velocity
            self.is_on_ground = True
        else:
            self.is_on_ground = False

        # JUMP
        if self.is_on_ground and self.keys["space"]:
            self.jump_sfx.play()
            self.y_velocity = self.jump_force
            self.is_on_ground = False

        # APPLY VERTICAL MOVEMENT
        new_z = self.camera.getZ() + self.y_velocity * dt

        # Clamp to floor
        if new_z < self.floor_pos:
            new_z = self.floor_pos

        self.camera.setZ(new_z)

        # APPLY MOVEMENT
        old_pos = self.camera.getPos()
        new_pos = old_pos + move_vec
        self.camera.setPos(new_pos)

        # Run collision detection
        self.cTrav.traverse(self.render)

        return Task.cont

    def toggle_mouse_lock(self):
        self.mouse_locked = not self.mouse_locked

        props = WindowProperties()

        if self.mouse_locked:
            print("Mouse LOCKED")
            props.setCursorHidden(True)
            self.win.requestProperties(props)

            # Recenter mouse when relocking
            self.win.movePointer(0, self.center_x, self.center_y)
        else:
            print("Mouse UNLOCKED")
            props.setCursorHidden(False)
            self.win.requestProperties(props)

app = Viewer()
app.run()
