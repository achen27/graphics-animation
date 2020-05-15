import mdl
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """
def first_pass( commands ):

    name = ''
    num_frames = 1
    vary = False

    for c in commands:
        if c['op'] == 'basename':
            name = c['args'][0]

        elif c['op'] == 'frames':
            num_frames = int(c['args'][0])

        elif c['op'] == 'vary':
            vary = True
    if vary and num_frames == 1:
        print("Vary found but no frames set.")
        exit()
    if num_frames > 1 and name == '':
        name = 'default'
        print("Setting bsename to 'default'")

    return (name, num_frames)

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def second_pass( commands, num_frames ):
    frames = [ {} for i in range(num_frames) ]
    # print("akjfbjesbfisbe")

    for c in commands:
        if c['op'] == 'vary':

            start_frame = int(c['args'][0])
            end_frame = int(c['args'][1])

            if end_frame > num_frames:
                print("end_frame is larger than total set frames")
                exit()

            if start_frame > end_frame:
                temp = start_frame
                start_frame = end_frame
                end_frame = temp
                print("Swapping start_frame and end_frame")

            start_knob = c['args'][2]
            end_knob = c['args'][3]
            knob = c['knob']

            value = (end_knob - start_knob) / (end_frame - start_frame)

            while start_frame <= end_frame:
                frames[start_frame][knob] = start_knob
                # print(frames)
                start_knob += value
                start_frame += 1

    return frames


def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print("Parsing failed.")
        return

    view = [0,
            0,
            1];
    ambient = [50,
               50,
               50]
    light = [[0.5,
              0.75,
              1],
             [255,
              255,
              255]]

    color = [0, 0, 0]
    symbols['.white'] = ['constants',
                         {'red': [0.2, 0.5, 0.5],
                          'green': [0.2, 0.5, 0.5],
                          'blue': [0.2, 0.5, 0.5]}]
    reflect = '.white'

    (name, num_frames) = first_pass(commands)
    frames = second_pass(commands, num_frames)

    i = 0
    anim = False
    if num_frames > 1:
        anim = True

    for f in range(num_frames):

        print("Saving frame: " + str(i))

        tmp = new_matrix()
        ident( tmp )

        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        step_3d = 100
        consts = ''
        coords = []
        coords1 = []

        if anim:
            # print(frames)
            for frame in frames[f]:
                symbols[frame][1] = frames[f][frame]
                # print symbols[frame]

        for command in commands:
            # print(command)
            c = command['op']
            args = command['args']
            knob_value = 1

            if c == 'box':
                if command['constants']:
                    reflect = command['constants']
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'

            elif c == 'sphere':
                if command['constants']:
                    reflect = command['constants']
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'

            elif c == 'torus':
                if command['constants']:
                    reflect = command['constants']
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'

            elif c == 'line':
                add_edge(tmp,
                         args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []

            elif c == 'move':
                xCor = args[0]
                yCor = args[1]
                zCor = args[2]
                if command['knob']:
                    xCor = xCor * symbols[command['knob']][1]
                    yCor = yCor * symbols[command['knob']][1]
                    zCor = zCor * symbols[command['knob']][1]
                tmp = make_translate(xCor, yCor, zCor)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []

            elif c == 'scale':
                xCor = args[0]
                yCor = args[1]
                zCor = args[2]
                if command['knob']:
                    xCor = xCor * symbols[command['knob']][1]
                    yCor = yCor * symbols[command['knob']][1]
                    zCor = zCor * symbols[command['knob']][1]
                tmp = make_scale(xCor, yCor, zCor)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []

            elif c == 'rotate':
                theta = args[1] * (math.pi/180)
                if command['knob']: theta = theta * symbols[command['knob']][1]
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []

            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )

            elif c == 'pop':
                stack.pop()

            elif c == 'display' and not anim:
                display(screen)

            elif c == 'save' and not anim:
                save_extension(screen, args[0])
            # end operation loop
        if anim:
            save_extension(screen, "./anim/"+ name + ("%03d"%i) + ".png")
            i += 1
    if anim:
        make_animation(name)
