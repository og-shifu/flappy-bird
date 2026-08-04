from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle, RoundedRectangle
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.core.window import Window
from random import randint, random
from math import sin


class FlappyBird(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.state = "menu"
        self.bird_x = 90
        self.bird_y = 0
        self.bird_size = 48
        self.velocity = 0

        self.gravity = -0.58
        self.jump = 10
        self.pipe_width = 78
        self.pipe_gap = 190
        self.pipe_speed = 4

        self.score = 0
        self.coins = 0
        self.high_score = 0

        self.pipes = []
        self.coin_objects = []
        self.clouds = []
        self.ground_x = 0
        self.world_time = 0
        self.day = True

        self.title = Label(
            text="FLAPPY SKY",
            font_size=52, bold=True,
            color=(1, 0.85, 0.1, 1),
            size_hint=(1, None), height=80,
            pos=(0, Window.height * 0.68)
        )
        self.add_widget(self.title)

        self.info = Label(
            text="",
            font_size=24, bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, None), height=100,
            pos=(0, Window.height * 0.48)
        )
        self.add_widget(self.info)

        self.score_label = Label(
            text="0",
            font_size=55, bold=True,
            color=(1, 1, 1, 1),
            size_hint=(None, None), size=(120, 80),
            pos=(Window.width / 2 - 60, Window.height - 105)
        )
        self.add_widget(self.score_label)

        self.coin_label = Label(
            text="🪙 0",
            font_size=28, bold=True,
            color=(1, 0.9, 0.1, 1),
            size_hint=(None, None), size=(150, 60),
            pos=(15, Window.height - 70)
        )
        self.add_widget(self.coin_label)

        self.game_over_label = Label(
            text="",
            font_size=34, bold=True,
            color=(1, 1, 1, 1),
            halign="center",
            size_hint=(1, None), height=180,
            pos=(0, Window.height / 2 - 90)
        )
        self.add_widget(self.game_over_label)

        self.make_clouds()
        self.reset_positions()

        Clock.schedule_interval(self.update, 1 / 60)

    def make_clouds(self):
        self.clouds = []
        for i in range(7):
            self.clouds.append({
                "x": random() * Window.width,
                "y": randint(int(Window.height * .55), int(Window.height * .9)),
                "size": randint(45, 95),
                "speed": random() * 0.8 + 0.25
            })

    def reset_positions(self):
        self.bird_y = Window.height / 2
        self.velocity = 0
        self.pipes = []
        self.coin_objects = []
        self.score = 0
        self.score_label.text = "0"
        self.coin_label.text = f"🪙 {self.coins}"
        self.create_pipe()

    def create_pipe(self):
        gap_y = randint(220, max(221, int(Window.height - 220)))
        top_height = Window.height - (gap_y + self.pipe_gap / 2)
        bottom_height = gap_y - self.pipe_gap / 2

        pipe = {
            "x": Window.width,
            "top": top_height,
            "bottom": bottom_height,
            "passed": False
        }
        self.pipes.append(pipe)

        # One collectible coin in the gap
        self.coin_objects.append({
            "x": Window.width + self.pipe_width / 2 - 13,
            "y": gap_y - 13,
            "size": 26,
            "taken": False
        })

    def start_game(self):
        self.state = "playing"
        self.title.text = ""
        self.info.text = ""
        self.game_over_label.text = ""
        self.reset_positions()

    def on_touch_down(self, touch):
        if self.state == "menu":
            # Tap anywhere on menu to start
            self.start_game()
        elif self.state == "playing":
            self.velocity = self.jump
        else:
            self.start_game()
        return True

    def update(self, dt):
        self.world_time += dt

        # Moving clouds always
        for cloud in self.clouds:
            cloud["x"] -= cloud["speed"]
            if cloud["x"] < -cloud["size"] * 1.5:
                cloud["x"] = Window.width + cloud["size"]
                cloud["y"] = randint(
                    int(Window.height * .55),
                    int(Window.height * .9)
                )

        # Day/night cycle: every ~25 seconds
        self.day = int(self.world_time / 25) % 2 == 0

        if self.state == "playing":
            self.velocity += self.gravity
            self.bird_y += self.velocity

            for pipe in self.pipes:
                pipe["x"] -= self.pipe_speed

            for coin in self.coin_objects:
                coin["x"] -= self.pipe_speed

            if len(self.pipes) == 0 or self.pipes[-1]["x"] < Window.width - 260:
                self.create_pipe()

            for pipe in self.pipes:
                if not pipe["passed"] and pipe["x"] + self.pipe_width < self.bird_x:
                    pipe["passed"] = True
                    self.score += 1
                    self.score_label.text = str(self.score)

            self.pipes = [p for p in self.pipes if p["x"] > -self.pipe_width]
            self.coin_objects = [
                c for c in self.coin_objects if c["x"] > -50 and not c["taken"]
            ]

            self.check_coin()
            self.check_collision()

        elif self.state == "menu":
            self.bird_y = Window.height * .55 + sin(self.world_time * 3) * 12

        self.draw_game()

    def check_coin(self):
        bx = self.bird_x + self.bird_size / 2
        by = self.bird_y + self.bird_size / 2

        for coin in self.coin_objects:
            cx = coin["x"] + coin["size"] / 2
            cy = coin["y"] + coin["size"] / 2

            if abs(bx - cx) < 35 and abs(by - cy) < 35:
                coin["taken"] = True
                self.coins += 1
                self.coin_label.text = f"🪙 {self.coins}"

    def check_collision(self):
        if self.bird_y <= 45 or self.bird_y + self.bird_size >= Window.height:
            self.end_game()
            return

        left = self.bird_x + 7
        right = self.bird_x + self.bird_size - 7
        bottom = self.bird_y + 7
        top = self.bird_y + self.bird_size - 7

        for pipe in self.pipes:
            if right > pipe["x"] and left < pipe["x"] + self.pipe_width:
                gap_bottom = pipe["bottom"]
                gap_top = Window.height - pipe["top"]

                if bottom < gap_bottom or top > gap_top:
                    self.end_game()
                    return

    def end_game(self):
        if self.state != "playing":
            return
        self.state = "gameover"
        if self.score > self.high_score:
            self.high_score = self.score

        self.game_over_label.text = (
            f"GAME OVER\n"
            f"Score: {self.score}   Best: {self.high_score}\n\n"
            f"TAP TO RESTART"
        )

    def draw_game(self):
        self.canvas.clear()

        with self.canvas:
            # Background day/night
            if self.day:
                Color(0.35, 0.75, 1, 1)
            else:
                Color(0.05, 0.09, 0.22, 1)

            Rectangle(pos=(0, 0), size=(Window.width, Window.height))

            # Sun / moon
            if self.day:
                Color(1, 0.85, 0.2, 1)
            else:
                Color(0.85, 0.9, 1, 1)

            Ellipse(
                pos=(Window.width - 85, Window.height - 130),
                size=(55, 55)
            )

            # Stars at night
            if not self.day:
                Color(1, 1, 1, .8)
                for i in range(25):
                    x = (i * 83) % int(Window.width)
                    y = Window.height - 100 - ((i * 47) % int(Window.height * .65))
                    Ellipse(pos=(x, y), size=(3, 3))

            # Clouds
            Color(1, 1, 1, .7 if self.day else .15)
            for cloud in self.clouds:
                x, y, s = cloud["x"], cloud["y"], cloud["size"]
                Ellipse(pos=(x, y), size=(s, s * .5))
                Ellipse(pos=(x + s * .35, y + 8), size=(s * .8, s * .6))
                Ellipse(pos=(x + s * .65, y), size=(s * .7, s * .45))

            # Pipes
            for pipe in self.pipes:
                x = pipe["x"]
                top = pipe["top"]
                bottom = pipe["bottom"]

                # shadow
                Color(.02, .2, .05, 1)
                Rectangle(pos=(x + 6, Window.height - top),
                          size=(self.pipe_width, top))
                Rectangle(pos=(x + 6, 0),
                          size=(self.pipe_width, bottom))

                # body
                Color(.08, .65, .2, 1)
                Rectangle(pos=(x, Window.height - top),
                          size=(self.pipe_width - 5, top))
                Rectangle(pos=(x, 0),
                          size=(self.pipe_width - 5, bottom))

                # bright stripe
                Color(.3, .95, .35, 1)
                Rectangle(pos=(x + 9, Window.height - top),
                          size=(12, top))
                Rectangle(pos=(x + 9, 0),
                          size=(12, bottom))

                # caps
                Color(.05, .48, .12, 1)
                RoundedRectangle(
                    pos=(x - 7, Window.height - top - 18),
                    size=(self.pipe_width + 9, 30),
                    radius=[8]
                )
                RoundedRectangle(
                    pos=(x - 7, bottom - 10),
                    size=(self.pipe_width + 9, 30),
                    radius=[8]
                )

                Color(.35, 1, .4, 1)
                Rectangle(
                    pos=(x + 2, Window.height - top - 8),
                    size=(50, 5)
                )
                Rectangle(
                    pos=(x + 2, bottom + 2),
                    size=(50, 5)
                )

            # Coins
            for coin in self.coin_objects:
                if not coin["taken"]:
                    x, y, s = coin["x"], coin["y"], coin["size"]

                    Color(.65, .4, .02, 1)
                    Ellipse(pos=(x - 2, y - 2), size=(s + 4, s + 4))

                    Color(1, .78, .05, 1)
                    Ellipse(pos=(x, y), size=(s, s))

                    Color(1, .95, .45, 1)
                    Ellipse(pos=(x + 5, y + 5), size=(s * .35, s * .35))

            # Bird shadow
            Color(.05, .1, .1, .2)
            Ellipse(pos=(self.bird_x + 5, self.bird_y - 5), size=(42, 14))

            # Bird outline
            Color(.75, .3, 0, 1)
            Ellipse(pos=(self.bird_x - 2, self.bird_y - 2),
                    size=(self.bird_size + 4, self.bird_size + 4))

            # Bird body
            Color(1, .78, .05, 1)
            Ellipse(pos=(self.bird_x, self.bird_y),
                    size=(self.bird_size, self.bird_size))

            # Belly
            Color(1, .9, .35, 1)
            Ellipse(pos=(self.bird_x + 8, self.bird_y + 4), size=(32, 30))

            # Wing
            Color(.95, .55, .02, 1)
            Ellipse(pos=(self.bird_x - 5, self.bird_y + 8), size=(30, 20))

            # Eye
            Color(1, 1, 1, 1)
            Ellipse(pos=(self.bird_x + 28, self.bird_y + 28), size=(16, 16))
            Color(.03, .03, .03, 1)
            Ellipse(pos=(self.bird_x + 35, self.bird_y + 33), size=(7, 7))

            # Beak
            Color(1, .35, .02, 1)
            Rectangle(pos=(self.bird_x + 39, self.bird_y + 15), size=(20, 10))

            # Ground
            Color(.65, .42, .16, 1)
            Rectangle(pos=(0, 0), size=(Window.width, 45))

            Color(.35, .75, .15, 1)
            Rectangle(pos=(0, 40), size=(Window.width, 14))

            # Ground stripes moving
            Color(.5, .3, .1, 1)
            stripe = 50
            offset = int(self.world_time * self.pipe_speed * 2) % stripe
            for x in range(-stripe, int(Window.width) + stripe, stripe):
                Rectangle(pos=(x - offset, 0), size=(25, 40))


class FlappyApp(App):
    def build(self):
        return FlappyBird()


if __name__ == "__main__":
    FlappyApp().run()
