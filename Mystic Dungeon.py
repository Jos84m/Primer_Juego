# Importamos la libreria de tkinter 
# Imnportamos a PIL, para el uso de images y gifs en nuetro juego asi le damos una interaccion mas visual.
# Importamos a random, para la creacion de objectos, obstaculos y moviminetos, basicamente para que aparezcan en nuestro juego de diferentes posiciones y moviminetos cada elemento o evento.
# Imporatmos os una extencion de Python segun en el manual de tkintery lo utilizamos para la creacion del guardado automatico de txt, ademas un mayor controlamiento en puntos.
# Imoportamos a pygame para utilizarlo "unicamente en la ejecucion del audio mp3(Es decir la musica de nuestro juego".

import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import random
import os
import pygame

pygame.init()
pygame.mixer.init()

# Variables globales
goku_pos = [950, 950]
lives = 3
volume_scale = None
enemy_pos = [960, 50]
enemy_speed = 5  # velocidad del enemigo
enemy_id = None
ground_enemy_pos = [960, 1030]  # Posición inicial del enemigo terrestre
ground_enemy_speed = 10  # velocidad del enemigo terrestre
ground_enemy_id = None  # ID del enemigo terrestre
score = 0
projectiles = []
player_name = "Jugador"
high_scores = []
level = 1
spheres = []
sphere_velocities = []
min_sphere_size = 10
level_scores = []
obstacles = []
lives_images = []
life_available = True 
goku_ammo = 20
ammo_items = []
level_images = [
    ("santuario.png", "DAT.gif"),
    ("santuario.png", "DAT.gif"),
    ("santuario.png", "DAT.gif")
]

level_backgrounds = [
    "santuario.png",
    "dragonf.gif",
    "fondo11.gif"
]

music_file = "Musica del juego.mp3"
start_window = None
background_label = None
frame_index = 0
background_frames = []

class Esfera:
    def __init__(self, x, y, radius, velocity):
        self.x = x
        self.y = y
        self.radius = radius
        self.velocity = velocity
        self.id = playground.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill="blue", outline="black"
        )

    def move(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        playground.move(self.id, self.velocity[0], self.velocity[1])

        # Colisiones con los bordes
        if self.x - self.radius <= 0 or self.x + self.radius >= 1920:
            self.velocity[0] = -self.velocity[0]
        if self.y - self.radius <= 0 or self.y + self.radius >= 1080:
            self.velocity[1] = -self.velocity[1]

        # Colisiones con obstáculos
        collision = next((obs for obs in obstacles if
                          (obs['x'] - self.radius <= self.x <= obs['x'] + self.radius) and
                          (obs['y'] - self.radius <= self.y <= obs['y'] + self.radius)), None)
        
        if collision:
            self.velocity[0] = -self.velocity[0]
            self.velocity[1] = -self.velocity[1]

    def is_destroyed(self):
        return self.radius < min_sphere_size

    def divide(self):
        new_spheres = []
        global life_available

        if self.radius // 2 >= min_sphere_size:
            new_radius = self.radius // 2
            new_velocity = [self.velocity[0] * 0.8, self.velocity[1] * 0.8]
            new_spheres = [
                Esfera(self.x + random.randint(-5, 5), self.y + random.randint(-5, 5), new_radius, new_velocity),
                Esfera(self.x + random.randint(-5, 5), self.y + random.randint(-5, 5), new_radius, new_velocity)
            ]

        if life_available and random.randint(0, 100) < 20:  # 20% de probabilidad de obtener una nueva vida
            create_life_item(self.x, self.y)
            life_available = False

        return new_spheres



def create_life_item(x, y):
    global lives_images
    life_img = ImageTk.PhotoImage(file="coraz9on.png")
    img_id = playground.create_image(x, y, anchor="center", image=life_img)
    lives_images.append((img_id, life_img))
    move_life_item(img_id)  # Inicia el movimiento de la vida



def move_life_item(img_id, speed=5):
    if playground.coords(img_id):
        x, y = playground.coords(img_id)
        if y + speed < 1080:
            y += speed
            playground.coords(img_id, x, y)
            playground.after(50, move_life_item, img_id, speed)
        else:
            check_life_item_collision_with_goku(img_id)



def check_life_item_collision_with_goku(img_id):
    global lives_images, lives

    if playground.coords(img_id):
        x, y = playground.coords(img_id)
        if abs(x - goku_pos[0]) < 50 and abs(y - goku_pos[1]) < 50:
            playground.delete(img_id)
            lives_images = list(filter(lambda img: img[0] != img_id, lives_images))
            lives += 1
            update_lives_display()


def move_life_items():
    global lives_images

    def process_life_item(life_item):
        img_id, img = life_item
        if playground.coords(img_id):
            x, y = playground.coords(img_id)
            check_life_item_collision_with_goku(img_id)

    list(map(process_life_item, lives_images))
    playground.after(50, move_life_items)

def load_gif_frames(gif_path, width, height):
    global background_frames
    gif = Image.open(gif_path)
    background_frames = list(map(lambda frame: ImageTk.PhotoImage(frame.copy().resize((width, height), Image.LANCZOS)),
                                  ImageSequence.Iterator(gif)))

def update_background_frame():
    global frame_index, background_label, start_window
    frame_index = (frame_index + 1) % len(background_frames)
    background_label.config(image=background_frames[frame_index])
    start_window.after(100, update_background_frame)


def show_levels_window():
    global selected_level
    selected_level = -1  # Nivel aún no seleccionado

    def select_level(level_idx):
        global selected_level
        selected_level = level_idx
        levels_window.destroy()
        start_game()

    levels_window = tk.Toplevel(start_window)
    levels_window.title("Niveles del Juego")
    levels_window.geometry("1920x1080")

    def create_level_frame(i, level_data):
        bg_image, gif_image = level_data
        
        frame = tk.Frame(levels_window, width=500, height=500, relief=tk.RAISED, borderwidth=2)
        frame.grid(row=i // 2, column=i % 2, padx=20, pady=20)
        frame.grid_propagate(False)  # Para evitar que el tamaño cambie con los widgets internos

        # Cargar el fondo del nivel
        background_image = Image.open(level_backgrounds[i])
        background_image = background_image.resize((500, 500), Image.LANCZOS)
        background_photo = ImageTk.PhotoImage(background_image)

        # Etiqueta para la imagen de fondo
        background_label = tk.Label(frame, image=background_photo)
        background_label.img = background_photo  # Evita que la imagen sea eliminada por el recolector de basura
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Mostrar nombre del nivel
        level_label = tk.Label(frame, text=f"Nivel {i + 1}", font=("Arial", 24), bg="white")
        level_label.pack(pady=10)

        # Mostrar GIF del nivel
        gif_label = tk.Label(frame, bg="white")
        gif_label.pack(pady=10)
        update_gif(gif_label, gif_image, 500, 500)

        # Botón para seleccionar el nivel
        select_button = tk.Button(levels_window, text="Empezar Juego", command=lambda: select_level(i + 1))
        select_button.grid(row=i // 2, column=2, padx=20, pady=20)
        select_button.lift()  # Mover el botón delante del fondo

    list(map(create_level_frame, range(len(level_images)), level_images))

    levels_window.mainloop()


def update_gif(label, gif_path, width, height):
    gif = Image.open(gif_path)
    frames = list(map(lambda frame: tk.PhotoImage(frame.copy().resize((width, height), Image.LANCZOS)),
                      ImageSequence.Iterator(gif)))
    animate_gif(label, frames, 0)

def animate_gif(label, frames, index):
    label.config(image=frames[index])
    next_index = (index + 1) % len(frames)
    label.after(100, animate_gif, label, frames, next_index)



def load_high_scores():
    if os.path.exists("high_scores.txt"):
        with open("high_scores.txt", "r") as f:
            return list(map(lambda line: line.strip().split(","), f.readlines()))
    return []

def save_high_scores():
    with open("high_scores.txt", "w") as f:
        list(map(lambda hs: f.write(f"{hs[0]},{hs[1]}\n"), 
                  sorted(high_scores, key=lambda x: int(x[1]), reverse=True)[:5]))

def move_projectile(projectile, x, y):
    proj = next(filter(lambda p: p[0] == projectile, projectiles), None)
    
    if proj is None:
        return

    dx, dy = proj[1], proj[2]
    coords = playground.coords(projectile)

    if len(coords) < 4:  # Verificar si las coordenadas son válidas
        projectiles.remove(proj)
        return

    playground.coords(projectile, x, y, x + dx, y + dy)

    # Verificar colisión con el enemigo
    if check_collision(projectile):
        hit_enemy(projectile)
        return

    # Verificar colisión con esferas
    sphere_collision = next(filter(lambda sphere: check_collision_with_sphere(projectile, sphere), spheres), None)
    if sphere_collision:
        hit_sphere(projectile, sphere_collision)
        return

    # Verificar si el proyectil está fuera de los límites de la pantalla
    if y < 0 or y > 1080 or x < 0 or x > 1920:
        playground.delete(projectile)
        projectiles.remove(proj)
        update_ammo_display()
        return

    # Mover el proyectil nuevamente después de un breve retraso
    playground.after(50, move_projectile, projectile, x + dx, y + dy)
            

def shoot(dx, dy): 
    x, y = goku_pos[0], goku_pos[1] 
    projectile = playground.create_line(x, y, x + dx, y + dy, fill="cyan", width=5) 
    projectiles.append((projectile, dx, dy))
    update_ammo_display() 
    move_projectile(projectile, x + dx, y + dy)



def move_ground_enemy():
    global ground_enemy_pos, ground_enemy_speed, ground_enemy_id

    if not ground_enemy_id:
        ground_enemy_img = tk.PhotoImage(Image.open("cajamuni.png").resize((100, 100), Image.LANCZOS))
        ground_enemy_id = playground.create_image(ground_enemy_pos[0], ground_enemy_pos[1], anchor="center",
                                                  image=ground_enemy_img)
        playground.image_cache.append(ground_enemy_img)  # Almacenar imagen para evitar que sea recolectada por el GC

    ground_enemy_pos[0] += ground_enemy_speed
    if ground_enemy_pos[0] > 1920 or ground_enemy_pos[0] < 0:
        ground_enemy_speed = -ground_enemy_speed

    playground.coords(ground_enemy_id, ground_enemy_pos[0], ground_enemy_pos[1])

    check_projectile_collision_with_ground_enemy()

    game_window.after(50, move_ground_enemy)


def check_projectile_collision_with_ground_enemy():
    global ground_enemy_id  # Declarar primero

    if not ground_enemy_id:
        return

    enemy_bbox = playground.bbox(ground_enemy_id)

    # Usar filter y next para verificar colisiones
    projectile_collision = next(
        filter(lambda proj: proj[0] and playground.bbox(proj[0]) and 
                (enemy_bbox[0] < playground.bbox(proj[0])[2] < enemy_bbox[2] and
                 enemy_bbox[1] < playground.bbox(proj[0])[3] < enemy_bbox[3]), 
                projectiles), 
        None
    )

    if projectile_collision:
        projectile, dx, dy = projectile_collision
        playground.delete(ground_enemy_id)
        playground.delete(projectile)
        ground_enemy_id = None
        projectiles.remove(projectile_collision)
        create_ammo_item(ground_enemy_pos[0], ground_enemy_pos[1])



def start_game():
    global volume_scale, enemy_id, enemy_pos, score, level, enemy_speed, player_name, life_available, selected_level
    volume = (volume_scale.get() / 100) if volume_scale else 0.5
    player_name = name_entry.get() or "Jugador"

    if selected_level != -1:
        level = selected_level + 1
    start_window.destroy()
    life_available = True  # Hacer disponible la vida al iniciar el juego
    initialize_game_window()

    move_enemy_air()  # Iniciar el movimiento del enemigo aéreo
    update_spheres()  # Iniciar el movimiento de las esferas


def initialize_game_window():
    global game_window, playground, lives_label, score_label, goku_id, enemy_id, ammo_label, ground_enemy_id
    game_window = tk.Tk()
    game_window.title("Juego")
    game_window.state('zoomed')
    game_window.geometry("1920x1080")
    playground = tk.Canvas(game_window, width=1920, height=1080, bg="white")
    playground.pack()

    load_images()

    sphere_count = 3 if level == 1 else 4 if level == 2 else 6 if level == 5 else 5
    create_spheres(sphere_count)

    create_obstacles(5)

    lives_label = tk.Label(game_window, text=f"Vidas: {lives}", font=("Arial", 20), bg="black", fg="white")
    lives_label.pack()

    score_label = tk.Label(game_window, text=f"Puntaje: {score}", font=("Arial", 20), bg="black", fg="white")
    score_label.pack()

    ammo_label = tk.Label(game_window, text=f"Munición: {len(projectiles)}", font=("Arial", 20), bg="black", fg="white")
    ammo_label.pack()

    exit_button = tk.Button(game_window, text="Salir al Menú", command=exit_to_menu)
    exit_button.pack()

    game_window.bind("<Key>", key_press)

    create_ground_enemy()  # Crear el enemigo terrestre
    game_window.after(50, move_ground_enemy)  # Comenzar el movimiento del enemigo terrestre

def move_enemy():
    update_lives_display()
    update_score_display()
    update_ammo_display()
    high_scores = load_high_scores()
    game_window.after(50, update_spheres)
    game_window.after(50, update_projectiles)
    game_window.after(50, move_life_items)  # Añadido para mover los ítems de vidas

    pygame.mixer.music.load(music_file)
    pygame.mixer.music.play(-1)
    game_window.mainloop()

def load_images():
    global gokuImg, enemyImg, background_photo, ground_enemy_img

    try:
        background_img = Image.open(level_images[level - 1][0])
        background_img = background_img.resize((1920, 1080), Image.LANCZOS)
        background_photo = ImageTk.PhotoImage(background_img)
        playground.create_image(0, 0, anchor="nw", image=background_photo)

        gokuImg = tk.PhotoImage(file="goku.png")
        global goku_id
        goku_id = playground.create_image(goku_pos[0], goku_pos[1], anchor="center", image=gokuImg)

        enemyImg = ImageTk.PhotoImage(file=level_images[level - 1][1])
        global enemy_id
        enemy_id = playground.create_image(enemy_pos[0], enemy_pos[1], anchor="center", image=enemyImg)
        
        # Cargar imagen del enemigo terrestre
        ground_enemy_img = ImageTk.PhotoImage(file="fantasma.png")
        
    except tk.TclError as e:
        print("Error al cargar imágenes:", e)


def create_ground_enemy():
    global ground_enemy_id
    ground_enemy_id = playground.create_image(ground_enemy_pos[0], ground_enemy_pos[1], anchor="center", image=ground_enemy_img)

def move_ground_enemy():
    global ground_enemy_pos, ground_enemy_speed
    # Mover el enemigo terrestre de izquierda a derecha y viceversa
    ground_enemy_pos[0] += ground_enemy_speed
    if ground_enemy_pos[0] <= 0 or ground_enemy_pos[0] >= 1920:
        ground_enemy_speed = -ground_enemy_speed  # Invertir dirección en los bordes laterales

    playground.coords(ground_enemy_id, ground_enemy_pos[0], ground_enemy_pos[1])
    playground.after(50, move_ground_enemy)



def create_spheres(sphere_count):
    def create_sphere(_):
        x = random.randint(100, 1820)
        y = random.randint(100, 800)
        sphere_size = 50
        velocity = [random.choice([-6, 6]), random.choice([-6, 6])]
        sphere = Esfera(x, y, sphere_size, velocity)
        spheres.append(sphere)

    list(map(create_sphere, range(sphere_count)))


def create_obstacles(obstacle_count):
    global obstacles
    
    def create_obstacle(_):
        x = random.randint(100, 1820)
        y = random.randint(100, 800)
        size = 20
        obstacle = {"x": x, "y": y, "size": size}
        playground.create_rectangle(x - size, y - size, x + size, y + size, fill="red", outline="black")
        obstacles.append(obstacle)
    
    list(map(create_obstacle, range(obstacle_count)))



def create_ammo_item(x, y):
    ammo_img = tk.PhotoImage(file="cajamuni.png")
    img_id = playground.create_image(x, y, anchor="center", image=ammo_img)
    playground.image_cache.append(ammo_img)  # Almacenar imagen para evitar que sea recolectada por el GC
    ammo_items.append(img_id)  # Agregar el ID del item a la lista
    move_ammo_item(img_id)

def check_collision(goku_pos, ammo_pos):
    # Verifica si hay colisión entre Goku y el item de munición
    goku_x, goku_y = goku_pos
    ammo_x, ammo_y = ammo_pos

    # Define un rango de colisión
    collision_range = 30
    return abs(goku_x - ammo_x) < collision_range and abs(goku_y - ammo_y) < collision_range





def on_goku_move(goku_pos):
    global goku_ammo
    
    # Función para procesar la munición
    def process_ammo(ammo_id):
        ammo_pos = playground.coords(ammo_id)
        if check_collision(goku_pos, ammo_pos):
            playground.delete(ammo_id)
            ammo_items.remove(ammo_id)
            global goku_ammo
            goku_ammo += 10
            print(f"Munición obtenida: {goku_ammo}")
    
    # Usar map para procesar cada item de munición
    list(map(process_ammo, ammo_items[:]))




def move_goku(dx):
    goku_pos[0] += dx
    goku_pos[0] = max(0, min(goku_pos[0], 1920))
    playground.coords(goku_id, goku_pos[0], goku_pos[1])



def key_press(event):
    if event.keysym == "Right":
        move_goku(10)
    elif event.keysym == "Left":
        move_goku(-10)
    elif event.keysym == "Up":
        shoot(0, -30)
    elif event.keysym == "space":
        shoot(30, 0)
    elif event.keysym == "Down":
        shoot(-30, 0)



def check_collision_with_sphere(projectile, sphere):
    projectile_coords = playground.coords(projectile)
    if not projectile_coords:
        return False
    sphere_coords = playground.coords(sphere.id)
    sphere_center_x = (sphere_coords[0] + sphere_coords[2]) / 2
    sphere_center_y = (sphere_coords[1] + sphere_coords[3]) / 2
    dx = abs(sphere_center_x - projectile_coords[0])
    dy = abs(sphere_center_y - projectile_coords[1])
    distance = (dx**2 + dy**2)**0.5
    return distance < sphere.radius


def hit_sphere(projectile, sphere):
    global score
    playground.delete(sphere.id)
    spheres.remove(sphere)
    score += 20
    update_score_display()
    
    new_spheres = sphere.divide()
    spheres.extend(new_spheres)
    
    playground.delete(projectile)
    update_ammo_display()
    
    # Usar map para eliminar el proyectil específico
    list(map(lambda proj: projectiles.remove(proj) if proj[0] == projectile else None, projectiles))
    
    if not spheres:
        advance_to_next_level()

def hit_sphere(projectile, sphere):
    global score
    playground.delete(sphere.id)
    spheres.remove(sphere)
    score += 20
    update_score_display()
    
    new_spheres = sphere.divide()
    spheres.extend(new_spheres)
    
    playground.delete(projectile)
    update_ammo_display()
    
    projectiles[:] = list(filter(lambda proj: proj[0] != projectile, projectiles))
    
    if not spheres:
        advance_to_next_level()


def advance_to_next_level():
    global level, spheres, projectiles, score, life_available
    level_scores.append(score)
    level += 1
    if level > len(level_images):
        game_over()
        return
    level_window = tk.Toplevel(game_window)
    level_window.title(f"Nivel {level}")
    level_window.geometry("400x200")

    tk.Label(level_window, text=f"Nivel {level}", font=("Arial", 24)).pack(pady=20)

    def start_next_level():
        level_window.destroy()
        reset_level()
        life_available = True  # Hacer disponible la vida al iniciar el nuevo nivel

    tk.Button(level_window, text="Empezar", command=start_next_level).pack(pady=20)


def reset_level():
    global spheres, projectiles
    spheres = []
    projectiles = []
    load_images()
    sphere_count = 3 if level == 1 else 4 if level == 2 else 6 if level == 5 else 5
    create_spheres(sphere_count)
    create_obstacles(5)
    update_score_display()
    update_lives_display()
    update_ammo_display()


def update_projectiles():
    list(map(lambda proj: move_projectile(proj[0], *playground.coords(proj[0])), projectiles))
    playground.after(50, update_projectiles)


def check_collision(projectile):
    projectile_coords = playground.coords(projectile)
    if (projectile_coords[2] >= enemy_pos[0] - 50 and projectile_coords[0] <= enemy_pos[0] + 50 and
            projectile_coords[1] <= enemy_pos[1] + 50 and projectile_coords[3] >= enemy_pos[1] - 50):
        return True
    return False

# Esta función se llama cuando el enemigo es golpeado por un proyectil.
def hit_enemy(projectile):
    global score
    playground.delete(enemy_id)
    score += 50
    reset_enemy()  # Volvemos a crear al enemigo
    update_score_display()
    playground.delete(projectile)
    update_ammo_display()


def reset_enemy():
    global enemy_pos, enemy_id
    enemy_pos = [random.randint(100, 1820), random.randint(50, 300)]
    enemy_id = playground.create_image(enemy_pos[0], enemy_pos[1], anchor="center",
                                       image=tk.PhotoImage(file=level_images[level - 1][1]))


def update_score_display():
    score_label.config(text=f"Puntaje: {score}")


def update_lives_display():
    lives_label.config(text=f"Vidas: {lives}")


def update_ammo_display():
    ammo_label.config(text=f"Munición: {len(projectiles)}")

def game_over():
    # Create a new window for the game over screen
    game_over_window = tk.Toplevel(game_window)
    game_over_window.title("Game Over")
    game_over_window.geometry("400x300")

    # Display final score
    tk.Label(game_over_window, text=f"FELICIDADES AS COMPLETADO EL JUEGO\nPuntaje Final: {score}\nNombre: {player_name}",font=("Times", 24), fg="green").pack(pady=20)

    # Buttons to restart or exit to the main menu
    restart_button = tk.Button(game_over_window, text="Reiniciar", command=restart_game, relief="groove", borderwidth=10)
    restart_button.pack(pady=10)

    exit_button = tk.Button(game_over_window, text="Volver al Menú", command=exit_to_menu, relief="groove", borderwidth=10)
    exit_button.pack(pady=10)

    # Disable the main game window while the game over window is open
    game_window.withdraw()  # Hide the main game window

    # Bind the destroy event to show the main window again when the game over window is closed
    game_over_window.protocol("WM_DELETE_WINDOW", lambda: (game_window.deiconify(), game_over_window.destroy()))



def restart_game():
    global lives, score, level, enemy_speed, spheres, sphere_velocities, level_scores, life_available
    lives = 3
    score = 0
    level = 1
    enemy_speed = 5
    spheres = []
    sphere_velocities = []
    level_scores = []
    life_available = True  # Hacer disponible la vida al reiniciar el juego
    update_lives_display()
    update_score_display()
    update_ammo_display()
    load_images()
    create_spheres(3)
    start_game()



def show_high_scores():
    high_scores_window = tk.Toplevel(game_window)
    high_scores_window.title("Mejores Puntajes")
    high_scores_window.geometry("400x300")

    tk.Label(high_scores_window, text="Mejores Puntajes", font=("Arial", 16)).pack(pady=10)

    list(map(lambda idx_level_score: tk.Label(high_scores_window, text=f"Nivel {idx_level_score[0] + 1}: {idx_level_score[1]} puntos", font=("Arial", 14)).pack(),
              enumerate(level_scores)))

    tk.Label(high_scores_window, text=f"Puntaje Total: {score}", font=("Arial", 14)).pack(pady=(10, 0))
    tk.Label(high_scores_window, text=f"Vidas Restantes: {lives}", font=("Arial", 14)).pack()

    tk.Label(high_scores_window, text="Top 5 puntajes altos:", font=("Arial", 14)).pack(pady=(10, 0))
    
    sorted_scores = sorted(high_scores, key=lambda x: int(x[1]), reverse=True)[:5]
    list(map(lambda idx_name_score: tk.Label(high_scores_window, text=f"{idx_name_score[0] + 1}. {idx_name_score[1][0]}: {idx_name_score[1][1]}", font=("Arial", 14)).pack(), 
              enumerate(sorted_scores)))




def move_enemy():
    global enemy_pos, enemy_speed, first_fall

    if first_fall:
        # Mover el enemigo hacia abajo
        enemy_pos[1] += enemy_speed

        # Si el enemigo alcanza el borde inferior, cambiar el comportamiento
        if enemy_pos[1] >= 1080:
            first_fall = False
            enemy_pos[1] = 200  # Ajustar a la nueva posición vertical deseada
            enemy_pos[0] = random.randint(20,
                                          1920)  # Ajustar posición X aleatoriamente para la nueva posición en la parte superior
            enemy_speed = 10  # Asegurar que la velocidad horizontal sea positiva inicialmente

    # Después de la primera caída, mover de izquierda a derecha
    if not first_fall:
        enemy_pos[0] += enemy_speed
        if enemy_pos[0] <= 0 or enemy_pos[0] >= 1920:
            enemy_speed = -enemy_speed  # Invertir dirección en los bordes laterales

    playground.coords(enemy_id, enemy_pos[0], enemy_pos[1])
    check_collision_with_goku()
    playground.after(50, move_enemy)

def move_enemy_air():
    global enemy_pos, enemy_speed, enemy_id

    if not enemy_id:
        enemy_img = ImageTk.PhotoImage(Image.open("DAT.png").resize((100, 100), Image.LANCZOS))
        enemy_id = playground.create_image(enemy_pos[0], enemy_pos[1], anchor="center", image=enemy_img)
        playground.image_cache = enemy_img

    enemy_pos[1] += enemy_speed
    if enemy_pos[1] > 1080 or enemy_pos[1] < 0:
        enemy_speed = -enemy_speed

    playground.coords(enemy_id, enemy_pos[0], enemy_pos[1])
    game_window.after(50, move_enemy_air)

def check_collision_with_goku():
    global lives
    if (abs(goku_pos[0] - enemy_pos[0]) < 50) and (abs(goku_pos[1] - enemy_pos[1]) < 50):
        lives -= 1
        update_lives_display()
        if lives <= 0:
            game_over()


def create_ammo_item(x, y):
    ammo_img = ImageTk.PhotoImage(file="cajamuni.png")
    img_id = playground.create_image(x, y, anchor="center", image=ammo_img)
    playground.image_cache.append(ammo_img)  # Almacenar imagen para evitar que sea recolectada por el GC
    move_ammo_item(img_id)


def move_ammo_item(img_id, speed=5):
    if playground.coords(img_id):
        x, y = playground.coords(img_id)
        if y + speed < 1080:
            y += speed
            playground.coords(img_id, x, y)
            playground.after(50, move_ammo_item, img_id, speed)
        else:
            check_ammo_item_collision_with_goku(img_id)


def check_ammo_item_collision_with_goku(img_id):
    if playground.coords(img_id):
        x, y = playground.coords(img_id)
        if abs(x - goku_pos[0]) < 50 and abs(y - goku_pos[1]) < 50:
            playground.delete(img_id)
            increase_ammo()


def increase_ammo():
    projectiles.append((None, 0, 0))  # Añadir munición a la lista (en blanco, ya que pueden ser disparados después)
    update_ammo_display()


def move_ground_enemy():
    global ground_enemy_pos, ground_enemy_speed, ground_enemy_id

    if not ground_enemy_id:
        ground_enemy_img = ImageTk.PhotoImage(Image.open("fantasma.png").resize((100, 100), Image.LANCZOS))
        ground_enemy_id = playground.create_image(ground_enemy_pos[0], ground_enemy_pos[1], anchor="center",
                                                  image=ground_enemy_img)
        playground.image_cache.append(ground_enemy_img)  # Almacenar imagen para evitar que sea recolectada por el GC

    ground_enemy_pos[0] += ground_enemy_speed
    if ground_enemy_pos[0] > 1920 or ground_enemy_pos[0] < 0:
        ground_enemy_speed = -ground_enemy_speed

    playground.coords(ground_enemy_id, ground_enemy_pos[0], ground_enemy_pos[1])

    check_projectile_collision_with_ground_enemy()

    game_window.after(50, move_ground_enemy)

def check_projectile_collision_with_ground_enemy():
    global ground_enemy_id  # Declarar global al inicio

    if not ground_enemy_id:
        return

    enemy_bbox = playground.bbox(ground_enemy_id)
    check_collision_with_projectiles(0, enemy_bbox)

def check_collision_with_projectiles(index, enemy_bbox):
    global ground_enemy_id  # Declarar global al inicio de esta función

    if index >= len(projectiles):
        return

    projectile, dx, dy = projectiles[index]
    if projectile and playground.bbox(projectile):
        proj_bbox = playground.bbox(projectile)
        if (enemy_bbox[0] < proj_bbox[2] < enemy_bbox[2] and
                enemy_bbox[1] < proj_bbox[3] < enemy_bbox[3]):
            playground.delete(ground_enemy_id)
            playground.delete(projectile)
            ground_enemy_id = None
            projectiles.remove((projectile, dx, dy))
            create_ammo_item(ground_enemy_pos[0], ground_enemy_pos[1])
            return

    check_collision_with_projectiles(index + 1, enemy_bbox)



def update_spheres():
    global spheres  # Declarar global al inicio
    update_spheres_recursively(0)

def update_spheres_recursively(index):
    global spheres  # Declarar global aquí también

    if index >= len(spheres):
        spheres = [sphere for sphere in spheres if not sphere.is_destroyed()]
        game_window.after(50, update_spheres)
        return

    sphere = spheres[index]
    sphere.move()
    update_spheres_recursively(index + 1)




def update_volume(val):
    volume = float(val) / 100
    pygame.mixer.music.set_volume(volume)


def open_settings():
    settings_window = tk.Toplevel(start_window)
    settings_window.title("Configuración")
    settings_window.geometry("400x300")
    tk.Label(settings_window, text="Configuración del Juego", font=("Arial", 16)).pack(pady=20)
    global volume_scale
    volume_scale = tk.Scale(settings_window, from_=0, to=100, orient=tk.HORIZONTAL, label="Volumen", command=update_volume)
    volume_scale.set(50)
    volume_scale.pack(pady=20)

def show_high_scores_start():
    high_scores_window = tk.Toplevel(start_window)
    high_scores_window.title("Mejores Puntajes")
    high_scores_window.geometry("400x300")
    tk.Label(high_scores_window, text="Mejores Puntajes", font=("Arial", 16)).pack(pady=10)

    sorted_scores = sorted(high_scores, key=lambda x: int(x[1]), reverse=True)[:5]
    show_high_scores_recursively(high_scores_window, sorted_scores, 0)

def show_high_scores_recursively(high_scores_window, sorted_scores, index):
    if index >= len(sorted_scores):
        return

    name, score = sorted_scores[index]
    tk.Label(high_scores_window, text=f"{index + 1}. {name}: {score}", font=("Arial", 14)).pack()
    show_high_scores_recursively(high_scores_window, sorted_scores, index + 1)

def exit_to_menu():
    global game_window
    pygame.mixer.music.stop()
    game_window.destroy()
    main()

def update_gif(label, gif_path, width, height):
    gif = Image.open(gif_path)
    frames = list(map(lambda frame: ImageTk.PhotoImage(frame.copy().resize((width, height), Image.LANCZOS)), 
                      ImageSequence.Iterator(gif)))

def main():
    global start_window, background_label, name_entry, selected_level
    selected_level = -1  # Inicializar aquí también
    start_window = tk.Tk()
    start_window.title("Inicio del Juego")
    start_window.state('zoomed')  # Para pantalla completa
    start_window.config(cursor="spider")
    screen_width = start_window.winfo_screenwidth()
    screen_height = start_window.winfo_screenheight()
    
    # Cargar y mostrar el GIF como fondo
    load_gif_frames("dragonf.gif", screen_width, screen_height)  # Reemplaza "tu_gif.gif" con la ruta de tu archivo GIF
    background_label = tk.Label(start_window)
    background_label.pack(fill=tk.BOTH, expand=tk.YES)
    update_background_frame()

    content_frame = tk.Frame(start_window, bg="grey", highlightbackground="black", highlightthickness=1, relief="ridge", borderwidth=20)
    content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER,)
    

    tk.Label(content_frame, text="Mystic Dungeon", font=("Times", 24), bg="white", relief="ridge",borderwidth=5).pack(pady=10)
    tk.Label(content_frame, text="Nombre de Jugador", font=("Times", 14), bg="white").pack(pady=(10, 0))
    name_entry = tk.Entry(content_frame, font=("Times", 14),relief="ridge")
    name_entry.pack(pady=10)
    tk.Button(content_frame, text="Empezar Juego", font=("Times", 14), command=show_levels_window,relief="groove", borderwidth=10).pack(pady=5)  # Mostrar ventana de niveles primero
    tk.Button(content_frame, text="Configuración", font=("Times", 14), command=open_settings, relief="groove", borderwidth=10).pack(pady=5)
    tk.Button(content_frame, text="Mejores Puntajes", font=("Times", 14), command=show_high_scores_start,relief="groove", borderwidth=10).pack(pady=5)

    start_window.mainloop()


if __name__ == "__main__":
    high_scores = load_high_scores()
    main()
