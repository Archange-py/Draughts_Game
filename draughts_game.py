from ion import keydown, KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, KEY_BACKSPACE, KEY_OK
from kandinsky import fill_rect, draw_string
from time import sleep

from typing import Iterator

class Screen:
    """A class for choosing the color of each things."""
    palette: dict = {
            "Pair": (255, 255, 255),
            "Impair": (0, 100, 200),
            "PrimaryTeam": (0, 0, 0),
            "SecondaryTeam": (140, 113, 82),
            "FillDame": (255, 255, 255),
            "Selection1": (225, 150, 0),
            "Selection2": (255, 225, 0),
            "Selection": (0, 255, 0),
            "Eaten": (255, 0, 0),
            "FillLine": (0, 0, 0),
            "Background": (255, 255, 255),
            "PrimaryColor": (0, 0, 0),
            "PrimaryText": (0, 200, 200),
            "SecondaryText": (255, 255, 255)
            }

class Pion:
    def __init__(self, x: int, y: int, team: int):
        """A class to represent a simple pion.

        Args:
            x (int): The position x of the pion.
            y (int): The position y of the pion.
            team (int): A number peer or impeer fo choose the team of the pion.
        """
        self.x, self.y = x, y
        self.team = team

    def draw(self, origine_x: int, origine_y: int, width: int, space: int):
        """A function to draw the pion.

        Args:
            origine_x (int): The origine x of a virtual table.
            origine_y (int): The origine y of a virtual table.
            width (int): The width of virtual cases.
            space (int): The space without different cases.
        """
        fill_rect(origine_x+self.x*(width+space)+5, origine_y+self.y*(width+space)+5, width-10, width-10, Screen.palette["PrimaryTeam" if self.team%2 else "SecondaryTeam"])

class Dame(Pion):
    def __init__(self, *args, **kwargs):
        """A class to represent a dame.

        Args:
            x (int): The position x of the dame.
            y (int): The position y of the dame.
            team (int): A number peer or impeer fo choose the team of the dame.
        """
        super().__init__(*args, **kwargs)

    def draw(self, origine_x: int, origine_y: int, width: int, space: int):
        """A function to draw the dame.

        Args:
            origine_x (int): The origine x of a virtual table.
            origine_y (int): The origine y of a virtual table.
            width (int): The width of virtual cases.
            space (int): The space without different cases.
        """
        fill_rect(origine_x+self.x*(width+space)+3, origine_y+self.y*(width+space)+3, width-6, width-6, Screen.palette["PrimaryTeam" if self.team%2 else "SecondaryTeam"])
        fill_rect(origine_x+self.x*(width+space)+6, origine_y+self.y*(width+space)+6, width-12, width-12, Screen.palette["FillDame"])
        fill_rect(origine_x+self.x*(width+space)+9, origine_y+self.y*(width+space)+9, width-18, width-18, Screen.palette["PrimaryTeam" if self.team%2 else "SecondaryTeam"])

class Case:
    def __init__(self, x: int, y: int, pion: Pion | Dame | None = None):
        """A class to represent a case of the game.

        Args:
            x (int): The position x of the case.
            y (int): The position y of the case.
            pion (Pion | None, optional): A pion contains in the case. Defaults to None.
        """
        self.x, self.y = x, y
        self.pion = pion

    def __iter__(self): return iter([self.pion.x, self.pion.y])

    def draw(self, origine_x: int, origine_y: int, width: int, space: int, color: str | tuple = None):
        """A function to draw the case, and the pion under it.

        Args:
            origine_x (int): The origine x of a virtual table.
            origine_y (int): The origine y of a virtual table.
            width (int): The width of the square.
            space (int): The space without different cases.
            color (str | tuple, optional): The color of the case. If isn't given, it's choose with Screen. Defaults to None.
        """
        fill_rect(origine_x+self.x*(width+space), origine_y+self.y*(width+space), width, width, Screen.palette["Pair" if (self.x+self.y)%2 else "Impair"] if color is None else color)
        if self.pion: self.pion.draw(origine_x, origine_y, width, space)

class Curseur:
    def __init__(self, *args, default=""):
        """Classe d'un itérateur infini incluant les changements de directions.

        Args:
            default (str, optional): élément qui detérminera où l'itération commence. Defaults to "".
        """
        self.args = args
        self.sens = "R"
        self.default = default

    def __iter__(self):
        """Surcharge de la méthode spéciale __iter__

        Returns:
            self: se retourne soit même
        """
        self.curs = self.default if self.default != ""  else self.args[-1]
        self.N = self.args.index(self.default) if self.default != ""  else -1
        return self

    def __next__(self):
        """Surcharge de la méthode spéciale __next__

        Returns:
            Any: renvoie le prochain élément contenu dans la liste args
        """
        self.N += 1 if self.sens == "R" else -1
        self.check()
        self.curs = self.args[self.N]
        return self.curs
    
    def check(self):
        """Méthode mettant à jour l'attribut N suivant deux conditions."""
        if self.N > len(self.args)-1: self.N = 0
        elif self.N < 0: self.N = len(self.args)-1

class Matrice:
    SPEED: float = 0.15
    FIRST_PLAYER: int = 0
    PLAYER: dict = {0: 'white', 1: 'black', None: 'Equality'}

    def __init__(self, N: int = 9, origine_x: int = 60, origine_y: int = 15, width: int = 21, space: int = 1):
        """A class to represent the matrice of the game.

        Args:
            N (int): The number of case. Defaults to 9.
            origine_x (int): The origine x of the matrice. Defaults to 60.
            origine_y (int): The origine y of the matrice. Defaults to 15.
            width (int, optional): The width of a case. Defaults to 21.
            space (int, optional): The space without different cases. Defaults to 1.
        """
        self.N = N
        self.winner = None
        self.width, self.space = width, space
        self.origine_x, self.origine_y = origine_x, origine_y
        self.matrice: list[list[Case]] = [[Case(x, y) for y in range(N)] for x in range(N)]

        for x in range(N):
          for y in range(round(N*(1/3))): self[x][y].pion = Pion(x, y, 1) if not (x+y)%2 else None

        for x in range(N):
          for y in range(round(N*(2/3)), self.N): self[x][y].pion = Pion(x, y, 0) if not (x+y)%2 else None

    def __getitem__(self, ij: tuple) -> Case: return self.matrice[ij]
    def __setitem__(self, ij: tuple, value: Case): self.matrice[ij] = value
    def __iter__(self) -> Iterator[Case]: return (self[x][y] for y in range(self.N) for x in range(self.N))

    def getNumberPion(self, team: int) -> int:
        """A method to get the number of pion in a specific team.

        Args:
            team (int): A number peer or impeer fo choose the team.

        Returns:
            int: Return the number of pion in the team.
        """
        return len([1 for C in self if C.pion != None and C.pion.team%2 == team%2])
    
    def getInstancePion(self, team: int) -> list[Case]:
        """A method to get pion's instances of the team.

        Args:
            team (int): A number peer or impeer fo choose the team.

        Returns:
            list[Case]: Return a list of case that is contains pion of this team.
        """
        liste: list[Case] = [C for C in self if C.pion != None and self.find_path(C, team)[0] and C.pion.team%2 == team%2]
        liste_eat: list[Case] = [C for C in liste if self.find_path(C, team)[1]]
        return liste if not bool(liste_eat) else liste_eat
    
    def getDiagonalsPion(self, case: Case) -> tuple[list[Case], list[Case], list[Case], list[Case]]:
        """A method to get 4 diagonals of a case.

        Args:
            case (Case): The case where you are.

        Returns:
            tuple[list[Case], list[Case], list[Case], list[Case]]: Return a tuple with 4 diagonals.
        """
        def update(x: int, y: int, liste: list):
            if self[x][y].pion is None: liste.append(self[x][y])
            elif self[x][y].pion.team%2 != case.pion.team%2: liste.append(self[x][y])
        diagonal_1, diagonal_2, diagonal_3, diagonal_4 = [], [], [], []
        x, y = case
        while x > 0 and y > 0: x -= 1 ; y -= 1 ; update(x, y, diagonal_1)
        x, y = case
        while x < self.N-1 and y > 0: x += 1 ; y -= 1 ; update(x, y, diagonal_2)
        x, y = case
        while x < self.N-1 and y < self.N-1: x += 1 ; y += 1 ; update(x, y, diagonal_3)
        x, y = case
        while x > 0 and y < self.N-1: x -= 1 ; y += 1 ; update(x, y, diagonal_4)
        return diagonal_1, diagonal_2, diagonal_3, diagonal_4

    def draw(self):
        """A fonction to draw the matrice."""
        for C in self: C.draw(self.origine_x, self.origine_y, self.width, self.space)

    def draw_path(self, possible_case: list[Case], possible_eaten: list[Case]):
        """A fonction to draw all possible cases, and cases that can be eaten.

        Args:
            possible_case (list[Case]): Cases where you can move.
            possible_eaten (list[Case]): Cases that can be eaten.
        """
        for C in possible_case:
            C.draw(self.origine_x, self.origine_y, self.width, self.space, Screen.palette["Selection2"])
        for C_eat in possible_eaten:
            C_eat.draw(self.origine_x, self.origine_y, self.width, self.space, Screen.palette["Eaten"])

    def find_path(self, case: Case, team: int) -> tuple[list[Case], list[Case], list[Case]]:
        """A function to get the path.

        Args:
            case (Case): The case where you are.
            team (int): A number peer or impeer fo choose the team.

        Returns:
            tuple[list[Case], list[Case], list[Case]]: Return cases that you can access, the case that you can eat, and
            the case that you can access when you must eat.
        """
        def update(case: Case, position: Case):
            """A simple function to facility the refactoring of this global function.

            Args:
                case (Case): The case that can be eaten.
                position (Case): The case that append to possible cases.
            """
            pion_must_eat.append(case) ; possible_case.append(position) ; possible_case_eat.append(position)
        if type(case.pion) == Pion:
            possible_case, pion_can_eat, pion_must_eat, possible_case_eat = [], [], [], []
            cond1: bool = case.x-1 >= 0
            cond2: bool = case.x+1 <= self.N-1
            cond3: bool = case.y-1 >= 0
            cond4: bool = case.y+1 <= self.N-1
            if team%2 == 0:
                if cond1 and cond3:
                    if self[case.x-1][case.y-1].pion is None: possible_case.append(self[case.x-1][case.y-1])
                    elif self[case.x-1][case.y-1].pion.team%2 != team: pion_can_eat.append(self[case.x-1][case.y-1])
                if cond2 and cond3:
                    if self[case.x+1][case.y-1].pion is None: possible_case.append(self[case.x+1][case.y-1])
                    elif self[case.x+1][case.y-1].pion.team%2 != team: pion_can_eat.append(self[case.x+1][case.y-1])
                if cond1 and cond4 and self[case.x-1][case.y+1].pion != None and self[case.x-1][case.y+1].pion.team%2 != team: pion_can_eat.append(self[case.x-1][case.y+1])
                if cond2 and cond4 and self[case.x+1][case.y+1].pion != None and self[case.x+1][case.y+1].pion.team%2 != team: pion_can_eat.append(self[case.x+1][case.y+1])
            elif team%2 == 1:
                if cond1 and cond4:
                    if self[case.x-1][case.y+1].pion is None: possible_case.append(self[case.x-1][case.y+1])
                    elif self[case.x-1][case.y+1].pion.team%2 != team: pion_can_eat.append(self[case.x-1][case.y+1])
                if cond2 and cond4:
                    if self[case.x+1][case.y+1].pion is None: possible_case.append(self[case.x+1][case.y+1])
                    elif self[case.x+1][case.y+1].pion.team%2 != team: pion_can_eat.append(self[case.x+1][case.y+1])
                if cond1 and cond3 and self[case.x-1][case.y-1].pion != None and self[case.x-1][case.y-1].pion.team%2 != team: pion_can_eat.append(self[case.x-1][case.y-1])
                if cond2 and cond3 and self[case.x+1][case.y-1].pion != None and self[case.x+1][case.y-1].pion.team%2 != team: pion_can_eat.append(self[case.x+1][case.y-1])
            cond1_eat: bool = case.x-2 >= 0
            cond2_eat: bool = case.x+2 <= self.N-1
            cond3_eat: bool = case.y-2 >= 0
            cond4_eat: bool = case.y+2 <= self.N-1
            for C in pion_can_eat:
                if cond1_eat and cond3_eat and case.x > C.x and case.y > C.y and self[C.x-1][C.y-1].pion is None: update(C, self[C.x-1][C.y-1])
                if cond2_eat and cond3_eat and case.x < C.x and case.y > C.y and self[C.x+1][C.y-1].pion is None: update(C, self[C.x+1][C.y-1])
                if cond1_eat and cond4_eat and case.x > C.x and case.y < C.y and self[C.x-1][C.y+1].pion is None: update(C, self[C.x-1][C.y+1])
                if cond2_eat and cond4_eat and case.x < C.x and case.y < C.y and self[C.x+1][C.y+1].pion is None: update(C, self[C.x+1][C.y+1])
        else:
            pion_must_eat, possible_case_eat = [], []
            diagonal_1, diagonal_2, diagonal_3, diagonal_4 = self.getDiagonalsPion(case)
            possible_case: list[Case] = [*diagonal_1, *diagonal_2, *diagonal_3, *diagonal_4]
            possible_case: list[Case] = list(filter(lambda C: C.pion is None, possible_case))
            for liste in [filter(lambda C: C.pion != None, diagonal_1),
                          filter(lambda C: C.pion != None, diagonal_2),
                          filter(lambda C: C.pion != None, diagonal_3),
                          filter(lambda C: C.pion != None, diagonal_4)]:
                forward: bool = True
                for C in liste:
                    if not forward: break
                    if C.x < case.x and C.y < case.y and C.x-1 > 0 and C.y-1 > 0 and not self[C.x-1][C.y-1].pion:
                        possible_case_eat.append(self[C.x-1][C.y-1]) ; pion_must_eat.append(C) ; forward = False
                    elif C.x > case.x and C.y < case.y and C.x+1 < self.N and C.y-1 > 0 and not self[C.x+1][C.y-1].pion:
                        possible_case_eat.append(self[C.x+1][C.y-1]) ; pion_must_eat.append(C) ; forward = False
                    elif C.x > case.x and C.y > case.y and C.x+1 < self.N and C.y+1 < self.N and not self[C.x+1][C.y+1].pion:
                        possible_case_eat.append(self[C.x+1][C.y+1]) ; pion_must_eat.append(C) ; forward = False
                    elif C.x < case.x and C.y > case.y and C.x-1 > 0 and C.y+1 < self.N and not self[C.x-1][C.y+1].pion:
                        possible_case_eat.append(self[C.x-1][C.y+1]) ; pion_must_eat.append(C) ; forward = False
        return possible_case, pion_must_eat, possible_case_eat

    def check_become_dame(self, x: int, y: int) -> Case:
        """A function to check if a pion can become a dame.

        Args:
            x (int): The position x of the pion.
            y (int): The position y of the pion.

        Returns:
            Case: Return a case, or a dame.
        """
        if type(self[x][y].pion) != Dame:
            if not self[x][y].pion.y and not self[x][y].pion.team: self[x][y].pion = Dame(x, y, 0)
            elif self[x][y].pion.y == self.N-1 and self[x][y].pion.team: self[x][y].pion = Dame(x, y, 1)

    def eat_pion(self, origine: Case, eat: Case, team: int):
        """A function to eat the pion under 'eat'.

        Args:
            origine (Case): The start case.
            eat (Case): The case where you will move.
            team (int): A number peer or impeer fo choose the team.
        """
        has_pion: bool = type(origine.pion) == Pion
        if eat.x < origine.x and eat.y < origine.y: self[eat.x+1][eat.y+1].pion = None
        elif eat.x > origine.x and eat.y < origine.y: self[eat.x-1][eat.y+1].pion = None
        elif eat.x < origine.x and eat.y > origine.y: self[eat.x+1][eat.y-1].pion = None
        elif eat.x > origine.x and eat.y > origine.y: self[eat.x-1][eat.y-1].pion = None
        self.matrice[origine.x][origine.y].pion, self.matrice[eat.x][eat.y].pion = None, Pion(eat.x, eat.y, team) if has_pion else Dame(eat.x, eat.y, team)
        self.check_become_dame(eat.x, eat.y)

    def check_eat(self, possible_case: list[Case], pion_must_eat: list[Case], possible_case_eat: list[Case]) -> tuple[list[Case], list[Case]]:
        """A method to verify if you can eat, if is True possible_case become possible_case_eat.

        Args:
            possible_case (list[Case]): All cases where you can move.
            pion_must_eat (list[Case]): Cases that you can eat.
            possible_case_eat (list[Case]): Just cases where you can move and eat.

        Returns:
            tuple[list[Case], list[Case]]: Return a list where you can move, and a list that you can eat.
        """
        return (possible_case, pion_must_eat) if not possible_case_eat else (possible_case_eat, pion_must_eat)

    def choice_pion(self, case: Case, team: int):
        """A function to choice the new case.

        Args:
            case (Case): The original case.
            team (int): A number peer or impeer fo choose the team.
        
        Returns:
            Case: Return the case that has been choice.
        """
        def update(sens: str):
            """A simple function to facility the refactoring of this global function.

            Args:
                sens (str): The new direction of the cursor.
            """
            P.curs.draw(self.origine_x, self.origine_y, self.width, self.space, Screen.palette["Selection2"])
            P.sens = sens ; next(P)
            P.curs.draw(self.origine_x, self.origine_y, self.width, self.space, Screen.palette["Selection"])
            sleep(Matrice.SPEED)
        possible_case, pion_must_eat = self.check_eat(*self.find_path(case, team))
        self.draw_path(possible_case, pion_must_eat)
        P: Iterator[Case] = iter(Curseur(*possible_case))
        update('R') ; sleep(Matrice.SPEED)
        while True:
            if keydown(KEY_RIGHT): update('R')
            elif keydown(KEY_LEFT): update('L')
            elif keydown(KEY_BACKSPACE) and not bool(self.epoch): self.backspace = True ; sleep(Matrice.SPEED) ; self.draw() ; break
            elif keydown(KEY_OK): self.eat_pion(case, P.curs, team) ; self.draw() ; sleep(Matrice.SPEED) ; break
        return P.curs

    def move_pion_on_path(self, case: Case, team: int) -> bool:
        """A 'recursive' fonction, that call an other function to choice a pion,
         and continue if the new pion can eat.

        Args:
            case (Case): The case to start.
            team (int): A number peer or impeer fo choose the team.

        Returns:
            bool: Return a bool to know if you must continue or not.
        """
        self.backspace: bool = False
        self.follow: bool = True
        self.epoch: int = 0
        while True:
            end = not bool(self.find_path(case, team)[1])
            case = self.choice_pion(case, team)
            if self.backspace: break
            possible_case, pion_must_eat = self.check_eat(*self.find_path(case, team))
            if not bool(pion_must_eat) or end: self.follow = False ; sleep(Matrice.SPEED) ; break
            self.epoch += 1
            case.draw(self.origine_x, self.origine_y, self.width, self.space, Screen.palette["Selection1"])
            self.draw_path(possible_case, pion_must_eat)
            sleep(Matrice.SPEED)
        return not self.follow

    def move_curseur(self, team: int):
        """A function to move a cursor on cases.

        Args:
            team (int): A number peer or impeer fo choose the team.
        """
        def update(sens: str):
            """A function to change the direction, and move the cursor.

            Args:
                sens (str): Must be 'R' or 'L' for right and left.
            """
            self.draw() ; C.sens = sens ; next(C)
            C.curs.draw(self.origine_x, self.origine_y, self.width, self.space, Screen.palette["Selection1"])
            self.draw_path(*self.check_eat(*self.find_path(C.curs, team)))
            sleep(Matrice.SPEED)
        instances = self.getInstancePion(team)
        if not instances: self.winner = 0 if self.getNumberPion(0) > self.getNumberPion(1) else 1 ; return False
        C: Iterator[Case] = iter(Curseur(*instances))
        update('R')
        while True:
            if keydown(KEY_RIGHT): update('R')
            elif keydown(KEY_LEFT): update('L')
            elif keydown(KEY_OK) and self.move_pion_on_path(C.curs, team): return True
            elif keydown(KEY_BACKSPACE): return False

    def main(self):
        """The main function to run the game."""
        fill_rect(self.origine_x-self.space, self.origine_y-self.space, self.N*(self.width+self.space)+self.space, self.N*(self.width+self.space)+self.space, Screen.palette["FillLine"])
        T: Iterator[int] = iter(Curseur(0, 1, default=Matrice.FIRST_PLAYER)) ; self.draw()
        while self.move_curseur(T.curs%2): next(T)

class GUI:
    COLOR_MODE: str = "light"
    
    @staticmethod
    def clean():
        """A static method to clear the background."""
        fill_rect(0,0,320,222,Screen.palette["Background"])
    
    @staticmethod
    def main():
        """A static method to run the run the menu interface."""
        GUI.Menu.draw()

    class Menu:
        """A simple menu interface."""
        @staticmethod
        def draw():
            """A function to draw the interface."""
            def draw_curseur(curseur):
                if curseur == "play":
                    draw_string(" >  play  <",110,100,Screen.palette["PrimaryText"],Screen.palette["SecondaryText"])
                    draw_string("  settings        ",105,130,Screen.palette["PrimaryText"],Screen.palette["SecondaryText"])
                elif curseur == "settings":
                    draw_string("  play        ",120,100,Screen.palette["PrimaryText"],Screen.palette["SecondaryText"])
                    draw_string(" >  settings  <",95,130,Screen.palette["PrimaryText"],Screen.palette["SecondaryText"])
            GUI.clean() ; I = iter(Curseur("play", "settings", default="play"))
            draw_string("Snake",138,50,Screen.palette["PrimaryText"],Screen.palette["SecondaryText"])
            draw_string("  play  ",120,100,Screen.palette["PrimaryText"],Screen.palette["SecondaryText"])
            draw_string("  settings  ",105,130,Screen.palette["PrimaryText"],Screen.palette["SecondaryText"])
            while True:
                if keydown(KEY_UP): I.sens = "L" ; next(I) ; draw_curseur(I.curs) ; sleep(0.15)
                if keydown(KEY_DOWN): I.sens = "R" ; next(I) ; draw_curseur(I.curs) ; sleep(0.15)
                if keydown(KEY_OK) and I.curs == "play": GUI.Play.draw() ; break
                if keydown(KEY_OK) and I.curs == "settings": GUI.Settings.draw() ; break
    class Play:
        """The interface of the game."""
        @staticmethod
        def draw():
            """A function to draw the interface."""
            GUI.clean() ; game = Matrice() ; game.main()
            draw_string(f"The winner is {Matrice.PLAYER[game.winner]} !",50,105,Screen.palette["PrimaryText"],Screen.palette["SecondaryText"])
            sleep(0.15)
            while True:
                if keydown(KEY_BACKSPACE): GUI.clean() ; GUI.Menu.draw()
    class Settings:
        """A simple settings interface."""
        @staticmethod
        def draw():
            """A function to draw the interface."""
            def draw_curseur(curseur):
                if curseur == "speed":
                    draw_string(">   "+str(Matrice.SPEED)+"   <    ",165,80,Screen.palette["PrimaryText"],Screen.palette["SecondaryText"])
                    draw_string("    "+str(Matrice.FIRST_PLAYER)+"        ",165,110,Screen.palette["PrimaryText"],Screen.palette["SecondaryText"])
                    draw_string("    "+GUI.COLOR_MODE+"        ",165,140,Screen.palette["PrimaryText"],Screen.palette["SecondaryText"])
                elif curseur == "first player":
                    draw_string("    "+str(Matrice.SPEED)+"       ",165,80,Screen.palette["PrimaryText"],Screen.palette["SecondaryText"])
                    draw_string(">   "+str(Matrice.FIRST_PLAYER)+"   <    ",165,110,Screen.palette["PrimaryText"],Screen.palette["SecondaryText"])
                    draw_string("    "+str(GUI.COLOR_MODE)+"        ",165,140,Screen.palette["PrimaryText"],Screen.palette["SecondaryText"])
                elif curseur == "color mode":
                    draw_string("    "+str(Matrice.SPEED)+"       ",165,80,Screen.palette["PrimaryText"],Screen.palette["SecondaryText"])
                    draw_string("    "+str(Matrice.FIRST_PLAYER)+"        ",165,110,Screen.palette["PrimaryText"],Screen.palette["SecondaryText"])
                    draw_string(">   "+GUI.COLOR_MODE+"   <    ",165,140,Screen.palette["PrimaryText"],Screen.palette["SecondaryText"])
            def change_color(mode):
                if mode == "light":
                    Screen.palette["Background"] = (255,255,255) ; Screen.palette["PrimaryText"] = (0,200,200) ;Screen.palette["SecondaryText"] = (255,255,255) ; Screen.palette["PrimaryColor"] = (0,0,0) ; Screen.palette["Pair"] = (255,255,255) ; Screen.palette["Impair"] = (0,100,200) ; Screen.palette["FillLine"] = (0,0,0)
                elif mode == "dark":
                    Screen.palette["Background"] = (80,80,100) ; Screen.palette["PrimaryText"] = (255,255,255) ; Screen.palette["SecondaryText"] = (80,80,100) ; Screen.palette["PrimaryColor"] = (255,255,255) ; Screen.palette["Pair"] = (140,140,160) ; Screen.palette["Impair"] = (110,110,130) ; Screen.palette["FillLine"] = (255,255,255)
            GUI.clean()
            I = iter(Curseur("speed", "first player", "color mode"))
            I_SPEED = iter(Curseur(0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, default=Matrice.SPEED))
            I_FIRST_PLAYER = iter(Curseur(0, 1, default=Matrice.FIRST_PLAYER))
            I_COLOR_MODE = iter(Curseur("light","dark",default=GUI.COLOR_MODE))
            draw_string("Settings",110,30,Screen.palette["PrimaryText"],Screen.palette["SecondaryText"])
            draw_string("speed",25,80,Screen.palette["PrimaryText"],Screen.palette["SecondaryText"])
            draw_string("first player",25,110,Screen.palette["PrimaryText"],Screen.palette["SecondaryText"])
            draw_string("color mode",25,140,Screen.palette["PrimaryText"],Screen.palette["SecondaryText"])
            draw_string("    "+str(Matrice.SPEED)+"       ",165,80,Screen.palette["PrimaryText"],Screen.palette["SecondaryText"])
            draw_string("    "+str(Matrice.FIRST_PLAYER)+"       ",165,110,Screen.palette["PrimaryText"],Screen.palette["SecondaryText"])
            draw_string("    "+GUI.COLOR_MODE+"        ",165,140,Screen.palette["PrimaryText"],Screen.palette["SecondaryText"])
            while True:
                if I.curs == "speed" and keydown(KEY_RIGHT): I_SPEED.sens = "R" ; next(I_SPEED) ; Matrice.SPEED = I_SPEED.curs ; draw_curseur(I.curs) ; sleep(0.15)
                if I.curs == "speed" and keydown(KEY_LEFT): I_SPEED.sens = "L" ; next(I_SPEED) ; Matrice.SPEED = I_SPEED.curs ; draw_curseur(I.curs) ; sleep(0.15)
                if I.curs == "first player" and keydown(KEY_RIGHT): I_FIRST_PLAYER.sens = "R" ; next(I_FIRST_PLAYER) ; Matrice.FIRST_PLAYER = I_FIRST_PLAYER.curs ; draw_curseur(I.curs) ; sleep(0.15)
                if I.curs == "first player" and keydown(KEY_LEFT): I_FIRST_PLAYER.sens = "L" ; next(I_FIRST_PLAYER) ; Matrice.FIRST_PLAYER = I_FIRST_PLAYER.curs ; draw_curseur(I.curs) ; sleep(0.15)
                if I.curs == "color mode" and keydown(KEY_RIGHT): I_COLOR_MODE.sens = "R" ; next(I_COLOR_MODE) ; GUI.COLOR_MODE = I_COLOR_MODE.curs ; draw_curseur(I.curs) ; sleep(0.15)
                if I.curs == "color mode" and keydown(KEY_LEFT): I_COLOR_MODE.sens = "L" ; next(I_COLOR_MODE) ; GUI.COLOR_MODE = I_COLOR_MODE.curs ; draw_curseur(I.curs) ; sleep(0.15)
                if keydown(KEY_UP): I.sens = "L" ; next(I) ; draw_curseur(I.curs) ; sleep(0.15)
                if keydown(KEY_DOWN): I.sens = "R" ; next(I) ; draw_curseur(I.curs) ; sleep(0.15)
                if keydown(KEY_BACKSPACE): change_color(GUI.COLOR_MODE) ; GUI.clean() ; GUI.Menu.draw() ; break

GUI.main()