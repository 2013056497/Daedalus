from Game import  Game

def main():
    instance = Game()
    while instance.gameover():
        instance.labyrinth()

if __name__ == "__main__":
    main()