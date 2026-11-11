import tkinter as tk


class GameObject(object):
    """Kelas dasar untuk seluruh objek visual di dalam game (OOP Base Class)."""
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
    """Objek bola yang memantul dan mendeteksi tabrakan (Inheritance dari GameObject)."""
    def __init__(self, canvas, x, y, speed=10):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = speed
        # Modifikasi Visual: Bola glowing emas dengan outline oranye arcade
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='#feca57', outline='#ff9f43', width=2)
        super(Ball, self).__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        # Pantulan dinding samping (kiri dan kanan)
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        # Pantulan dinding atas di bawah garis HUD (y >= 44)
        if coords[1] <= 44:
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

        # Modifikasi OOP: Mengumpulkan skor dari setiap bata yang tertabrak
        points_earned = 0
        for game_object in game_objects:
            if isinstance(game_object, Brick):
                points_earned += game_object.hit()
        return points_earned


class Paddle(GameObject):
    """Objek raket pemain yang dapat digerakkan ke kiri dan kanan."""
    def __init__(self, canvas, x, y):
        self.width = 95
        self.height = 12
        self.ball = None
        # Modifikasi Visual: Paddle modern neon cyan dengan border rapi
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
    """Objek bata sasaran dengan variasi ketahanan & poin per level hit."""
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
        self.hits -= 1
        if self.hits == 0:
            self.delete()
            return 25  # Bonus 25 poin saat bata hancur total
        else:
            self.canvas.itemconfig(self.item, fill=Brick.COLORS[self.hits])
            return 10  # 10 poin saat memukul lapisan bata


class Game(tk.Frame):
    """Controller utama game yang mengatur siklus hidup, HUD, kontrol, dan level."""
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.is_running = False
        self.paused = False

        self.width = 610
        self.height = 430
        self.canvas = tk.Canvas(self, bg='#1a1a2e',
                                width=self.width,
                                height=self.height,
                                highlightthickness=0)
        self.canvas.pack()
        self.pack()

        # Garis batas pembagi HUD di atas arena game
        self.canvas.create_line(0, 44, self.width, 44, fill='#30336b', width=1.5)

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 375)
        self.items[self.paddle.item] = self.paddle

        self.text = None
        self.subtext = None
        self.pause_text = None
        self.pause_sub = None
        self.hud_score = None
        self.hud_level = None
        self.hud_lives = None

        self.load_level(self.level)
        self.setup_game()
        self.canvas.focus_set()

        # Modifikasi Kontrol: Dukungan kontrol panah keyboard dan tombol A / D
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-14))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(14))
        self.canvas.bind('<a>', lambda _: self.paddle.move(-14))
        self.canvas.bind('<d>', lambda _: self.paddle.move(14))
        self.canvas.bind('<A>', lambda _: self.paddle.move(-14))
        self.canvas.bind('<D>', lambda _: self.paddle.move(14))

        # Modifikasi Kontrol: Tombol Pause [P], Quick Restart [R], dan Screenshot [F12]
        self.canvas.bind('<p>', lambda _: self.toggle_pause())
        self.canvas.bind('<P>', lambda _: self.toggle_pause())
        self.canvas.bind('<r>', lambda _: self.restart_game())
        self.canvas.bind('<R>', lambda _: self.restart_game())
        self.canvas.bind('<F12>', lambda _: self.capture_screenshot())

    def capture_screenshot(self):
        """Menyimpan tangkapan layar tampilan game langsung ke folder screenshots/."""
        try:
            import os
            from PIL import ImageGrab
            os.makedirs('screenshots', exist_ok=True)
            self.master.update()
            x = self.master.winfo_rootx()
            y = self.master.winfo_rooty()
            w = self.master.winfo_width()
            h = self.master.winfo_height()
            img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
            img.save('screenshots/tampilan_modifikasi.png')
            print("Screenshot berhasil disimpan ke screenshots/tampilan_modifikasi.png")
        except Exception as e:
            print(f"Gagal mengambil screenshot: {e}")

    def load_level(self, level):
        """Membuat susunan bata berdasarkan tingkat level (Level 1 atau Level 2)."""
        # Hapus sisa bata lama jika ada
        for item_id in list(self.items.keys()):
            if isinstance(self.items[item_id], Brick):
                self.items[item_id].delete()
                del self.items[item_id]

        if level == 1:
            for x in range(5, self.width - 5, 75):
                self.add_brick(x + 37.5, 70, 2)
                self.add_brick(x + 37.5, 95, 1)
                self.add_brick(x + 37.5, 120, 1)
        elif level == 2:
            # Level 2: Formasi 4 baris bata lebih tebal dengan variasi Emerald Hit 3
            for x in range(5, self.width - 5, 75):
                self.add_brick(x + 37.5, 65, 3)
                self.add_brick(x + 37.5, 88, 2)
                self.add_brick(x + 37.5, 111, 2)
                self.add_brick(x + 37.5, 134, 1)

    def setup_game(self):
        """Menyiapkan posisi bola di atas paddle dan instruksi mulai."""
        self.add_ball()
        self.update_hud()
        if self.text:
            self.canvas.delete(self.text)
        if self.subtext:
            self.canvas.delete(self.subtext)

        self.text = self.draw_text(self.width / 2, 220,
                                   'Press SPACE to Start', size='22', fill='#ffffff')
        self.subtext = self.draw_text(self.width / 2, 255,
                                      'Controls: [A/D] or [<-/->] Move | [P] Pause | [R] Restart',
                                      size='11', fill='#8395a7')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        speed = 10 if self.level == 1 else 12
        self.ball = Ball(self.canvas, x, 355, speed=speed)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='24', fill='#ffffff'):
        font = ('Segoe UI', size, 'bold')
        return self.canvas.create_text(x, y, text=text,
                                       font=font, fill=fill)

    def add_score(self, points):
        self.score += points
        if self.score > self.high_score:
            self.high_score = self.score
        self.update_hud()

    def update_hud(self):
        """Menampilkan status skor, level, dan nyawa dalam simbol hati."""
        score_text = f'SCORE: {self.score}  (HIGH: {self.high_score})'
        level_text = f'LEVEL: {self.level}'
        hearts = '❤️ ' * max(0, self.lives) if self.lives > 0 else '💔 GAME OVER'

        if self.hud_score is None:
            self.hud_score = self.canvas.create_text(
                110, 22, text=score_text,
                font=('Segoe UI', 11, 'bold'), fill='#feca57')
            self.hud_level = self.canvas.create_text(
                self.width / 2, 22, text=level_text,
                font=('Segoe UI', 11, 'bold'), fill='#48dbfb')
            self.hud_lives = self.canvas.create_text(
                self.width - 80, 22, text=hearts,
                font=('Segoe UI', 11, 'bold'), fill='#ff6b6b')
        else:
            self.canvas.itemconfig(self.hud_score, text=score_text)
            self.canvas.itemconfig(self.hud_level, text=level_text)
            self.canvas.itemconfig(self.hud_lives, text=hearts)

    def start_game(self):
        self.canvas.unbind('<space>')
        if self.text:
            self.canvas.delete(self.text)
            self.text = None
        if self.subtext:
            self.canvas.delete(self.subtext)
            self.subtext = None
        self.paddle.ball = None
        self.is_running = True
        self.game_loop()

    def toggle_pause(self):
        """Fitur jeda (pause) dan melanjutkan permainan."""
        if not self.is_running:
            return
        self.paused = not self.paused
        if self.paused:
            self.pause_text = self.draw_text(self.width / 2, 215, 'PAUSED', size='28', fill='#ffd32a')
            self.pause_sub = self.draw_text(self.width / 2, 255, 'Press [P] to Resume', size='13', fill='#ffffff')
        else:
            if self.pause_text:
                self.canvas.delete(self.pause_text)
                self.pause_text = None
            if self.pause_sub:
                self.canvas.delete(self.pause_sub)
                self.pause_sub = None

    def restart_game(self):
        """Reset total permainan kembali ke kondisi awal (Level 1, Skor 0, Nyawa 3)."""
        self.is_running = False
        self.paused = False
        if self.pause_text:
            self.canvas.delete(self.pause_text)
            self.pause_text = None
        if self.pause_sub:
            self.canvas.delete(self.pause_sub)
            self.pause_sub = None

        self.lives = 3
        self.score = 0
        self.level = 1
        self.load_level(1)
        self.setup_game()

    def game_loop(self):
        if not self.is_running:
            return
        if self.paused:
            self.after(100, self.game_loop)
            return

        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:
            self.is_running = False
            self.ball.speed = 0
            if self.level == 1:
                self.add_score(100)  # Bonus tamat Level 1
                self.text = self.draw_text(self.width / 2, 215, 'LEVEL 1 CLEARED!', size='26', fill='#1dd1a1')
                self.subtext = self.draw_text(self.width / 2, 255, 'Get ready for Level 2...', size='13', fill='#c8d6e5')
                self.after(2000, self.start_level_2)
            else:
                self.text = self.draw_text(self.width / 2, 215, 'VICTORY! ALL LEVELS CLEARED!', size='26', fill='#1dd1a1')
                self.subtext = self.draw_text(self.width / 2, 255,
                                              f'Final Score: {self.score} | Press [R] to Play Again',
                                              size='13', fill='#ffd32a')
        elif self.ball.get_position()[3] >= self.height:
            self.is_running = False
            self.lives -= 1
            self.update_hud()
            if self.lives < 0:
                self.text = self.draw_text(self.width / 2, 215, 'GAME OVER', size='32', fill='#ff6b6b')
                self.subtext = self.draw_text(self.width / 2, 255,
                                              f'Score: {self.score} | Press [R] to Restart',
                                              size='13', fill='#c8d6e5')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def start_level_2(self):
        """Memulai Level 2 dengan kecepatan bola lebih lincah dan pola bata baru."""
        if self.text:
            self.canvas.delete(self.text)
            self.text = None
        if self.subtext:
            self.canvas.delete(self.subtext)
            self.subtext = None
        self.level = 2
        self.load_level(2)
        self.setup_game()

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
