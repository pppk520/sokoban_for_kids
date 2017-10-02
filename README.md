### Docker                                                                      
```bash                                                                         
# this is for x-window to accept signals from any source
sudo xhost +                                                                    

sudo make build                                                                 
sudo make run                                                                   

# the main process                                                                                
python sokoban.py                                                               
```                                                                             
                                                                                
### Operations                                                                  
**Left**, **Right**, **Top**, **Down** for moves                                                
**Backspace** for undo                                                              
                                                                                
### Program Structure                                                           
```Python                                                                       
def main():                                                                     
    app = Application()                                                         
    app.bind_all("<Key>", app.key)                                              
    app.mainloop()                                                              

class Application(tk.Frame):                                                                           
    def key(self, event)
    def load_level_file(self, level_file)
    def start_next_level(self)
    def draw_level(self, level)
    def draw_item(self, item_char, row, column)
    def draw_player(self, player_position)
    def move_player(self, direction)
    def move_crate(self, location, next_location)
    def undo(self)
```                                                                             
1. Application bind and listen key events
2. Load level files and draw it on Frame
3. Draw maze, record holes for checking completion.
4. Draw player
5. (Loop) If key is in monitoring, check and move crate/player, record status before moving for undo.
                                                                                
                                                                                
### Reference                                                                   
https://github.com/Risto-Stevcev/pysokoban.git                                  
                                                                                
### Sokoban Levels                                                              
www.sourcecode.se/sokoban/levels                                                
~                                    
