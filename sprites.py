import copy

import pygame
import os
import config


class BaseSprite(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, row, col, file_name, transparent_color=None):
        pygame.sprite.Sprite.__init__(self)
        if file_name in BaseSprite.images:
            self.image = BaseSprite.images[file_name]
        else:
            self.image = pygame.image.load(os.path.join(config.IMG_FOLDER, file_name)).convert()
            self.image = pygame.transform.scale(self.image, (config.TILE_SIZE, config.TILE_SIZE))
            BaseSprite.images[file_name] = self.image
        # making the image transparent (if needed)
        if transparent_color:
            self.image.set_colorkey(transparent_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (col * config.TILE_SIZE, row * config.TILE_SIZE)
        self.row = row
        self.col = col


class Agent(BaseSprite):
    def __init__(self, row, col, file_name):
        super(Agent, self).__init__(row, col, file_name, config.DARK_GREEN)

    def move_towards(self, row, col):
        row = row - self.row
        col = col - self.col
        self.rect.x += col
        self.rect.y += row

    def place_to(self, row, col):
        self.row = row
        self.col = col
        self.rect.x = col * config.TILE_SIZE
        self.rect.y = row * config.TILE_SIZE

    # game_map - list of lists of elements of type Tile
    # goal - (row, col)
    # return value - list of elements of type Tile
    def get_agent_path(self, game_map, goal):
        pass


class ExampleAgent(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        path = [game_map[self.row][self.col]]

        row = self.row
        col = self.col
        while True:
            if row != goal[0]:
                row = row + 1 if row < goal[0] else row - 1
            elif col != goal[1]:
                col = col + 1 if col < goal[1] else col - 1
            else:
                break
            path.append(game_map[row][col])
        return path


class Tile(BaseSprite):
    def __init__(self, row, col, file_name):
        super(Tile, self).__init__(row, col, file_name)

    def position(self):
        return self.row, self.col

    def cost(self):
        pass

    def kind(self):
        pass


class Stone(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'stone.png')

    def cost(self):
        return 1000

    def kind(self):
        return 's'


class Water(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'water.png')

    def cost(self):
        return 500

    def kind(self):
        return 'w'


class Road(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'road.png')

    def cost(self):
        return 2

    def kind(self):
        return 'r'


class Grass(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'grass.png')

    def cost(self):
        return 3

    def kind(self):
        return 'g'


class Mud(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'mud.png')

    def cost(self):
        return 5

    def kind(self):
        return 'm'


class Dune(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'dune.png')

    def cost(self):
        return 7

    def kind(self):
        return 's'


class Goal(BaseSprite):
    def __init__(self, row, col):
        super().__init__(row, col, 'x.png', config.DARK_GREEN)


class Trail(BaseSprite):
    def __init__(self, row, col, num):
        super().__init__(row, col, 'trail.png', config.DARK_GREEN)
        self.num = num

    def draw(self, screen):
        text = config.GAME_FONT.render(f'{self.num}', True, config.WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


# ///////////////////////


class Aki(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_allpossible_neighbours(self, game_map: list[list[Tile]], put: list[Tile], row, col):
        neigh: list[Tile] = []
        if row - 1 >= 0: neigh.insert(0, game_map[row - 1][col])  # sever
        if col + 1 < len(game_map[0]): neigh.insert(0, game_map[row][col + 1])  # istok
        if row + 1 < len(game_map): neigh.insert(0, game_map[row + 1][col])  # jug
        if col - 1 >= 0: neigh.insert(0, game_map[row][col - 1])  # zapad
        final_list = [elem for elem in neigh if elem not in put]
        return sorted(final_list, key=lambda elem: (elem.cost()), reverse=True)

    def get_agent_path(self, game_map: list[list[Tile]], goal):
        row = self.row
        col = self.col
        put: list[Tile] = []
        lista: list[list[int]] = []
        lista.append([row, col, 0])  # dodajaem nivo -0
        level_before = 0
        level_now = 0
        while True:
            # ako je lista prazna znaci da nismo dobili resenje
            if (len(lista) == 0):
                print("GRESKA_ PRAZNA LISTA")
            # skidam iz lliste sa pocetka
            elemLista = lista.pop(0)
            level_before = level_now
            level_now = elemLista[2]
            if level_now < level_before:
                for i in range(0, level_before - level_now):
                    put.pop()
            elem = game_map[int(elemLista[0])][int(elemLista[1])]
            # dodajem u put
            put.append(elem)
            # da li je ciljni? da- gotovo
            if elem.position()[0] == goal[0] and elem.position()[1] == goal[1]:
                return put
            # else dodaj sledbenike na pocetak
            poss_neigh = self.get_allpossible_neighbours(game_map, put, elemLista[0], elemLista[1])  # lista tile
            # ako nema sledbenike skidam iz puta
            if len(poss_neigh) == 0:
                put.pop()
                # treba da se popuje jos razlika levela
            else:
                for pn in poss_neigh:
                    lista.insert(0, [pn.position()[0], pn.position()[1], level_now + 1])


# -----------------------------------------------------------


class bfs_tile():
    # pos:list[int]
    row: int
    col: int
    path: list[Tile]


class Jocke(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    # -*-
    # *|*
    # -!-
    # mi smo ! i trazimo prosek od |
    #     ! je from
    def get_avg_neigh(self, game_map: list[list[Tile]], neighFrom: Tile, curr: Tile):
        add = 0;  # ukupna cena za susede
        num = 0;  # ukupno suseda
        row = curr.position()[0]
        col = curr.position()[1]
        if row - 1 >= 0 and game_map[row - 1][col].position() != neighFrom.position():  # sever
            add += game_map[row - 1][col].cost()
            num += 1
        if col + 1 < len(game_map[0]) and game_map[row][col + 1].position() != neighFrom.position():  # istok
            add += game_map[row][col + 1].cost()
            num += 1
        if row + 1 < len(game_map) and game_map[row + 1][col].position() != neighFrom.position():  # jug
            add += game_map[row + 1][col].cost()
            num += 1
        if col - 1 >= 0 and game_map[row][col - 1].position() != neighFrom.position():  # zapad
            add += game_map[row][col - 1].cost()
            num += 1
        return add / num

    def get_allpossible_neighbours(self, game_map: list[list[Tile]], row, col, elem_lista: bfs_tile, visited:list[Tile]):
        put: list[Tile] = elem_lista.path
        neigh: list[Tile] = []
        if row - 1 >= 0: neigh.append(game_map[row - 1][col])  # sever
        if col + 1 < len(game_map[0]): neigh.append(game_map[row][col + 1])  # istok
        if row + 1 < len(game_map): neigh.append(game_map[row + 1][col])  # jug
        if col - 1 >= 0: neigh.append(game_map[row][col - 1])  # zapad
        # elem je tipa Tile
        final_list = [elem for elem in neigh if elem not in put and elem not in visited]
        neighFrom = game_map[row][col]
        t_list = sorted(final_list, key=lambda elem: (self.get_avg_neigh(game_map, neighFrom, elem)))
        return t_list

    def get_agent_path(self, game_map, goal):
        put: list[Tile] = []
        lista: list[bfs_tile] = []
        row = self.row
        col = self.col
        temp_new_bfs_tile: list[Tile] = []
        new_bfs_tile = bfs_tile()
        new_bfs_tile.row = row
        new_bfs_tile.col = col
        new_bfs_tile.path = []
        lista.append(new_bfs_tile)

        visited:list[Tile]=[]

        while True:
            # ukloni cvor sa pocetka liste
            elemLista = lista.pop(0)
            elem = game_map[int(elemLista.row)][int(elemLista.col)]
            if elem in visited: continue
            visited.append(elem)
            # da li je ciljni
            if elem.position()[0] == goal[0] and elem.position()[1] == goal[1]:
                # return put
                return elemLista.path
            poss_neigh = self.get_allpossible_neighbours(game_map, elemLista.row, elemLista.col,
                                                         elemLista,visited)  # lista tile
            # dodaj sledbenike na kraj
            if poss_neigh == 0:
                continue
            temp_new_bfs_tile = []
            if len(elemLista.path) != 0:
                for ii in elemLista.path:
                    # temp_new_bfs_tile.path.append(ii)
                    temp_new_bfs_tile.append(ii)
            temp_new_bfs_tile.append(elem)
            for pn in poss_neigh:
                new_bfs_tile = bfs_tile()
                new_bfs_tile.path = []
                new_bfs_tile.row = pn.position()[0]
                new_bfs_tile.col = pn.position()[1]
                # treba dodati u path path oca
                new_bfs_tile.path = temp_new_bfs_tile
                if pn.position()[0] == goal[0] and pn.position()[1] == goal[1]:
                    new_bfs_tile.path.append(game_map[goal[0]][goal[1]])
                    return new_bfs_tile.path
                lista.append(new_bfs_tile)


class part_path():
    path: list[Tile]
    cost: int
    path_len: int


class Draza(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_part_path_cost(self, part_path_cur: part_path):
        return part_path_cur.cost

    def get_part_path_len(self, part_path_cur: part_path):
        return part_path_cur.path_len

    def get_allpossible_neighbours(self, game_map: list[list[Tile]], cur_part_path: part_path, visited:list[Tile]):
        parc_put: list[Tile] = cur_part_path.path
        row = parc_put[-1].position()[0]
        col = parc_put[-1].position()[1]
        neigh: list[Tile] = []
        if row - 1 >= 0: neigh.append(game_map[row - 1][col])  # sever
        if col + 1 < len(game_map[0]): neigh.append(game_map[row][col + 1])  # istok
        if row + 1 < len(game_map): neigh.append(game_map[row + 1][col])  # jug
        if col - 1 >= 0: neigh.append(game_map[row][col - 1])  # zapad
        # elem je tipa Tile
        final_list = [elem for elem in neigh if elem not in parc_put and elem not in visited]

        return final_list

    def get_agent_path(self, game_map: list[list[Tile]], goal):
        path = [game_map[self.row][self.col]]
        list_partial_paths: list[part_path] = []
        row = self.row
        col = self.col
        new_part_path = part_path()
        new_part_path.cost = game_map[row][col].cost()
        new_part_path.path_len = 1
        new_part_path.path = []
        new_part_path.path.append(game_map[row][col])
        list_partial_paths.append(new_part_path)
        visited:list[Tile]=[]
        while True:
            # if len(list_partial_paths)==0 return GRESKA
            # uklanjamo putanju sa pocetka
            # obrisi parc putanju oca
            cur_part_path: part_path = list_partial_paths.pop(0)
            cur_tile: Tile = cur_part_path.path[-1]  # dohvati poslednji Tile
            if cur_tile in visited:continue
            visited.append(cur_tile)
            if (cur_tile.position()[0] == goal[0] and cur_tile.position()[1] == goal[1]):
                return cur_part_path.path
            # nadji komsije i poredjaj ih po ceni rastuce- vratice listu komsija tj Tileova
            # ja ovde nisam sortirala komsije
            poss_neigh = self.get_allpossible_neighbours(game_map, cur_part_path,visited)  # lista tile
            # ako nema komsija
            if len(poss_neigh) == 0:
                continue

            for n in poss_neigh:
                new_part_path: part_path = part_path()
                # new_part_path = copy.copy(cur_part_path)
                new_part_path.cost = self.get_part_path_cost(cur_part_path) + n.cost()
                new_part_path.path_len =cur_part_path.path_len+1
                new_part_path.path = []
                new_part_path.path = cur_part_path.path[:]

                new_part_path.path.append(n)
                # ovde kad se doddaje sortiraj i po ceni i po duzini
                list_partial_paths.append(new_part_path)
            list_partial_paths=sorted(list_partial_paths, key=lambda elem: (self.get_part_path_cost(elem), self.get_part_path_len(elem)))





class Bole(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_part_path_cost(self, part_path_cur: part_path):
        return part_path_cur.cost

    def get_part_path_len(self, part_path_cur: part_path):
        return part_path_cur.path_len

    def get_allpossible_neighbours(self, game_map: list[list[Tile]], cur_part_path: part_path, visited:list[Tile]):
        parc_put: list[Tile] = cur_part_path.path
        row = parc_put[-1].position()[0]
        col = parc_put[-1].position()[1]
        neigh: list[Tile] = []
        if row - 1 >= 0: neigh.append(game_map[row - 1][col])  # sever
        if col + 1 < len(game_map[0]): neigh.append(game_map[row][col + 1])  # istok
        if row + 1 < len(game_map): neigh.append(game_map[row + 1][col])  # jug
        if col - 1 >= 0: neigh.append(game_map[row][col - 1])  # zapad
        # elem je tipa Tile
        final_list = [elem for elem in neigh if elem not in parc_put and elem not in visited]

        return final_list
    def heuristic(self,goal,node:Tile,min):
        dx = abs(node.position()[0] - goal[0])
        dy = abs(node.position()[1] - goal[1])

        return  min*(dx + dy)

    def get_agent_path(self, game_map: list[list[Tile]], goal):
        path = [game_map[self.row][self.col]]
        list_partial_paths: list[part_path] = []
        row = self.row
        col = self.col

        # ubaci iznad while
        min= game_map[0][0].cost()
        for i in range(0,len(game_map)):
            for j in range(0,len(game_map[i])):
                if game_map[i][j].cost()<min:
                    min=game_map[i][j].cost()



        new_part_path = part_path()
        new_part_path.cost = game_map[row][col].cost()
        new_part_path.path_len = 1
        new_part_path.path = []
        new_part_path.path.append(game_map[row][col])
        list_partial_paths.append(new_part_path)
        visited:list[Tile]=[]
        while True:
            # if len(list_partial_paths)==0 return GRESKA
            # uklanjamo putanju sa pocetka
            # obrisi parc putanju oca
            cur_part_path: part_path = list_partial_paths.pop(0)
            cur_tile: Tile = cur_part_path.path[-1]  # dohvati poslednji Tile
            if cur_tile in visited:continue
            visited.append(cur_tile)
            if (cur_tile.position()[0] == goal[0] and cur_tile.position()[1] == goal[1]):
                return cur_part_path.path
            # nadji komsije i poredjaj ih po ceni rastuce- vratice listu komsija tj Tileova
            # ja ovde nisam sortirala komsije
            poss_neigh = self.get_allpossible_neighbours(game_map, cur_part_path,visited)  # lista tile
            # ako nema komsija
            if len(poss_neigh) == 0:
                continue

            for n in poss_neigh:
                new_part_path: part_path = part_path()
                # new_part_path = copy.copy(cur_part_path)
                new_part_path.cost = cur_part_path.cost + n.cost()
                new_part_path.path_len =cur_part_path.path_len+1
                new_part_path.path = []
                new_part_path.path = cur_part_path.path[:]

                new_part_path.path.append(n)
                # ovde kad se doddaje sortiraj i po ceni i po duzini
                list_partial_paths.append(new_part_path)
            list_partial_paths=sorted(list_partial_paths, key=lambda elem: (elem.cost + self.heuristic(goal,elem.path[-1],min), elem.path_len))


