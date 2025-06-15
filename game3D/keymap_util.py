# Utility to map string key names to pygame key constants
import pygame
from pygame.locals import *

KEY_NAME_TO_PYGAME = {
    'a': K_a,
    'b': K_b,
    'c': K_c,
    'd': K_d,
    'e': K_e,
    'f': K_f,
    'g': K_g,
    'h': K_h,
    'i': K_i,
    'j': K_j,
    'k': K_k,
    'l': K_l,
    'm': K_m,
    'n': K_n,
    'o': K_o,
    'p': K_p,
    'q': K_q,
    'r': K_r,
    's': K_s,
    't': K_t,
    'u': K_u,
    'v': K_v,
    'w': K_w,
    'x': K_x,
    'y': K_y,
    'z': K_z,
    'space': K_SPACE,
    '1': K_1,
    '2': K_2,
    '3': K_3,
    '4': K_4,
    '5': K_5,
    '6': K_6,
    '7': K_7,
    '8': K_8,
    '9': K_9,
    '0': K_0,
    # Add more as needed
}

def get_key_constant(key_name):
    return KEY_NAME_TO_PYGAME.get(key_name.lower())
