from superwires import games, color
import random

games.init(screen_width=1280, screen_height=720, fps=50)


class Man(games.Sprite):

    image = games.load_image("Stiv.png")

    def __init__(self):
        super(Man, self).__init__(image=Man.image, x = games.mouse.x, y=games.screen.height - 100)

    def update(self):
        self.x = games.mouse.x
        if self.left < 0:
            self.left = 0
        elif self.right > games.screen.width:
            self.right = games.screen.width
        self.check_catch()

    def check_catch(self):
        for nakovalny in self.overlapping_sprites:
            nakovalny.handle_caught()
            nakovalny.end_game()


class Nakovalny(games.Sprite):
    image = games.load_image("Nak (2).png")
    speed = 1.5

    def __init__(self, x,y = 100):
        super(Nakovalny, self).__init__(image=Nakovalny.image, x = x, y = y, dy=Nakovalny.speed)

    def update(self):
        if self.bottom > games.screen.height:
            self.destroy()

    def handle_caught(self):
        """Разрушение пиццы при пересечениии с сковородкой"""
        self.destroy()

    def end_game(self):
        end_message = games.Message(value="Game Over!", size = 90, color=color.red,
                                        x=games.screen.width / 2, y=games.screen.height / 2, lifetime=2*games.screen.fps,
                                        after_death = games.screen.quit)
        games.screen.add(end_message)

class Sky(games.Sprite):
    time_til_drop = 0
    image_sky = games.load_image("Sky.png")

    def __init__(self, y = -10, speed = 2, change = 200):
        super(Sky, self).__init__(image = Sky.image_sky, x=games.screen.width/2, y=y, dx=speed)
        self.change = change

    def update(self):
        if self.left < 0 or self.right > games.screen.width:
            self.dx = -self.dx
        elif random.randrange(self.change) == 0:
            self.dx = -self.dx
        self.check_drop()

    def check_drop(self):
        if self.time_til_drop > 0:
            self.time_til_drop -= 1
        else:
            new_krip = Nakovalny(x = self.x)
            games.screen.add(new_krip)
            self.time_til_drop = int(new_krip.height * 1.2 / Nakovalny.speed)

def main():
    background_image = games.load_image("back_image.jpg", transparent=False)
    games.screen.background = background_image

    the_Man = Man()
    the_Sky = Sky()

    games.screen.add(the_Man)
    games.screen.add(the_Sky)

    games.mouse.is_visible = False
    games.mouse.event_grab = True
    games.screen.mainloop()


if __name__ == '__main__':
    main()
