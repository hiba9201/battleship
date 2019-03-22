import tkinter
from PIL import ImageTk, Image
from game import environment


class Application:
    @staticmethod
    def run():
        Game.create_window()


class Game:
    @staticmethod
    def generate_field(root, play_field):
        image = ImageTk.PhotoImage(Image.open("images/blue_cell.png"))
        bot_field_gui = tkinter.Frame(root, bd=5, bg='blue')
        for x in range(len(play_field)):
            for y in range(len(play_field[x])):
                frame = tkinter.Frame(bot_field_gui)
                cell = tkinter.Button(frame, bd=5, width=10,
                                      height=10,
                                      image=image)
                cell.pack()
                frame.grid(row=x, column=y)
        bot_field_gui.pack()

    @staticmethod
    def create_window():
        window = tkinter.Tk()
        window.title('Battleship')
        bot_field = environment.Field.create_field()
        Game.generate_field(window, bot_field)

        window.mainloop()


def process_click():
    pass
