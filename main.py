import tkinter as tk


class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = 10
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='#feca57', outline='#ff9f43', width=2)
        super(Ball, self).__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        # Batasi pantulan atas di bawah garis HUD (y >= 42)
        if coords[1] <= 42:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        points_earned = 0
        for game_object in game_objects:
            if isinstance(game_object, Brick):
                points_earned += game_object.hit()
        return points_earned


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 90
        self.height = 12
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#00d2d3', outline='#54a0ff', width=2)
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)


class Brick(GameObject):
    COLORS = {1: '#ff6b6b', 2: '#48dbfb', 3: '#1dd1a1'}

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, outline='#222f3e', width=1.5,
                                       tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        # Modifikasi Scoring: Poin diperoleh berdasarkan hit atau hancur total
        self.hits -= 1
        if self.hits == 0:
            self.delete()
            return 25  # Bonus 25 poin saat bata hancur total
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])
            return 10  # 10 poin saat terkena pantulan pertama


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.score = 0
        self.high_score = 0
        self.width = 610
        self.height = 430
        self.canvas = tk.Canvas(self, bg='#1a1a2e',
                                width=self.width,
                                height=self.height,
                                highlightthickness=0)
        self.canvas.pack()
        self.pack()

        # Garis pembatas HUD atas
        self.canvas.create_line(0, 42, self.width, 42, fill='#30336b', width=1.5)

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 370)
        self.items[self.paddle.item] = self.paddle
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 70, 2)
            self.add_brick(x + 37.5, 95, 1)
            self.add_brick(x + 37.5, 120, 1)

        self.score_hud = None
        self.high_score_hud = None
        self.lives_hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>',
                         lambda _: self.paddle.move(-12))
        self.canvas.bind('<Right>',
                         lambda _: self.paddle.move(12))

    def setup_game(self):
        self.add_ball()
        self.update_hud()
        self.text = self.draw_text(self.width / 2, 230,
                                   'Press SPACE to Start', size='22', fill='#ffffff')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 352)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='30', fill='#ffffff'):
        font = ('Segoe UI', size, 'bold')
        return self.canvas.create_text(x, y, text=text,
                                       font=font, fill=fill)

    def add_score(self, points):
        self.score += points
        if self.score > self.high_score:
            self.high_score = self.score
        self.update_hud()

    def update_hud(self):
        # Modifikasi HUD: Skor, High Score, dan Nyawa Simbol Hati (Heart Icons)
        score_text = f'SCORE: {self.score}'
        high_text = f'HIGH: {self.high_score}'
        hearts = '❤️ ' * max(0, self.lives) if self.lives > 0 else '💔 GAME OVER'

        if self.score_hud is None:
            self.score_hud = self.canvas.create_text(
                65, 21, text=score_text,
                font=('Segoe UI', 12, 'bold'), fill='#feca57')
            self.high_score_hud = self.canvas.create_text(
                self.width / 2, 21, text=high_text,
                font=('Segoe UI', 12, 'bold'), fill='#c8d6e5')
            self.lives_hud = self.canvas.create_text(
                self.width - 80, 21, text=hearts,
                font=('Segoe UI', 12, 'bold'), fill='#ff6b6b')
        else:
            self.canvas.itemconfig(self.score_hud, text=score_text)
            self.canvas.itemconfig(self.high_score_hud, text=high_text)
            self.canvas.itemconfig(self.lives_hud, text=hearts)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:
            self.ball.speed = None
            self.draw_text(self.width / 2, 230, 'YOU WIN!', size='36', fill='#1dd1a1')
        elif self.ball.get_position()[3] >= self.height:
            self.ball.speed = None
            self.lives -= 1
            self.update_hud()
            if self.lives < 0:
                self.draw_text(self.width / 2, 230, 'GAME OVER', size='36', fill='#ff6b6b')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        points_earned = self.ball.collide(objects)
        if points_earned > 0:
            self.add_score(points_earned)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Brick Breaker Arcade - Ilham (20240140118)')
    root.resizable(False, False)
    game = Game(root)
    game.mainloop()
