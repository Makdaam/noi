#!/usr/bin/env python
import libtcodpy as libtcod
import os
import random

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
MAP_WIDTH = 70
MAP_HEIGHT = 50
START_X = 35
START_Y = 25

LIMIT_FPS = 20

state = {}

class Entity:
    def __init__(self, x, y, char, color, background=libtcod.black, walkable = True):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.background = background
        self.walkable = walkable
 
    def move(self, dx, dy, check_collisions=True):
        global state

        if check_collisions:
            #map
            mp = state['maps'][state['current_level']]
            if not mp[self.x+dx][self.y+dy].walkable:
                return
            #entities
            for e in state['entities'][state['current_level']]:
                if e.x==self.x+dx and e.y==self.y+dy:
                    if e.pushed_by:
                        e.pushed_by(self)
                    if not e.walkable:
                        return
        #move by the given amount
        self.x += dx
        self.y += dy
 
    def draw(self, con=0):
        #set the color and then draw the character that represents this object at its position
        libtcod.console_set_default_foreground(con, self.color)
        libtcod.console_put_char(con, self.x, self.y, self.char, self.background)
 
    def clear(self):
        #erase the character that represents this object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)


def pick_walkable_tile(tilemap):
    x = random.randint(0,MAP_WIDTH-1)
    y = random.randint(0,MAP_HEIGHT-1)
    while (not tilemap[x][y].walkable):
        x = random.randint(0,MAP_WIDTH-1)
        y = random.randint(0,MAP_HEIGHT-1)
    return (x,y)

def generate_maps():
    global state

    #map 0 - surface
    mp = state['maps'][0]
    #landing site
    mp[START_X-1][START_Y-1].solidify('\xc9')
    mp[START_X][START_Y-1].solidify('\xcd')
    mp[START_X+1][START_Y-1].solidify('\xbb')
    mp[START_X-1][START_Y].solidify('\xc8')
    mp[START_X+1][START_Y].solidify('\xbc')

    #random mountains
    for i in range(MAP_WIDTH):
        for j in range(MAP_HEIGHT):
            if (i-START_X)*(i-START_X)+(j-START_Y)*(j-START_Y)>16:
                #if further away from the landing site
                if random.random()<0.2:
                    mp[i][j].solidify(random.choice(['^','#']))
    
    #place teleport to next level
    coords = pick_walkable_tile(mp)
    state['entities'][0].append(Teleport(coords[0],coords[1],'>',10,10,1,libtcod.grey))

    #place spaceship entrance
    state['entities'][0].append(Spaceship(START_X,START_Y))

def init_state():
    global state
    
#    state['seed'] = os.urandom(8)
    state['seed'] = 0
    random.seed(state['seed'])

    libtcod.console_set_custom_font('dejavu10x10_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
    state['buffer']={}
    state['buffer']['map'] = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
    con = state['buffer']['map']
    libtcod.console_set_default_foreground(con, libtcod.grey)
    libtcod.console_set_default_background(con, libtcod.black)


    state['maps'] = {}
    state['maps'][0] = make_map()
    state['maps'][1] = make_map()
    state['maps'][2] = make_map()
    state['maps'][3] = make_map()
    state['maps'][4] = make_map()

    state['entities']={}
    state['entities'][0] = list()
    state['entities'][1] = list()
    state['entities'][2] = list()
    state['entities'][3] = list()
    state['entities'][4] = list()

    generate_maps()

    state['current_level'] = 0
    state['player'] = Entity(START_X,START_Y,'@',libtcod.white)


def make_map():
    #fill map with "unblocked" tiles
    tilemap = [[ Tile()
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]
    return tilemap

class Teleport(Entity):
    def __init__(self, x, y, char,destx,desty,destz, color, background=libtcod.black):
        self.destx = destx
        self.desty = desty
        self.destz = destz
        Entity.__init__(self,x,y,char,color,background,True)
    
    def pushed_by(self,entity):
        global state
        if (entity == state['player']):
            state['current_level']=self.destz
            state['player'].x = self.destx
            state['player'].y = self.desty

class Spaceship(Entity):
    def __init__(self,x,y):
        Entity.__init__(self,x,y,'O',libtcod.white,libtcod.white,True)

    def pushed_by(self,entity):
        global state
        if (entity == state['player']):
            #TODO show menu
            pass
        else:
            #TODO Kill it
            pass


class Tile:
    def __init__(self, walkable = True, transparent = True, char = '.', color=libtcod.grey, background=libtcod.black ):
        self.walkable = walkable
        self.transparent = transparent
        self.char = char
        self.color = color
        self.background = background

    def draw(self, x, y, con):
        #set the color and then draw the character that represents this object at its position
        libtcod.console_set_default_foreground(con, self.color)
        libtcod.console_put_char(con, x, y, self.char, self.background)

    def solidify(self,char='#', color=None ,background=None):
        self.walkable = False
        self.transparent = False
        self.char=char
        if color:
            self.color=color
        if background:
            self.background=background


def handle_keys():
 
    key = libtcod.console_wait_for_keypress(True)
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
 
    elif key.vk == libtcod.KEY_ESCAPE:
        return True  #exit game

    #movement keys
    if libtcod.console_is_key_pressed(libtcod.KEY_UP):
        state['player'].move(0,-1)
 
    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
        state['player'].move(0,1)
 
    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
        state['player'].move(-1,0)
 
    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
        state['player'].move(1,0)

def render_map():
    global state
    con = state['buffer']['map']
    libtcod.console_clear(con)
    tilemap = state['maps'][state['current_level']]
    for i in range(len(tilemap)):
        for j in range(len(tilemap[i])):
            tilemap[i][j].draw(i,j,con)

def render_entities():
    global state

    for e in state['entities'][state['current_level']]:
        e.draw(state['buffer']['map'])

def blit_stuff():
    global state

    libtcod.console_clear(0)
    libtcod.console_blit(state['buffer']['map'],0,0,MAP_WIDTH,MAP_HEIGHT,0,0,0,1,1)
    #TODO make FOV
    state['player'].draw()
    libtcod.console_flush()

if __name__=='__main__':
    init_state()
    #menu

    #main game loop
    while not libtcod.console_is_window_closed():
        render_map()
        render_entities()
        blit_stuff()
        if handle_keys():
            break;
