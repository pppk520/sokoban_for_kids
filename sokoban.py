#!/usr/bin/env python

import tkinter as tk
from tkinter.filedialog import askopenfilenames
import pydoc
import os
from copy import deepcopy

_ROOT = os.path.abspath(os.path.dirname(__file__))
_LEVEL_FOLDER = os.path.join(_ROOT, 'levels')

def enum(**enums):
    return type('Enum', (), enums)

Hole = enum(filled=True, empty=False)

def get_file_list(folder, recursive=True):                     
    file_list = []                                                          
                                                                            
    if not os.path.isdir(folder):                                           
        return file_list                                                    
                                                                            
    if not recursive:                                                       
        for f in os.listdir(folder):                                        
            file_list.append(os.path.join(folder, f))                       
                                                                            
        return file_list                                                    
                                                                            
    for root, sub_folders, files in os.walk(folder):                        
        for f in files:                                                     
            file_list.append(os.path.join(root, f))                         
                                                                            
    return file_list

class Menu(object):
    def __init__(self, app):
        self.app = app

    def load_level_files(self, filenames=None): 
        if not filenames:            
            level_files = get_file_list(_LEVEL_FOLDER)

        self.app.grid_forget()                                                  
        self.app.level_files = level_files                                
        self.app.start_next_level() 

    def open_file(self):
        filenames = askopenfilenames(initialdir=_LEVEL_FOLDER)
        self.load_levels(filenames)

class Direction(object):
    left = 'Left'
    right = 'Right'
    up = 'Up'
    down = 'Down'

class CompleteDialog(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self = tk.Toplevel()
        self.title("Congratulation!")

        info = tk.Label(self, text=("You've completed all levels!"))
        info.grid(row=0)

        self.ok_button = tk.Button(self, text="OK", command=self.destroy)
        self.ok_button.grid(row=1)


class Maze(object):
    wall = '*'
    hole = 'o'
    crate_in_hole = '@'
    crate = '#'
    player = 'P'
    floor = ' '


class Image(object):
    wall = os.path.join(_ROOT, 'images/wall.gif')
    hole = os.path.join(_ROOT, 'images/hole.gif')
    crate_in_hole = os.path.join(_ROOT, 'images/crate-in-hole.gif')
    crate = os.path.join(_ROOT, 'images/crate.gif')
    player = os.path.join(_ROOT, 'images/player.gif')
    player_in_hole = os.path.join(_ROOT, 'images/player-in-hole.gif')

class Level(object):
    def __init__(self):
        self.level_file = None
        self.maze = []
        self.crates = {}
        self.holes = {}
        self.player_position = ()
        self.player = None

    def __str__(self):
        maze = []
        for row in self.maze:
            maze.append(''.join(row))

        return 'maze = \n{maze}\nplayer = {player}'.format(
                      maze=''.join(maze), 
                      player=self.player_position)

    def copy(self):
        ret = Level()

        ret.level_file = self.level_file
        ret.maze = deepcopy(self.maze)
        ret.crates = self.crates.copy()
        ret.holes = self.holes.copy()
        ret.player_position = self.player_position
        ret.player = self.player

        return ret


class StepUndo(object):
    def __init__(self):
        # record the diff part
        self.maze_old = None
        self.maze_new = None

        # info only, directly copy full dict
        self.holes = {}

        # reference
        self.crate_old = None
        self.crate_new = None

        self.player_position_old = None

    def __str__(self):
        return 'maze_old = {}, maze_new = {}'.format(self.maze_old, self.maze_new)

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.configure(background="black")
        self.master.resizable(0,0)

        self.DEFAULT_SIZE = 200
        self.frame = tk.Frame(self, height=self.DEFAULT_SIZE, width=self.DEFAULT_SIZE)
        self.frame.grid()

        self.current_level_file = None
        self.level = Level()
        self.step_undo_history = []

        self.create_menu() 
 
    def key(self, event):
        print('key event received: {}'.format(event.keysym))

        directions = {Direction.left, 
                      Direction.right, 
                      Direction.up, 
                      Direction.down}

        if event.keysym in directions:
            self.move_player(event.keysym)
        elif event.keysym == 'BackSpace':
            self.undo()

    def undo(self):
        if len(self.step_undo_history) > 0:
            print("undo")
            step_undo = self.step_undo_history.pop()
            self.apply_step_undo(step_undo)

    def create_menu(self):
        root = self.master
        menu = tk.Menu(root)
        user_menu = Menu(self)
        root.config(menu=menu)

        file_menu = tk.Menu(menu)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Restart", command=self.restart_level)
        file_menu.add_command(label="Open...", command=user_menu.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=menu.quit)

        op_menu = tk.Menu(menu)
        menu.add_cascade(label="Operation", menu=op_menu)
        op_menu.add_command(label="Undo", command=self.undo)

        user_menu.load_level_files()

    def new_frame(self):
        try:
            self.frame.destroy()
        except:
            pass

        self.grid()
        self.frame = tk.Frame(self)
        self.frame.grid()


    def start_next_level(self):
        if len(self.level_files) > 0:
            self.current_level_file = self.level_files.pop(0)
            self.new_frame()
            self.load_level_file(self.current_level_file)
            self.master.title(os.path.basename(self.current_level_file))
        else:
            self.current_level_file = None
            CompleteDialog()

    def restart_level(self):
        if self.current_level_file:
            self.level_files.insert(0, self.current_level_file)
            self.start_next_level()

    def apply_step_undo(self, step_undo):
        self.level.holes = step_undo.holes

        print(step_undo)

        if step_undo.maze_old:
            location, char = step_undo.maze_old
            row, column = location

            self.draw_item(char, row, column)

        if step_undo.maze_new:                                                  
            location, char = step_undo.maze_new 
            row, column = location                                              
                                                                                
            self.draw_item(char, row, column)                                   
                                                 

        
    def draw_item(self, char, row, column):
        if char == Maze.wall:                                           
            wall = tk.PhotoImage(file=Image.wall)                       
            w = tk.Label(self.frame, image=wall)                        
            w.wall = wall # keep the reference or it will be garbage-collected
            w.grid(row=row, column=column)                              
                                                                        
        elif char == Maze.hole:                                         
            hole = tk.PhotoImage(file=Image.hole)                       
            w = tk.Label(self.frame, image=hole)                        
            w.hole = hole                                               
            w.grid(row=row, column=column)                              
                                                                        
        elif char == Maze.crate_in_hole:                                
            crate_in_hole = tk.PhotoImage(file=Image.crate_in_hole)     
            w = tk.Label(self.frame, image=crate_in_hole)               
            w.crate_in_hole = crate_in_hole                             
            w.grid(row=row, column=column)                              
            self.level.crates[(row, column)] = w                        
                                                                        
        elif char == Maze.crate:                                        
            crate = tk.PhotoImage(file=Image.crate)                     
            w = tk.Label(self.frame, image=crate)                       
            w.crate = crate                                             
            w.grid(row=row, column=column)                              
            self.level.crates[(row, column)] = w  


    def draw_level(self, level):
        self.new_frame()

        for row, parts in enumerate(level.maze):  
            for column, char in enumerate(parts):                                
                self.draw_item(char, row, column)

        # draw player, in maze it's overwritten by floor                                                                                
        self.draw_player(level.player_position)

    def draw_player(self, player_position):
        player_image = tk.PhotoImage(file=Image.player)                         
        self.level.player = tk.Label(self.frame, image=player_image)            
        self.level.player.player_image = player_image                           
        self.level.player.grid(row=player_position[0],                    
                               column=player_position[1]) 

    def clear_data(self):
        self.level = Level()
        self.step_undo_history = []


    def load_level_file(self, level_file):
        ''' Load a complete new level file
        '''
        
        self.clear_data()

        with open(level_file) as f:
            for row, line in enumerate(f):
                level_row = list(line)

                for column,x in enumerate(level_row):
                    if x == Maze.player:
                        # overwrite
                        level_row[column] = Maze.floor
                        self.level.player_position = (row, column) 

                    elif x == Maze.hole:
                        self.level.holes[(row, column)] = Hole.empty

                    elif x == Maze.crate_in_hole:
                        self.level.holes[(row, column)] = Hole.filled

                self.level.maze.append(level_row)

        print(self.level)
        self.draw_level(self.level)


    def move_player(self, direction):
        row, column = self.level.player_position
        prev_row, prev_column = row, column

        blocked = True
        undo_step = StepUndo()

        if direction == Direction.left and self.level.maze[row][column - 1] is not Maze.wall and column > 0:
            blocked, undo_step = self.move_crate((row, column - 1), (row, column - 2))
            if not blocked:
                self.level.player_position = (row, column - 1)

        elif direction == Direction.right and self.level.maze[row][column + 1] is not Maze.wall:
            blocked, undo_step = self.move_crate((row, column + 1), (row, column + 2))
            if not blocked:
                self.level.player_position = (row, column + 1)

        elif direction == Direction.down and self.level.maze[row + 1][column] is not Maze.wall:
            blocked, undo_step = self.move_crate((row + 1, column), (row + 2, column))
            if not blocked:
                self.level.player_position = (row + 1, column)                

        elif direction == Direction.up and self.level.maze[row - 1][column] is not Maze.wall and row > 0:
            blocked, undo_step = self.move_crate((row - 1, column), (row - 2, column))
            if not blocked:
                self.level.player_position = (row - 1, column)

        all_holes_filled = True
        for hole in self.level.holes.values():
            if hole is not Hole.filled:
                all_holes_filled = False

        if all_holes_filled:
            print('All holes are filled! Start next level!')
            self.start_next_level()
            return

        row, column = self.level.player_position
        # player moved from a hole, fill the hole back
        if self.level.maze[prev_row][prev_column] is Maze.hole and not blocked:
            hole = tk.PhotoImage(file=Image.hole)
            w = tk.Label(self.frame, image=hole)
            w.hole = hole
            w.grid(row=prev_row, column=prev_column)

        if not blocked:
            undo_step.player_position_old = (prev_row, prev_column)

            self.level.player.grid_forget()

            if self.level.maze[row][column] is Maze.hole:
                player_image = tk.PhotoImage(file=Image.player_in_hole)
            else:
                player_image = tk.PhotoImage(file=Image.player)

            self.level.player = tk.Label(self.frame, image=player_image)
            self.level.player.player_image = player_image
            self.level.player.grid(row=row, column=column)

            self.step_undo_history.append(undo_step)


    def move_crate(self, location, next_location):                              
        if self.is_blocked(location, next_location):                            
            return True, None

        row, column = location                                                  
        next_row, next_column = next_location                                   
                                                                                
        crate = None                                                            

        step_undo = StepUndo()
        step_undo.holes = self.level.holes.copy()

        if self.level.maze[row][column] is Maze.crate and self.level.maze[next_row][next_column] is Maze.floor:
            crate = tk.PhotoImage(file=Image.crate)                             
                    
            self.level.maze[row][column] = Maze.floor                               
            self.level.maze[next_row][next_column] = Maze.crate
                                                                                
        elif self.level.maze[row][column] is Maze.crate and self.level.maze[next_row][next_column] is Maze.hole:
            crate = tk.PhotoImage(file=Image.crate_in_hole)                     
                     
            self.level.maze[row][column] = Maze.floor                               
            self.level.maze[next_row][next_column] = Maze.crate_in_hole             
            self.level.holes[(next_row, next_column)] = Hole.filled                   
                                                                                
        elif self.level.maze[row][column] is Maze.crate_in_hole and self.level.maze[next_row][next_column] is Maze.floor:
            crate = tk.PhotoImage(file=Image.crate)                             

            self.level.maze[row][column] = Maze.hole                                
            self.level.maze[next_row][next_column] = Maze.crate                     
            self.level.holes[(row, column)] = Hole.empty                              
                                                                                
        elif self.level.maze[row][column] is Maze.crate_in_hole and self.level.maze[next_row][next_column] is Maze.hole:
            crate = tk.PhotoImage(file=Image.crate_in_hole)                     

            self.level.maze[row][column] = Maze.hole                                
            self.level.maze[next_row][next_column] = Maze.crate_in_hole             
            self.level.holes[(row, column)] = Hole.empty                              
            self.level.holes[(next_row, next_column)] = Hole.filled                   
                                                                                
        if not crate:                                                               
            return False, step_undo

        step_undo.maze_old = (location, self.level.maze[row][column])           
        step_undo.maze_new = (next_location, self.level.maze[next_row][next_column])

        step_undo.crates_old = (location, self.level.crates[location])
        if next_location in self.level.crates:
            step_undo.crates_new = (next_location, self.level.crates[next_location])

        # make the old crate invisible
        self.level.crates[(row, column)].grid_forget()                            

        # draw a new crate in grid
        w = tk.Label(self.frame, image=crate)                               
        w.crate = crate                                                     
        w.grid(row=next_row, column=next_column)                            

        # keep the crate object reference                                                                                
        self.level.crates[(next_row, next_column)] = w
                                                                                
        return False, step_undo

    def is_blocked(self, location, next_location):
        row, column = location
        next_row, next_column = next_location

        if self.level.maze[row][column] is Maze.crate and self.level.maze[next_row][next_column] is Maze.wall:
            return True
        elif self.level.maze[row][column] is Maze.crate_in_hole and self.level.maze[next_row][next_column] is Maze.wall:
            return True
        elif (self.level.maze[row][column] is Maze.crate_in_hole and
                  (self.level.maze[next_row][next_column] is Maze.crate or
                           self.level.maze[next_row][next_column] is Maze.crate_in_hole)):
            return True
        elif (self.level.maze[row][column] is Maze.crate and
                  (self.level.maze[next_row][next_column] is Maze.crate or
                           self.level.maze[next_row][next_column] is Maze.crate_in_hole)):
            return True


def main():
    app = Application()
    app.bind_all("<Key>", app.key)
    app.mainloop()


if __name__ == "__main__":
    main()

