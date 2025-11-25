import os
import sys
import random
import math

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    Vec3, Point3, LColor, Plane,
    BitMask32, CardMaker, NodePath, 
    Texture, PNMImage, TransparencyAttrib,
    DirectionalLight, AmbientLight,
    Material, AntialiasAttrib, TextNode,
    Filename, loadPrcFileData, LineSegs
)
from panda3d.bullet import (
    BulletWorld, BulletPlaneShape, 
    BulletRigidBodyNode, BulletBoxShape, 
    BulletDebugNode
)
from direct.gui.OnscreenText import OnscreenText

# --- CONFIGURATION ---
loadPrcFileData('', 'load-file-type p3gltf')

# --- 1. PHYSICS BOX DIMENSIONS (The Invisible Container) ---
# Adjust these until the "Green Wireframe" box matches your table's play area
TABLE_WIDTH_PHYSICS = 18.0   
TABLE_DEPTH_PHYSICS = 12.0   
WALL_HEIGHT = 15.0

# --- 2. VISUAL TABLE ALIGNMENT (The 3D Model) ---
# Use F1 to see the mismatch, then change these numbers.
TABLE_MODEL_SCALE = 12     # Make the table bigger/smaller
TABLE_VISUAL_Z = -6   # Move table UP (+) or DOWN (-) to match floor

# --- DICE CONFIG ---
DIE_SIZE = 0.8          
FRICTION_FELT = 0.9     
BOUNCINESS = 0.5        
DAMPING_ANGULAR = 0.5   

# --- ASSETS ---
FOLDER_NAME = "dice"
DICE_FILE_NAME = "test3.glb" 
TABLE_FILE_NAME = "poker-table.glb" 
DICE_MODEL_SCALE = 10.0 

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- SCORING CALIBRATION ---
DIE_AXIS_MAPPING = { "UP": 4, "DOWN": 3, "RIGHT": 2, "LEFT": 1, "FWD": 5, "BACK": 6 }

# --- LIBRARY CHECK ---
try:
    import simplepbr
    import gltf
except ImportError:
    print("\nCRITICAL ERROR: Libraries missing.\nRun: pip install panda3d-gltf panda3d-simplepbr\n")
    sys.exit()

# --- PROCEDURAL TEXTURE ---
def create_die_face_texture(number, size=512): 
    image = PNMImage(size, size)
    image.fill(0.96, 0.94, 0.90) 
    for x in range(size):
        for y in range(size):
            d = min(x, y, size-x, size-y)
            if d < 40:
                f = d / 40.0
                v = 0.7 + (0.3 * f)
                bg = image.getXel(x, y)
                image.setXel(x, y, bg[0]*v, bg[1]*v, bg[2]*v)
    pips = []
    c, l, r = 0.5, 0.22, 0.78 
    if number==1: pips=[(c,c)]
    elif number==2: pips=[(l,r),(r,l)]
    elif number==3: pips=[(l,r),(c,c),(r,l)]
    elif number==4: pips=[(l,l),(l,r),(r,l),(r,r)]
    elif number==5: pips=[(l,l),(l,r),(r,l),(r,r),(c,c)]
    elif number==6: pips=[(l,l),(l,r),(r,l),(r,r),(l,c),(r,c)]
    rad = size * 0.10 
    for px, py in pips:
        cx, cy = int(px*size), int(py*size)
        min_x, max_x = max(0, int(cx-rad)), min(size, int(cx+rad))
        min_y, max_y = max(0, int(cy-rad)), min(size, int(cy+rad))
        for x in range(min_x, max_x):
            for y in range(min_y, max_y):
                dist = math.sqrt((x-cx)**2 + (y-cy)**2)
                if dist < rad:
                    a = 1.0
                    if dist > rad - 2.0: a = (rad - dist) / 2.0
                    bg = image.getXel(x, y)
                    inv = 1.0 - a
                    image.setXel(x, y, bg[0]*inv, bg[1]*inv, bg[2]*inv)
    t = Texture()
    t.load(image)
    t.setMinfilter(Texture.FTLinearMipmapLinear)
    t.setMagfilter(Texture.FTLinear)
    return t

class DiceSimulator(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        simplepbr.init(use_normal_maps=True, enable_shadows=True, use_occlusion_maps=True)
        if hasattr(gltf, 'patch_loader'): gltf.patch_loader(self.loader)

        # Physics
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -25.0)) 
        
        # Visuals
        self.setBackgroundColor(0.05, 0.05, 0.1, 1) 
        self.disableMouse()
        self.camera.setPos(0, -28, 24)
        self.camera.lookAt(0, 0, 0)
        
        # Lighting
        dlight = DirectionalLight('dlight')
        dlight.setColor((0.9, 0.9, 0.85, 1))
        dlight.setShadowCaster(True, 4096, 4096)
        lens = dlight.getLens(); lens.setFilmSize(30, 30)
        self.render.setLight(self.render.attachNewNode(dlight))
        self.render.attachNewNode(dlight).setHpr(45, -60, 0)
        
        alight = AmbientLight('alight')
        alight.setColor((0.4, 0.4, 0.4, 1))
        self.render.setLight(self.render.attachNewNode(alight))

        # Scene
        self.face_textures = {i: create_die_face_texture(i) for i in range(1, 7)}
        self.create_poker_table()
        self.dice = []
        
        # Interaction
        self.holding_dice = False
        self.drag_plane = Plane(Vec3(0, 0, 1), Point3(0, 0, 6))
        self.last_mouse_pos_3d = Point3(0, 0, 0)
        self.mouse_velocity = Vec3(0, 0, 0)

        # Controls
        self.accept('space', self.reset_position)
        self.accept('mouse1', self.grab_dice)
        self.accept('mouse1-up', self.throw_dice)
        self.accept('f1', self.toggle_debug)
        
        # UI
        self.info_txt = OnscreenText(text="CLICK & DRAG to Throw | SPACE to Center | F1 to Calibrate", 
                                     pos=(-0.9, 0.9), scale=0.06, fg=(1,1,1,1), align=TextNode.ALeft)
        self.score_txt = OnscreenText(text="TOTAL: 0", pos=(0, 0.8), scale=0.12, 
                                      fg=(1, 0.8, 0.2, 1), align=TextNode.ACenter, shadow=(0,0,0,1))

        self.spawn_dice()
        self.taskMgr.add(self.update, 'update')

    def spawn_dice(self):
        for i in range(2):
            pos = Point3(-1.5 + (i * 3.0), 0, 2.0)
            self.create_die_body(pos)

    def reset_position(self):
        self.holding_dice = False
        for i, body in enumerate(self.dice):
            body.setLinearVelocity(Vec3(0,0,0))
            body.setAngularVelocity(Vec3(0,0,0))
            np = NodePath(body)
            np.setPos(-1.5 + (i * 3.0), 0, 5.0)
            np.setHpr(random.uniform(0,360), random.uniform(0,360), random.uniform(0,360))

    # --- INPUT LOGIC ---
    def get_mouse_in_world(self):
        if not self.mouseWatcherNode.hasMouse(): return None
        mpos = self.mouseWatcherNode.getMouse()
        p_from = Point3(); p_to = Point3()
        self.camLens.extrude(mpos, p_from, p_to)
        p_from = self.render.getRelativePoint(self.cam, p_from)
        p_to = self.render.getRelativePoint(self.cam, p_to)
        intersection = Point3()
        if self.drag_plane.intersectsLine(intersection, p_from, p_to):
            return intersection
        return None

    def grab_dice(self):
        self.holding_dice = True
        self.score_txt.setText("Aiming...")
        mouse_pos = self.get_mouse_in_world()
        if mouse_pos: self.last_mouse_pos_3d = mouse_pos

        for body in self.dice:
            body.setKinematic(True)
            body.setCollisionResponse(False)

    def throw_dice(self):
        if not self.holding_dice: return
        self.holding_dice = False
        THROW_POWER = 12.0 
        
        for i, body in enumerate(self.dice):
            body.setKinematic(False)
            body.setCollisionResponse(True)
            body.setActive(True)
            force = self.mouse_velocity * THROW_POWER
            spin = Vec3(random.uniform(-20,20), random.uniform(-20,20), random.uniform(-20,20))
            body.applyImpulse(force, Point3(0,0,0))
            body.applyTorqueImpulse(spin)

    def update(self, task):
        dt = globalClock.getDt()
        
        # --- DRAG LOGIC ---
        if self.holding_dice:
            target_pos = self.get_mouse_in_world()
            
            if target_pos:
                # Use PHYSICS DIMENSIONS for clamping
                bounds_x = (TABLE_WIDTH_PHYSICS / 2.0) - DIE_SIZE
                bounds_y = (TABLE_DEPTH_PHYSICS / 2.0) - DIE_SIZE
                target_pos.x = max(-bounds_x, min(bounds_x, target_pos.x))
                target_pos.y = max(-bounds_y, min(bounds_y, target_pos.y))
                
                if dt > 0:
                    self.mouse_velocity = (target_pos - self.last_mouse_pos_3d) / dt
                self.last_mouse_pos_3d = target_pos
                
                for i, body in enumerate(self.dice):
                    offset = Vec3(-0.8 + (i*1.6), 0, 0)
                    np = NodePath(body)
                    new_pos = target_pos + offset
                    np.setPos(new_pos)
                    np.setHpr(np.getHpr() + Vec3(100*dt, 50*dt, 0))

        self.world.doPhysics(dt, 10, 1.0/180.0)
        
        # Scoring
        if not self.holding_dice:
            speed = sum(b.getLinearVelocity().length() + b.getAngularVelocity().length() for b in self.dice)
            if speed < 0.1:
                total = sum(self.get_die_number(b) for b in self.dice)
                self.score_txt.setText(f"TOTAL: {total}")
            else:
                self.score_txt.setText("Rolling...")

        return task.cont

    # --- CREATE DICE ---
    def create_die_body(self, pos):
        shape = BulletBoxShape(Vec3(DIE_SIZE, DIE_SIZE, DIE_SIZE))
        body = BulletRigidBodyNode('Die')
        body.setMass(1.0)
        body.addShape(shape)
        body.setFriction(FRICTION_FELT)
        body.setRestitution(BOUNCINESS)
        body.setAngularDamping(DAMPING_ANGULAR)
        body.setCcdMotionThreshold(1e-7); body.setCcdSweptSphereRadius(0.2)
        np = self.render.attachNewNode(body)
        np.setPos(pos)
        self.world.attachRigidBody(body)
        self.build_visual_die(np)
        self.dice.append(body)

    def build_visual_die(self, parent):
        path = os.path.join(SCRIPT_DIR, FOLDER_NAME, DICE_FILE_NAME)
        p_path = Filename.fromOsSpecific(path)
        if os.path.exists(path):
            try:
                m = self.loader.loadModel(p_path)
                m.reparentTo(parent)
                m.setScale(DICE_MODEL_SCALE) 
                m.setTwoSided(True)
                return
            except: 
                print("Dice model load failed, using fallback.")
            
        cm = CardMaker('face'); cm.setFrame(-DIE_SIZE, DIE_SIZE, -DIE_SIZE, DIE_SIZE) 
        m = Material(); m.setSpecular(LColor(1,1,1,1)); m.setShininess(60.0); m.setAmbient(LColor(0.5,0.5,0.5,1))
        parent.setMaterial(m)
        faces = [
            (1, Vec3(0,0,DIE_SIZE), Vec3(0,-90,0)), (6, Vec3(0,0,-DIE_SIZE), Vec3(0,90,0)),
            (2, Vec3(0,-DIE_SIZE,0), Vec3(0,0,0)), (5, Vec3(0,DIE_SIZE,0), Vec3(180,0,180)),
            (3, Vec3(-DIE_SIZE,0,0), Vec3(90,0,0)), (4, Vec3(DIE_SIZE,0,0), Vec3(-90,0,0))
        ]
        for n, p, h in faces:
            f = parent.attachNewNode(cm.generate()); f.setPos(p); f.setHpr(h); f.setTexture(self.face_textures[n]); f.setTwoSided(True)

    def get_die_number(self, body):
        q = body.getTransform().getQuat()
        w = Vec3(0, 0, 1)
        alignments = [
            (q.getUp().dot(w),      DIE_AXIS_MAPPING["UP"]),    
            (-q.getUp().dot(w),     DIE_AXIS_MAPPING["DOWN"]),  
            (q.getRight().dot(w),   DIE_AXIS_MAPPING["RIGHT"]), 
            (-q.getRight().dot(w),  DIE_AXIS_MAPPING["LEFT"]),  
            (q.getForward().dot(w), DIE_AXIS_MAPPING["FWD"]),   
            (-q.getForward().dot(w),DIE_AXIS_MAPPING["BACK"])   
        ]
        return max(alignments, key=lambda x: x[0])[1]

    # --- CREATE TABLE (WITH ALIGNMENT CONTROLS) ---
    def create_poker_table(self):
        # 1. Physics Floor (At Z=0)
        shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        node = BulletRigidBodyNode('Ground'); node.addShape(shape); node.setFriction(FRICTION_FELT)
        self.world.attachRigidBody(node)
        
        # 2. Invisible Physics Walls (Calculated from TABLE_WIDTH_PHYSICS)
        for pos, sz in [
            (Point3(TABLE_WIDTH_PHYSICS/2+0.5,0,7),Vec3(1,TABLE_DEPTH_PHYSICS+5,15)), 
            (Point3(-TABLE_WIDTH_PHYSICS/2-0.5,0,7),Vec3(1,TABLE_DEPTH_PHYSICS+5,15)),
            (Point3(0,TABLE_DEPTH_PHYSICS/2+0.5,7),Vec3(TABLE_WIDTH_PHYSICS+5,1,15)), 
            (Point3(0,-TABLE_DEPTH_PHYSICS/2-0.5,7),Vec3(TABLE_WIDTH_PHYSICS+5,1,15)),
            (Point3(0,0,WALL_HEIGHT),Vec3(TABLE_WIDTH_PHYSICS+5,TABLE_DEPTH_PHYSICS+5,1))
        ]:
            w = BulletRigidBodyNode('Wall'); w.addShape(BulletBoxShape(sz/2)); w.setRestitution(0.5)
            self.world.attachRigidBody(w); self.render.attachNewNode(w).setPos(pos)

        # 3. Visual Table Model
        path = os.path.join(SCRIPT_DIR, FOLDER_NAME, TABLE_FILE_NAME)
        if os.path.exists(path):
            try:
                table_model = self.loader.loadModel(Filename.fromOsSpecific(path))
                table_model.reparentTo(self.render)
                table_model.setScale(TABLE_MODEL_SCALE)
                
                # --- KEY FIX: OFFSET ---
                # Move the table up or down so the felt matches the Z=0 physics floor
                table_model.setPos(0, 0, TABLE_VISUAL_Z) 
                print(f"Loaded Table: {path}")
                return
            except Exception as e:
                print(f"Error loading table: {e}")
        
        # Fallback
        print("Fallback to Procedural Table")
        cm = CardMaker('felt'); cm.setFrame(-TABLE_WIDTH_PHYSICS/2, TABLE_WIDTH_PHYSICS/2, -TABLE_DEPTH_PHYSICS/2, TABLE_DEPTH_PHYSICS/2) 
        flr = self.render.attachNewNode(cm.generate()); flr.setP(-90); flr.setColor(0.1, 0.35, 0.15, 1) 

    def toggle_debug(self):
        if self.world.getDebugNode():
            self.world.clearDebugNode(); self.debugNP.removeNode()
        else:
            dn = BulletDebugNode('Debug'); dn.showWireframe(True); dn.showConstraints(True)
            self.debugNP = self.render.attachNewNode(dn); self.debugNP.show(); self.world.setDebugNode(dn)

if __name__ == "__main__":
    app = DiceSimulator()
    app.run()