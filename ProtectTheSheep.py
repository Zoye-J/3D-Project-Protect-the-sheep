from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time
last_time = time.time()



camera_angle = 0  
camera_height = 400 
camera_distance = 500  
camera_mode = "third_person"  
fovY = 120  # Field of view
GRID_LENGTH = 900 


trees = []
opening_radius = 500  
middle_radius = 680  
outer_radius = 900  
num_trees = 300    


# Night Morning properties
is_night = False
night_transition = 0 
stars = []
morning_transition = 0 
is_morning = False
night_transition_speed = 0.05 
morning_transition_speed = 0.05  


# Shepherd properties
shepherd_pos = [0, 0, 30]  # Starting position (x, y, z)
shepherd_rotation = 0      # Facing direction in degrees
shepherd_speed = 10         # Movement speed

# Sheep properties
sheeps = []
num_sheeps = 3
sheep_speed = 1.7
sheep_direction_change_time = 0.2  # Time between direction changes (seconds)
sheep_wander_distance = opening_radius-50 

#Interactons
last_whistle_time = -30   # to manage cooldown
follow_duration = 15.0
stuck_sheep = None
whistle_cooldown = 30  
rescue_distance = 60  
stuck_countdown = 30  
stuck_start_time = 0   

# Wood chopping site variables
wood_site_pos = [370, 20, 30] 
wood_site_radius = 60        
axe_attached = False         
current_wood_chops = 0       
max_chops = 3               
wood_respawn_timer = 0       
current_wood_visible = True

wood_count = 0
max_wood_capacity = 3
can_chop_wood = True

# Fire properties
fire_lit_count = 0  
fires_needed_for_morning = 3 
final_fire_active = False 
fire_stage = 0  

fire_stage_durations = [0, 180, 120, 120]
fire_timer = 0
fire_pos = [0, 0, 0] 
carrying_wood = False  

# Wolf properties
wolves = []
wolf_speed = 0.5                 
max_wolves = 5
wolf_spawned_this_night = False

stones = []                 
stone_speed = 35.0
stone_ttl = 2.0                  
stone_radius = 6.0            

WOLF_HIT_RADIUS = 22.0            
WOLF_EAT_RADIUS = 28.0  


heart_points = 3 
game_over = False 



def create_stars():
    global stars
    stars = []
    for _ in range(800):
      
        angle1 = random.uniform(0, 2 * math.pi)
        angle2 = random.uniform(0, math.pi)
        distance = 1900  
        
        x = distance * math.sin(angle2) * math.cos(angle1)
        y = distance * math.sin(angle2) * math.sin(angle1) 
        z = distance * math.cos(angle2) - 1000  

        size = random.uniform(0.5, 2.0)
        brightness = random.uniform(0.7, 1.0)
        
        stars.append((x, y, z, size, brightness))

create_stars()


def generate_trees():
    global trees
    trees = []
 
    for _ in range(num_trees // 3):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(opening_radius + 10, middle_radius - 20)
        
        x = distance * math.cos(angle)
        y = distance * math.sin(angle)
        z = 0
        

        height = random.uniform(120, 120)
        trunk_width = random.uniform(8, 12)
        
    
        green_shade = random.uniform(0.4, 0.7)
        foliage_color = (0.0, green_shade, 0.0)
        
        trees.append(("deciduous", x, y, z, height, trunk_width, foliage_color))
    

    for _ in range(6 * num_trees // 3):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(middle_radius + 10, outer_radius - 20)
        
        
        x = distance * math.cos(angle)
        y = distance * math.sin(angle)
        z = 0
        
    
        height = random.uniform(180, 280)
        trunk_width = random.uniform(12, 20)
        
 
        green_shade = random.uniform(0.3, 0.8)
        foliage_color = (0.0, green_shade, 0.0)
        
     
        rand_val = random.random()
        if rand_val < 0.3:
            tree_type = "pine"
        elif rand_val < 0.6:
            tree_type = "spike_pine" 
        else:
            tree_type = "deciduous"
        trees.append((tree_type, x, y, z, height, trunk_width, foliage_color))

# Initialize trees
generate_trees()

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_sky():
    
    if is_night:
        sky_color = (0.05, 0.1, 0.2) 
        fog_color = (0.02, 0.06, 0.12)  
    elif is_morning:
        
        sky_color = (
            0.8 * morning_transition + 0.05 * (1 - morning_transition),  # R
            0.4 * morning_transition + 0.1 * (1 - morning_transition),   # G
            0.1 * morning_transition + 0.2 * (1 - morning_transition)    # B
        )
        fog_color = (
            0.7 * morning_transition + 0.02 * (1 - morning_transition),   # R
            0.5 * morning_transition + 0.06 * (1 - morning_transition),   # G 
            0.3 * morning_transition + 0.12 * (1 - morning_transition)    # B
        )
    else:
       
        blend = min(night_transition, 1.0)
        sky_color = (
            0.53 * (1 - blend) + 0.05 * blend,  # R
            0.81 * (1 - blend) + 0.1 * blend,   # G
            0.98 * (1 - blend) + 0.2 * blend    # B
        )
        fog_color = (
            0.7 * (1 - blend) + 0.02 * blend,   # R
            0.5 * (1 - blend) + 0.06 * blend,   # G 
            0.95 * (1 - blend) + 0.12 * blend   # B
        )

    glPushMatrix()
    glColor3f(*sky_color)
    glTranslatef(0, 0, -1000)
    glutSolidSphere(2000, 32, 32)
    glPopMatrix()
    
    
    if is_night or (night_transition > 0 and not is_morning):
        glPushMatrix()
        for x, y, z, size, brightness in stars:
            glPushMatrix()
            glTranslatef(x, y, z)

            star_alpha = brightness * min(night_transition, 1.0) * (1 - morning_transition)
            glColor4f(1.0, 1.0, 1.0, star_alpha)
            glutSolidSphere(size, 6, 6)
            glPopMatrix()
        glPopMatrix()

    
   
    glPushMatrix()
    glColor3f(*sky_color)
    glTranslatef(0, 0, -1000)
    glutSolidSphere(2000, 32, 32)
    glPopMatrix()
    
 
    if is_night or night_transition > 0:
        glPushMatrix()
        for x, y, z, size, brightness in stars:
            glPushMatrix()
            glTranslatef(x, y, z)

            star_alpha = brightness * min(night_transition, 1.0)
            glColor4f(1.0, 1.0, 1.0, star_alpha)
            glutSolidSphere(size, 6, 6)
            glPopMatrix()
        glPopMatrix()

def draw_ground():

    if is_night:
        opening_color = (0.0, 0.35, 0.0)   
        middle_color = (0.0, 0.3, 0.0)  
        forest_color = (0.0, 0.15, 0.0)    
    else:

        blend = min(night_transition, 1.0)
        opening_color = (
            0.0 * (1 - blend) + 0.0 * blend,   # R
            0.7 * (1 - blend) + 0.3 * blend,   # G
            0.0 * (1 - blend) + 0.3 * blend    # B
        )
        middle_color = (
            0.0 * (1 - blend) + 0.0 * blend,   # R
            0.6 * (1 - blend) + 0.25 * blend,  # G
            0.0 * (1 - blend) + 0.25 * blend   # B
        )
        forest_color = (
            0.1 * (1 - blend) + 0.1 * blend,   # R
            0.3 * (1 - blend) + 0.2 * blend,   # G
            0.05 * (1 - blend) + 0.2 * blend   # B
        )
    

    glBegin(GL_QUADS)
    glColor3f(*opening_color)
    segments = 32
    for i in range(segments):
        angle1 = i * 2 * math.pi / segments
        angle2 = (i + 1) * 2 * math.pi / segments
        x1 = opening_radius * math.cos(angle1)
        y1 = opening_radius * math.sin(angle1)
        x2 = opening_radius * math.cos(angle2)
        y2 = opening_radius * math.sin(angle2)
        glVertex3f(x1, y1, 0)
        glVertex3f(x2, y2, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 0)
    glEnd()
    
   
    glBegin(GL_QUADS)
    glColor3f(*middle_color)
    for i in range(segments):
        angle1 = i * 2 * math.pi / segments
        angle2 = (i + 1) * 2 * math.pi / segments
        x1_inner = opening_radius * math.cos(angle1)
        y1_inner = opening_radius * math.sin(angle1)
        x2_inner = opening_radius * math.cos(angle2)
        y2_inner = opening_radius * math.sin(angle2)
        x1_outer = middle_radius * math.cos(angle1)
        y1_outer = middle_radius * math.sin(angle1)
        x2_outer = middle_radius * math.cos(angle2)
        y2_outer = middle_radius * math.sin(angle2)
        glVertex3f(x1_inner, y1_inner, 0)
        glVertex3f(x2_inner, y2_inner, 0)
        glVertex3f(x2_outer, y2_outer, 0)
        glVertex3f(x1_outer, y1_outer, 0)
    glEnd()
 
    glBegin(GL_QUADS)
    glColor3f(*forest_color)
    for i in range(segments):
        angle1 = i * 2 * math.pi / segments
        angle2 = (i + 1) * 2 * math.pi / segments
        x1_inner = middle_radius * math.cos(angle1)
        y1_inner = middle_radius * math.sin(angle1)
        x2_inner = middle_radius * math.cos(angle2)
        y2_inner = middle_radius * math.sin(angle2)
        x1_outer = outer_radius * math.cos(angle1)
        y1_outer = outer_radius * math.sin(angle1)
        x2_outer = outer_radius * math.cos(angle2)
        y2_outer = outer_radius * math.sin(angle2)
        glVertex3f(x1_inner, y1_inner, 0)
        glVertex3f(x2_inner, y2_inner, 0)
        glVertex3f(x2_outer, y2_outer, 0)
        glVertex3f(x1_outer, y1_outer, 0)
    glEnd()

def draw_deciduous_tree(x, y, z, height, trunk_width, foliage_color):
    glPushMatrix()
    glTranslatef(x, y, z)
    
 
    if is_night:
        trunk_color = (0.35, 0.17, 0.04) 
 
        dark_foliage = (
            foliage_color[0] * 0.5,
            foliage_color[1] * 0.5, 
            foliage_color[2] * 0.5
        )
    else:
        trunk_color = (0.55, 0.27, 0.07) 
        dark_foliage = foliage_color  
    
    # Draw trunk
    glColor3f(*trunk_color)
    glPushMatrix()
    glRotatef(0, 1, 0, 90)  
    glutSolidCylinder(trunk_width, height * 0.8, 10, 3)  
    glPopMatrix()
    
    # Draw foliage layers
    glPushMatrix()
    glTranslatef(0, 0, height * 0.6)
    
    # Bottom foliage
    glColor3f(dark_foliage[0] * 0.8, dark_foliage[1] * 0.8, dark_foliage[2] * 0.8)
    glutSolidSphere(height * 0.3, 8, 8)
    
    # Middle foliage
    glTranslatef(0, 0, height * 0.15)
    glColor3f(dark_foliage[0] * 0.9, dark_foliage[1] * 0.9, dark_foliage[2] * 0.9)
    glutSolidSphere(height * 0.2, 10, 10)
    
    # Top foliage
    glTranslatef(0, 0, height * 0.1)
    glColor3f(*dark_foliage)
    glutSolidSphere(height * 0.1, 8, 8)
    
    glPopMatrix()
    glPopMatrix()

def draw_pine_tree(x, y, z, height, trunk_width, foliage_color):
    glPushMatrix()
    glTranslatef(x, y, z)
    
 
    if is_night:
        trunk_color = (0.3, 0.15, 0.03) 
     
        dark_foliage = (
            foliage_color[0] * 0.6,
            foliage_color[1] * 0.6,
            foliage_color[2] * 0.6
        )
    else:
        trunk_color = (0.4, 0.2, 0.05) 
        dark_foliage = foliage_color 
    
    # Draw trunk
    glColor3f(*trunk_color)
    glPushMatrix()
    glRotatef(0, 1, 0, 90)
    glutSolidCylinder(trunk_width, height * 0.4, 12, 3)
    glPopMatrix()
    
   
    glPushMatrix()
    glTranslatef(0, 0, height * 0.3)
    

    glColor3f(dark_foliage[0] * 0.7, dark_foliage[1] * 0.7, dark_foliage[2] * 0.7)
    glPushMatrix()
    glRotatef(0, 1, 0, 90)
    glutSolidCone(height * 0.35, height * 0.4, 12, 3)
    glPopMatrix()
    
 
    glTranslatef(0, 0, height * 0.25)
    glColor3f(dark_foliage[0] * 0.85, dark_foliage[1] * 0.85, dark_foliage[2] * 0.85)
    glPushMatrix()
    glRotatef(0, 1, 0, 90)
    glutSolidCone(height * 0.25, height * 0.3, 10, 3)
    glPopMatrix()
    
   
    glTranslatef(0, 0, height * 0.15)
    glColor3f(*dark_foliage)
    glPushMatrix()
    glRotatef(0, 1, 0, 90)
    glutSolidCone(height * 0.15, height * 0.2, 8, 3)
    glPopMatrix()
    
    glPopMatrix()
    glPopMatrix()

def draw_spike_pine_tree(x, y, z, height, trunk_width, foliage_color):
    glPushMatrix()
    glTranslatef(x, y, z)
    

    if is_night:
        trunk_color = (0.3, 0.15, 0.03)
        dark_foliage = (
            foliage_color[0] * 0.4,
            foliage_color[1] * 0.4,
            foliage_color[2] * 0.4
        )
    else:
        trunk_color = (0.4, 0.2, 0.05) 
        dark_foliage = (foliage_color[0] * 0.5, foliage_color[1] * 0.5, foliage_color[2] * 0.5)
    

    glColor3f(*trunk_color)
    glPushMatrix()
    glRotatef(0, 1, 0, 90)
    glutSolidCylinder(trunk_width * 0.4, height * 0.4, 10, 20)
    glPopMatrix()
   
    glPushMatrix()
    glTranslatef(0, 0, height * 0.4)

    glColor3f(*dark_foliage)
  
    glPushMatrix()
    glRotatef(0, 1, 0, 9)
    glutSolidCone(height * 0.1, height * 0.8, 10, 3)
    glPopMatrix()
    
    glPopMatrix()
    glPopMatrix()

def draw_environment():
    draw_sky()
    draw_ground()

    for tree in trees:
        tree_type, x, y, z, height, trunk_width, foliage_color = tree
        if tree_type == "pine":
            draw_pine_tree(x, y, z, height, trunk_width, foliage_color)
        elif tree_type == "spike_pine":
            draw_spike_pine_tree(x, y, z, height, trunk_width, foliage_color)
        else:
            draw_deciduous_tree(x, y, z, height, trunk_width, foliage_color)

def draw_shapes():
    glPushMatrix()
    glColor3f(0, 0, 1)
    glTranslatef(0, 0, 30)
    glPopMatrix()


def draw_shepherd(first_person=False):
    glPushMatrix()
    glTranslatef(shepherd_pos[0], shepherd_pos[1], shepherd_pos[2])
    glRotatef(shepherd_rotation, 0, 0, 1) 


    glScalef(0.8, 0.8, 0.8)


    glPushMatrix()
    glColor3f(0.6, 0.4, 0.2) 
    glTranslatef(0, 0, 16)
    glScalef(20, 28, 40)
    glutSolidCube(1)
    glPopMatrix()


    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)  
    glTranslatef(0, 0, 25)  

    glPushMatrix()
    glTranslatef(10, -1, 5) 
    glutSolidSphere(1.5, 8, 8)
    glPopMatrix()
 
    glPushMatrix()
    glTranslatef(10, -1, 0) 
    glutSolidSphere(1.5, 8, 8)
    glPopMatrix()
   
    glPushMatrix()
    glTranslatef(10, -1, -5) 
    glutSolidSphere(1.5, 8, 8)
    glPopMatrix()
    glPopMatrix()

   
    if not first_person and camera_mode == "third_person":
        glPushMatrix()
        glColor3f(1.0, 0.8, 0.6)  
        glTranslatef(0, 0, 48)    #
        gluSphere(gluNewQuadric(), 12, 16, 16)  
        glPopMatrix()
        glPushMatrix()
        glColor3f(0.3, 0.2, 0.1)  
        glTranslatef(0, 0, 60)  
        glRotatef(1, 0, 90, 0) 
        glutSolidCylinder(10, 4, 16, 3) 
        glPopMatrix()

    glPushMatrix()
    glTranslatef(2, 16, 35)  
    glRotatef(180, 1, 0, 0)


    glPushMatrix()
    glColor3f(0.6, 0.4, 0.2) 
    glutSolidCylinder(5, 8, 12, 3) 
    glPopMatrix()

    glTranslatef(0, 0, 8) 
    glColor3f(1.0, 0.8, 0.6) 
    glutSolidCylinder(5, 24, 12, 3) 

    glPopMatrix()
  
    glPushMatrix()
    glTranslatef(2, -16, 35)  
    glRotatef(180, 1, 0, 0)

    glPushMatrix()
    glColor3f(0.6, 0.4, 0.2) 
    glutSolidCylinder(5, 8, 12, 3)
    glPopMatrix()


    glTranslatef(0, 0, 8)  
    glColor3f(1.0, 0.8, 0.6)  
    glutSolidCylinder(5, 24, 12, 3)  

    glPopMatrix()

    glPushMatrix()
    glColor3f(0.3, 0.2, 0.1) 
    glTranslatef(-4, -12, 2)  
    glRotatef(180, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 5, 2, 32, 12, 6)  
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.3, 0.2, 0.1)
    glTranslatef(-4, 12, 2) 
    glRotatef(180, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 5, 2, 32, 12, 6)  
    glPopMatrix()

    glPopMatrix()   

def move_shepherd(dx, dy):
    global shepherd_pos
    

    angle_rad = math.radians(shepherd_rotation)
    move_x = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
    move_y = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)

    max_distance = opening_radius - 50  
    current_distance = math.sqrt(shepherd_pos[0]**2 + shepherd_pos[1]**2)
    if current_distance > max_distance:
        scale = max_distance / current_distance
        shepherd_pos[0] *= scale
        shepherd_pos[1] *= scale
    
   

def create_sheep():
    global sheeps
    sheeps = []
    

    for i in range(num_sheeps):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(50, 100)
        x = distance * math.cos(angle)
        y = distance * math.sin(angle)
        z = 30
 
        wool_colors = [
            (0.95, 0.95, 0.95), 
            (0.85, 0.85, 0.85),  
            (0.98, 0.94, 0.86)   
        ]
        wool_color = random.choice(wool_colors)
        
        sheeps.append({
            'pos': [x, y, z],
            'wool_color': wool_color,
            'rotation': random.uniform(0, 360),
            'stuck': False,
            'stuck_timer': 0,
            'follow_until': 0, 
        })


create_sheep()

def draw_sheep(sheep):
    glPushMatrix()
    glTranslatef(sheep['pos'][0], sheep['pos'][1], sheep['pos'][2])
    glRotatef(sheep['rotation'], 0, 0, 1)

    glColor3f(*sheep['wool_color'])

    glPushMatrix()
    glTranslatef(0, 0, 10) 
    glColor3f(*sheep['wool_color'])
    glutSolidSphere(20, 16, 16) 
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-8, 0, 15) 
    glColor3f(*sheep['wool_color'])
    glutSolidSphere(15, 12, 12) 
    glPopMatrix()
    
 
    glPushMatrix()
    glTranslatef(18, 0, 15)  
    glColor3f(0.1, 0.1, 0.1)
    glutSolidSphere(10, 12, 12) 
    glPopMatrix()
   
    leg_positions = [
        (-12, -8, 0),   
        (-12, 8, 0),   
        (8, -8, 0),  
        (8, 8, 0)       
    ]
    
    for leg_x, leg_y, leg_z in leg_positions:
        glPushMatrix()
        glTranslatef(leg_x, leg_y, leg_z)
        glColor3f(0.1, 0.1, 0.1)  
        glRotatef(180, 1, 0, 0)  
        glutSolidCylinder(3, 25, 8, 3)  
        glPopMatrix()
    
    glPopMatrix()

def draw_all_sheeps():
    for sheep in sheeps:
        draw_sheep(sheep)

def update_sheep_movement(delta_time):
    global stuck_sheep, num_sheeps, heart_points
    
    for sheep in sheeps:
        if sheep['stuck']:
  
            sheep['stuck_timer'] += delta_time
            continue

        now = time.time()
        if now < sheep['follow_until']:

            dx = shepherd_pos[0] - sheep['pos'][0]
            dy = shepherd_pos[1] - sheep['pos'][1]
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0:
                dx /= distance
                dy /= distance
            
       
            follow_speed = sheep_speed * 1.5
            sheep['pos'][0] += dx * follow_speed
            sheep['pos'][1] += dy * follow_speed
   
            sheep['rotation'] = math.degrees(math.atan2(dy, dx))
            
    
            distance_from_center = math.sqrt(sheep['pos'][0]**2 + sheep['pos'][1]**2)
            if distance_from_center > opening_radius - 40:
                angle_to_center = math.atan2(sheep['pos'][1], sheep['pos'][0])
                sheep['pos'][0] = (opening_radius - 50) * math.cos(angle_to_center)
                sheep['pos'][1] = (opening_radius - 50) * math.sin(angle_to_center)
        
        # NIGHT TIME
        elif is_night and fire_stage > 0:

            dx = fire_pos[0] - sheep['pos'][0]
            dy = fire_pos[1] - sheep['pos'][1]
            distance = math.sqrt(dx**2 + dy**2)
   
            target_distance = random.uniform(100, 150)
            if distance > target_distance + 5:  # Not yet at target position
        
                if distance > 0:
                    dx /= distance
                    dy /= distance
               
                sheep['pos'][0] += dx * sheep_speed * 0.8
                sheep['pos'][1] += dy * sheep_speed * 0.8
          
                sheep['rotation'] = math.degrees(math.atan2(dy, dx))
                
            else:

                if distance > 0:
                    dx /= distance
                    dy /= distance
                    sheep['rotation'] = math.degrees(math.atan2(dy, dx))
      
        else:
           
            if 'move_timer' not in sheep:
                sheep['move_timer'] = 0
                sheep['current_direction'] = random.uniform(0, 2 * math.pi)
                sheep['move_duration'] = random.uniform(0.5, 2.0)
                sheep['wander_intensity'] = random.uniform(1.5, 3.0)
            
            sheep['move_timer'] += delta_time
            
 
            if sheep['move_timer'] >= sheep['move_duration']:
                sheep['move_timer'] = 0
                sheep['current_direction'] = random.uniform(0, 2 * math.pi)
                sheep['move_duration'] = random.uniform(0.5, 2.0)
                sheep['wander_intensity'] = random.uniform(1.5, 3.0)
            

            move_x = math.cos(sheep['current_direction']) * sheep_speed * sheep['wander_intensity']
            move_y = math.sin(sheep['current_direction']) * sheep_speed * sheep['wander_intensity']
            
            sheep['pos'][0] += move_x
            sheep['pos'][1] += move_y
            
            distance_from_center = math.sqrt(sheep['pos'][0]**2 + sheep['pos'][1]**2)
            if distance_from_center > opening_radius - 40:
                angle_to_center = math.atan2(sheep['pos'][1], sheep['pos'][0])
                bounce_variation = random.uniform(-0.5, 0.5)
                sheep['current_direction'] = angle_to_center + math.pi + bounce_variation
                sheep['pos'][0] = (opening_radius - 50) * math.cos(angle_to_center)
                sheep['pos'][1] = (opening_radius - 50) * math.sin(angle_to_center)
            
            sheep['rotation'] = sheep['current_direction'] * 180/math.pi
    

    if not is_night and stuck_sheep is None and random.random() < 0.003: 
        available_sheep = [s for s in sheeps if not s['stuck']]
        if available_sheep:
            stuck_sheep = random.choice(available_sheep)
            stuck_sheep['stuck'] = True
            stuck_sheep['stuck_pulse'] = 0
            print("Sheep got stuck! Press 'P' to rescue it.")

    if stuck_sheep and stuck_sheep['stuck_timer'] >= stuck_countdown:
        sheeps.remove(stuck_sheep)
        num_sheeps -= 1
        heart_points -= 1 
        stuck_sheep = None
        print(" Too late! You lost a sheep and a heart point!")
        print(f"Heart Points: {heart_points}, Sheep: {num_sheeps}")
    check_game_over()

def whistle():
    global last_whistle_time
    now = time.time()
    if now - last_whistle_time >= whistle_cooldown:
        last_whistle_time = now
        for sheep in sheeps:
            sheep['follow_until'] = now + follow_duration 
        print("📯 Whistle! Sheep following...")
    else:
        cooldown_left = whistle_cooldown - (now - last_whistle_time)
        print(f"Whistle is on cooldown! {cooldown_left:.1f} seconds remaining")

def rescue_sheep():
    global stuck_sheep, stuck_start_time
    if not is_night and stuck_sheep:  

        dx = stuck_sheep['pos'][0] - shepherd_pos[0]
        dy = stuck_sheep['pos'][1] - shepherd_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < rescue_distance:
            stuck_sheep['stuck'] = False
            time_saved = stuck_countdown - stuck_sheep['stuck_timer']
            stuck_sheep = None
            print(f"Sheep rescued! {time_saved:.1f} seconds remaining")
        else:
            print("Too far from the stuck sheep!")
    elif is_night:
        print("Can only rescue sheep during the day!")
    else:
        print("No sheep needs rescuing!")

def draw_wolf(wolf):
    glPushMatrix()
    glTranslatef(wolf['pos'][0], wolf['pos'][1], wolf['pos'][2])
    glRotatef(wolf['rotation'], 0, 0, 1)
    
 
    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)
    glTranslatef(8, 0, 15)   
    glRotatef(-90, 1, 0, 0)   

    gluCylinder(gluNewQuadric(), 15, 12, 25, 16, 8)

    gluDisk(gluNewQuadric(), 0, 15, 16, 2)

    glPushMatrix()
    glTranslatef(0, 0, 25)
    gluDisk(gluNewQuadric(), 0, 12, 16, 2)
    glPopMatrix()
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1) 
    glTranslatef(-8, 0, 10) 
    glRotatef(-90, 1, 0, 0) 

    gluCylinder(gluNewQuadric(), 10, 8, 22, 14, 6)

    gluDisk(gluNewQuadric(), 0, 10, 14, 2)

    glPushMatrix()
    glTranslatef(0, 0, 22)
    gluDisk(gluNewQuadric(), 0, 8, 14, 2)
    glPopMatrix()
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1) 
    glTranslatef(28, 20, 30)   

    glutSolidSphere(12, 16, 10)

    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)  
    glTranslatef(10, 0, 0)     
    glRotatef(90, 0, 1, 0)    


    gluCylinder(gluNewQuadric(), 5, 3, 10, 10, 4)

    glColor3f(0.1, 0.1, 0.1)
    gluDisk(gluNewQuadric(), 0, 5, 5, 2) 


    glPushMatrix()
    glTranslatef(0, 0, 10) 
    gluDisk(gluNewQuadric(), 0, 3, 10, 2)
    glPopMatrix()

    glPopMatrix()
    glPopMatrix()
    

    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)
    glTranslatef(30, 25, 38) 
    
    glutSolidCone(4, 8, 8, 4)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)
    glTranslatef(30, 15, 38) 
    
    glutSolidCone(4, 8, 8, 4) 
    glPopMatrix()
  
    leg_positions = [
        (-12, 15, 2), 
        (-12, 5, 2), 
        (8, 5, 2),  
        (8, 18, 2)    
    ]
    
    for leg_x, leg_y, leg_z in leg_positions:
        glPushMatrix()
        glTranslatef(leg_x, leg_y, leg_z)
        glColor3f(0.1, 0.1, 0.1) 
        glRotatef(180, 1, 0, 0) 
        glutSolidCylinder(3, 25, 8, 3) 
        glPopMatrix()
    

    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)
    glTranslatef(-20,10,2)
    glRotatef(25, 0, 1, 0)

    gluCylinder(gluNewQuadric(), 6, 1, 18, 10, 4) 
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)
    glTranslatef(-20, 10, 2)
    glRotatef(-150, 0, 1, 0)

    gluCylinder(gluNewQuadric(), 6, 1, 18, 10, 4) 
    glPopMatrix()
    
   
    glPushMatrix()
    glTranslatef(36, 25, 30) 
    
    # Eye glow effect
    glPushMatrix()
    glColor4f(1.0, 0.0, 0.0, 0.3)
    glutSolidSphere(3.0, 8, 8)
    glPopMatrix()
    
   
    glColor3f(1.0, 0.0, 0.0)
    glutSolidSphere(1.8, 12, 12)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(36, 15, 30) 
    
    
    glPushMatrix()
    glColor4f(1.0, 0.0, 0.0, 0.3)
    glutSolidSphere(3.0, 8, 8)
    glPopMatrix()
    
    glPopMatrix()

    glPopMatrix()

def draw_all_wolves():
    for wolf in wolves:
        draw_wolf(wolf)

def spawn_wolves_if_needed():
    global wolf_spawned_this_night

    if not is_night:
        wolf_spawned_this_night = False
        return

    if wolf_spawned_this_night or len(wolves) > 0:
        return

      
    if random.random() < 0.03: 
        count = random.randint(1, max_wolves - len(wolves))
        for _ in range(count):
 
            ang = random.uniform(0, 2*math.pi)
            r = random.uniform(opening_radius + 40, middle_radius - 20)
            
            x = r * math.cos(ang)
            y = r * math.sin(ang)
            
            wolves.append({
                'pos': [x, y, 30],
                'rotation': random.uniform(0, 360),
                'state': 'hunt',
                'hits': 0
            })
        print(f" {count} wolves spawned from the forest!")

def nearest_sheep_pos(wolf):
    if not sheeps:
        return None
    wx, wy, _ = wolf['pos']
    best = None
    best_d2 = 1e18
    for s in sheeps:
        sx, sy, _ = s['pos']
        d2 = (sx-wx)*(sx-wx) + (sy-wy)*(sy-wy)
        if d2 < best_d2:
            best_d2 = d2
            best = (sx, sy)
    return best


def update_wolves(delta_time):
    global num_sheeps, heart_points
  
    if not is_night:
        wolves.clear()
        return

    spawn_wolves_if_needed()

    for wolf in list(wolves):
        tgt = nearest_sheep_pos(wolf)
        if not tgt:
            continue
        wx, wy, wz = wolf['pos']
        tx, ty = tgt
        dx, dy = tx - wx, ty - wy
        dist = math.hypot(dx, dy)
        if dist > 0:
            nx, ny = dx/dist, dy/dist
            wolf['pos'][0] += nx * wolf_speed
            wolf['pos'][1] += ny * wolf_speed
            wolf['rotation'] = math.degrees(math.atan2(ny, nx))

        if dist < WOLF_EAT_RADIUS and sheeps:
         
            kill_idx = None
            best_d2 = 1e18
            for i, s in enumerate(sheeps):
                sx, sy, _ = s['pos']
                d2 = (sx-wx)*(sx-wx) + (sy-wy)*(sy-wy)
                if d2 < best_d2:
                    best_d2 = d2
                    kill_idx = i
            if kill_idx is not None:
                sheeps.pop(kill_idx)
                num_sheeps = len(sheeps)
                heart_points -= 1 
                print(f"💔 A sheep was eaten! Heart Points: {heart_points}, Remaining sheep: {num_sheeps}")
        
      
                check_game_over()


def throw_stone():
 
    ang = math.radians(shepherd_rotation)
    fx, fy = math.cos(ang), math.sin(ang)
    spawn_x = shepherd_pos[0] + fx*25
    spawn_y = shepherd_pos[1] + fy*25
    stones.append({
        'pos': [spawn_x, spawn_y, shepherd_pos[2] + 35],
        'dir': [fx, fy],
        'ttl': stone_ttl
    })


def update_stones(delta_time):

    for st in list(stones):
        st['pos'][0] += st['dir'][0] * stone_speed
        st['pos'][1] += st['dir'][1] * stone_speed
        st['ttl'] -= delta_time
        if st['ttl'] <= 0:
            stones.remove(st)
            continue


        sx, sy, _ = st['pos']
        hit_any = False
        for w in list(wolves):
            wx, wy, _ = w['pos']
            if math.hypot(sx - wx, sy - wy) < WOLF_HIT_RADIUS:
                w['hits'] += 1
                hit_any = True
                print(f"Wolf hit ({w['hits']}/3)")
                if w['hits'] >= 3:
                    wolves.remove(w)
                    print("Wolf down!")
                break
        if hit_any:
            stones.remove(st)


def draw_stones():
 
    for st in stones:
        glPushMatrix()
        glTranslatef(st['pos'][0], st['pos'][1], st['pos'][2])
        glColor3f(0.6, 0.6, 0.6)
        glutSolidSphere(stone_radius, 10, 8)
        glPopMatrix()


def draw_wood_chopping_site():
   
    glPushMatrix()
    glTranslatef(wood_site_pos[0], wood_site_pos[1], wood_site_pos[2])

    glPushMatrix()
    glColor3f(0.55, 0.27, 0.07)
    glRotatef(180, 1, 0, 0) 

  
    gluCylinder(gluNewQuadric(), 20, 20, 60, 16, 4)
    

    glPushMatrix()
    glColor3f(0.35, 0.15, 0.05)
    gluCylinder(gluNewQuadric(), 20.5, 20.5, 60, 16, 4) 
    glPopMatrix()

  
    glPushMatrix()
    glColor3f(0.35, 0.15, 0.05) 
    glColor3f(0.75, 0.45, 0.25) 
    gluDisk(gluNewQuadric(), 0, 19.5, 16, 2)  
    gluDisk(gluNewQuadric(), 19.5, 20.5, 16, 2)
    glColor3f(0.55, 0.27, 0.07) 
    
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 0, 60)
    glColor3f(0.98, 0.94, 0.86) 
    gluDisk(gluNewQuadric(), 0, 19.5, 16, 2)
    glColor3f(0.35, 0.15, 0.05)
    gluDisk(gluNewQuadric(), 19.5, 20.5, 16, 2)
    
    glPopMatrix()

    glPopMatrix() 

    if current_wood_visible:
        glPushMatrix()
        glTranslatef(0, -10, 10)  
        glColor3f(0.75, 0.45, 0.25)  

        if current_wood_chops == 1:
            glTranslatef(-3, 0, 0) 
        elif current_wood_chops == 2:
            glTranslatef(-6, 0, 0)  
    
        glRotatef(-90, 1, 0, 0) 
   
        gluCylinder(gluNewQuadric(), 12, 12, 25, 12, 3)
        
 
        glPushMatrix()
        glColor3f(0.35, 0.15, 0.05) 
        gluCylinder(gluNewQuadric(), 12.5, 12.5, 25, 12, 3) 
        glPopMatrix()
    
     
        glPushMatrix()
        glColor3f(0.35, 0.15, 0.05)  
        gluDisk(gluNewQuadric(), 11.5, 12.5, 12, 2)
        glColor3f(0.75, 0.45, 0.25)
        gluDisk(gluNewQuadric(), 0, 11.5, 12, 2) 
        glPopMatrix()
    

        glPushMatrix()
        glTranslatef(0, 0, 25)
        glColor3f(0.35, 0.15, 0.05) 
        gluDisk(gluNewQuadric(), 11.5, 12.5, 12, 2) 
        glColor3f(0.75, 0.45, 0.25)  
        gluDisk(gluNewQuadric(), 0, 11.5, 12, 2)  
        glPopMatrix()
    
        glPopMatrix()  

    if is_night and wood_count > 0:
        glPushMatrix()
        glTranslatef(wood_site_pos[0] + 80, wood_site_pos[1], wood_site_pos[2] - 20)
        glColor4f(1.0, 1.0, 0.0, 0.5) 
        glutSolidSphere(30, 8, 6)
        glPopMatrix()

    glPopMatrix()  

    pile_offsets = [-80, 0, 80]
    
    for pile_offset in pile_offsets:
        glPushMatrix()
        glTranslatef(wood_site_pos[0] + 80 , pile_offset+ wood_site_pos[1], wood_site_pos[2] - 30)
        
        wood_radius = 10
        wood_length = 30

        positions = [
            (0, 0, wood_radius), 
            (wood_radius * 1.8, 0, wood_radius), 
            (-wood_radius * 1.8, 0, wood_radius),
            (wood_radius * 0.9, 0, wood_radius * 2.2),
            (-wood_radius * 0.9, 0, wood_radius * 2.2),
            (0, 0, wood_radius * 3.4)
        ]

        wood_shades = [
            (0.45, 0.25, 0.10), (0.45, 0.25, 0.10), (0.45, 0.25, 0.10),
            (0.55, 0.35, 0.15), (0.55, 0.35, 0.15), (0.65, 0.45, 0.20)
        ]

        for i, (pos_x, pos_y, pos_z) in enumerate(positions):
            glPushMatrix()
            glTranslatef(pos_x, pos_y, pos_z)
            glColor3f(*wood_shades[i])
            glRotatef(90, 1, 0, 0)  
            

            gluCylinder(gluNewQuadric(), wood_radius, wood_radius, wood_length, 12, 3)
    
            glPushMatrix()
            glColor3f(0.35, 0.15, 0.05)
            gluCylinder(gluNewQuadric(), wood_radius + 0.5, wood_radius + 0.5, wood_length, 12, 3)
            glPopMatrix()
       
            glPushMatrix()
            glColor3f(0.35, 0.15, 0.05)
            gluDisk(gluNewQuadric(), wood_radius - 1, wood_radius + 0.5, 12, 2)
            glColor3f(*wood_shades[i])
            gluDisk(gluNewQuadric(), 0, wood_radius - 1, 12, 2)
            glPopMatrix()
       
            glPushMatrix()
            glTranslatef(0, 0, wood_length)
            glColor3f(0.35, 0.15, 0.05)
            gluDisk(gluNewQuadric(), wood_radius - 1, wood_radius + 0.5, 12, 2)
            glColor3f(*wood_shades[i])
            gluDisk(gluNewQuadric(), 0, wood_radius - 1, 12, 2)
            glPopMatrix()
            
            glPopMatrix() 

        glPopMatrix() 

def draw_axe_in_hand():
    if axe_attached:
        glPushMatrix()
        glTranslatef(shepherd_pos[0], shepherd_pos[1], shepherd_pos[2] + 40) 
        glRotatef(shepherd_rotation + 45, 0, 0, 1)  
        

        glPushMatrix()
        glColor3f(0.55, 0.27, 0.07) 
        glTranslatef(20, 0, 0)
        glRotatef(90, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 2, 2, 40, 8, 2)
        glPopMatrix()
        
  
        glPushMatrix()
        glColor3f(0.7, 0.7, 0.7) 
        glTranslatef(55, 0, -5)
        glScalef(12, 2, 10)
        glutSolidCube(1)
        glPopMatrix()
        glPopMatrix()


def check_wood_site_interaction():
    global axe_attached, wood_respawn_timer, current_wood_visible
    

    distance = math.sqrt((shepherd_pos[0] - wood_site_pos[0])**2 + 
                         (shepherd_pos[1] - wood_site_pos[1])**2)
    
  
    distance = math.sqrt((shepherd_pos[0] - wood_site_pos[0])**2 + 
                         (shepherd_pos[1] - wood_site_pos[1])**2)
    

    if distance < wood_site_radius and not is_night:
        axe_attached = True
    else:
        axe_attached = False
    

    if not is_night and wood_respawn_timer > 0:
        wood_respawn_timer -= 1
        if wood_respawn_timer == 0 and wood_count < max_wood_capacity:
            current_wood_visible = True

def handle_wood_chopping():
    global current_wood_chops, wood_respawn_timer, current_wood_visible, wood_count, is_night
    
   
    distance = math.sqrt((shepherd_pos[0] - wood_site_pos[0])**2 + 
                         (shepherd_pos[1] - wood_site_pos[1])**2)
    
    if distance < wood_site_radius and axe_attached and current_wood_visible and wood_count < max_wood_capacity:
        current_wood_chops += 1
        print(f"Chop {current_wood_chops}/{max_chops}")
        
        if current_wood_chops >= max_chops:
            wood_count += 1
            current_wood_visible = False
            wood_respawn_timer = 100
            current_wood_chops = 0
            print(f"Wood chopped! Total: {wood_count}/{max_wood_capacity}")

          
            if wood_count >=  max_wood_capacity:
                is_night = True
                current_wood_visible = False  
                current_wood_chops = 0
                wood_respawn_timer = 100     
                print("NIGHT HAS FALLEN! Wolves become active!")

def draw_bonfire():
    
    if not is_night:
        return
    
    glPushMatrix()
    glTranslatef(fire_pos[0], fire_pos[1], fire_pos[2])


    glPushMatrix()
    glColor3f(0.35, 0.17, 0.04)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 6, 40, 8, 3)
    glPopMatrix()
    
   
    if fire_stage == 1:  
        glPushMatrix()
        glColor4f(1.0, 0.5, 0.0, 0.8)
        glTranslatef(0, 20, 25)
        glutSolidSphere(25, 16, 12)

     
        glColor4f(1.0, 0.8, 0.0, 0.6) 
        glTranslatef(0, 0, 15)
        glutSolidSphere(20, 12, 10)
        glPopMatrix()
        
    elif fire_stage == 2:  
        glPushMatrix()
        glColor4f(1.0, 0.4, 0.0, 0.6) 
        glTranslatef(0, 20, 20)
        glutSolidSphere(15, 12, 10)
        
      
        glColor4f(1.0, 0.6, 0.0, 0.5)  
        glTranslatef(0, 0, 10)
        glutSolidSphere(12, 10, 8)
        glPopMatrix()
        
    elif fire_stage == 3: 
       
        if int(time.time() * 2) % 2 == 0:
            glPushMatrix()
            glColor4f(1.0, 0.3, 0.0, 0.4) 
            glTranslatef(0, 20, 15)
            glutSolidSphere(10, 10, 8)
            glPopMatrix()
    
    
    glPopMatrix()

def draw_wood_in_hand():
    if carrying_wood:
        glPushMatrix()
        glTranslatef(shepherd_pos[0], shepherd_pos[1], shepherd_pos[2]+40 )
        glRotatef(shepherd_rotation + 45, 0, 0, 1)
        
       
        glColor3f(0.35, 0.17, 0.04) 
        glRotatef(90, 0, 1, 0)
        glTranslatef(20, 0, 10)
        gluCylinder(gluNewQuadric(), 4, 4, 20, 8, 3)
        
        
        gluDisk(gluNewQuadric(), 0, 4, 8, 2)
        glPushMatrix()
        glTranslatef(0, 0, 20)
        gluDisk(gluNewQuadric(), 0, 4, 8, 2)
        glPopMatrix()
        
        glPopMatrix()


def handle_wood_collection():
    global carrying_wood, wood_count
    
    if not is_night or wood_count <= 0 or carrying_wood:
        return
    

    wood_pile_pos = [wood_site_pos[0] + 80, wood_site_pos[1], wood_site_pos[2] - 30]
    distance = math.sqrt((shepherd_pos[0] - wood_pile_pos[0])**2 + 
                         (shepherd_pos[1] - wood_pile_pos[1])**2)
 
    if distance < 50:
        carrying_wood = True
        wood_count -= 1
        print(f"Collected 1 wood from pile! Carrying: {carrying_wood}, Remaining: {wood_count}")

def handle_wood_throw():
    global carrying_wood, fire_stage, fire_timer, wood_count, fire_lit_count, final_fire_active
    
    if not carrying_wood or not is_night:
        return
    

    distance_to_fire = math.sqrt((shepherd_pos[0] - fire_pos[0])**2 + 
                                (shepherd_pos[1] - fire_pos[1])**2)
    
    if distance_to_fire < 80: 
        carrying_wood = False
        
   
        fire_lit_count += 1
        print(f"🔥 Fire lit! ({fire_lit_count}/{fires_needed_for_morning})")
        
      
        if fire_stage in [2, 3]:
            fire_stage = 1  
            fire_timer = fire_stage_durations[1]
            print("Wood added to fire! Fire restored to stage 1")
        
     
        elif fire_stage == 0:
            fire_stage = 1 
            fire_timer = fire_stage_durations[1]
            print("Wood added to fire! Fire restarted from out")

   
        if fire_lit_count >= fires_needed_for_morning:
            final_fire_active = True 
            print("Final fire lit! Morning will come after this fire burns out.")
    
            fire_stage = 1
            fire_timer = 5 
            
    
    if fire_lit_count >= fires_needed_for_morning and fire_stage == 0 and not is_morning:
        start_morning_transition()
        
def start_morning_transition():
    global is_night, is_morning, morning_transition, wood_count, fire_stage, final_fire_active
    
    is_morning = True
    morning_transition = 0
    final_fire_active = False  
    
    # Reset fire
    fire_stage = 0
    fire_timer = 0
    
    print("Morning is coming...")

def complete_morning_transition():
    global is_night, is_morning, morning_transition, night_transition, fire_lit_count, final_fire_active
    
    is_night = False
    is_morning = False
    night_transition = 0
    morning_transition = 0
    fire_lit_count = 0 
    final_fire_active = False  
    
   
    wood_count = 0
    current_wood_visible = True 
    current_wood_chops = 0       
    wood_respawn_timer = 0       
    
    print(" Morning has arrived! You can chop wood again.")

def check_game_over():
    global game_over, heart_points, num_sheeps
    
    
    if heart_points <= 0 or num_sheeps <= 0:
        game_over = True
        print("GAME OVER! Press 'R' to restart")
        return True
    return False

def reset_game():
    global game_over, heart_points, num_sheeps, shepherd_pos, shepherd_rotation
    global is_night, night_transition, wood_count, wolves, stones, sheeps
    global current_wood_visible, current_wood_chops, fire_stage, fire_timer
    global carrying_wood, axe_attached, fire_lit_count, final_fire_active

    game_over = False
    heart_points = 3
    num_sheeps = 3
    shepherd_pos = [0, 0, 30]
    shepherd_rotation = 0
    is_night = False
    night_transition = 0
    wood_count = 0
    current_wood_visible = True
    current_wood_chops = 0
    fire_stage = 0
    fire_timer = 0
    carrying_wood = False
    axe_attached = False
    fire_lit_count = 0
    final_fire_active = False

    camera_angle = 0
    camera_height = 400

    wolves.clear()
    stones.clear()

    sheeps.clear()
    create_sheep()
    
    print(" Game restarted! Good luck!")

def keyboardListener(key, x, y):
    global  shepherd_rotation, carrying_wood, game_over


    
    key = key.lower()

    if key == b'w':
        shepherd_pos[0] += math.cos(math.radians(shepherd_rotation)) * shepherd_speed
        shepherd_pos[1] += math.sin(math.radians(shepherd_rotation)) * shepherd_speed
    elif key == b's':
        shepherd_pos[0] -= math.cos(math.radians(shepherd_rotation)) * shepherd_speed
        shepherd_pos[1] -= math.sin(math.radians(shepherd_rotation)) * shepherd_speed

    elif key == b'a':
        shepherd_rotation = (shepherd_rotation + shepherd_speed) % 360
    elif key == b'd':
        shepherd_rotation = (shepherd_rotation - shepherd_speed) % 360
    elif key == b'v':  
        whistle()
    elif key == b'p': 
        rescue_sheep()
    
    
    if is_night:
        if key == b'c':  
            handle_wood_collection()
        elif key == b't': 
            handle_wood_throw()
    else:
        if key == b'c': 
            handle_wood_chopping()
    if game_over and key == b'r':
        reset_game()
        return
    
    if game_over:
        return  
   
    if key == b'v':  
        
        pass

def specialKeyListener(key, x, y):
    global camera_angle, camera_height
    if key == GLUT_KEY_LEFT:
        camera_angle -= 5
    elif key == GLUT_KEY_RIGHT:
        camera_angle += 5
    elif key == GLUT_KEY_UP:
        camera_height += 20
    elif key == GLUT_KEY_DOWN:
        camera_height = max(50, camera_height - 20)

def mouseListener(button, state, x, y):
    global camera_mode
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        camera_mode = "first_person" if camera_mode == "third_person" else "third_person"

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if is_night: 
            throw_stone()
            print("Threw a stone!")

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if camera_mode == "third_person":
        cam_x = camera_distance * math.cos(math.radians(camera_angle))
        cam_y = camera_distance * math.sin(math.radians(camera_angle))
        cam_z = camera_height
        
        
        gluLookAt(cam_x, cam_y, cam_z, 
                  0, 0, 30, 
                  0, 0, 1)
    else:
        
        head_height = 60 
        
        
        look_ahead = 10
        look_x = shepherd_pos[0] + math.cos(math.radians(shepherd_rotation)) * look_ahead
        look_y = shepherd_pos[1] + math.sin(math.radians(shepherd_rotation)) * look_ahead
        
        gluLookAt(shepherd_pos[0],                 
                  shepherd_pos[1],                  
                  shepherd_pos[2] + head_height,    
                  look_x,                          
                  look_y,                          
                  shepherd_pos[2] + head_height,    
                  0, 0, 1)

def idle():
    global last_time, night_transition, fire_timer, fire_stage, wood_count, carrying_wood
    global is_night, is_morning, morning_transition 

    current_time = time.time()
    delta_time = current_time - last_time
    last_time = current_time

    
    if is_night:
        if night_transition < 1.0:
            night_transition += night_transition_speed
            if night_transition > 1.0:
                night_transition = 1.0
    else:
    
        if night_transition > 0:
            night_transition -= night_transition_speed
            if night_transition < 0:
                night_transition = 0

   
    if is_morning and morning_transition < 1.0:
        morning_transition += morning_transition_speed
        if morning_transition >= 1.0:
            complete_morning_transition()

     
    if is_night:
        if fire_stage > 0: 
            fire_timer -= 1
            
            
            if final_fire_active:
                fire_timer -= 2 
                
            if fire_timer <= 0:
                if fire_stage < 3: 
                    fire_stage += 1
                    fire_timer = fire_stage_durations[fire_stage]
                    print(f"Fire weakened to stage {fire_stage}")
                    
                   
                    if final_fire_active:
                        if fire_stage == 2:
                            print(" Final fire is getting smaller...")
                        elif fire_stage == 3:
                            print(" Final fire is blinking fast!")
                            
                            fire_timer = fire_stage_durations[fire_stage] // 2
                            
                else: 
                    fire_stage = 0 
                    fire_timer = 0
                    print("Fire went out completely!")
                    
                   
                    if final_fire_active and not is_morning:
                        print(" Final fire has burned out! Morning is coming...")
                        start_morning_transition()
    
    check_wood_site_interaction()
    update_sheep_movement(delta_time)
    update_wolves(delta_time)
    update_stones(delta_time)

    
    
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
  
    if game_over:

        glViewport(0, 0, 1000, 800)
        setupCamera()
        draw_environment()
        draw_shapes()
        draw_shepherd()
        draw_all_wolves()
        draw_all_sheeps()
        draw_wood_chopping_site()
        if axe_attached:
            draw_axe_in_hand()
        draw_stones()
        
      
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
    
        glColor3f(1.0, 0.0, 0.0)  # Bright red text
        draw_text(350, 450, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)
        
      
        glColor3f(1.0, 1.0, 1.0)
        draw_text(350, 400, f"Heart Points: {heart_points}", GLUT_BITMAP_HELVETICA_18)
        draw_text(350, 370, f"Sheep Remaining: {num_sheeps}", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 300, "Press 'R' to Restart", GLUT_BITMAP_HELVETICA_18)
      
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
        glutSwapBuffers()
        return
    
  
    glViewport(0, 0, 1000, 800)
    setupCamera()
    draw_environment()
    draw_shapes()
    draw_shepherd()
    draw_all_wolves()
    draw_all_sheeps()
    draw_wood_chopping_site()
    if axe_attached:
        draw_axe_in_hand()
    
    draw_stones()
    
    draw_text(10, 710, f"Hearts: {heart_points}/3", GLUT_BITMAP_HELVETICA_18)

    if not can_chop_wood:
        draw_text(10, 590, "MAX CAPACITY - Go to fire!")


    if is_night:
        draw_text(10, 500, "NIGHT TIME - Be careful!", GLUT_BITMAP_HELVETICA_12)
        # Show fire lit progress
        draw_text(10, 520, f"Fires lit: {fire_lit_count}/{fires_needed_for_morning}", GLUT_BITMAP_HELVETICA_12)
 
        if final_fire_active:
            glColor3f(1.0, 0.8, 0.0)  # Gold color for final fire
            draw_text(400, 750, "FINAL FIRE! Morning coming soon!", GLUT_BITMAP_HELVETICA_18)
            glColor3f(1.0, 1.0, 1.0)  # Reset to white
    elif night_transition > 0:
        draw_text(10, 500, "Dusk is falling...", GLUT_BITMAP_HELVETICA_12)

  
    if is_night and not is_morning:
        draw_bonfire()
 
    if carrying_wood:
        draw_wood_in_hand()

    if is_night and not is_morning:
        fire_status = ["OUT - Needs wood", "Big", "Small", "Blinking", "OUT"]
        draw_text(10, 480, f"Fire: {fire_status[fire_stage]}", GLUT_BITMAP_HELVETICA_12)
        if fire_stage == 0:
            draw_text(10, 460, "Fire is out! Add wood with T", GLUT_BITMAP_HELVETICA_12)
        elif carrying_wood:
            draw_text(10, 460, "Carrying wood! Press T near fire", GLUT_BITMAP_HELVETICA_12)
    
    # Whistle 
    now = time.time()
    cooldown_remaining = whistle_cooldown - (now - last_whistle_time)
    if cooldown_remaining > 0:
        draw_text(10, 440, f"Whistle: {cooldown_remaining:.1f}s cooldown", GLUT_BITMAP_HELVETICA_12)
    else:
        draw_text(10, 440, "Whistle: Ready (V)", GLUT_BITMAP_HELVETICA_12)
    
    if stuck_sheep:
        time_remaining = stuck_countdown - stuck_sheep['stuck_timer']
        if time_remaining > 0:
           
            glColor3f(1.0, 0.0, 0.0)  # Red color
            draw_text(400, 700, "SHEEP STUCK, HELP!", GLUT_BITMAP_HELVETICA_18)
            draw_text(400, 680, f"Time: {time_remaining:.1f}s", GLUT_BITMAP_HELVETICA_18)
            draw_text(400, 660, "Press P to rescue", GLUT_BITMAP_HELVETICA_12)
            # Reset color to white for other text
            glColor3f(1.0, 1.0, 1.0)
        else:
  
            draw_text(400, 700, "TOO LATE! SHEEP LOST!", GLUT_BITMAP_HELVETICA_18)
            glColor3f(1.0, 1.0, 1.0)  # Reset color

    draw_text(10, 730, f"Wood :{wood_count}/{max_wood_capacity}")
    draw_text(10, 690, f"Sheeps: {num_sheeps}")

    
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Protect the Sheep - Forest Environment")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()