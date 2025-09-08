from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, random, time

try:
    from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
    FONT = GLUT_BITMAP_HELVETICA_18
except Exception:
    from OpenGL.GLUT import GLUT_BITMAP_8_BY_13 as FONT


player_pos = [0, 0, 0]
initial_Gun_Angle = 180
gun_angle = initial_Gun_Angle
player_dir = [0, 1]  

camera_mode = "third"
camera_distance = 500
camera_height = 500
camera_angle = 0

cheat_mode = False
auto_camera = False
fp_cam_yaw = 0.0  
bullets = []
enemies = []

life = 5
missed_bullets = 0
score = 0
game_over = False

grid_length = 1250
enemy_speed = 0.03
bullet_speed = 5
last_fire_time = time.time()
player_margin = 30  
cheat_speed = 2
cheat_path = 35 
cheat_coolDown = 0.12
Muzzle_Forward = 48.0  
Muzzle_Height = 40.0   
Torso_Height = 26      
leg_top_radius = 6.0
leg_bottom_radius = 2.5
Cam_Min_Hei = 80   
Cam_Max_Hei = 1200  
fov_first = 60
fov_third = 82  
road_width = 100

def update_player_dir():
    global player_dir
    rad = math.radians(gun_angle)
    player_dir = [math.sin(rad), math.cos(rad)]


def draw_text(x, y, text):
    glColor3f(1, 1, 1)
    glWindowPos2f(x, y)
    for ch in text:
        	glutBitmapCharacter(FONT, ord(ch))


def draw_player():
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(gun_angle, 0, 1, 0)
    if game_over:
        glRotatef(90, 1, 0, 0)
    torso_y = 30 if not game_over else 12
    head_y  = 60 if not game_over else 25  

   
    glPushMatrix()
    glTranslatef(0, torso_y, 0)
    glColor3f(0, 0.3, 0)
    glScalef(30, Torso_Height, 15)
    glutSolidCube(1)
    glPopMatrix()

    
    if camera_mode != 'first':
        glPushMatrix()
        glTranslatef(0, head_y, 0)
        glColor3f(0, 0, 0)
        glutSolidSphere(12, 20, 20)
        glPopMatrix()

     
    glPushMatrix()
    arm_y = 45 if not game_over else torso_y + 10  
    skin = (0.9, 0.75, 0.65)
    for side in (-1, 1):
        glPushMatrix()
        glTranslatef(side * 10, arm_y, 5)
        glColor3f(*skin)
        glutSolidSphere(4, 10, 10)
        quad = gluNewQuadric()
        gluCylinder(quad, 3, 3, 35, 10, 10)
        glPopMatrix()
 
    glPushMatrix()
    glTranslatef(0, arm_y, 7.6)  
    glColor3f(0.5, 0.5, 0.5)
    quad = gluNewQuadric()
    # Tapered gun
    gluCylinder(quad, 4.5, 2, 40, 16, 8)
    glPopMatrix()
    glPopMatrix()

    # Static legs 
    leg_y = 20 if not game_over else torso_y - 5
    glColor3f(0, 0, 0.5)
    for x_off in (-10, 10):
        glPushMatrix()
        glTranslatef(x_off, leg_y, 0)
        glRotatef(90, 1, 0, 0) 
        quad = gluNewQuadric()
        gluCylinder(quad, leg_top_radius, leg_bottom_radius, 25, 12, 6)
        glPopMatrix()

    glPopMatrix()


def draw_grid():
    glColor3f(0.8, 0.8, 0.8)
    glBegin(GL_QUADS)
    glVertex3f(-grid_length, 0, -grid_length)
    glVertex3f(-grid_length, 0, grid_length)
    glVertex3f(-road_width, 0, grid_length)
    glVertex3f(-road_width, 0, -grid_length)

    glVertex3f(grid_length, 0, -grid_length)
    glVertex3f(grid_length, 0, grid_length)
    glVertex3f(road_width, 0, grid_length)
    glVertex3f(road_width, 0, -grid_length)
    glEnd()

def draw_road():
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3f(-road_width, 2, -grid_length)
    glVertex3f(road_width, 2, -grid_length)
    glVertex3f(road_width, 2, grid_length)
    glVertex3f(-road_width, 2, grid_length)
    
    glVertex3f(-grid_length, 2, 350)   # bottom-left
    glVertex3f(-road_width, 2, 350)    # bottom-right
    glVertex3f(-road_width, 2, 550)    # top-right
    glVertex3f(-grid_length, 2, 550)   # top-left


    glVertex3f(-grid_length, 2, -350)   # bottom-left
    glVertex3f(-road_width, 2, -350)    # bottom-right
    glVertex3f(-road_width, 2, -550)    # top-right
    glVertex3f(-grid_length, 2, -550)

    glVertex3f(grid_length, 2, 350)   # bottom-left
    glVertex3f(road_width, 2, 350)    # bottom-right
    glVertex3f(road_width, 2, 550)    # top-right
    glVertex3f(grid_length, 2, 550)

    glVertex3f(grid_length, 2, -350)   # bottom-left
    glVertex3f(road_width, 2, -350)    # bottom-right
    glVertex3f(road_width, 2, -550)    # top-right
    glVertex3f(grid_length, 2, -550)
    glEnd()
    

def draw_wall(x1,z1,x2,z2,h,color):
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex3f(x1,0,z1)
    glVertex3f(x1,h,z1)
    glVertex3f(x2,h,z2)
    glVertex3f(x2,0,z2)
    glEnd()

def draw_boundaries():
    h=100
    draw_wall(-grid_length,-grid_length, -grid_length, grid_length, h,(0.96, 0.64, 0.35))
    draw_wall(-grid_length,grid_length, grid_length,grid_length, h,(0.96, 0.64, 0.35))
    draw_wall(grid_length,grid_length, grid_length,-grid_length, h,(0.96, 0.64, 0.35))
    draw_wall(grid_length,-grid_length,-grid_length,-grid_length,h,(0.96, 0.64, 0.35))


# =================================....DRAW DUSTBIN...=================================
def draw_cylinder_bin(color, top, bottom, hei):
    glPushMatrix()
    glColor3f(color[0], color[1], color[2])  
    glRotatef(-90, 1, 0, 0)  # Rotate so cylinder stands up
    gluCylinder(gluNewQuadric(), top, bottom, hei, 20, 20)
    glPopMatrix()


def draw_cube_bin(color):
    glPushMatrix()
    glColor3f(color[0], color[1], color[2])         
    glutSolidCube(45)          # Cube as the bin body
    glPopMatrix()



def draw_bins():
    # Paper bin (Pink)
    glPushMatrix()
    glTranslatef(-50, 30, 1200)
    draw_cube_bin([1.0, 0.078, 0.576])
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-50, 52, 1200)
    draw_cylinder_bin([1.0, 0.81, 0.91], 22, 15, 20)
    glPopMatrix()


    # Plastic (Green)
    glPushMatrix()
    glTranslatef(50, 30, 1200)
    draw_cube_bin([0.0, 0.39, 0.0])
    glPopMatrix()

    glPushMatrix()
    glTranslatef(50, 52, 1200)
    draw_cylinder_bin([0.56, 0.93, 0.56], 22, 15, 20)
    glPopMatrix()


    # Kitchen (Blue)
    glPushMatrix()
    glTranslatef(-50, 30, -1200)
    draw_cube_bin([0, 0, 0.9])
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-50, 52, -1200)
    draw_cylinder_bin([0.33, 0.75, 0.88], 22, 15, 20)
    glPopMatrix()


    # Metal (Red)
    glPushMatrix()
    glTranslatef(50, 30, -1200)
    draw_cube_bin([0.9, 0.0, 0.0])
    glPopMatrix()

    glPushMatrix()
    glTranslatef(50, 52, -1200)
    draw_cylinder_bin([0.95, 0.65, 0.65], 22, 15, 20)
    glPopMatrix()


#===========================...DRAW HOUSE...=================================
def draw_square():
    glPushMatrix()
    glColor3f(1, 1, 0)        # Yellow
    glTranslatef(-650, 0, 900)
    glScalef(6, 4, 3)       # Flatten cube into a square plate
    glutSolidCube(50)
    glPopMatrix()


# =====================...DRAW LAMP...==================================
def draw_lamp(x, y):
    glPushMatrix()
    glTranslatef(x, 0, y)
    draw_cylinder_bin([0.55, 0.27, 0.07], 5, 5, 120)  #Brown
    glPopMatrix()
    
    glPushMatrix()
    glColor3f(1, 1, 0)   # Yellow
    glTranslatef(x, 120, y)
    gluSphere(gluNewQuadric(), 25, 20, 20)
    glPopMatrix()


def set_lamp():
    draw_lamp(100, 900)
    draw_lamp(-100, 900)    
    draw_lamp(100, -900)
    draw_lamp(-100, -900)
    draw_lamp(100, 0)
    draw_lamp(-100, 0)

    draw_lamp(-620, 550)
    draw_lamp(-620, 350)
    draw_lamp(620, 550)
    draw_lamp(620, 350)
    draw_lamp(-620, -550)
    draw_lamp(-620, -350)
    draw_lamp(620, -550)
    draw_lamp(620, -350)



def check_collisions():
    global score, life, game_over
    for b in bullets[:]:
        for e in enemies:
            if math.hypot(b["pos"][0]-e["pos"][0], b["pos"][2]-e["pos"][2])<50:
                score+=1; bullets.remove(b)
                e["pos"]=[random.randint(-400,400),0,random.randint(-400,400)]
                break
    for e in enemies:
        if math.hypot(player_pos[0]-e["pos"][0], player_pos[2]-e["pos"][2])<50:
            life-=1
            print(f"Remaining life: {life} (collision)")
            e["pos"]=[random.randint(-400,400),0,random.randint(-400,400)]
            if life<=0:
                game_over=True
                print("Game Over (life depleted)")


def keyboardListener(key,x,y):
    global gun_angle, cheat_mode, auto_camera, player_pos, fp_cam_yaw
    key=key.decode("utf-8").lower()
    if game_over:
        if key=="r": reset_game(); return
        return  
    if key=="w": player_pos[0]+=player_dir[0]*10; player_pos[2]+=player_dir[1]*10
    elif key=="s": player_pos[0]-=player_dir[0]*10; player_pos[2]-=player_dir[1]*10
    elif key=="a": gun_angle+=5; update_player_dir()
    elif key=="d": gun_angle-=5; update_player_dir()
    elif key=="c":
        cheat_mode = not cheat_mode
        print('Cheat Mode:', 'ON' if cheat_mode else 'OFF')
        if cheat_mode and camera_mode == "first":
            auto_camera = False 
            fp_cam_yaw = gun_angle
        else:
            auto_camera = False
    elif key=="v" and cheat_mode and camera_mode=="first":
        auto_camera = not auto_camera
        if auto_camera:
            fp_cam_yaw = gun_angle  
        print('Auto Camera Follow:', 'ON' if auto_camera else 'OFF')
       
   
    limit = grid_length - player_margin
    player_pos[0] = max(-limit, min(limit, player_pos[0]))
    player_pos[2] = max(-limit, min(limit, player_pos[2]))

def specialKeyListener(key,x,y):
    global camera_height,camera_angle
    if key==GLUT_KEY_UP: camera_height+=10
    elif key==GLUT_KEY_DOWN: camera_height-=10
    elif key==GLUT_KEY_LEFT: camera_angle+=5
    elif key==GLUT_KEY_RIGHT: camera_angle-=5
   
    if camera_height < Cam_Min_Hei: camera_height = Cam_Min_Hei
    if camera_height > Cam_Max_Hei: camera_height = Cam_Max_Hei

def mouseListener(button,state,x,y):
    global camera_mode, fp_cam_yaw, auto_camera 
    if button==GLUT_RIGHT_BUTTON and state==GLUT_DOWN:
        if camera_mode=="third":
            camera_mode="first"
            if cheat_mode:
                auto_camera = False
                fp_cam_yaw = gun_angle
        else:
            camera_mode="third"
            globals()['camera_angle'] = gun_angle
            if globals()['camera_distance'] > 400: globals()['camera_distance'] = 320
            if globals()['camera_height'] > 300: globals()['camera_height'] = 140


def setupCamera():
    glMatrixMode(GL_PROJECTION); glLoadIdentity()
    aspect=glutGet(GLUT_WINDOW_WIDTH)/max(1,glutGet(GLUT_WINDOW_HEIGHT))
    fov = fov_third if camera_mode=="third" else fov_first
    gluPerspective(fov,aspect,0.1,2500)
    glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    if camera_mode=="third":
        cx = player_pos[0] + math.sin(math.radians(camera_angle)) * camera_distance
        cz = player_pos[2] + math.cos(math.radians(camera_angle)) * camera_distance
        gluLookAt(cx, camera_height, cz, player_pos[0], player_pos[1]+50, player_pos[2], 0, 1, 0)
    else:
        global fp_cam_yaw
        if cheat_mode and not auto_camera:
            yaw = fp_cam_yaw
        else:
            yaw = gun_angle
            if cheat_mode and auto_camera:
                fp_cam_yaw = yaw  
        dir_x = math.sin(math.radians(yaw))
        dir_z = math.cos(math.radians(yaw))
        head_height = 60
        eye_x = player_pos[0] + dir_x*5
        eye_y = player_pos[1] + head_height
        eye_z = player_pos[2] + dir_z*5
        look_x = eye_x + dir_x*120
        look_y = eye_y
        look_z = eye_z + dir_z*120
        gluLookAt(eye_x, eye_y, eye_z, look_x, look_y, look_z, 0, 1, 0)

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    setupCamera()
    draw_grid()
    draw_road()
    draw_bins()
    draw_square()
    set_lamp()
    draw_boundaries() 
    draw_player()
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0,glutGet(GLUT_WINDOW_WIDTH),0,glutGet(GLUT_WINDOW_HEIGHT))
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    if not game_over: draw_text(10,glutGet(GLUT_WINDOW_HEIGHT)-20,f"Life:{life} Score:{score} Missed:{missed_bullets}")
    else: draw_text(10,glutGet(GLUT_WINDOW_HEIGHT)-20,f"GAME OVER. Score {score}. Press R.")
    glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW); glPopMatrix()
    glEnable(GL_DEPTH_TEST); glutSwapBuffers()

def idle():
    if not game_over:
        check_collisions()
    glutPostRedisplay()

def reset_game():
    global life,score,missed_bullets,game_over,bullets,gun_angle
    life=5;score=0;missed_bullets=0;game_over=False;bullets.clear()
    gun_angle=initial_Gun_Angle;update_player_dir()
    print('New game started')


glutInit()
glutInitDisplayMode(GLUT_DOUBLE|GLUT_RGB|GLUT_DEPTH)
glutInitWindowSize(1000,800)
glutCreateWindow(b"Bullet Frenzy - Alternative Implementation")
glClearColor(0,0,0,1)
glEnable(GL_DEPTH_TEST)
update_player_dir()
glutDisplayFunc(showScreen)
glutKeyboardFunc(keyboardListener)
glutSpecialFunc(specialKeyListener)
glutMouseFunc(mouseListener)
glutIdleFunc(idle)
glutMainLoop()
