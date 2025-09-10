from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, random, time

# Font setup
try:
    from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
    FONT = GLUT_BITMAP_HELVETICA_18
except Exception:
    from OpenGL.GLUT import GLUT_BITMAP_8_BY_13 as FONT

# Player variables
player_pos = [0, 0, 0]
initial_Player_Angle = 180
player_angle = initial_Player_Angle
player_dir = [0, 1]  

# Camera settings
camera_mode = "third"
camera_distance = 200
camera_height = 150
camera_angle = 0

auto_camera = False
fp_cam_yaw = 0.0  

# Game state
score = 0
game_over = False
game_start_time = None
current_level = 1
max_level_reached = 1
game_won = False
game_lost = False

def get_level_requirements(level):
    base_time = 10 * 60
    time_limit = max(2 * 60, base_time - (level - 1) * 2 * 60)
    trash_count = 20 + (level - 1) * 5
    win_percentage = 0.5 + (level - 1) * 0.1
    return time_limit, trash_count, win_percentage

# World settings
grid_length = 1250
player_margin = 30  
Torso_Height = 30      
leg_top_radius = 5.5
leg_bottom_radius = 3.5
Cam_Min_Hei = 80   
Cam_Max_Hei = 1200  
fov_first = 60
fov_third = 82  
road_width = 200

# Movement settings
movement_keys = {"w": False, "s": False, "a": False, "d": False}
movement_speed = 3
rotation_speed = 1.5

def update_player_dir():
    global player_dir
    rad = math.radians(player_angle)
    player_dir = [math.sin(rad), math.cos(rad)]


def draw_text(x, y, text):
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))


def draw_minimap():
    # Draw minimap background
    map_size = 150
    map_x = glutGet(GLUT_WINDOW_WIDTH) - map_size - 10
    map_y = glutGet(GLUT_WINDOW_HEIGHT) - map_size - 10
    
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_QUADS)
    glVertex2f(map_x, map_y)
    glVertex2f(map_x + map_size, map_y)
    glVertex2f(map_x + map_size, map_y + map_size)
    glVertex2f(map_x, map_y + map_size)
    glEnd()
    
    # Draw border
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(2)
    glBegin(GL_LINE_LOOP)
    glVertex2f(map_x, map_y)
    glVertex2f(map_x + map_size, map_y)
    glVertex2f(map_x + map_size, map_y + map_size)
    glVertex2f(map_x, map_y + map_size)
    glEnd()
    
    scale = map_size / (2 * grid_length)
    
    def world_to_minimap(world_x, world_z):
        map_pixel_x = map_x + (-world_x + grid_length) * scale
        map_pixel_y = map_y + (-world_z + grid_length) * scale
        return map_pixel_x, map_pixel_y
    
    # Draw bins
    glColor3f(0.0, 1.0, 0.0)
    glPointSize(6)
    glBegin(GL_POINTS)
    for bin_item in bins:
        bx, by, bz = bin_item["pos"]
        px, py = world_to_minimap(bx, bz)
        glVertex2f(px, py)
    glEnd()
    
    # Draw trash
    glColor3f(1.0, 0.0, 0.0)
    glPointSize(4)
    glBegin(GL_POINTS)
    for trash in trash_items:
        tx, ty, tz = trash["pos"]
        px, py = world_to_minimap(tx, tz)
        glVertex2f(px, py)
    glEnd()
    
    # Draw player as triangle
    px, py = world_to_minimap(player_pos[0], player_pos[2])
    
    triangle_size = 4
    angle_rad = math.radians(player_angle + 90)
    
    front_x = px + math.cos(angle_rad) * triangle_size
    front_y = py + math.sin(angle_rad) * triangle_size
    
    left_x = px + math.cos(angle_rad + 2.4) * triangle_size * 0.7
    left_y = py + math.sin(angle_rad + 2.4) * triangle_size * 0.7
    
    right_x = px + math.cos(angle_rad - 2.4) * triangle_size * 0.7
    right_y = py + math.sin(angle_rad - 2.4) * triangle_size * 0.7
    
    glColor3f(1.0, 1.0, 0.0)
    glBegin(GL_TRIANGLES)
    glVertex2f(front_x, front_y)
    glVertex2f(left_x, left_y)
    glVertex2f(right_x, right_y)
    glEnd()
    
    glLineWidth(1)


def draw_player():
    # Draw player body
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_angle, 0, 1, 0)
    torso_y = 35 
    head_y  = 65  

    glPushMatrix()
    glTranslatef(0, torso_y, 0)
    glColor3f(0, 0, 0.3)
    glScalef(30, Torso_Height, 15)
    glutSolidCube(1)
    glPopMatrix()

    # Draw neck
    glPushMatrix()
    glTranslatef(0, torso_y + 20, 0)
    glColor3f(0.9, 0.75, 0.65)
    glScalef(10, 8, 10)
    glutSolidCube(1)
    glPopMatrix()

    # Draw head (only in third person)
    if camera_mode != 'first':
        glPushMatrix()
        glTranslatef(0, head_y, 0)
        glColor3f(0.957, 0.743, 0.576)
        glutSolidSphere(12, 20, 20)
        glPopMatrix()
    
    # HAT
    glPushMatrix()
    glColor3f(0.545, 0.271, 0.075)  
    glTranslatef(0, head_y + 10, 0)
    glRotatef(-90, 1, 0, 0)  
    gluCylinder(gluNewQuadric(), 20, 0, 20, 20, 20)
    glPopMatrix()
     
    # Draw arms
    glPushMatrix()
    arm_y = 50
    skin = (0.9, 0.75, 0.65)
    for side in (-1, 1):
        glPushMatrix()
        glTranslatef(side * 10, arm_y, 5)
        glColor3f(*skin)
        glutSolidSphere(4, 10, 10)
        quad = gluNewQuadric()
        gluCylinder(quad, 3, 3, 25, 10, 10)
        glPopMatrix()
    glPopMatrix()

    # Held trash
    if latest_picked_trash_color is not None:
        glPushMatrix()
        glTranslatef(0, arm_y, 15)
        glColor3f(*latest_picked_trash_color)
        glutSolidCube(8)
        glPopMatrix()

    # Draw legs
    leg_y = 20 
    glColor3f(0, 0, 0)
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
    glVertex3f(-(road_width / 2), 0, grid_length)
    glVertex3f(-(road_width / 2), 0, -grid_length)

    glVertex3f(grid_length, 0, -grid_length)
    glVertex3f(grid_length, 0, grid_length)
    glVertex3f((road_width / 2), 0, grid_length)
    glVertex3f((road_width / 2), 0, -grid_length)
    glEnd()

def draw_road():
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3f(-(road_width / 2), 2, -grid_length)
    glVertex3f((road_width / 2), 2, -grid_length)
    glVertex3f((road_width / 2), 2, grid_length)
    glVertex3f(-(road_width / 2), 2, grid_length)
    
    glVertex3f(-grid_length, 2, 350)
    glVertex3f(-(road_width / 2), 2, 350)
    glVertex3f(-(road_width / 2), 2, 550)
    glVertex3f(-grid_length, 2, 550)

    glVertex3f(-grid_length, 2, -350)
    glVertex3f(-(road_width / 2), 2, -350)
    glVertex3f(-(road_width / 2), 2, -550)
    glVertex3f(-grid_length, 2, -550)

    glVertex3f(grid_length, 2, 350)
    glVertex3f((road_width / 2), 2, 350)
    glVertex3f((road_width / 2), 2, 550)
    glVertex3f(grid_length, 2, 550)

    glVertex3f(grid_length, 2, -350)
    glVertex3f((road_width / 2), 2, -350)
    glVertex3f((road_width / 2), 2, -550)
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

# Maze generation
def generate_maze():
    global maze_walls
    maze_walls = []
    h = 100
    color = (0.6, 0.4, 0.3)
    min_cell_size = 100 

    half_grid = grid_length
    road = road_width
    offset = 100

    open_width = (2 * half_grid - road) / 2
    open_height = (2 * half_grid - 2 * road) / 3

    x_centers = [-open_width / 2, open_width / 2 + road]
    z_centers = [half_grid - open_height / 2,
                 half_grid - open_height - road - open_height / 2,
                 -half_grid + open_height / 2]

    for zc in z_centers:
        for xc in x_centers:
            maze_cols = max(1, int(open_width // min_cell_size))
            maze_rows = max(1, int(open_height // min_cell_size))
            maze_cell_size_x = open_width / maze_cols
            maze_cell_size_z = open_height / maze_rows

            start_x = xc - open_width / 2 - offset
            start_z = zc - open_height / 2

            grid = [[[False, True, True, True, True] for _ in range(maze_cols)] for _ in range(maze_rows)]

            stack = [(maze_rows // 2, maze_cols // 2)]
            grid[maze_rows // 2][maze_cols // 2][0] = True
            while stack:
                r, c = stack[-1]
                dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
                random.shuffle(dirs)
                moved = False
                for dr, dc in dirs:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < maze_rows and 0 <= nc < maze_cols and not grid[nr][nc][0]:
                        if dr == 1:
                            grid[r][c][3] = False
                            grid[nr][nc][1] = False
                        elif dr == -1:
                            grid[r][c][1] = False
                            grid[nr][nc][3] = False
                        elif dc == 1:
                            grid[r][c][2] = False
                            grid[nr][nc][4] = False
                        elif dc == -1:
                            grid[r][c][4] = False
                            grid[nr][nc][2] = False
                        grid[nr][nc][0] = True
                        stack.append((nr, nc))
                        moved = True
                        break
                if not moved:
                    stack.pop()

            # Convert to walls
            for r in range(maze_rows):
                for c in range(maze_cols):
                    x1 = start_x + c * maze_cell_size_x
                    z1 = start_z + r * maze_cell_size_z
                    x2 = x1 + maze_cell_size_x
                    z2 = z1 + maze_cell_size_z

                    if r > 0 and grid[r][c][1]:
                        maze_walls.append([x1, z1, x2, z1, h, color])
                    if c < maze_cols - 1 and grid[r][c][2]:
                        maze_walls.append([x2, z1, x2, z2, h, color])
                    if r < maze_rows - 1 and grid[r][c][3]:
                        maze_walls.append([x1, z2, x2, z2, h, color])
                    if c > 0 and grid[r][c][4]:
                        maze_walls.append([x1, z1, x1, z2, h, color])


def draw_maze():
    for wall in maze_walls:
        x1, z1, x2, z2, h, color = wall
        draw_wall(x1, z1, x2, z2, h, color)


def draw_home_boundary():
    h = 100
    x1, z1, x2, z2 = grid_length, 550, road_width/2, 350

    # Left roads
    draw_wall(-x1, z1, -x2, z1, h, (0.96, 0.64, 0.35)) 
    draw_wall(-x1, z2, -x2, z2, h, (0.96, 0.64, 0.35))
    draw_wall(-x1, -z1, -x2, -z1, h, (0.96, 0.64, 0.35)) 
    draw_wall(-x1, -z2, -x2, -z2, h, (0.96, 0.64, 0.35))  

    # Right roads
    draw_wall(x1, z1, x2, z1, h, (0.96, 0.64, 0.35)) 
    draw_wall(x1, z2, x2, z2, h, (0.96, 0.64, 0.35))
    draw_wall(x1, -z1, x2, -z1, h, (0.96, 0.64, 0.35)) 
    draw_wall(x1, -z2, x2, -z2, h, (0.96, 0.64, 0.35)) 

    # Center walls
    draw_wall(-100, grid_length, -100, 900, h, (0.96, 0.64, 0.35)) 
    draw_wall(100, grid_length, 100, 900, h, (0.96, 0.64, 0.35))
    draw_wall(-100, -grid_length, -100, -900, h, (0.96, 0.64, 0.35))
    draw_wall(100, -grid_length, 100, -900, h, (0.96, 0.64, 0.35))

    draw_wall(-100, 350, -100, 0, h, (0.96, 0.64, 0.35)) 
    draw_wall(100, -350, 100, 0, h, (0.96, 0.64, 0.35))   

def draw_cylinder_bin(color, top, bottom, hei):
    glPushMatrix()
    glColor3f(*color)  
    glRotatef(-90, 1, 0, 0)  
    gluCylinder(gluNewQuadric(), top, bottom, hei, 20, 20)
    glPopMatrix()


def draw_cube_bin(color):
    glPushMatrix()
    glColor3f(*color)         
    glutSolidCube(45)  # Cube base for the bin
    glPopMatrix()

# Bin definitions
bins = [
    {"type": "PAPER", "pos": (-1200, 30, 450), "color": ([0.6, 0.6, 0.7], [0.33, 0.6, .5])},           # grey / Greenish
    {"type": "PLASTIC", "pos": (0, 30, 1200), "color": ([0.9, 0.0, 0.9], [1.0, 0.6, 1.0])},            # Purple / Pink
    {"type": "GLASS", "pos": (1200, 30, 450), "color": ([0.0, 0.5, 0.0], [0.5, 1.0, 0.5])},            # Dark / Light Green
    {"type": "METAL", "pos": (-0, 30, -1200), "color": ([0.8, 0.8, 0.8], [0.9, 0.9, 0.9])},          # Silver
    {"type": "BIODEGRADABLE", "pos": (1200, 30, -450), "color": ([0.55, 0.27, 0.07], [0.82, 0.71, 0.55])} # Brown / Beige
]

def get_text_width(text, font=GLUT_BITMAP_HELVETICA_18):
    return len(text) * 10  # Approximate width

def draw_bin_body(x, y, z, cube_color, cyl_color, label="BIN"):
    # Cube base
    glPushMatrix()
    glTranslatef(x, y, z)
    draw_cube_bin(cube_color)
    glPopMatrix()

    # Cylinder top (bin opening)
    glPushMatrix()
    glTranslatef(x, y + 25, z)
    draw_cylinder_bin(cyl_color, 20, 18, 22)
    glPopMatrix()

    glPushMatrix()
    glColor3f(1, 1, 1)
    glRasterPos3f(x - 15, y + 50, z)
    for ch in label:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    glPopMatrix()

def draw_bins():
    for b in bins:
        draw_bin_body(
            b["pos"][0], b["pos"][1], b["pos"][2],
            b["color"][0], b["color"][1],
            label=b["type"]  
        )

# Inventory system
current_bin = None
inventory = []
inventory_limit = 3
current_inventory_index = 0
latest_picked_trash_color = None  

def check_bin_in_front():
    global current_bin
    current_bin = None
    for b in bins:
        bx, by, bz = b["pos"]
        dist = math.hypot(player_pos[0] - bx, player_pos[2] - bz)
        if dist < 65:
            current_bin = b
            break

def draw_lamp(x, y):
    glPushMatrix()
    glTranslatef(x, 0, y)
    draw_cylinder_bin([0.55, 0.27, 0.07], 5, 5, 130)  #Brown
    glPopMatrix()
    
    glPushMatrix()
    glColor3f(1, 1, 0)   # Yellow
    glTranslatef(x, 130, y)
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


def keyboardListener(key,x,y):
    global player_angle, auto_camera, player_pos, fp_cam_yaw
    global current_trash, inventory, inventory_message, inventory_message_time, current_inventory_index
    global movement_keys, camera_mode, score, latest_picked_trash_color
    key=key.decode("utf-8").lower()
    if game_over:
        if key=="r": reset_game(); return
        return  
    
    # Set movement flags for smooth movement
    if key in movement_keys:
        movement_keys[key] = True
    elif key=="v":
        # Toggle camera mode
        if camera_mode=="third":
            camera_mode="first"
        else:
            camera_mode="third"
        print(f"Camera mode: {camera_mode.upper()}")
       
    elif key == "n" and current_trash:
        if len(inventory) < inventory_limit:
            inventory.append(current_trash["name"])
            latest_picked_trash_color = current_trash["color"]  # Store the color
            trash_items.remove(current_trash)
            print(f"Collected: {current_trash['name']}")
            inventory_message = f"Collected: {current_trash['name']}"
            inventory_message_time = time.time()
            current_trash = None
        else:
            print("Inventory full!")
            inventory_message = "Inventory full!"
            inventory_message_time = time.time()
    elif key == "m" and current_bin and inventory:
        item = inventory[current_inventory_index]
        
        trash_category = get_trash_category(item)
        bin_type = current_bin['type']
        
        if trash_category == bin_type:
            # Correct bin - increase score
            score += 1
            print(f"Correct! Dumped {item} into {bin_type} bin - Score: {score}")
            inventory_message = f"Correct! +1 point - Score: {score}"
        else:
            # Wrong bin - decrease score (can go negative)
            score -= 1
            print(f"Wrong bin! {item} doesn't belong in {bin_type} bin - Score: {score}")
            inventory_message = f"Wrong bin! -1 point - Score: {score}"
            
        inventory_message_time = time.time()
        inventory.pop(current_inventory_index)
        if inventory:
            current_inventory_index %= len(inventory)
        else:
            current_inventory_index = 0
            latest_picked_trash_color = None  # Clear color when inventory is empty

    # Cycle through inventory
    elif key == "\t" and inventory:   # using TAB (Shift alternative)
        current_inventory_index = (current_inventory_index + 1) % len(inventory)
        print(f"Selected inventory item: {inventory[current_inventory_index]}")
        inventory_message = f"Selected: {inventory[current_inventory_index]}"
        inventory_message_time = time.time()
#====================================================================================

# Handle key release
def keyboardUpListener(key, x, y):
    global movement_keys
    key = key.decode("utf-8").lower()
    if key in movement_keys:
        movement_keys[key] = False

def update_movement():
    global player_pos, player_angle
    
    if game_over:
        return
        
    move_x, move_z = 0, 0
    
    if movement_keys["w"]:
        move_x += player_dir[0] * movement_speed
        move_z += player_dir[1] * movement_speed
    if movement_keys["s"]:
        move_x -= player_dir[0] * movement_speed
        move_z -= player_dir[1] * movement_speed
    if movement_keys["a"]:
        player_angle += rotation_speed
        update_player_dir()
    if movement_keys["d"]:
        player_angle -= rotation_speed
        update_player_dir()
    
    if move_x != 0 or move_z != 0:
        new_x = player_pos[0] + move_x
        new_z = player_pos[2] + move_z
        if is_position_free(new_x, new_z, margin=20):
            player_pos[0] = new_x
            player_pos[2] = new_z
    
    limit = grid_length - player_margin
    player_pos[0] = max(-limit, min(limit, player_pos[0]))
    player_pos[2] = max(-limit, min(limit, player_pos[2]))

def specialKeyListener(key,x,y):
    global camera_height,camera_angle
    # Arrow keys only work in first person mode
    if camera_mode == "first":
        if key==GLUT_KEY_UP: camera_height+=10
        elif key==GLUT_KEY_DOWN: camera_height-=10
        elif key==GLUT_KEY_LEFT: camera_angle+=5
        elif key==GLUT_KEY_RIGHT: camera_angle-=5
       
        if camera_height < Cam_Min_Hei: camera_height = Cam_Min_Hei
        if camera_height > Cam_Max_Hei: camera_height = Cam_Max_Hei

def mouseListener(button,state,x,y):
    pass

def setupCamera():
    glMatrixMode(GL_PROJECTION); glLoadIdentity()
    aspect=glutGet(GLUT_WINDOW_WIDTH)/max(1,glutGet(GLUT_WINDOW_HEIGHT))
    fov = fov_third if camera_mode=="third" else fov_first
    gluPerspective(fov,aspect,0.1,2500)
    glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    if camera_mode=="third":
        follow_angle = player_angle + 180
        cx = player_pos[0] + math.sin(math.radians(follow_angle)) * camera_distance
        cz = player_pos[2] + math.cos(math.radians(follow_angle)) * camera_distance
        gluLookAt(cx, camera_height, cz, player_pos[0], player_pos[1]+50, player_pos[2], 0, 1, 0)
    else:
        yaw = player_angle
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
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Draw 3D scene
    setupCamera()
    draw_grid()
    draw_road()
    draw_bins()
    draw_home_boundary()
    set_lamp()
    draw_boundaries()
    draw_maze()
    draw_player()
    draw_trash()

    # Draw 2D HUD
    glDisable(GL_DEPTH_TEST)

    # Switch to 2D rendering
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, glutGet(GLUT_WINDOW_WIDTH), 0, glutGet(GLUT_WINDOW_HEIGHT))

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Draw HUD text
    if not game_over:
        time_limit, trash_count, win_percentage = get_level_requirements(current_level)
        
        # Top-left: Game status
        draw_text(10, glutGet(GLUT_WINDOW_HEIGHT) - 25,
                f"Level {current_level} | Score: {score}")
        
        # Timer below level
        if game_start_time:
            elapsed = time.time() - game_start_time
            remaining = max(0, time_limit - elapsed)
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            draw_text(10, glutGet(GLUT_WINDOW_HEIGHT) - 50,
                    f"Time: {minutes}:{seconds:02d}")
        
        # Goal progress
        required_score = int(trash_count * win_percentage)
        draw_text(10, glutGet(GLUT_WINDOW_HEIGHT) - 75,
                f"Goal: {required_score}/{trash_count} ({int(win_percentage*100)}%)")
        
        # Inventory display
        if inventory:
            draw_text(10, glutGet(GLUT_WINDOW_HEIGHT) - 100,
                    f"Inventory: {', '.join(inventory)}")
    else:
        # Game only ends on failure
        draw_text(10, glutGet(GLUT_WINDOW_HEIGHT) - 25,
                  f"LEVEL {current_level} FAILED! Press R to restart from Level 1.")

    # Interaction messages (middle area)
    if current_trash:
        draw_text(10, glutGet(GLUT_WINDOW_HEIGHT) - 140,
                  f"Press N to collect: {current_trash['name']}")
        
    # Notification messages
    if inventory_message and (time.time() - inventory_message_time) < 2:
        draw_text(10, glutGet(GLUT_WINDOW_HEIGHT) - 165, inventory_message)

    # Bin interaction (bottom area)
    if current_bin and inventory:
        draw_text(10, glutGet(GLUT_WINDOW_HEIGHT) - 190,
                  f"Press M to dump into {current_bin['type']} bin")
        draw_text(10, glutGet(GLUT_WINDOW_HEIGHT) - 215,
                  "Press TAB to cycle inventory")

    # Draw minimap
    draw_minimap()

    # Restore previous projection/modelview
    glPopMatrix() 
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)
    glutSwapBuffers()

# Game loop
def idle():
    global game_over, game_won, game_lost, game_start_time
    
    if not game_over:
        # Start timer on first frame
        if game_start_time is None:
            game_start_time = time.time()
        
        update_movement()  # Continuous movement
        check_trash_in_front() # View trash
        check_bin_in_front() # For bins
        check_game_conditions()  # Check win/lose conditions
    glutPostRedisplay()

def check_game_conditions():
    global game_over, game_won, game_lost, game_start_time, current_level, max_level_reached
    global score, inventory, current_inventory_index, latest_picked_trash_color
    
    if game_over:
        return
    
    time_limit, trash_count, win_percentage = get_level_requirements(current_level)
    required_score = int(trash_count * win_percentage)
    
    # Check if player has reached the goal score - advance to next level
    if score >= required_score:
        current_level += 1
        max_level_reached = max(max_level_reached, current_level)
        print(f"LEVEL {current_level - 1} COMPLETED! Advancing to Level {current_level}!")
        
        # Reset for next level
        score = 0
        game_start_time = time.time()  # Reset timer
        inventory.clear()
        current_inventory_index = 0
        latest_picked_trash_color = None
        
        # Generate new trash for next level
        new_time_limit, new_trash_count, new_win_percentage = get_level_requirements(current_level)
        generate_trash(new_trash_count)
        
        print(f"Level {current_level} started - Goal: {int(new_trash_count * new_win_percentage)}/{new_trash_count} ({int(new_win_percentage*100)}%) in {new_time_limit//60}:{new_time_limit%60:02d}")
        return
    
    # Check time limit
    if game_start_time:
        elapsed = time.time() - game_start_time
        if elapsed >= time_limit:
            # Time's up - player didn't achieve goal
            game_lost = True
            print(f"LEVEL {current_level} FAILED! Time's up. Needed {required_score}, got {score}")
            game_over = True
            return
    
    # Check if all trash collected (but goal not reached - this shouldn't happen now)
    if len(trash_items) == 0:
        if score >= required_score:
            game_won = True
            print(f"LEVEL {current_level} COMPLETED! All trash collected!")
        else:
            game_lost = True
            print(f"LEVEL {current_level} FAILED! All collected but needed {required_score}, got {score}")
        game_over = True
        return
    
    # Check if it's impossible to reach goal
    max_possible_score = score + len(trash_items)  # Current score + remaining trash
    if max_possible_score < required_score:
        game_lost = True
        game_over = True
        print(f"LEVEL {current_level} IMPOSSIBLE! Max possible: {max_possible_score}, needed: {required_score}")

def reset_game():
    global score, game_over, player_angle, inventory, current_inventory_index, latest_picked_trash_color
    global game_start_time, game_won, game_lost, current_level, max_level_reached
    
    # Game only ends on failure - restart from level 1
    current_level = 1
    print('GAME OVER - Restarting from Level 1')
    
    score = 0
    game_over = False
    game_won = False
    game_lost = False
    game_start_time = None
    player_angle = initial_Player_Angle
    inventory.clear()
    current_inventory_index = 0
    latest_picked_trash_color = None
    
    # Generate trash for level 1
    time_limit, trash_count, win_percentage = get_level_requirements(current_level)
    generate_trash(trash_count)
    
    update_player_dir()
    print(f'Level {current_level} started - Goal: {int(trash_count * win_percentage)}/{trash_count} ({int(win_percentage*100)}%)')

# Trash system
def get_trash_category(trash_name):
    """Find which category a trash item belongs to"""
    for category, items in trash_types.items():
        for item_name, color in items:
            if item_name == trash_name:
                return category
    return None  # Unknown trash type

trash_items = []
trash_types = {
    "PAPER": [("Newspaper",(1,1,0.8)), ("Quiz script",(1,1,0.9)), ("Cardboard box",(0.9,0.9,0.6)), ("Paper cup",(1,0.9,0.8)), ("Envelope",(1,0.95,0.8)), ("Paper bag",(0.95,0.85,0.7))],
    "GLASS": [("Glass jar",(0.7,0.9,1)), ("Drinking glass",(0.8,1,1)), ("Wine bottle",(0.6,0.8,1)), ("Jam jar",(0.5,0.7,1)), ("Medicine syrup bottle",(0.4,0.6,1))],
    "PLASTIC": [("Chanachur packet",(0,1,0)), ("Chips packet",(0.1,0.9,0)), ("Shampoo sachet",(0,0.8,0)), ("Water bottle",(0,0.7,0.2)), ("Plastic bags",(0.2,0.9,0)), ("Oil container",(0,0.6,0))],
    "METAL": [("Soft drink can",(1,0,0)), ("Food can",(0.8,0,0)), ("Foil paper",(1,0.2,0)), ("Murir tin",(0.9,0,0)), ("Mosquito spray can",(0.7,0,0))],
    "BIODEGRADABLE": [("Banana peel",(1,0.9,0.2)), ("Coconut shell",(0.8,0.7,0.3)), ("Fish bones",(1,1,1)), ("Eggshell",(0.9,0.9,0.8)), ("Leftover rice",(1,1,0.9))]
}

def generate_trash(n=20, min_distance_from_player=100):
    trash_items.clear()
    attempts = 0
    max_attempts = n * 10

    while len(trash_items) < n and attempts < max_attempts:
        attempts += 1

        category = random.choice(list(trash_types.keys()))
        name, color = random.choice(trash_types[category])
        shape = random.choice(["cube", "cylinder"])
        size = random.randint(20, 40)

        x = random.randint(-grid_length + 50, grid_length - 50)
        z = random.randint(-grid_length + 50, grid_length - 50)

        # Check distance from player and other trash
        if math.hypot(player_pos[0] - x, player_pos[2] - z) >= min_distance_from_player \
           and is_position_free(x, z, margin=size):
            trash_items.append({
                "pos": [x, 0, z],
                "shape": shape,
                "size": size,
                "color": color,
                "name": name
            })

def is_position_free(x, z, margin=25):
    # Check collision with trash items
    for t in trash_items:
        tx, tz = t["pos"][0], t["pos"][2]
        if math.hypot(x - tx, z - tz) < (margin + t["size"]/2):
            return False
    
    # Check collision with bins
    for b in bins:
        bx, by, bz = b["pos"]
        bin_radius = 25  # Bin collision radius
        if math.hypot(x - bx, z - bz) < (margin + bin_radius):
            return False
    
    # Check collision with maze walls (dark brown)
    for wall in maze_walls:
        x1, z1, x2, z2, _, _ = wall
        # Check wall proximity
        if is_near_wall_segment(x, z, x1, z1, x2, z2, margin):
            return False
    
    # Check collision with boundary walls (light brown walls beside roads)
    # Check wall segments only
    
    # Outside grid perimeter walls
    if (x <= -grid_length + margin or x >= grid_length - margin or 
        z <= -grid_length + margin or z >= grid_length - margin):
        return False
    
    # Boundary wall segments
    wall_segments = [
        # Left bottom road walls
        (-grid_length, 550, -road_width/2, 550),  # horizontal wall at z=550
        (-grid_length, 350, -road_width/2, 350),  # horizontal wall at z=350
        
        # Left top road walls
        (-grid_length, -550, -road_width/2, -550),  # horizontal wall at z=-550
        (-grid_length, -350, -road_width/2, -350),  # horizontal wall at z=-350
        
        # Right bottom road walls
        (grid_length, 550, road_width/2, 550),   # horizontal wall at z=550
        (grid_length, 350, road_width/2, 350),   # horizontal wall at z=350
        
        # Right top road walls
        (grid_length, -550, road_width/2, -550),  # horizontal wall at z=-550
        (grid_length, -350, road_width/2, -350),  # horizontal wall at z=-350
        
        # Center road walls (vertical)
        (-100, grid_length, -100, 900),   # left center wall
        (100, grid_length, 100, 900),     # right center wall
        (-100, -grid_length, -100, -900), # left center wall (bottom)
        (100, -grid_length, 100, -900),   # right center wall (bottom)
        
        # Center connecting walls
        (-100, 350, -100, 0),    # left connector
        (100, -350, 100, 0),     # right connector
    ]
    
    # Check collision with wall segments
    for x1, z1, x2, z2 in wall_segments:
        if is_near_wall_segment(x, z, x1, z1, x2, z2, margin):
            return False
    
    return True

def is_near_wall_segment(px, pz, x1, z1, x2, z2, margin):
    
    # Vector from start to end of wall
    wall_dx = x2 - x1
    wall_dz = z2 - z1
    wall_length_sq = wall_dx * wall_dx + wall_dz * wall_dz
    
    if wall_length_sq == 0:
        # Wall is a point
        return math.hypot(px - x1, pz - z1) < margin
    
    # Vector from wall start to point
    point_dx = px - x1
    point_dz = pz - z1
    
    # Project point onto wall line (parameter t)
    t = max(0, min(1, (point_dx * wall_dx + point_dz * wall_dz) / wall_length_sq))
    
    # Find closest point on wall
    closest_x = x1 + t * wall_dx
    closest_z = z1 + t * wall_dz
    
    # Check distance from point to closest point on wall
    distance = math.hypot(px - closest_x, pz - closest_z)
    return distance < margin

def draw_trash():
    if not trash_items:
        return

    quad = gluNewQuadric() 
    for t in trash_items:
        glPushMatrix()
        glTranslatef(t["pos"][0], t["size"]/2, t["pos"][2])
        glColor3f(*t["color"])

        if t["shape"] == "cube":
            glPushMatrix()
            glScalef(t["size"], t["size"], t["size"])
            glutSolidCube(1)
            glPopMatrix()
        else:  
            glPushMatrix()
            glRotatef(-90, 1, 0, 0)
            gluCylinder(quad, t["size"]/2, t["size"]/2, t["size"], 12, 12)
            glPopMatrix()

        glPopMatrix()
    gluDeleteQuadric(quad)

# Trash collection
inventory = []          # Holds collected trash
inventory_limit = 3     # Max trash the player can carry
current_trash = None   
inventory_message = ""
inventory_message_time = 0


def check_trash_in_front():
    global current_trash
    current_trash = None
    for t in trash_items:
        dx = t["pos"][0] - player_pos[0]
        dz = t["pos"][2] - player_pos[2]
        distance = math.hypot(dx, dz)
        
        if distance < 50: 
            angle_to_trash = math.atan2(dz, dx)
            player_angle_rad = math.atan2(player_dir[1], player_dir[0])
            angle_diff = (angle_to_trash - player_angle_rad + math.pi) % (2*math.pi) - math.pi
            if abs(angle_diff) < math.radians(60):
                current_trash = t

                break

# Initialize OpenGL and start game
glutInit()
glutInitDisplayMode(GLUT_DOUBLE|GLUT_RGB|GLUT_DEPTH)
glutInitWindowSize(1000,800)
glutCreateWindow(b"ECO GUARDIAN")
glClearColor(0,0,0,1)
glEnable(GL_DEPTH_TEST)
update_player_dir()
generate_maze()

# Initialize first level
time_limit, trash_count, win_percentage = get_level_requirements(current_level)
generate_trash(n=trash_count)
print(f'Game started - Level {current_level}: Goal {int(trash_count * win_percentage)}/{trash_count} ({int(win_percentage*100)}%)')

# Register callbacks and start main loop
glutDisplayFunc(showScreen)
glutKeyboardFunc(keyboardListener)
glutKeyboardUpFunc(keyboardUpListener)
glutSpecialFunc(specialKeyListener)
glutMouseFunc(mouseListener)
glutIdleFunc(idle)
glutMainLoop()
