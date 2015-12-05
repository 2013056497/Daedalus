import pygame
import os
import random
import time
pygame.init()
class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.FPS = 15
        self.white = (250,250,250)
        self.black = (0,0,0)
        self.gameDisplay = pygame.display.set_mode((800,600))
        pygame.display.set_caption('Daedalus: Labyrinth Escape Game')
        self.width,self.height = 25,19
        #font & loading
        self.font1 = pygame.font.Font(os.path.join('data','slkscr.ttf'),24)
        self.font = pygame.font.Font(os.path.join('data','slkscr.ttf'),36)
        self.load_text = self.font.render('Loading . . .',1,self.white)
        self.gameDisplay.blit(self.load_text, (310,300))
        pygame.display.update()
        #sound
        self.intro_sound = pygame.mixer.Sound(os.path.join('data','intro_roar.wav'))
        self.menu_sound = pygame.mixer.Sound(os.path.join('data','menu.ogg'))
        self.lab_sound = pygame.mixer.Sound(os.path.join('data','lab.ogg'))
        #images
        self.narration = (
            pygame.image.load(os.path.join('data','King Minos.gif')),
            pygame.image.load(os.path.join('data','Minotaur.gif')),
            pygame.image.load(os.path.join('data','Theseus.gif')),
            pygame.image.load(os.path.join('data','Labyrinth Gate.gif')))
        self.floor = pygame.image.load(os.path.join('data','floor.png'))
        self.verwall = pygame.image.load(os.path.join('data','verwall.png'))
        self.horwall = pygame.image.load(os.path.join('data','horwall.png'))
        self.goal = pygame.image.load(os.path.join('data','goal.png'))
        self.startscreen = pygame.image.load(os.path.join('data','Start.gif'))
        self.gameover_scr = pygame.image.load(os.path.join('data','gameover.gif'))
        #theseus
        self.theseus_sprite = pygame.image.load(os.path.join('data','Theseus.png'))
        self.theseus_x = 0
        self.theseus_y = 0
        #thread
        self.threadlist = []
        #walls
        self.walls=[]
        #minotaur
        self.mino_spriteL = pygame.image.load(os.path.join('data','MinotaurR.png'))
        self.mino_spriteR = pygame.image.load(os.path.join('data','MinotaurL.png'))
        self.mino_x = random.randrange(160,800,32)
        self.mino_y = random.randrange(160,600,32)
        #level
        self.current_lvl = 1
        self.status = "Start"
        self.source = int(self.theseus_y//32*self.width+self.theseus_x//32)
        self.shortest_path = self.dijkstra(self.source,self.walls,self.width,self.height)
        self.moves=0
        self.mino_moves=0
        self.cell = int(self.mino_y//32*self.width+self.mino_x//32)
        self.moved=False
        #fade
        self.alphaSurface = pygame.Surface((800,600))
        self.alphaSurface.fill((255,255,255))
        self.alphaSurface.set_alpha(255)
        self.alph = 255

    def screen(self):
        press_text = self.font.render('Press Enter',1,self.white)
        proceed = False
        self.menu_sound.play(loops=-1)
        self.gameDisplay.blit(self.startscreen,(0,0))
        pygame.display.update()
        disp = True
        while not proceed:
            disp = not disp
            self.gameDisplay.blit(self.startscreen,(0,0))
            if disp:
                self.gameDisplay.blit(press_text,(290,365))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.intro_sound.play()
                        while not self.alph<=0:
                            self.gameDisplay.fill((0,0,0))
                            self.alph -= .6
                            self.alphaSurface.set_alpha(self.alph)
                            self.gameDisplay.blit(self.alphaSurface,(0,0))
                            pygame.display.update()
                            proceed = True
            self.clock.tick(3)
            pygame.display.update()
        self.story()

    def story(self):
        i=0
        while not i>=4:
            self.gameDisplay.blit(self.narration[i],(0,0))
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        i += 1
        self.menu_sound.stop()
        self.labyrinth()

    def labyrinth(self):
        self.gameDisplay.fill(self.black)
        warning = self.font1.render('Beware: The Minotaur knows secret passages',1,self.white)
        warning1 = self.font1.render('throughout his labyrinth.',1,self.white)
        self.gameDisplay.blit(warning, (75,390))
        self.gameDisplay.blit(warning1, (190,440))
        pygame.display.update()
        self.threadlist=[]
        self.walls = self.generate_walls(self.width,self.height)
        self.theseus_x = 0#(self.width-1)*32
        self.theseus_y = 0#(self.height-1)*32
        if not self.status=="Start":
            self.mino_x = random.randrange(0,800,32)
            self.mino_y = random.randrange(0,600,32)
            self.source = int(self.theseus_y//32*self.width+self.theseus_x//32)
            self.shortest_path = self.dijkstra(self.source,self.walls,self.width,self.height)
            self.moves=0
            self.mino_moves=0
            self.cell = int(self.mino_y//32*self.width+self.mino_x//32)
        self.status = "Lose"
        self.lab_sound.play(-1)
        self.gameDisplay.fill(self.white)
        gameover = False
        while not gameover:
            threadhead=[]
            self.gameDisplay.blit(self.floor,(0,0))
            self.gameDisplay.blit(self.goal,(772,572))
            for wall in self.walls:
                if wall[0]==wall[2]:
                    self.gameDisplay.blit(self.horwall,(wall[2]*32,wall[3]*32-4))
                elif wall[1]==wall[3]:
                    self.gameDisplay.blit(self.verwall,(wall[2]*32-4,wall[3]*32))
            self.moved=False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    key = pygame.key.get_pressed()
                    if key[pygame.K_UP]:
                        if self.theseus_y>0:
                            if self.is_passable(self.theseus_x,self.theseus_y,"up"):
                                self.moves+=1
                                self.theseus_y-=32
                                threadhead.append(self.theseus_x)
                                threadhead.append(self.theseus_y)
                                threadhead.append("up")
                                self.minotaur_move()
                    elif key[pygame.K_DOWN]:
                        if self.theseus_y<568:
                            if self.is_passable(self.theseus_x,self.theseus_y,"down"):
                                self.moves+=1
                                self.theseus_y+=32
                                threadhead.append(self.theseus_x)
                                threadhead.append(self.theseus_y)
                                threadhead.append("down")
                                self.minotaur_move()
                    elif key[pygame.K_LEFT]:
                        if self.theseus_x>0:
                            if self.is_passable(self.theseus_x, self.theseus_y,"left"):
                                self.moves+=1
                                self.theseus_x-=32
                                threadhead.append(self.theseus_x)
                                threadhead.append(self.theseus_y)
                                threadhead.append("left")
                                self.minotaur_move()
                    elif key[pygame.K_RIGHT]:
                        if self.theseus_x<768:
                            if self.is_passable(self.theseus_x, self.theseus_y,"right"):
                                self.moves+=1
                                self.theseus_x+=32
                                threadhead.append(self.theseus_x)
                                threadhead.append(self.theseus_y)
                                threadhead.append("right")
                                self.minotaur_move()
                    self.threadlist.append(threadhead)
            pygame.draw.lines(self.gameDisplay, (255,0,0), True, [(self.mino_x+4,self.mino_y+4), (self.mino_x+24,self.mino_y+4), (self.mino_x+24,self.mino_y+24), (self.mino_x+4,self.mino_y+24)], 1)
            self.thread(self.threadlist)
            self.gameDisplay.blit(self.theseus_sprite,(self.theseus_x,self.theseus_y))
            if self.mino_x>=self.theseus_x:
                self.gameDisplay.blit(self.mino_spriteR,(self.mino_x-25, self.mino_y-65))
            else:
                self.gameDisplay.blit(self.mino_spriteL,(self.mino_x-42, self.mino_y-65))
            pygame.display.update()
            if self.theseus_x == self.mino_x and self.theseus_y == self.mino_y:
                self.status = "Lose"
                gameover=True
            elif self.theseus_x == (self.width-1)*32 and self.theseus_y == (self.height-1)*32:
                self.current_lvl+=1
                self.status="Win"
                gameover=True
        time.sleep(.8)
        self.lab_sound.stop()

    def gameover(self):
        if self.status == "Start":
            return True
        self.gameDisplay.fill(self.black)
        done=False
        while not done:
            if self.status=="Lose":
                self.gameDisplay.blit(self.gameover_scr,(0,0))
                text = self.font.render('Press R to Restart,',1,self.white)
                text3 = self.font.render('Q to Quit',1,self.white)
                text1 = self.font.render('Level Reached: '+str(self.current_lvl),1,self.white)
                self.gameDisplay.blit(text, (200,430))
                self.gameDisplay.blit(text1, (235,365))
                self.gameDisplay.blit(text3, (320,475))
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            pygame.quit()
                            quit()
                        elif event.key == pygame.K_r:
                            self.current_lvl =1
                            done = True
            else:
                text2 = self.font.render('Next Level: '+str(self.current_lvl),1,self.white)
                self.gameDisplay.blit(text2, (272,300))
                pygame.display.update()
                time.sleep(3)
                done = True
            pygame.display.update()
        return True

    def generate_walls(self,w,h):
        width, height = w, h
        # create a list of all walls
        # (all connections between squares in the maze)
        # add all of the vertical walls into the list
        walls = [(x,y,x+1,y)
            for x in range(width-1)
            for y in range(height)]
        # add all of the horizontal walls into the list
        walls.extend([(x,y,x,y+1)
            for x in range(width)
            for y in range(height-1)])
        # create a set for each square in the maze
        cell_sets = [set([(x,y)])
            for x in range(width)
            for y in range(height)]
        # in Kruskal's algorithm, the walls need to be
        # visited in order of weight
        # since we want a random maze, we will shuffle
        # it and pretend that they are sorted by weight
        walls_copy = walls[:]
        random.shuffle(walls_copy)
        for wall in walls_copy:
            set_a = None
            set_b = None
            # find the sets that contain the squares
            # that are connected by the wall
            for s in cell_sets:
                if (wall[0], wall[1]) in s:
                    set_a = s
                if (wall[2], wall[3]) in s:
                    set_b = s
            # if the two squares are in separate sets,
            # then combine the sets and remove the
            # wall that connected them
            if set_a is not set_b:
                cell_sets.remove(set_a)
                cell_sets.remove(set_b)
                cell_sets.append(set_a.union(set_b))
                walls.remove(wall)
        return walls

    def dijkstra(self,source,walllist,width,height):
        #EDGES: walls width height | returns: edges
        edge_u=[]
        edge_v=[]
        size=height*width
        inf=float('infinity')
        edges = [(x,y,x+1,y)
            for x in range(width-1)
            for y in range(height)]
        edges.extend([(x,y,x,y+1)
            for x in range(width)
            for y in range(height-1)])
        for edge_ in edges:
            for wall in walllist:
                if edge_ == wall:
                    i=edges.index(edge_)
                    del edges[i]
        for edge in edges:
            u=edge[1]*width+edge[0]
            v=edge[3]*width+edge[2]
            edge_u.append(u)#first node
            edge_v.append(v)#second node
        #ADJMAT: size e_u e_v | returns: adjmat
        adjMatrix = [[inf for i in range(size)] for k in range(size)]
        for i in range(len(edge_u)):
            u = edge_u[i]
            v = edge_v[i]
            adjMatrix[u][v] = 1
            adjMatrix[v][u] = 1
        #DIJKSTRA: graph,source | returns: dist,pred
        # Graph[u][v] is the weight from u to v (however 0 means infinity)
        n = len(adjMatrix)
        dist = [inf]*n   # Unknown distance function from source to v
        previous = [inf]*n # Previous node in optimal path from source
        dist[source] = 0        # Distance from source to source
        Q = list(range(n)) # All nodes in the graph are unoptimized - thus are in Q
        while Q:           # The main loop
            u = min(Q, key=lambda n:dist[n]) # vertex in Q with smallest dist[]
            Q.remove(u)
            if dist[u] == inf:
                break # all remaining vertices are inaccessible from source
            for v in range(n):               # each neighbor v of u
                if adjMatrix[u][v] and (v in Q): # where v has not yet been visited
                    alt = dist[u] + adjMatrix[u][v]
                    if alt < dist[v]:       # Relax (u,v,a)
                        dist[v] = alt
                        previous[v] = u
        return previous

    def minotaur_move(self):
        if self.moves % (6 - self.current_lvl) == 0 and self.theseus_x != 0 and self.theseus_y != 0:
            if self.mino_moves % (10 - self.current_lvl) == 0 or self.cell == self.source:
                self.thread(self.threadlist)
                self.gameDisplay.blit(self.theseus_sprite,(self.theseus_x,self.theseus_y))
                pygame.draw.lines(self.gameDisplay, (255,0,0), True, [(self.mino_x+4,self.mino_y+4), (self.mino_x+24,self.mino_y+4), (self.mino_x+24,self.mino_y+24), (self.mino_x+4,self.mino_y+24)], 1)
                if self.mino_x>=self.theseus_x:
                    self.gameDisplay.blit(self.mino_spriteR,(self.mino_x-25, self.mino_y-65))
                else:
                    self.gameDisplay.blit(self.mino_spriteL,(self.mino_x-42, self.mino_y-65))
                text = [self.font1.render('The Minotaur follows...',1,self.white),
                        self.font1.render('The Minotaur smells your blood...',1,self.white),
                        self.font1.render('The Minotaur is on the hunt...',1,self.white)
                        ]
                self.gameDisplay.blit(text[random.randrange(0,3)], (170,430))
                pygame.display.update()
                self.source = int(self.theseus_y//32*self.width+self.theseus_x//32)
                self.shortest_path = self.dijkstra(self.source,self.walls,self.width,self.height)
            if self.shortest_path[self.cell]!=float('infinity'):
                if not self.moved:
                    self.cell = self.shortest_path[self.cell]
                    self.mino_moves+=1
                    self.moved=True
                self.mino_x=(self.cell%self.width)*32
                self.mino_y=(self.cell//self.width)*32

    def is_passable(self,theseus_x,theseus_y,direction):
        passable=True
        for wall in self.walls:
            if direction=="up":
                if wall[0]*32==theseus_x and wall[1]*32==theseus_y-32 and wall[2]*32==theseus_x and wall[3]*32==theseus_y:
                    passable = False
            elif direction=="down":
                if wall[0]*32==theseus_x and wall[1]*32==theseus_y and wall[2]*32==theseus_x and wall[3]*32==theseus_y+32:
                    passable = False
            elif direction=="left":
                if wall[0]*32==theseus_x-32 and wall[1]*32==theseus_y and wall[2]*32==theseus_x and wall[3]*32==theseus_y:
                    passable = False
            elif direction=="right":
                if wall[0]*32==theseus_x and wall[1]*32==theseus_y and wall[2]*32==theseus_x+32 and wall[3]*32==theseus_y:
                    passable = False
        return passable

    def thread(self,threadlist):
        for XnY in threadlist:
            if len(XnY)!=0:
                if XnY[2]=='up':
                    pygame.draw.line(self.gameDisplay,(255,215,0),(XnY[0]+16,XnY[1]+16),(XnY[0]+16,XnY[1]+48))
                elif XnY[2]=='down':
                    pygame.draw.line(self.gameDisplay,(255,215,0),(XnY[0]+16,XnY[1]+16),(XnY[0]+16,XnY[1]-16))
                elif XnY[2]=='left':
                    pygame.draw.line(self.gameDisplay,(255,215,0),(XnY[0]+16,XnY[1]+16),(XnY[0]+48,XnY[1]+16))
                elif XnY[2]=='right':
                    pygame.draw.line(self.gameDisplay,(255,215,0),(XnY[0]+16,XnY[1]+16),(XnY[0]-16,XnY[1]+16))