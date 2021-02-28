#!/bin/env python3
# https://tetris.fandom.com/wiki/Tetris_Guideline
import pygame
# import pygame_gui
import random
import time
from pygame.locals import *

class BlockType:
    Empty = 0
    I = 1
    O = 2
    T = 3
    S = 4
    Z = 5
    J = 6
    L = 7

class Tetromino:
    block_type: BlockType
    position = (0, 0)
    angle = 0
    lock_start = 0
    last_move_time = 0
    last_drop_time = 0

    def __init__(self, block_type, position) -> None:
        self.block_type = block_type
        self.position = position
        self.rotations = {
            BlockType.I: {
                0: 0b0000111100000000,
                1: 0b0010001000100010,
                2: 0b0000000011110000,
                3: 0b0100010001000100},
            BlockType.O: {
                0: 0b1111,
                1: 0b1111,
                2: 0b1111,
                3: 0b1111},
            BlockType.T: {
                0: 0b010111000,
                1: 0b010011010,
                2: 0b000111010,
                3: 0b010110010},
            BlockType.S: {
                0: 0b011110000,
                1: 0b010011001,
                2: 0b000011110,
                3: 0b100110010},
            BlockType.Z: {
                0: 0b110011000,
                1: 0b001011010,
                2: 0b000110011,
                3: 0b010110100},
            BlockType.J: {
                0: 0b100111000,
                1: 0b011010010,
                2: 0b000111001,
                3: 0b010010110},
            BlockType.L: {
                0: 0b001111000,
                1: 0b010010011,
                2: 0b000111100,
                3: 0b110010010}}
        self.last_drop_time = time.time()

    def drop(self) -> None:
        self.position = (self.position[0], self.position[1] + 1)
        self.last_drop_time = time.time()

    def try_turn_clockwise(self, cells):
        if self.block_type == BlockType.I:
            rules = [[(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
 	                 [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
 	                 [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
 	                 [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)]]
        else:
            rules = [[(0, 0), (-1, 0), (-1, 1),(0, -2), (-1, -2)],
                     [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
                     [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
                     [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)]]
        for r in rules[self.angle]:
            # subtract rules position because playfield is reversed
            pos = (self.position[0] - r[0], self.position[1] - r[1])
            if not self.check_intersection(pos, cells, self.turn_clockwise()):
                self.position = pos
                self.angle = self.turn_clockwise()
                return True
        return False

    def try_turn_counterclockwise(self, cells):
        if self.block_type == BlockType.I:
            rules = [
                [(0, 0), (-1, 0), (2, 0), (-1, 2), ( 2, -1)],
                [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
 	            [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
 	            [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)]]
        else:
            rules = [
                [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
                [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
                [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
                [(0, 0), (-1, 0), (-1,-1), (0, 2), (-1, 2)]]
        for r in rules[self.angle]:
            # subtract rules position because playfield is reversed
            pos = (self.position[0] - r[0], self.position[1] - r[1])
            if not self.check_intersection(pos, cells, self.turn_counterclockwise()):
                self.position = pos
                self.angle = self.turn_counterclockwise()
                return True
        return False

    def turn_clockwise(self, angle=None) -> None:
        if angle is None:
            angle = self.angle
        angle += 1
        if angle == 4:
            angle = 0
        return angle

    def turn_counterclockwise(self, angle=None) -> None:
        if angle is None:
            angle = self.angle
        angle -= 1
        if angle == -1:
            angle = 3
        return angle

    def move_left(self):
        self.position = (self.position[0] - 1, self.position[1])

    def move_right(self):
        self.position = (self.position[0] + 1, self.position[1])

    def get_bb_dim(self):
        if self.block_type == BlockType.I:
            return (4, 4)
        elif self.block_type == BlockType.O:
            return (2, 2)
        else:
            return (3, 3)

    def int_repr(self) -> int:
        return self.rotations[self.block_type][self.angle]

    def check_grounded(self, playfield):
        d = self.get_bb_dim()
        for y in range(d[1]):
            for x in range(d[0]):
                if (self.int_repr() >> ((d[1] - y - 1) * d[0] + d[0] - x - 1)) & 1:
                    if (y + self.position[1] + 1 == 20
                        or playfield[y + self.position[1] + 1][x + self.position[0]] != BlockType.Empty):
                        self.lock_start = time.time()
                        self.last_drop_time = time.time()
                        return
        self.lock_start = 0

    def check_intersection(self, position, playfield, angle=None):
        d = self.get_bb_dim()
        if angle is None:
            angle = self.angle
        r = self.rotations[self.block_type][angle]
        for y in range(d[1]):
            for x in range(d[0]):
                if (r >> ((d[1] - y - 1) * d[0] + d[0] - x - 1)) & 1:
                    if x + position[0] < 0 or x + position[0] > 9 or y + position[1] > 19:
                        return True
                    elif y + position[1] < 0:
                        continue
                    elif playfield[y + position[1]][x + position[0]] != BlockType.Empty:
                        return True
        return False

class Playfield:
    width: int = 10
    height: int = 20

    level: int = 1
    score: int = 0
    current_level_score: int = 0
    going = True
    ghost_position = (0, 0)
    line_clear_start = 0
    held_piece = None
    can_hold = True
    time_constant = 1.0

    cell_dim = (30, 30)

    def __init__(self) -> None:
        self.cells = [[None] * self.width for i in range(self.height)]
        for y in range(len(self.cells)):
            for x in range(len(self.cells[0])):
                self.cells[y][x] = 0

        self.block_sprites = {
            BlockType.I: Playfield.create_block_sprite(self.cell_dim, 3, (0, 200, 200)),
            BlockType.O: Playfield.create_block_sprite(self.cell_dim, 3, (200, 200, 0)),
            BlockType.T: Playfield.create_block_sprite(self.cell_dim, 3, (200, 0, 200)),
            BlockType.S: Playfield.create_block_sprite(self.cell_dim, 3, (0, 200, 0)),
            BlockType.Z: Playfield.create_block_sprite(self.cell_dim, 3, (200, 0, 0)),
            BlockType.J: Playfield.create_block_sprite(self.cell_dim, 3, (80, 80, 200)),
            BlockType.L: Playfield.create_block_sprite(self.cell_dim, 3, (200, 100, 0))
        }

        self.block_sprites[BlockType.Empty] = pygame.Surface(self.cell_dim)
        self.block_sprites[BlockType.Empty].fill((32, 32, 32))
        pygame.draw.rect(self.block_sprites[BlockType.Empty],
                         (16, 16, 16),
                         pygame.Rect((0, 0), self.cell_dim),
                         width=1)

        self.shadow = pygame.Surface(self.cell_dim)
        self.shadow.fill((32, 32, 32))
        pygame.draw.rect(self.shadow, (64, 64, 64), (0, 0, 30, 30), width=2)

        self.current_piece = Tetromino(random.randrange(1, 8), (self.width // 2 - 1, 0))
        self.next_piece = Tetromino(random.randrange(1, 8), (self.width // 2 - 1, 0))
        self.ghost_position = self.calc_ghost()

        self.surface = pygame.Surface((self.cell_dim[0]*10, self.cell_dim[1]*20))
        self.hold_surface = pygame.Surface((self.cell_dim[0]*4, self.cell_dim[1]*4))
        self.next_surface = pygame.Surface((self.cell_dim[0]*4, self.cell_dim[1]*4))
        self.repaint()

    def create_block_sprite(dim, v, color) -> pygame.Surface:
        lighter_color = [min(255, color[i] + 64) for i in range(3)]
        lightest_color = [min(255, color[i] + 96) for i in range(3)]
        darker_color = [max(0, color[i] - 64) for i in range(3)]
        darkest_color = [max(0, color[i] - 96) for i in range(3)]
        block = pygame.Surface(dim)
        block.fill(color)
        # top
        pygame.draw.polygon(block, lightest_color, [(0,0), (dim[0], 0), (dim[0] - v, v), (v, v)])
        # left
        pygame.draw.polygon(block, lighter_color, [(0,0), (0, dim[1]), (v, dim[1] - v), (v, v)])
        # right
        pygame.draw.polygon(block, darker_color, [(dim[0] - v, v),
                                                  (dim[0], 0),
                                                  (dim[0], dim[1]),
                                                  (dim[0] - v, dim[1] - v)])
        # bottom
        pygame.draw.polygon(block, darkest_color, [(0, dim[1]),
                                                   (v, dim[1] - v),
                                                   (dim[0] - v, dim[1] - v),
                                                   (dim[0], dim[1])])
        return block

    def transfer_piece(self):
        d = self.current_piece.get_bb_dim()
        pos = self.current_piece.position
        for y in range(d[1]):
            for x in range(d[0]):
                if (self.current_piece.int_repr() >> ((d[1] - y - 1) * d[0] + d[0] - x - 1)) & 1:
                    self.cells[y + pos[1]][x + pos[0]] = self.current_piece.block_type

    def calc_ghost(self):
        for y in range(self.current_piece.position[1], self.height):
            if self.current_piece.check_intersection((self.current_piece.position[0],
                                                      y + 1),
                                                     self.cells):
                return (self.current_piece.position[0], y)
        return self.current_piece.position

    def clear_lines(self) -> None:
        for y in range(self.height-1, 0, -1):
            combo = 0
            while sum([1 for c in self.cells[y] if c != BlockType.Empty]) == self.width:
                combo += 1
                for i in range(y, 0, -1):
                    self.cells[i][:] = self.cells[i-1][:]
                self.cells[0] = [BlockType.Empty for x in range(self.width)]

            self.score += [0, 1, 3, 5, 8][combo]
            self.current_level_score += [0, 1, 3, 5, 8][combo]

        if self.current_level_score > (10 * self.level) and self.level < 20:
            self.level += 1
            self.current_level_score = 0
            self.time_constant = (0.8 - ((self.level - 1) * 0.007)) ** (self.level - 1)

    def add_next_piece(self):
        self.current_piece = self.next_piece
        self.next_piece = Tetromino(random.randrange(1, 8), (self.width // 2 - 1, -1))

    def hold_piece(self):
        if self.held_piece:
            tmp = Tetromino(self.current_piece.block_type, (self.width // 2 - 1, -1))
            self.current_piece = self.held_piece
            self.held_piece = tmp
        else:
            self.held_piece = Tetromino(self.current_piece.block_type, (self.width // 2 - 1, -1))
            self.add_next_piece()
        self.can_hold = False

    def update(self, events) -> bool:
        if not self.going:
            return False
        for event in events:
            if event.type == KEYDOWN:
                if event.key == K_LEFT or event.key == K_q:
                    if self.current_piece.try_turn_clockwise(self.cells):
                        self.ghost_position = self.calc_ghost()
                        self.current_piece.check_grounded(self.cells)
                elif event.key == K_RIGHT or event.key == K_e:
                    if self.current_piece.try_turn_counterclockwise(self.cells):
                        self.ghost_position = self.calc_ghost()
                        self.current_piece.check_grounded(self.cells)
                elif event.key == K_a:
                    if not self.current_piece.check_intersection((self.current_piece.position[0] - 1,
                                                                  self.current_piece.position[1]),
                                                                 self.cells):
                        self.current_piece.move_left()
                        self.ghost_position = self.calc_ghost()
                        self.current_piece.check_grounded(self.cells)
                elif event.key == K_d:
                    if not self.current_piece.check_intersection((self.current_piece.position[0] + 1,
                                                                  self.current_piece.position[1]),
                                                                 self.cells):
                        self.current_piece.move_right()
                        self.ghost_position = self.calc_ghost()
                        self.current_piece.check_grounded(self.cells)
                elif event.key == K_s or event.key == K_DOWN:
                    if not self.current_piece.check_intersection((self.current_piece.position[0],
                                                                  self.current_piece.position[1] + 1),
                                                                 self.cells):
                        self.current_piece.drop()
                        self.ghost_position = self.calc_ghost()
                        self.current_piece.check_grounded(self.cells)

                elif event.key == K_SPACE:
                    for y in range(self.height):
                        if not self.current_piece.check_intersection((self.current_piece.position[0],
                                                                      self.current_piece.position[1] + 1),
                                                                     self.cells):
                            self.current_piece.drop()
                            self.ghost_position = self.calc_ghost()
                            self.current_piece.check_grounded(self.cells)
                            self.current_piece.last_drop_time = time.time()
                        else:
                            break
                elif event.key == K_TAB and self.can_hold:
                    self.hold_piece()

        if self.current_piece.lock_start > 0 and time.time() - self.current_piece.lock_start > 0.5:
            self.transfer_piece()
            self.clear_lines()
            self.add_next_piece()
            self.can_hold = True
            self.ghost_position = self.calc_ghost()
            if not self.current_piece.check_intersection((self.current_piece.position[0],
                                                          self.current_piece.position[1] + 1),
                                                         self.cells):
                self.current_piece.drop()
                self.current_piece.check_grounded(self.cells)
            else:
                self.going = False
        elif time.time() - self.current_piece.last_drop_time > self.time_constant:
            self.current_piece.drop()
            self.ghost_position = self.calc_ghost()
            self.current_piece.check_grounded(self.cells)
        # TODO: only do if there were changes
        self.repaint()
        return True

    def repaint(self) -> None:
        # draw stationary blocks
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
               self.surface.blit(self.block_sprites[self.cells[y][x]],
                                 (self.cell_dim[0] * x,
                                  self.cell_dim[1] * y,
                                  self.cell_dim[0],
                                  self.cell_dim[1]))

        d = self.current_piece.get_bb_dim()
        # draw ghost
        for y in range(d[1]):
            for x in range(d[0]):
                if (self.current_piece.int_repr() >> ((d[1] - y - 1) * d[0] + d[0] - x - 1)) & 0b1:
                    self.surface.blit(self.shadow,
                                      (self.cell_dim[0] * (x + self.ghost_position[0]),
                                       self.cell_dim[1] * (y + self.ghost_position[1]),
                                       self.cell_dim[0],
                                       self.cell_dim[1]))

        # draw current piece
        for y in range(d[1]):
            for x in range(d[0]):
                if (self.current_piece.int_repr() >> ((d[1] - y - 1) * d[0] + d[0] - x - 1)) & 0b1:
                    self.surface.blit(self.block_sprites[self.current_piece.block_type],
                                      (self.cell_dim[0] * (x + self.current_piece.position[0]),
                                       self.cell_dim[1] * (y + self.current_piece.position[1]),
                                       self.cell_dim[0],
                                       self.cell_dim[1]))
        # draw next piece
        d = self.next_piece.get_bb_dim()
        self.next_surface.fill((64, 64, 64))
        for y in range(d[1]):
            for x in range(d[0]):
                if (self.next_piece.int_repr() >> ((d[1] - y - 1) * d[0] + d[0] - x - 1)) & 0b1:
                    self.next_surface.blit(self.block_sprites[self.next_piece.block_type],
                                           (self.cell_dim[0] * x, self.cell_dim[1] * y))
        # draw hold
        if self.held_piece is not None:
            d = self.held_piece.get_bb_dim()
            self.hold_surface.fill((64, 64, 64))
            for y in range(d[1]):
                for x in range(d[0]):
                    if (self.held_piece.int_repr() >> ((d[1] - y - 1) * d[0] + d[0] - x - 1)) & 0b1:
                        self.hold_surface.blit(self.block_sprites[self.held_piece.block_type],
                                               (self.cell_dim[0] * x, self.cell_dim[1] * y))
        else:
            self.hold_surface.fill((64, 64, 64))

pygame.init()
screen = pygame.display.set_mode([512, 640])
running = True
clock = pygame.time.Clock()
font = pygame.font.Font('assets/KrabbyPatty.ttf', 32)
score_label = font.render('Score', True, (255, 127, 0))
level_label = font.render('Level', True, (255, 127, 0))
next_piece_label = font.render('Next', True, (255, 127, 0))
hold_piece_label = font.render('Hold', True, (255, 127, 0))
you_died = font.render('YOU DIED', True, (255, 0, 0))
you_died_sprite = pygame.Surface((screen.get_size()[0], 100))
you_died_sprite.blit(you_died, ((you_died_sprite.get_size()[0] - you_died.get_size()[0]) // 2,
                                (you_died_sprite.get_size()[1] - you_died.get_size()[1]) // 2))
playfield = Playfield()
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        elif event.type == pygame.QUIT:
            running = False

    playfield.update(events)

    score_value_label = font.render("{}".format(playfield.score), True, (255, 255, 255))
    level_value_label = font.render("{}".format(playfield.level), True, (255, 255, 255))

    screen.fill((64, 64, 64))
    pygame.draw.rect(screen, (255, 255, 255), (17, 17, 306, 606), width=3)
    screen.blit(playfield.surface, pygame.Rect((20, 20), playfield.surface.get_size()))

    screen.blit(next_piece_label, (340, 20))
    screen.blit(playfield.next_surface, (340, 60))

    screen.blit(score_label, (340, 200))
    screen.blit(score_value_label, (440, 200))

    screen.blit(level_label, (340, 240))
    screen.blit(level_value_label, (440, 240))

    screen.blit(hold_piece_label, (340, 280))
    screen.blit(playfield.hold_surface, (340, 320))

    if not playfield.going:
        screen.blit(you_died_sprite, ((screen.get_size()[0] - you_died_sprite.get_size()[0]) // 2,
                                      (screen.get_size()[1] - you_died_sprite.get_size()[1]) // 2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
