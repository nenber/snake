import difflib
from turtle import color
from django.conf import settings
import pygame
import time
import random
import json
import io


surfaceW = 1000  # Dimension de la fenêtre / Largeur
surfaceH = 1000  # Dimension de la fenêtre / Longueur


class Menu:
    """ Création et gestion des boutons d'un menu """

    def __init__(self, application, *groupes):
        self.couleurs = dict(
            normal=(0, 200, 0),
            survol=(0, 200, 200),
        )
        font = pygame.font.SysFont('Helvetica', 24, bold=True)
        # noms des menus et commandes associées
        items = (
            ('JOUER', application.jeu),
            ('SETTINGS', application.settings),
            ('QUITTER', application.quitter)
        )
        x = 500
        y = 300
        self._boutons = []
        for texte, cmd in items:
            mb = MenuBouton(
                texte,
                self.couleurs['normal'],
                font,
                x,
                y,
                200,
                50,
                cmd
            )
            self._boutons.append(mb)
            y += 120
            for groupe in groupes:
                groupe.add(mb)

    def update(self, events):
        clicGauche, *_ = pygame.mouse.get_pressed()
        posPointeur = pygame.mouse.get_pos()
        for bouton in self._boutons:
            # Si le pointeur souris est au-dessus d'un bouton
            if bouton.rect.collidepoint(*posPointeur):
                # Changement du curseur par un quelconque
                pygame.mouse.set_cursor(*pygame.cursors.tri_left)
                # Changement de la couleur du bouton
                bouton.dessiner(self.couleurs['survol'])
                # Si le clic gauche a été pressé
                if clicGauche:
                    # Appel de la fonction du bouton
                    bouton.executerCommande()
                break
            else:
                # Le pointeur n'est pas au-dessus du bouton
                bouton.dessiner(self.couleurs['normal'])
        else:
            # Le pointeur n'est pas au-dessus d'un des boutons
            # initialisation au pointeur par défaut
            pygame.mouse.set_cursor(*pygame.cursors.arrow)

    def detruire(self):
        # initialisation du pointeur
        pygame.mouse.set_cursor(*pygame.cursors.arrow)


class MenuBouton(pygame.sprite.Sprite):
    """ Création d'un simple bouton rectangulaire """

    def __init__(self, texte, couleur, font, x, y, largeur, hauteur, commande):
        super().__init__()
        self._commande = commande

        self.image = pygame.Surface((largeur, hauteur))

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.texte = font.render(texte, True, (0, 0, 0))
        self.rectTexte = self.texte.get_rect()
        self.rectTexte.center = (largeur/2, hauteur/2)

        self.dessiner(couleur)

    def dessiner(self, couleur):
        self.image.fill(couleur)
        self.image.blit(self.texte, self.rectTexte)

    def executerCommande(self):
        # Appel de la commande du bouton
        self._commande()


class Application:
    """ Classe maîtresse gérant les différentes interfaces du jeu """
    difficultyLvl = 1

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snake python")

        self.fond = (150,)*3

        self.fenetre = pygame.display.set_mode((surfaceW, surfaceH))
        # Groupe de sprites utilisé pour l'affichage
        self.groupeGlobal = pygame.sprite.Group()
        self.statut = True
        self.difficultyLvl = 1

    def _initialiser(self):
        try:
            self.ecran.detruire()
            # Suppression de tous les sprites du groupe
            self.groupeGlobal.empty()
        except AttributeError:
            pass

    def getDifficulty(self):
        return self.difficultyLvl

    def difficulty(self):

        if self.difficultyLvl == 1:
            self.difficultyLvl = 2
        elif self.difficultyLvl == 2:
            self.difficultyLvl = 3
        elif self.difficultyLvl == 3:
            self.difficultyLvl = 1

        # with open("conf.txt", "r") as f:
        #     lines = f.readlines()
        # if len(lines) != 0:
        #     lines[0] = str(self.difficultyLvl)+".\n"
        # else:
        #     lines.append("1\n")

        with open("conf.txt", "w+") as f:
            f.write(str(self.difficultyLvl))
        print(self.difficultyLvl)

        self.settings()

    def menu(self):
        # Affichage du menu
        self._initialiser()
        self.ecran = Menu(self, self.groupeGlobal)

    def jeu(self):
        # Affichage du jeu
        self._initialiser()
        self.ecran = Jeu(self, self.groupeGlobal)

    def settings(self):
        self._initialiser()
        self.ecran = Settings(self, self.groupeGlobal)

    def quitter(self):
        self.statut = False

    def update(self):
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                self.quitter()
                return

        self.fenetre.fill(self.fond)
        self.ecran.update(events)
        self.groupeGlobal.update()
        self.groupeGlobal.draw(self.fenetre)
        pygame.display.update()


class Settings:
    fenetre = None
    app = None

    def __init__(self, application, *groupes):
        self.fenetre = application.fenetre
        self.couleurs = dict(
            normal=(0, 200, 0),
            survol=(0, 200, 200),
        )
        diffVal = ""

        # Using readlines()
        file = open('conf.txt', 'r')
        Lines = file.read()
        count = 0
        # Strips the newline character
        diffVal = Lines
        self.app = application
        # application.difficultyLvl = int(diffVal)
        font = pygame.font.SysFont('Helvetica', 24, bold=True)
        # noms des menus et commandes associées
        self.items = (
            ('DIFFICULTY ' + str(diffVal), app.difficulty),
            ('SETTINGS', app.settings),
            ('RETOUR', app.menu)
        )
        x = 500
        y = 300
        self._boutons = []
        for texte, cmd in self.items:
            mb = MenuBouton(
                texte,
                self.couleurs['normal'],
                font,
                x,
                y,
                200,
                50,
                cmd
            )
            self._boutons.append(mb)
            y += 120
            for groupe in groupes:
                groupe.add(mb)

    def update(self, events):
        clicGauche, *_ = pygame.mouse.get_pressed()
        posPointeur = pygame.mouse.get_pos()
        for bouton in self._boutons:
            # Si le pointeur souris est au-dessus d'un bouton
            if bouton.rect.collidepoint(*posPointeur):
                # Changement du curseur par un quelconque
                pygame.mouse.set_cursor(*pygame.cursors.tri_left)
                # Changement de la couleur du bouton
                bouton.dessiner(self.couleurs['survol'])
                # Si le clic gauche a été pressé
                if clicGauche:
                    # Appel de la fonction du bouton
                    r = bouton.executerCommande()

                break
            else:
                # Le pointeur n'est pas au-dessus du bouton
                bouton.dessiner(self.couleurs['normal'])
        else:
            # Le pointeur n'est pas au-dessus d'un des boutons
            # initialisation au pointeur par défaut
            pygame.mouse.set_cursor(*pygame.cursors.arrow)

    def detruire(self):
        # initialisation du pointeur
        pygame.mouse.set_cursor(*pygame.cursors.arrow)


class snake():
    body = []
    turns = {}

    def __init__(self, color, pos):
        # pos is given as coordinates on the grid ex (1,5)
        self.color = color
        self.head = cube(pos)
        self.body.append(self.head)
        self.dirnx = 0
        self.dirny = 1

    def move(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            keys = pygame.key.get_pressed()

            for key in keys:
                if keys[pygame.K_LEFT]:
                    self.dirnx = -1
                    self.dirny = 0
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
                elif keys[pygame.K_RIGHT]:
                    self.dirnx = 1
                    self.dirny = 0
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
                elif keys[pygame.K_UP]:
                    self.dirny = -1
                    self.dirnx = 0
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
                elif keys[pygame.K_DOWN]:
                    self.dirny = 1
                    self.dirnx = 0
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        for i, c in enumerate(self.body):
            p = c.pos[:]
            if p in self.turns:
                turn = self.turns[p]
                c.move(turn[0], turn[1])
                if i == len(self.body)-1:
                    self.turns.pop(p)
            else:
                c.move(c.dirnx, c.dirny)

    def reset(self, pos):
        self.head = cube(pos)
        self.body = []
        self.body.append(self.head)
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1

    def addCube(self):
        tail = self.body[-1]
        dx, dy = tail.dirnx, tail.dirny

        if dx == 1 and dy == 0:
            self.body.append(cube((tail.pos[0]-1, tail.pos[1])))
        elif dx == -1 and dy == 0:
            self.body.append(cube((tail.pos[0]+1, tail.pos[1])))
        elif dx == 0 and dy == 1:
            self.body.append(cube((tail.pos[0], tail.pos[1]-1)))
        elif dx == 0 and dy == -1:
            self.body.append(cube((tail.pos[0], tail.pos[1]+1)))

        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy

    def addSuperCube(self):
        self.addCube()
        self.addCube()

    def deleteCube(self):
        self.body.pop()

    def draw(self, surface):
        for i, c in enumerate(self.body):
            if i == 0:
                c.draw(surface, True)
            else:
                c.draw(surface)


class cube():
    rows = 40
    w = 1000

    def __init__(self, start, dirnx=1, dirny=0, color=(255, 0, 0)):
        self.pos = start
        self.dirnx = dirnx
        self.dirny = dirny  # "L", "R", "U", "D"
        self.color = color

    def move(self, dirnx, dirny):
        self.dirnx = dirnx
        self.dirny = dirny
        self.pos = (self.pos[0] + self.dirnx, self.pos[1] + self.dirny)

    def draw(self, surface, eyes=False):
        dis = surfaceW // self.rows
        i = self.pos[0]
        j = self.pos[1]

        pygame.draw.rect(surface, self.color, (i*dis+1, j*dis+1, dis-2, dis-2))
        if eyes:
            centre = dis//2
            radius = 3
            circleMiddle = (i*dis+centre-radius, j*dis+8)
            circleMiddle2 = (i*dis + dis - radius*2, j*dis+8)
            pygame.draw.circle(surface, (0, 0, 0), circleMiddle, radius)
            pygame.draw.circle(surface, (0, 0, 0), circleMiddle2, radius)


class Jeu:
    """ Simulacre de l'interface du jeu """
    cols = 25
    rows = 40
    fenetre = None
    snack = None
    snackNegative = None
    snackSuper = None
    s = None

    def __init__(self, jeu, *groupes):
        self.fenetre = jeu.fenetre
        s = snake((255, 0, 0), (10, 10))
        self.s = s
        s.addCube()
        self.snack = cube(self.randomSnack(s), color=(0, 255, 0))
        self.snackNegative = cube(self.randomSnack(s), color=(255, 0, 0))
        self.snackSuper = cube(self.randomSnack(s), color=(250, 245, 87))
        flag = True
        clock = pygame.time.Clock()
        pygame.display.update()
        while flag:
            pygame.time.delay(30)
            clock.tick(10)
            s.move()
            headPos = s.head.pos
            if headPos[0] >= 40 or headPos[0] < 0 or headPos[1] >= 40 or headPos[1] < 0:
                print("Score:", len(s.body))
                s.reset((10, 10))

            if s.body[0].pos == self.snack.pos:
                s.addCube()
                self.snack = cube(self.randomSnack(s), color=(0, 255, 0))
            if s.body[0].pos == self.snackSuper.pos:
                s.addSuperCube()
                self.snackSuper = cube(self.randomSnack(s), color=(250, 245, 87))
            if s.body[0].pos == self.snackNegative.pos:
                if len(s.body) == 1:
                    s.reset((10, 10))
                    print("You lose")
                else:
                    s.deleteCube()
                self.snackNegative = cube(self.randomSnack(s), color=(255, 0, 0))

            for x in range(len(s.body)):
                if s.body[x].pos in list(map(lambda z: z.pos, s.body[x+1:])):
                    print("Score:", len(s.body))
                    s.reset((10, 10))
                    break

            self.redrawWindow()
        font = pygame.font.SysFont(None, 24)

        img = font.render('hello', True, color=(255, 255, 255))
        self.fenetre.blit(img, (20, 20))

        self._fenetre = jeu.fenetre
        jeu.fond = (0, 0, 0)
        self.drawGrid()

    def redrawWindow(self):
        self.fenetre.fill((0, 0, 0))
        self.drawGrid()
        self.s.draw(self.fenetre)
        self.snack.draw(self.fenetre)
        self.snackNegative.draw(self.fenetre)
        self.snackSuper.draw(self.fenetre)
        pygame.display.update()
        pass

    def randomSnack(rows, item):
        positions = item

        while True:
            x = random.randrange(1, rows.rows-1)
            y = random.randrange(1, rows.rows-1)
            if len(list(filter(lambda z: z.pos == (x, y), positions))) > 0:
                continue
            else:
                break

        return (x, y)

    def drawGrid(self):
        sizeBtwn = surfaceW // self.rows

        x = 0
        y = 0
        for l in range(self.rows):
            x = x + sizeBtwn
            y = y + sizeBtwn

            pygame.draw.line(self.fenetre, (255, 255, 255),
                             (x, 0), (x, surfaceW))
            pygame.draw.line(self.fenetre, (255, 255, 255),
                             (0, y), (surfaceW, y))

    def randomSnack(rows, item):
        positions = item.body

        while True:
            x = random.randrange(1, rows.rows-1)
            y = random.randrange(1, rows.rows-1)
            if len(list(filter(lambda z: z.pos == (x, y), positions))) > 0:
                continue
            else:
                break

        return (x, y)

    def update(self, events):
        # self._fenetre.blit(self.texte, self.rectTexte)
        print(events)
        for event in events:
            if event.type == self._CLIGNOTER:
                self.creerTexte()
                break

    def detruire(self):
        pygame.time.set_timer(self._CLIGNOTER, 0)  # désactivation du timer


app = Application()
app.menu()

clock = pygame.time.Clock()

while app.statut:
    app.update()
    clock.tick(30)

pygame.quit()
