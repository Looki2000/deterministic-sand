import pygame
import numpy as np
import colorsys
from PIL import Image

#############################
# SORRY FOR MY CODE QUALITY #
#     IT'S A PROTOTYPE      #
#############################

##### CONFIG #####
window_size = (1000, 1000)
fps = 60

falling_debug = False

# window size must be divisible by pixel_size
pixel_size = 8

brush_size = 5

mapping_mode = False
##################

brush_start = brush_size // 2 * -1
brush_end = brush_size // 2 + 1


if window_size[0] % pixel_size != 0 or window_size[1] % pixel_size != 0:
    raise Exception("Window size must be divisible by pixel size")


map_size = (window_size[0] // pixel_size, window_size[1] // pixel_size)

# each pixel of map containts:
# tupple - color
# bool - is pixel a sand
# bool - is pixel falling
# int - id
map = np.zeros((map_size[1], map_size[0], 4), dtype=object)


# pygame init
pygame.init()
window = pygame.display.set_mode(window_size)
clock = pygame.time.Clock()


# make numpy random sequence deterministic
np.random.seed(0)


texture_name = "image.png"

if mapping_mode:
    # load image
    texture = Image.open(texture_name)
    # scale image to map size
    texture = texture.resize((map_size[0], map_size[1]))
    # convert image to flattened 2d numpy array (map_size[0] * map_size[1], 3)
    texture = np.array(texture).reshape((map_size[0] * map_size[1], 3))

    captured_movement = []

else:
    # load mapped texture from file
    mapped_texture = np.load(texture_name.split(".")[0] + "_texture.npy")

    # load captured movement from file
    captured_movement = np.load(texture_name.split(".")[0] + "_movement.npy")

    cap_mov_index = 0


color_hue = 0

calculate_physics = False
anything_moved = True

pixel_id = 0

#brush_pos_x = np.random.randint(map_size[0] - brush_size)
#brush_target_x = np.random.randint(map_size[0] - brush_size)

# main loop
delta_time = fps / 1000

frame = 0
while True:

    # events, keypresses, mouse input etc.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if mapping_mode:
            # if press m
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                print("Mapping and saving the texture...")

                mapping_ids = []

                # iterate over every sand pixel
                for y in range(map_size[1]):
                    for x in range(map_size[0]):
                        if map[y, x, 1]:
                            mapping_ids.append(map[y, x, 3])
                        else:
                            mapping_ids.append(-1)

                # combine texture and mapping ids
                texture_sorted = np.concatenate((texture, np.array(mapping_ids).reshape((map_size[0] * map_size[1], 1))), axis=1)
                # sort texture by mapping ids
                texture_sorted = texture_sorted[texture_sorted[:, 3].argsort()]
                # remove pixels with mapping id -1
                texture_sorted = texture_sorted[texture_sorted[:, 3] != -1]
                # remove mapping ids
                texture_sorted = texture_sorted[:, :3]

                # save as numpy array to file
                np.save(texture_name.split(".")[0] + "_texture.npy", texture_sorted)

                # save captured movement to file
                np.save(texture_name.split(".")[0] + "_movement.npy", np.array(captured_movement))

                print("Done!")

    # process physics
    if calculate_physics:

        # if nothing moved in last frame, disable physics processing
        if not anything_moved:
            calculate_physics = False
            anything_moved = True

        else:
            anything_moved = False
            map_phys_processing = np.copy(map)

            for y in range(map_size[1]):
                # invert y
                y = map_size[1] - y - 1

                x_range = np.arange(map_size[0])
                # shuffle x_range
                np.random.shuffle(x_range)

                for x in x_range:

                    # if sand is falling
                    if map[y, x, 2]:

                        # if map is still below
                        if y + 1 < map_size[1]:

                            # if pixel below is empty
                            if not map_phys_processing[y + 1, x, 1]:
                                # move sand down
                                map_phys_processing[y + 1, x] = map[y, x]

                                # reset current pixel
                                map_phys_processing[y, x] = ((0, 0, 0), False, False, 0)

                                anything_moved = True

                            # else pixel below is sand
                            else:
                                ## if pixel below not falling
                                #if not map_phys_processing[y + 1, x, 2]:
                                empty_side_pixels = []
                                # if pixel to the left below is empty
                                if x - 1 >= 0 and not map_phys_processing[y + 1, x - 1, 1]:
                                    empty_side_pixels.append((y + 1, x - 1))
                                # if pixel to the right below is empty
                                if x + 1 < map_size[0] and not map_phys_processing[y + 1, x + 1, 1]:
                                    empty_side_pixels.append((y + 1, x + 1))

                                # if len empty_side_pixels is 1, move sand to that pixel
                                if len(empty_side_pixels) == 1:
                                    map_phys_processing[empty_side_pixels[0]] = map[y, x]
                                    map_phys_processing[y, x] = ((0, 0, 0), False, False, 0)
                                    anything_moved = True

                                # if len empty_side_pixels is 2, move sand to random pixel
                                elif len(empty_side_pixels) == 2:
                                    random_pixel = empty_side_pixels[np.random.randint(2)]
                                    map_phys_processing[random_pixel] = map[y, x]
                                    map_phys_processing[y, x] = ((0, 0, 0), False, False, 0)
                                    anything_moved = True

                                # if len empty_side_pixels is 0 and pixels below left and right are not falling, disable falling
                                elif len(empty_side_pixels) == 0:
                                    not_falling_side_belows = 0
                                    if not x - 1 >= 0 or not map_phys_processing[y + 1, x - 1, 2]:
                                        not_falling_side_belows += 1
                                    if not x + 1 < map_size[0] or not map_phys_processing[y + 1, x + 1, 2]:
                                        not_falling_side_belows += 1

                                    if not_falling_side_belows == 2:
                                        map_phys_processing[y, x, 2] = False

                        else:
                            # disable falling
                            map_phys_processing[y, x, 2] = False

            map = map_phys_processing


    
    # mouse press
    if (pygame.mouse.get_pressed()[0] and mapping_mode) or (not mapping_mode and cap_mov_index < len(captured_movement) and captured_movement[cap_mov_index, 2] == frame):
        # plaace sand
        if mapping_mode:
            mouse_pos = pygame.mouse.get_pos()
        else:
            mouse_pos = captured_movement[cap_mov_index, :2] * pixel_size
            mouse_pos = (mouse_pos[1], mouse_pos[0])
            cap_mov_index += 1

        # clamp mouse pos
        if mouse_pos[0] < 0:
            mouse_pos = (0, mouse_pos[1])
        if mouse_pos[1] < 0:
            mouse_pos = (mouse_pos[0], 0)
        if mouse_pos[0] >= window_size[0]:
            mouse_pos = (window_size[0] - 1, mouse_pos[1])
        if mouse_pos[1] >= window_size[1]:
            mouse_pos = (mouse_pos[0], window_size[1] - 1)

        pixel_pos = (mouse_pos[1] // pixel_size, mouse_pos[0] // pixel_size)

        if mapping_mode:
            captured_movement.append((*pixel_pos, frame))

            color = colorsys.hsv_to_rgb(color_hue, 1, 1)
            color = (color[0] * 255, color[1] * 255, color[2] * 255)

        any_pixel_placed = False


        for y in range(brush_start, brush_end):
            for x in range(brush_start, brush_end):

                # if pixel is in map
                if pixel_pos[0] + y >= 0 and pixel_pos[0] + y < map_size[1] and pixel_pos[1] + x >= 0 and pixel_pos[1] + x < map_size[0]:

                    # if pixel is empty
                    if not map[pixel_pos[0] + y, pixel_pos[1] + x, 1]:

                        if not mapping_mode:
                            color = mapped_texture[pixel_id]

                        # place sand
                        map[pixel_pos[0] + y, pixel_pos[1] + x] = (color, True, True, pixel_id)
                        any_pixel_placed = True
                        pixel_id += 1
        


        if any_pixel_placed:
            if mapping_mode:
                color_hue += 0.01
                if color_hue >= 1:
                    color_hue -= 1

            calculate_physics = True

    

    ## place sand at random x pos
    #if True:#np.random.randint(0) == 0:
    #    for y in range(brush_start, brush_end):
    #        for x in range(brush_start, brush_end):
    #            
    #            # if pixel is empty
    #            if not map[y - brush_start, brush_pos_x + x, 1]:
    #                map[y - brush_start, brush_pos_x + x] = ((255, 255, 255) if mapping_mode else (mapped_texture[pixel_id, 0], mapped_texture[pixel_id, 1], mapped_texture[pixel_id, 2]), True, True, pixel_id)
    #                pixel_id += 1
    #    
    #    calculate_physics = True
#
    #    # calculate direction of pos x movement
    #    if brush_pos_x - brush_target_x < 0:
    #        brush_pos_x_direction = 1
    #    elif brush_pos_x - brush_target_x > 0:
    #        brush_pos_x_direction = -1
    #    else:
    #        brush_pos_x_direction = 0
#
    #    # move brush pos x
    #    brush_pos_x += brush_pos_x_direction
#
    #    # if its already at brush target x, change target x
    #    if brush_pos_x == brush_target_x:
    #        brush_target_x = np.random.randint(-20, map_size[0] - brush_size)


    window.fill((0, 0, 0))
    
    # render map
    for y in range(map_size[1]):
        for x in range(map_size[0]):
            if map[y, x, 1]:
                if falling_debug:
                    pygame.draw.rect(window, (0, 255, 0) if map[y, x, 2] else (255, 0, 0), (x * pixel_size, y * pixel_size, pixel_size, pixel_size))
                else:
                    pygame.draw.rect(window, map[y, x, 0], (x * pixel_size, y * pixel_size, pixel_size, pixel_size))


    # update
    pygame.display.update()
    delta_time = clock.tick(fps) / 1000
    frame += 1