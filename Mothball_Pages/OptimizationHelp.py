import sys, os
# import tkinter as tk

folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(folder_path)

# from ballgui import HelpPage
from Mothball_Pages.HelpPage import Page

class Calculators(Page):
    def __init__(self, master = None, pack=True):
        super().__init__(master, pack)
        self.heading("Calculation Based Functions")
        self.insert_text("Mothball provides several functions that will assist in calculating and outputting more complex operations. Before continuing on, you should be familiar with what ")
        self.inline_code("outz zb zmm")
        self.insert_text(" are and their differences. Below are some of these special functions:\n\n")
        self.inline_code("bwmm"); self.insert_text(" and "); self.inline_code("xbwmm"); self.insert_text(" - given the movement sequence, finds the backward speed that perfectly uses the given blocks of momentum, in other words, optimizes for "); self.inline_code("zmm/xmm"); self.insert_text("\n")
        self.inline_code("wall"); self.insert_text(" and "); self.inline_code("xwall"); self.insert_text(" - given the movement sequence, finds the backward speed that perfectly uses the given distance, in other words, optimizes for "); self.inline_code("outz/outx"); self.insert_text("\n")
        self.inline_code("blocks"); self.insert_text(" and "); self.inline_code("xblocks"); self.insert_text(" - given the movement sequence, finds the backward speed that perfectly uses the given blocks, in other words, optimizes for "); self.inline_code("zb/xb"); self.insert_text("\n")
        self.inline_code("repeat"); self.insert_text(" or "); self.inline_code("r"); self.insert_text(" - repeat the sequence a given number of times\n")
        self.inline_code("poss/xposs/xzposs"); self.insert_text(" - list all ticks that land a factor of a pixel distance by a small offset on the z/x/x and z axis\n\n")

        self.heading("Optimization Functions")
        self.insert_text("These functions include ")
        self.inline_code("bwmm xbwmm wall xwall blocks xblocks")
        self.insert_text(". They take two arguments. First is a number, also called the target distance, and the second is the Mothball code. What they do is they find the right speed so that whatever is run in the Mothball code, the player's position traverses the target distance. The target distance corresponds to how that distance is measured. For example, ")
        self.inline_code("bwmm")
        self.insert_text(" optimizes for ")
        self.inline_code("zmm")
        self.insert_text(", ")
        self.inline_code("wall")
        self.insert_text(" optimizes for ")
        self.inline_code("outz")
        self.insert_text(", ")
        self.inline_code("blocks")
        self.insert_text(" optimizes for ")
        self.inline_code("zb")
        self.insert_text(", and same thing for the x versions.\n\nLet's look at an example. Suppose I would like to know how much speed I would need to fit ")
        self.inline_code("sj45(12)")
        self.insert_text(" into 1 block of momentum. Then I would do\n\n")

        self.code_snippet_with_output("bwmm(1, sj45(12))")
        self.insert_text("\nso i would need a z speed of -0.2929913. To double check this, we can add a ")
        self.inline_code("zmm(1)")
        self.insert_text(" at the end to see that we really do use up exactly 1 block of momentum.\n\n")
        
        self.code_snippet_with_output("bwmm(1, sj45(12)) zmm(1)")

        self.insert_text("\nJust a little note, putting ")
        self.inline_code("zmm(1)")
        self.insert_text(" inside or outside the ")
        self.inline_code("bwmm")
        self.insert_text(" doesn't make a difference, as ")
        self.inline_code("zmm(1)")
        self.insert_text(" is not a movement related function.\n\n")

        self.insert_text("Let's see another example. What if we wanted to fit ")
        self.inline_code("wj45 sa45(11) s45")
        self.insert_text(" into 1 block of distance, a 1bm frontwall if you will? Since we are dealing with a frontwall, we know that we want to optimize based on ")
        self.inline_code("outz(1)")
        self.insert_text(" so we use ")
        self.inline_code("wall")
        self.insert_text(" to do this.\n\n")

        self.code_snippet_with_output("wall(1, wj45 sa45(11) s45) outz(1)")
        self.insert_text("\nso we need -0.2009824 z speed.\n\nBut we have been doing this under the assumption that we are on the ground before the sequence inside the function begins. In the last example, Mothball said that we need -0.2009824 z speed to fit a 1bm frontwall momentum. That z speed must be achieved by running on the ground. What if instead we wanted the z speed to be for air? Simple, we let Mothball know by giving an air movement function before the optimize function. It doesn't matter which function, as long as its air movement.\n\n")

        self.code_snippet_with_output("sta wall(1, wj45 sa45(11) s45) outz(1)")
        self.insert_text("\nNow the speed is different, although this is worse than getting the required speed on the ground. A good way to test this is to add ")
        self.inline_code("vec")
        self.insert_text(" at the end of the sequence and compare.\n\n")

        self.heading2("The Twist!")
        self.insert_text("But there's also another twist! Sometimes, the required z speed given yields an unexpected result! To see this, let's understand optimizing for ")
        self.inline_code("zmm(2)")
        self.insert_text(" with the sequence ")
        self.inline_code("sj(12)")
        self.insert_text(". Assume we are starting on ground, as that is typically the best strat.\n\n")

        self.code_snippet_with_output("bwmm(2, sj(12)) zmm(2)")
        self.insert_text("\nThe actual momentum used does not equal 2, and that is because of what the warning says. Inertia has been involved and thus the backward speed is not accurate! So how do we get around this?\n\n")

        self.insert_text("There are a few things you could try.\n\n")
        self.insert_text("    1. Play around with angles\n")
        self.insert_text("    2. Use a different strategy\n")
        self.insert_text("    3. Start the optimization in a different state (ground, air, etc.)\n\n")
        self.insert_text("Changing the angles could help to a degree.\n\n")

        self.code_snippet_with_output("bwmm(2, sj(1, 10) sa(11)) zmm(2)")

        self.insert_text("\nOr we can use a completely different strategy. Don't worry if this strat is confusing.\n\n")

        self.code_snippet_with_output("bwmm(2, s sj.wd outz | sa(11)) zmm(2)")

        self.insert_text("\nOr we try starting not on ground.\n\n")

        self.code_snippet_with_output("sta bwmm(2, sj(12)) zmm(2)")

        self.insert_text("\nIn this case, changing the initial state doesn't work, but in some situations, it does provide a valid alternative approach. It is up to you to decide how to get around this.\n\n")

        self.heading("The Repeat Function")
        self.insert_text("Every language has repetition, whether that is spoken language or a programming language (we call them loops). Mothball obviously provides its own loop function ")
        self.inline_code("repeat")
        self.insert_text(" or ")
        self.inline_code("r")
        self.insert_text(" for short. This function takes two arguments. The first one is the Mothball code, and the second one is the number of times to loop. Suppose we want to print numbers from 1 to 100. How can we use the ")
        self.inline_code("repeat")
        self.insert_text(" function to do this?\n\n")

        self.code_snippet("var(num, 1)\nrepeat( print({num}) var(num, num + 1), 100)")

        self.insert_text("\nI'll let you see the output yourself. What about jumping on flat ground 34 times?\n\n")

        self.code_snippet_with_output("r( sj(12), 34)")
        self.insert_text("\n")

        self.heading("The Possibilities Functions")
        self.insert_text("Using these functions ")
        self.inline_code("poss xposs xzposs")
        self.insert_text(", we can find ticks where a given Mothball sequence makes a certain pixel distance by a small enough offset. These functions take 2 main arguments. The first one is the Mothball code, and the second one is the maximum offset to display. Let's suppose we want to find potentially precise jumps for a 6 block momentum single 45 jump, and we want to look for jumps whose offset is less than 0.005.\n\n")

        self.code_snippet_with_output("sj(12) sj(12) zmm(6) | poss(sj45(30), 0.005)")

        self.insert_text("\nBased on the result, we found 3 candidate jump distances with offsets less than 0.005. The choice of ")
        self.inline_code("sj45(30)")
        self.insert_text(" being 30 ticks is an arbitrary choice. It just means we will see results up to 30 ticks of airtime.\n\n")

        self.insert_text("So far though, we've only found precise jump distance measured in blocks, as in ")
        self.inline_code("zb xb")
        self.insert_text(". What if we wanted it to find ticks for ")
        self.inline_code("outz outx")
        self.insert_text(" and ")
        self.inline_code("zmm xmm")
        self.insert_text("? Simple! These functions take an optional 3rd parameter which is the offset of the calculation. By default, the offset is 0.6, which measures the distance akin to ")
        self.inline_code("zb xb")
        self.insert_text(". Set the offset to 0 if you want to measure distance just like ")
        self.inline_code("outz outx")
        self.insert_text(". Finally, set the offset to -0.6 for ")
        self.inline_code("zmm xmm")
        self.insert_text(". Below, observe that ")
        self.inline_code("sj(12) sj(12) zmm(6) | poss(sj45(30), 0.005)")
        self.insert_text(" is the same as\n\n")
        self.code_snippet_with_output("sj(12) sj(12) zmm(6) | poss(sj45(30), 0.005, 0.6)")

        self.insert_text("\nThe offset is the same even if we are going the opposite direction. Mothball will interpret 0.6 to mean \"measure the distance in terms of blocks\", likewise for 0 and -0.6. Below, we show what happens when we face 180 instead of 0.\n\n")
        self.code_snippet_with_output("f(180) sj(12) sj(12) zmm(-6) | poss(sj45(30), 0.005, 0.6)")

        self.insert_text("\nAs a final note, if you, for some reason, want to check if there are any near misses, you can! Using the keyword argument ")
        self.inline_code("miss = offset")
        self.insert_text(", it will display all ticks where the distance traveled misses the next pixel distance by at most ")
        self.inline_code("offset")
        self.insert_text(".\n\n")

        self.code_snippet_with_output("bwmm(2, sj45(12)) | poss( sj45(30), 0.01, miss=0.001)")

        self.insert_text("\nYea... that tick 27 is one unfortunate miss.")

        self.finalize()

if __name__ == "__main__":
    a = Calculators()
    a.mainloop()
