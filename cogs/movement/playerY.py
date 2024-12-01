from numpy import float32 as fl
import math

class PlayerY:

    pi = 3.14159265358979323846
    
    def __init__(self):
        self.y = 0.0
        self.vy = 0.0
        self.inertia_threshold = 0.005
        self.water = 0
        self.previously_in_web = 0 # New web movement
        self.jump_boost = 0
        self.ceiling = None
        self.hit_ceiling = False

    
    def move(self, ctx):
        args = ctx.args

        # Defining variables


        airborne = args.get('airborne', False)
        sneaking = args.get('sneaking', False)
        jumping = args.get('jumping', False)
        water = args.get('water', self.water)
        slime = args.get('slime', False)
        web = args.get('web', False)
        jump_boost = args.get('jump_boost', self.jump_boost)
    
        
        # End defining
        
        # Moving the player
        self.last_y = self.y
        self.y += self.vy

        if self.hit_ceiling:
            self.vy = 0
            self.y = self.ceiling - 1.8
            self.hit_ceiling = False

        # idk
        if self.previously_in_web:
            self.vy = 0

        if jumping:
            self.vy = 0.42 + 0.1 * jump_boost
            # self.y = 0.0
            
        else:
            if slime:
                self.vy = -self.vy
            self.vy = (self.vy - 0.08) * 0.98
        
        # idk

        if abs(self.vy) < self.inertia_threshold:
            self.vy = 0

        if web:
            self.vy = self.vy / 20

        self.previously_in_web = web

        if self.ceiling is not None and self.y + self.vy + 1.8 >= self.ceiling:
            self.vy = self.ceiling - self.y - 1.8
            self.hit_ceiling = True


        
        ctx.history.append((self.y, self.vy))
