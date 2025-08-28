from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time
last_time = time.time()


# Camera-related variables
camera_angle = 0  # Orbit angle around the center
camera_height = 400  # Height of camera
camera_distance = 500  # Fixed distance from center
camera_mode = "third_person"  # Can be "first_person" or "third_person"
fovY = 120  # Field of view
GRID_LENGTH = 900  # Length of grid lines

# Environment variables
trees = []
opening_radius = 500  # Inner zone - no trees
middle_radius = 680   # Middle zone - sparse trees
outer_radius = 900    # Outer zone - dense forest
num_trees = 300      # Total number of trees


# Night time properties
is_night = False
night_transition = 0  # Smooth transition value (0-1)
stars = []

# Shepherd properties
shepherd_pos = [0, 0, 30]  # Starting position (x, y, z)
shepherd_rotation = 0      # Facing direction in degrees
shepherd_speed = 10         # Movement speed

# Sheep properties
sheeps = []
num_sheeps = 5
sheep_speed = 1
sheep_direction_change_time = 0.2  # Time between direction changes (seconds)
sheep_wander_distance = opening_radius-50 


# Wood chopping site variables
wood_site_pos = [370, 20, 30]  # Position of wood chopping area
wood_site_radius = 60        
axe_attached = False         
current_wood_chops = 0       
max_chops = 3                
wood_respawn_timer = 0       
current_wood_visible = True

wood_count = 0
max_wood_capacity = 2
can_chop_wood = True

# Wolf properties
wolves = []




# Create stars
def create_stars():
    global stars
    stars = []
    for _ in range(800):  # 200 stars
        # Random position on sky sphere
        angle1 = random.uniform(0, 2 * math.pi)
        angle2 = random.uniform(0, math.pi)
        distance = 1900  # Slightly inside sky sphere
        
        x = distance * math.sin(angle2) * math.cos(angle1)
        y = distance * math.sin(angle2) * math.sin(angle1) 
        z = distance * math.cos(angle2) - 1000  # Position in sky
        
        # Random star size and brightness
        size = random.uniform(0.5, 2.0)
        brightness = random.uniform(0.7, 1.0)
        
        stars.append((x, y, z, size, brightness))

create_stars()

# Generate tree positions in three zones
def generate_trees():
    global trees
    trees = []
    
    # Zone 2: Middle ring (sparse, short trees)
    for _ in range(num_trees // 3):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(opening_radius + 10, middle_radius - 20)
        
        x = distance * math.cos(angle)
        y = distance * math.sin(angle)
        z = 0
        
        # Shorter trees for middle zone
        height = random.uniform(120, 120)
        trunk_width = random.uniform(8, 12)
        
        # Random green shade
        green_shade = random.uniform(0.4, 0.7)
        foliage_color = (0.0, green_shade, 0.0)
        
        trees.append(("deciduous", x, y, z, height, trunk_width, foliage_color))
    
    # Zone 3: Outer ring (dense forest, tall trees - mix of deciduous and pine)
    for _ in range(6 * num_trees // 3):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(middle_radius + 10, outer_radius - 20)
        
        
        x = distance * math.cos(angle)
        y = distance * math.sin(angle)
        z = 0
        
        # Taller trees for outer zone
        height = random.uniform(180, 280)
        trunk_width = random.uniform(12, 20)
        
        # Random green shade
        green_shade = random.uniform(0.3, 0.8)
        foliage_color = (0.0, green_shade, 0.0)
        
        #tree generation type
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
    # Blend between day and night colors
    if is_night:
        sky_color = (0.05, 0.1, 0.2)  # Dark blue night sky
        fog_color = (0.02, 0.06, 0.12)  # Dark teal fog
    else:
        # Smooth transition between day and night
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
    
    # Draw sky sphere
    glPushMatrix()
    glColor3f(*sky_color)
    glTranslatef(0, 0, -1000)
    glutSolidSphere(2000, 32, 32)
    glPopMatrix()
    
    # Draw stars at night
    if is_night or night_transition > 0:
        glPushMatrix()
        for x, y, z, size, brightness in stars:
            glPushMatrix()
            glTranslatef(x, y, z)
            # Fade stars in during transition
            star_alpha = brightness * min(night_transition, 1.0)
            glColor4f(1.0, 1.0, 1.0, star_alpha)
            glutSolidSphere(size, 6, 6)
            glPopMatrix()
        glPopMatrix()

def draw_ground():
    # Blend between day and night colors
    if is_night:
        opening_color = (0.0, 0.35, 0.0)   
        middle_color = (0.0, 0.3, 0.0)  
        forest_color = (0.0, 0.15, 0.0)    
    else:
        # Smooth transition between day and night
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
    
    # Draw the green opening (Zone 1)
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
    
    # Draw middle zone (Zone 2)
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
    
    # Draw outer forest zone (Zone 3)
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
    
    # Adjust colors for night time
    if is_night:
        trunk_color = (0.35, 0.17, 0.04)  # Darker brown trunk at night
        # Darker foliage at night
        dark_foliage = (
            foliage_color[0] * 0.5,
            foliage_color[1] * 0.5, 
            foliage_color[2] * 0.5
        )
    else:
        trunk_color = (0.55, 0.27, 0.07)  # Normal brown trunk
        dark_foliage = foliage_color  # Normal foliage
    
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
    
    # Adjust colors for night time
    if is_night:
        trunk_color = (0.3, 0.15, 0.03)  # Darker brown trunk
        # Darker foliage at night
        dark_foliage = (
            foliage_color[0] * 0.6,
            foliage_color[1] * 0.6,
            foliage_color[2] * 0.6
        )
    else:
        trunk_color = (0.4, 0.2, 0.05)  # Normal brown trunk
        dark_foliage = foliage_color  # Normal foliage
    
    # Draw trunk
    glColor3f(*trunk_color)
    glPushMatrix()
    glRotatef(0, 1, 0, 90)
    glutSolidCylinder(trunk_width, height * 0.4, 12, 3)
    glPopMatrix()
    
    # Draw conical pine foliage
    glPushMatrix()
    glTranslatef(0, 0, height * 0.3)
    
    # Bottom cone (largest)
    glColor3f(dark_foliage[0] * 0.7, dark_foliage[1] * 0.7, dark_foliage[2] * 0.7)
    glPushMatrix()
    glRotatef(0, 1, 0, 90)
    glutSolidCone(height * 0.35, height * 0.4, 12, 3)
    glPopMatrix()
    
    # Middle cone
    glTranslatef(0, 0, height * 0.25)
    glColor3f(dark_foliage[0] * 0.85, dark_foliage[1] * 0.85, dark_foliage[2] * 0.85)
    glPushMatrix()
    glRotatef(0, 1, 0, 90)
    glutSolidCone(height * 0.25, height * 0.3, 10, 3)
    glPopMatrix()
    
    # Top cone (smallest, pointy)
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
    
    # Adjust colors for night time
    if is_night:
        trunk_color = (0.3, 0.15, 0.03)  # Darker brown trunk
        # Much darker foliage for spike pines at night
        dark_foliage = (
            foliage_color[0] * 0.4,
            foliage_color[1] * 0.4,
            foliage_color[2] * 0.4
        )
    else:
        trunk_color = (0.4, 0.2, 0.05)  # Normal brown trunk
        dark_foliage = (foliage_color[0] * 0.5, foliage_color[1] * 0.5, foliage_color[2] * 0.5)
    
    # Draw trunk
    glColor3f(*trunk_color)
    glPushMatrix()
    glRotatef(0, 1, 0, 90)
    glutSolidCylinder(trunk_width * 0.4, height * 0.4, 10, 20)
    glPopMatrix()
    
    # Draw single conical spike foliage
    glPushMatrix()
    glTranslatef(0, 0, height * 0.4)
    
    # Dark foliage color
    glColor3f(*dark_foliage)
    
    # Single tall, narrow cone
    glPushMatrix()
    glRotatef(0, 1, 0, 9)
    glutSolidCone(height * 0.1, height * 0.8, 10, 3)
    glPopMatrix()
    
    glPopMatrix()
    glPopMatrix()

def draw_environment():
    draw_sky()
    draw_ground()
    
    # Draw trees
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
    glRotatef(shepherd_rotation, 0, 0, 1)  # Use shepherd_rotation instead of gun_angle

    # Scale everything down to make him smaller (0.8 scale)
    glScalef(0.8, 0.8, 0.8)

    # body - light brown shirt
    glPushMatrix()
    glColor3f(0.6, 0.4, 0.2)  # Light brown shirt
    glTranslatef(0, 0, 16)
    glScalef(20, 28, 40)
    glutSolidCube(1)
    glPopMatrix()

    # Black buttons on shirt
    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)  # Black buttons
    glTranslatef(0, 0, 25)  # Center of chest
    
    # Button 1 (top)
    glPushMatrix()
    glTranslatef(10, -1, 5)  # Center front of shirt
    glutSolidSphere(1.5, 8, 8)  # Small black sphere button
    glPopMatrix()
    # Button 2 (middle)
    glPushMatrix()
    glTranslatef(10, -1, 0)  # Middle front
    glutSolidSphere(1.5, 8, 8)
    glPopMatrix()
    # Button 3 (bottom)
    glPushMatrix()
    glTranslatef(10, -1, -5)  # Bottom front
    glutSolidSphere(1.5, 8, 8)
    glPopMatrix()
    glPopMatrix()

    # head (smaller, only in third person)
    if not first_person and camera_mode == "third_person":
        glPushMatrix()
        glColor3f(1.0, 0.8, 0.6)  # Skin tone instead of black
        glTranslatef(0, 0, 48)    # Adjusted height
        gluSphere(gluNewQuadric(), 12, 16, 16)  # Smaller head
        glPopMatrix()

        # Dark brown round cap on head
        glPushMatrix()
        glColor3f(0.3, 0.2, 0.1)  # Dark brown cap
        glTranslatef(0, 0, 60)  # On top of head
        glRotatef(1, 0, 90, 0)  # Rotate to sit horizontally
        glutSolidCylinder(10, 4, 16, 3)  # Flat cylindrical cap
        glPopMatrix()

    # arms (smaller)
     # Left arm with light brown base segment
    glPushMatrix()
    glTranslatef(2, 16, 35)   # Adjusted position
    glRotatef(180, 1, 0, 0)

# Base segment (light brown sleeve)
    glPushMatrix()
    glColor3f(0.6, 0.4, 0.2)  # Light brown sleeve
    glutSolidCylinder(5, 8, 12, 3)  # First 8 units - sleeve
    glPopMatrix()

# Forearm (skin tone)
    glTranslatef(0, 0, 8)  # Move to end of sleeve
    glColor3f(1.0, 0.8, 0.6)  # Skin tone
    glutSolidCylinder(5, 24, 12, 3)  # Remaining 24 units - forearm

    glPopMatrix()

# Right arm with light brown base segment  
    glPushMatrix()
    glTranslatef(2, -16, 35)  # Adjusted position
    glRotatef(180, 1, 0, 0)

# Base segment (light brown sleeve)
    glPushMatrix()
    glColor3f(0.6, 0.4, 0.2)  # Light brown sleeve
    glutSolidCylinder(5, 8, 12, 3)  # First 8 units - sleeve
    glPopMatrix()

# Forearm (skin tone)
    glTranslatef(0, 0, 8)  # Move to end of sleeve
    glColor3f(1.0, 0.8, 0.6)  # Skin tone
    glutSolidCylinder(5, 24, 12, 3)  # Remaining 24 units - forearm

    glPopMatrix()

    # legs 
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
    
    # Calculate movement based on rotation
    angle_rad = math.radians(shepherd_rotation)
    move_x = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
    move_y = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
    

    
    # Keep within bounds (opening radius)
    max_distance = opening_radius - 50  # Leave some margin
    current_distance = math.sqrt(shepherd_pos[0]**2 + shepherd_pos[1]**2)
    if current_distance > max_distance:
        scale = max_distance / current_distance
        shepherd_pos[0] *= scale
        shepherd_pos[1] *= scale
    
   

def create_sheep():
    # Create initial sheep positions around the shepherd
    for i in range(num_sheeps):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(50, 100)  # Start close to shepherd
        x = distance * math.cos(angle)
        y = distance * math.sin(angle)
        z = 30  # On ground
        
        # Random slight color variations for wool
        wool_colors = [
            (0.95, 0.95, 0.95),  # White
            (0.85, 0.85, 0.85),  # Light gray
            (0.98, 0.94, 0.86)   # Cream
        ]
        wool_color = random.choice(wool_colors)
        
        sheeps.append({
            'pos': [x, y, z],
            'wool_color': wool_color,
            'rotation': random.uniform(0, 360),
            'stuck': False,
            'stuck_timer': 0
        })

# Initialize sheep
create_sheep()

def draw_sheep(sheep):
    glPushMatrix()
    glTranslatef(sheep['pos'][0], sheep['pos'][1], sheep['pos'][2])
    glRotatef(sheep['rotation'], 0, 0, 1)  # Random rotation for variety
    
    # Main wooly body (large sphere)
    glPushMatrix()
    glTranslatef(0, 0, 10)  # Center of body
    glColor3f(*sheep['wool_color'])
    glutSolidSphere(20, 16, 16)  # Main body sphere
    glPopMatrix()
    
    # Back wool bump (smaller sphere)
    glPushMatrix()
    glTranslatef(-8, 0, 15)  # Slightly back and up
    glColor3f(*sheep['wool_color'])
    glutSolidSphere(15, 12, 12)  # Back wool bump
    glPopMatrix()
    
    # Head (black sphere)
    glPushMatrix()
    glTranslatef(18, 0, 15)  # In front of body
    glColor3f(0.1, 0.1, 0.1)  # Black head
    glutSolidSphere(10, 12, 12)  # Head sphere
    glPopMatrix()
    
    # Legs (black cylinders)
    leg_positions = [
        (-12, -8, 0),   # Front left
        (-12, 8, 0),    # Front right
        (8, -8, 0),     # Back left
        (8, 8, 0)       # Back right
    ]
    
    for leg_x, leg_y, leg_z in leg_positions:
        glPushMatrix()
        glTranslatef(leg_x, leg_y, leg_z)
        glColor3f(0.1, 0.1, 0.1)  # Black legs
        glRotatef(180, 1, 0, 0)  # Rotate to stand upright
        glutSolidCylinder(3, 25, 8, 3)  # Thin black cylinders for legs
        glPopMatrix()
    
    glPopMatrix()

def draw_all_sheeps():
    for sheep in sheeps:
        draw_sheep(sheep)

def update_sheep_movement(delta_time):
    for sheep in sheeps:
        if sheep['stuck']:
            continue  # Skip movement if sheep is stuck
            
        # Update movement timer
        if 'move_timer' not in sheep:
            sheep['move_timer'] = 0
            sheep['current_direction'] = random.uniform(0, 2 * math.pi)
            sheep['move_duration'] = random.uniform(1.0, 3.0)
        
        sheep['move_timer'] += delta_time
        
        # Change direction when timer expires
        if sheep['move_timer'] >= sheep['move_duration']:
            sheep['move_timer'] = 0
            sheep['current_direction'] = random.uniform(0, 2 * math.pi)
            sheep['move_duration'] = random.uniform(1.0, 3.0)
        
        # Move sheep in current direction
        move_x = math.cos(sheep['current_direction']) * sheep_speed
        move_y = math.sin(sheep['current_direction']) * sheep_speed
        
        sheep['pos'][0] += move_x
        sheep['pos'][1] += move_y
        
        # Keep sheep within the opening boundaries
        distance_from_center = math.sqrt(sheep['pos'][0]**2 + sheep['pos'][1]**2)
        if distance_from_center > opening_radius - 40:  # Leave margin
            # Bounce back from edge
            angle_to_center = math.atan2(sheep['pos'][1], sheep['pos'][0])
            sheep['current_direction'] = angle_to_center + math.pi  # Turn around
            sheep['pos'][0] = (opening_radius - 50) * math.cos(angle_to_center)
            sheep['pos'][1] = (opening_radius - 50) * math.sin(angle_to_center)

def draw_wolf(wolf):
    glPushMatrix()
    glTranslatef(wolf['pos'][0], wolf['pos'][1], wolf['pos'][2])
    glRotatef(wolf['rotation'], 0, 0, 1)
    
    # Front body/chest (big solid cylinder)
    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)  # Gray
    glTranslatef(8, 0, 15)     # Position toward front
    glRotatef(-90, 1, 0, 0)    # Rotate to stand upright

# Main cylinder
    gluCylinder(gluNewQuadric(), 15, 12, 25, 16, 8)

# Front cap
    gluDisk(gluNewQuadric(), 0, 15, 16, 2)

# Back cap
    glPushMatrix()
    glTranslatef(0, 0, 25)
    gluDisk(gluNewQuadric(), 0, 12, 16, 2)
    glPopMatrix()
    glPopMatrix()

# Back body/hindquarters (thinner solid cylinder)
    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)  # Slightly darker gray
    glTranslatef(-8, 0, 10)      # Position toward back
    glRotatef(-90, 1, 0, 0)      # Rotate to stand upright

# Main cylinder
    gluCylinder(gluNewQuadric(), 10, 8, 22, 14, 6)

# Front cap
    gluDisk(gluNewQuadric(), 0, 10, 14, 2)

# Back cap
    glPushMatrix()
    glTranslatef(0, 0, 22)
    gluDisk(gluNewQuadric(), 0, 8, 14, 2)
    glPopMatrix()
    glPopMatrix()


# Wolf head (solid sphere)
    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)  # Darker gray
    glTranslatef(28, 20, 30)   

# Main head sphere
    glutSolidSphere(12, 16, 10)

# Wolf snout (solid cylinder)
    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)  # Lighter gray
    glTranslatef(10, 0, 0)     # Extend from head
    glRotatef(90, 0, 1, 0)     # Rotate to point forward

# FIRST: Draw the cylinder
    gluCylinder(gluNewQuadric(), 5, 3, 10, 10, 4)

# SECOND: Draw the front cap (nose) - at current position
    glColor3f(0.1, 0.1, 0.1)
    gluDisk(gluNewQuadric(), 0, 5, 5, 2)  # Front cap (radius 5)

# THIRD: Draw the back cap - move to end of cylinder first
    glPushMatrix()
    glTranslatef(0, 0, 10)     # Move to end of cylinder
    gluDisk(gluNewQuadric(), 0, 3, 10, 2)  # Back cap (radius 3)
    glPopMatrix()

    glPopMatrix()
    glPopMatrix()
    
# Wolf ears (solid cones)
    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)
    glTranslatef(30, 25, 38)   # Position on head
    
    glutSolidCone(4, 8, 8, 4) # Solid pointy ear cones
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)
    glTranslatef(30, 15, 38)  # Position on head
    
    glutSolidCone(4, 8, 8, 4) # Solid pointy ear cones
    glPopMatrix()
    # Legs (black cylinders)
    leg_positions = [
        (-12, 15, 2),   # Front left
        (-12, 5, 2),    # Front right
        (8, 5, 2),     # Back left
        (8, 18, 2)       # Back right
    ]
    
    for leg_x, leg_y, leg_z in leg_positions:
        glPushMatrix()
        glTranslatef(leg_x, leg_y, leg_z)
        glColor3f(0.1, 0.1, 0.1) 
        glRotatef(180, 1, 0, 0)  # Rotate to stand upright
        glutSolidCylinder(3, 25, 8, 3)  # Thin black cylinders for legs
        glPopMatrix()
    
     # Wolf tail (fluffy)
    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)
    glTranslatef(-20,10,2)
    glRotatef(25, 0, 1, 0)

    gluCylinder(gluNewQuadric(), 6, 1, 18, 10, 4)  # Fluffytail
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)
    glTranslatef(-20, 10, 2)
    glRotatef(-150, 0, 1, 0)

    gluCylinder(gluNewQuadric(), 6, 1, 18, 10, 4)  # tail2
    glPopMatrix()
    
    
   # GLOWING RED EYES
    glPushMatrix()
    glTranslatef(36, 25, 30)  # Right eye position
    
    # Eye glow effect
    glPushMatrix()
    glColor4f(1.0, 0.0, 0.0, 0.3)
    glutSolidSphere(3.0, 8, 8)
    glPopMatrix()
    
    # Main red eye
    glColor3f(1.0, 0.0, 0.0)
    glutSolidSphere(1.8, 12, 12)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(36, 15, 30)  # Left eye position
    
    # Eye glow effect
    glPushMatrix()
    glColor4f(1.0, 0.0, 0.0, 0.3)
    glutSolidSphere(3.0, 8, 8)
    glPopMatrix()
    

    glPopMatrix()
    
   
    glPopMatrix()

def draw_all_wolves():
    for wolf in wolves:
        draw_wolf(wolf)

# Add this function to create wolves at specific positions
def create_static_wolves():
    global wolves
    
    # Pre-defined wolf positions around the forest
    wolf_positions = [
        [400, 200, 30],    # Right-front
        [-350, -250, 30],  # Left-back  
        [300, -300, 30],   # Right-back
        [-400, 150, 30]    # Left-front
    ]
    
    for pos in wolf_positions:
        wolves.append({
            'pos': pos,
            'rotation': random.uniform(0, 360),
            'state': 'idle'
        })
    
    print(f"Created {len(wolves)} static wolves")

# Call this once at startup (add to main() or after variable initialization)
create_static_wolves()

def draw_wood_chopping_site():
    # Draw the main log (always visible)
    glPushMatrix()
    glTranslatef(wood_site_pos[0], wood_site_pos[1], wood_site_pos[2])

    # Main log - SOLID brown cylinder with border
    glPushMatrix()
    glColor3f(0.55, 0.27, 0.07)  # Brown log color
    glRotatef(180, 1, 0, 0)       # Rotate to stand upright

    # Solid log with dark border
    gluCylinder(gluNewQuadric(), 20, 20, 60, 16, 4)
    
    # Dark border around the log cylinder
    glPushMatrix()
    glColor3f(0.35, 0.15, 0.05)  # Dark border color
    gluCylinder(gluNewQuadric(), 20.5, 20.5, 60, 16, 4)  # Slightly larger for border
    glPopMatrix()

    # Top cap (on ground) with border
    glPushMatrix()
    glColor3f(0.35, 0.15, 0.05)  # Dark border
    glColor3f(0.75, 0.45, 0.25)  # Cream color for top
    gluDisk(gluNewQuadric(), 0, 19.5, 16, 2)  # Inner cream circle
    gluDisk(gluNewQuadric(), 19.5, 20.5, 16, 2)  # Border ring
    glColor3f(0.55, 0.27, 0.07)  # Main log color
    
    glPopMatrix()

    # Bottom cap with cream color and border
    glPushMatrix()
    glTranslatef(0, 0, 60)
    glColor3f(0.98, 0.94, 0.86)  # Cream color for top
    gluDisk(gluNewQuadric(), 0, 19.5, 16, 2)  # Inner cream circle
    glColor3f(0.35, 0.15, 0.05)  # Dark border
    gluDisk(gluNewQuadric(), 19.5, 20.5, 16, 2)  # Border ring
    
    glPopMatrix()

    glPopMatrix()  # Closes the main log matrix

    # Wood piece on log (for chopping) - only if visible
    if current_wood_visible:
        glPushMatrix()
        glTranslatef(0, -10, 10)  # Directly on top of the main log
        glColor3f(0.75, 0.45, 0.25)  # Lighter brown wood piece
    
        # Visual feedback based on chop progress
        if current_wood_chops == 1:
            glTranslatef(-3, 0, 0)  # Slightly offset after first chop
        elif current_wood_chops == 2:
            glTranslatef(-6, 0, 0)  # More offset after second chop
    
        glRotatef(-90, 1, 0, 0)  # Stand upright like the log
    
        # Solid wood piece with dark border
        gluCylinder(gluNewQuadric(), 12, 12, 25, 12, 3)
        
        # Dark border around the wood piece
        glPushMatrix()
        glColor3f(0.35, 0.15, 0.05)  # Dark border color
        gluCylinder(gluNewQuadric(), 12.5, 12.5, 25, 12, 3)  # Border
        glPopMatrix()
    
        # Bottom cap with border
        glPushMatrix()
        glColor3f(0.35, 0.15, 0.05)  # Dark border
        gluDisk(gluNewQuadric(), 11.5, 12.5, 12, 2)  # Border ring
        glColor3f(0.75, 0.45, 0.25)  # Wood color
        gluDisk(gluNewQuadric(), 0, 11.5, 12, 2)  # Inner circle
        glPopMatrix()
    
        # Top cap with border
        glPushMatrix()
        glTranslatef(0, 0, 25)
        glColor3f(0.35, 0.15, 0.05)  # Dark border
        gluDisk(gluNewQuadric(), 11.5, 12.5, 12, 2)  # Border ring
        glColor3f(0.75, 0.45, 0.25)  # Wood color
        gluDisk(gluNewQuadric(), 0, 11.5, 12, 2)  # Inner circle
        glPopMatrix()
    
        glPopMatrix()  # Closes the wood piece matrix

    glPopMatrix()  # Closes the main translate matrix

    # Draw three wood piles side by side
    pile_offsets = [-80, 0, 80]  # Left, center, right positions
    
    for pile_offset in pile_offsets:
        glPushMatrix()
        glTranslatef(wood_site_pos[0] + 80 , pile_offset+ wood_site_pos[1], wood_site_pos[2] - 30)
        
        # Draw stacked wood pieces as solid cylinders with different shades
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
            glRotatef(90, 1, 0, 0)  # Lay horizontally
            
            # Solid wood piece with dark border
            gluCylinder(gluNewQuadric(), wood_radius, wood_radius, wood_length, 12, 3)
            
            # Dark border around wood piece
            glPushMatrix()
            glColor3f(0.35, 0.15, 0.05)
            gluCylinder(gluNewQuadric(), wood_radius + 0.5, wood_radius + 0.5, wood_length, 12, 3)
            glPopMatrix()
            
            # Front cap with border
            glPushMatrix()
            glColor3f(0.35, 0.15, 0.05)
            gluDisk(gluNewQuadric(), wood_radius - 1, wood_radius + 0.5, 12, 2)
            glColor3f(*wood_shades[i])
            gluDisk(gluNewQuadric(), 0, wood_radius - 1, 12, 2)
            glPopMatrix()
            
            # Back cap with border
            glPushMatrix()
            glTranslatef(0, 0, wood_length)
            glColor3f(0.35, 0.15, 0.05)
            gluDisk(gluNewQuadric(), wood_radius - 1, wood_radius + 0.5, 12, 2)
            glColor3f(*wood_shades[i])
            gluDisk(gluNewQuadric(), 0, wood_radius - 1, 12, 2)
            glPopMatrix()
            
            glPopMatrix()  # Closes each wood piece matrix

        glPopMatrix()  # Closes each wood pile matrix

def draw_axe_in_hand():
    if axe_attached:
        glPushMatrix()
        glTranslatef(shepherd_pos[0], shepherd_pos[1], shepherd_pos[2] + 40)  # Hand height
        glRotatef(shepherd_rotation + 45, 0, 0, 1)  # Follow player rotation
        
        # Axe handle
        glPushMatrix()
        glColor3f(0.55, 0.27, 0.07)  # Wood brown
        glTranslatef(20, 0, 0)
        glRotatef(90, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 2, 2, 40, 8, 2)
        glPopMatrix()
        
        # Axe head
        glPushMatrix()
        glColor3f(0.7, 0.7, 0.7)  # Metal gray
        glTranslatef(55, 0, -5)
        glScalef(12, 2, 10)
        glutSolidCube(1)
        glPopMatrix()
        glPopMatrix()


def check_wood_site_interaction():
    global axe_attached, wood_respawn_timer, current_wood_visible
    
    # Calculate distance to wood site
    distance = math.sqrt((shepherd_pos[0] - wood_site_pos[0])**2 + 
                         (shepherd_pos[1] - wood_site_pos[1])**2)
    
    # Attach axe when player enters radius, detach when leaves
    if distance < wood_site_radius:
        axe_attached = True
    else:
        axe_attached = False  # DETACH when leaving the area
    
    # Handle wood respawn timer
    if wood_respawn_timer > 0:
        wood_respawn_timer -= 1
        if wood_respawn_timer == 0 and wood_count < max_wood_capacity:
            current_wood_visible = True
            print("New wood has respawned!")

def handle_wood_chopping():
    global current_wood_chops, wood_respawn_timer, current_wood_visible, wood_count, is_night
    
    # First, check if we're actually at the wood site (axe should only be attached when we are)
    distance = math.sqrt((shepherd_pos[0] - wood_site_pos[0])**2 + 
                         (shepherd_pos[1] - wood_site_pos[1])**2)
    
    # Only allow chopping if we're at the wood site AND have the axe AND wood is visible
    if distance < wood_site_radius and axe_attached and current_wood_visible and wood_count < max_wood_capacity:
        current_wood_chops += 1
        print(f"Chop {current_wood_chops}/{max_chops}")
        
        if current_wood_chops >= max_chops:
            wood_count += 1
            current_wood_visible = False
            wood_respawn_timer = 100
            current_wood_chops = 0
            print(f"Wood chopped! Total: {wood_count}/{max_wood_capacity}")

            # CHECK FOR NIGHT TIME - when wood reaches 15
            if wood_count >=  max_wood_capacity:
                is_night = True
                print("NIGHT HAS FALLEN! Wolves become active!")



def keyboardListener(key, x, y):
    global  shepherd_rotation 

    if key == b' ':  # SPACE key
        space_pressed = True
        print("Space pressed")
    
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
    
    
    #Wood
    if key == b'c':  # Chop wood key
        handle_wood_chopping()

    
    # Whistle ability
    if key == b'v':  # Whistle key
        # Implement whistle cooldown and sheep attraction
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

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if camera_mode == "third_person":
        # Static camera position orbiting around a fixed point
        cam_x = camera_distance * math.cos(math.radians(camera_angle))
        cam_y = camera_distance * math.sin(math.radians(camera_angle))
        cam_z = camera_height
        
        # Camera stays in fixed position, looks at the center or shepherd's position
        gluLookAt(cam_x, cam_y, cam_z,  # Fixed camera position
                  0, 0, 30,  # Look at center point (or use shepherd_pos for follow)
                  0, 0, 1)
    else:
        # First person - fixed head level view looking in facing direction
        head_height = 60  # Shepherd's eye level height
        
        # Calculate look-at point based on shepherd's rotation (10 units ahead)
        look_ahead = 10
        look_x = shepherd_pos[0] + math.cos(math.radians(shepherd_rotation)) * look_ahead
        look_y = shepherd_pos[1] + math.sin(math.radians(shepherd_rotation)) * look_ahead
        
        gluLookAt(shepherd_pos[0],                  # X position
                  shepherd_pos[1],                  # Y position  
                  shepherd_pos[2] + head_height,    # Z position (head level)
                  look_x,                           # Look at point X
                  look_y,                           # Look at point Y
                  shepherd_pos[2] + head_height,    # Look at same height (straight ahead)
                  0, 0, 1)

def idle():
    global last_time, night_transition

    current_time = time.time()
    delta_time = current_time - last_time
    last_time = current_time

    
    # Smooth night transition
    if is_night and night_transition < 1.0:
        night_transition += 0.01  # Smooth transition over time
    elif not is_night and night_transition > 0:
        night_transition -= 0.01

    check_wood_site_interaction()

    update_sheep_movement(delta_time)
    
    
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
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
    
    if not can_chop_wood:
        draw_text(10, 590, "MAX CAPACITY - Go to fire!")

    # Night time indicator
    if is_night:
        draw_text(10, 500, "🌙 NIGHT TIME - Be careful!", GLUT_BITMAP_HELVETICA_12)
    elif night_transition > 0:
        draw_text(10, 500, "Dusk is falling...", GLUT_BITMAP_HELVETICA_12)

    draw_text(10, 730, f"Wood :{wood_count}/{max_wood_capacity}")
    draw_text(10, 710, f"Heart Points:")
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