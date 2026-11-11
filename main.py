import tkinter as tk
import random
import threading
import os

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False


def play_sound(sound_type, sound_enabled=True):
    """Memutar efek suara retro arcade secara asynchronous (tidak memblokir GUI)."""
    if not sound_enabled or not HAS_WINSOUND:
        return

    def _beep():
        try:
            if sound_type == 'bounce':
                winsound.Beep(550, 30)
            elif sound_type == 'brick':
                winsound.Beep(850, 35)
            elif sound_type == 'destroy':
                winsound.Beep(1150, 50)
            elif sound_type == 'powerup':
                winsound.Beep(1450, 60)
            elif sound_type == 'lose':
                winsound.Beep(260, 160)
            elif sound_type == 'win':
                winsound.Beep(950, 80)
                winsound.Beep(1300, 100)
        except Exception:
            pass

    threading.Thread(target=_beep, daemon=True).start()


class GameObject(object):
    """Kelas dasar (Base Class) untuk seluruh entitas grafis di dalam Canvas Tkinter."""
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
    """Kelas Ball turunan GameObject: menangani gerak bola, batas canvas, dan pantulan sudut."""
    def __init__(self, canvas, x, y, speed=10):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = speed
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='#feca57', outline='#ff9f43', width=2)
        super(Ball, self).__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        # Pantulan dinding kiri dan kanan
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
            play_sound('bounce')
        # Pantulan dinding atas di bawah garis HUD (y >= 44)
        if coords[1] <= 44:
            self.direction[1] *= -1
            play_sound('bounce')

        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        hit_anything = False

        if len(game_objects) > 1:
            self.direction[1] *= -1
            hit_anything = True
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1
            hit_anything = True

        hit_results = []
        for game_object in game_objects:
            if isinstance(game_object, Brick):
                pts, destroyed, pos = game_object.hit()
                hit_results.append((pts, destroyed, pos))
            elif isinstance(game_object, Paddle):
                play_sound('bounce')

        return hit_anything, hit_results


class Paddle(GameObject):
    """Kelas Paddle turunan GameObject: raket pemain dengan kemampuan power-up pelebaran ukuran."""
    def __init__(self, canvas, x, y):
        self.base_width = 95
        self.width = self.base_width
        self.height = 12
        self.ball = None
        self.expand_timer = 0
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

    def expand(self, duration_frames=200):
        """Power-Up: Memperlebar ukuran paddle untuk mempermudah pemain menangkap bola."""
        self.width = 135
        self.expand_timer = duration_frames
        coords = self.get_position()
        x_center = (coords[0] + coords[2]) * 0.5
        y_center = (coords[1] + coords[3]) * 0.5
        self.canvas.coords(self.item,
                           x_center - self.width / 2, y_center - self.height / 2,
                           x_center + self.width / 2, y_center + self.height / 2)
        self.canvas.itemconfig(self.item, fill='#2ed573', outline='#7bed9f')

    def reset_width(self):
        """Mengembalikan ukuran paddle ke lebar standar saat efek power-up habis."""
        self.width = self.base_width
        self.expand_timer = 0
        coords = self.get_position()
        x_center = (coords[0] + coords[2]) * 0.5
        y_center = (coords[1] + coords[3]) * 0.5
        self.canvas.coords(self.item,
                           x_center - self.width / 2, y_center - self.height / 2,
                           x_center + self.width / 2, y_center + self.height / 2)
        self.canvas.itemconfig(self.item, fill='#00d2d3', outline='#54a0ff')

    def tick(self):
        if self.expand_timer > 0:
            self.expand_timer -= 1
            if self.expand_timer == 0:
                self.reset_width()


class Brick(GameObject):
    """Kelas Brick turunan GameObject: bata target dengan tingkat ketahanan, warna, dan poin skor."""
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
        pos = self.get_position()
        center = ((pos[0] + pos[2]) * 0.5, (pos[1] + pos[3]) * 0.5)

        if self.hits == 0:
            self.delete()
            play_sound('destroy')
            return 25, True, center  # 25 poin bonus hancur total
        else:
            self.canvas.itemconfig(self.item, fill=Brick.COLORS[self.hits])
            play_sound('brick')
            return 10, False, center  # 10 poin pantulan lapisan


class PowerUp(GameObject):
    """Kelas PowerUp turunan GameObject: kapsul item bonus yang jatuh saat bata hancur."""
    TYPES = {
        'LIFE': {'color': '#ff4757', 'label': '+❤️ LIFE', 'outline': '#ff6b81'},
        'EXPAND': {'color': '#2ed573', 'label': '⚡ EXPAND', 'outline': '#7bed9f'},
        'SLOW': {'color': '#1e90ff', 'label': '⏳ SLOW', 'outline': '#70a1ff'}
    }

    def __init__(self, canvas, x, y, kind='EXPAND'):
        self.kind = kind
        self.width = 65
        self.height = 18
        self.speed = 3
        cfg = PowerUp.TYPES[kind]
        item = canvas.create_rectangle(x - self.width / 2, y - self.height / 2,
                                       x + self.width / 2, y + self.height / 2,
                                       fill=cfg['color'], outline=cfg['outline'], width=1.5,
                                       tags='powerup')
        super(PowerUp, self).__init__(canvas, item)
        self.text_item = canvas.create_text(x, y, text=cfg['label'],
                                            font=('Segoe UI', 8, 'bold'), fill='#ffffff')

    def move(self):
        super(PowerUp, self).move(0, self.speed)
        self.canvas.move(self.text_item, 0, self.speed)

    def delete(self):
        self.canvas.delete(self.text_item)
        super(PowerUp, self).delete()


class FloatingText(object):
    """Partikel visual teks skor melayang (+10 / +25) untuk efek animasi dinamis."""
    def __init__(self, canvas, x, y, text, color='#feca57'):
        self.canvas = canvas
        self.item = canvas.create_text(x, y, text=text,
                                       font=('Segoe UI', 10, 'bold'), fill=color)
        self.lifetime = 12

    def update(self):
        self.canvas.move(self.item, 0, -2)
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.canvas.delete(self.item)
            return False
        return True


class Game(tk.Frame):
    """Game Controller utama: mengelola siklus permainan, HUD, level, power-up, dan input pemain."""
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.max_level = 3
        self.is_running = False
        self.paused = False
        self.sound_enabled = True

        self.width = 610
        self.height = 430
        self.canvas = tk.Canvas(self, bg='#1a1a2e',
                                width=self.width,
                                height=self.height,
                                highlightthickness=0)
        self.canvas.pack()
        self.pack()

        # Garis batas visual HUD pemisah arena game
        self.canvas.create_line(0, 44, self.width, 44, fill='#30336b', width=1.5)

        self.items = {}
        self.powerups = []
        self.floating_texts = []
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
        self.hud_sound = None

        self.load_level(self.level)
        self.setup_game()
        self.canvas.focus_set()

        # Kontrol Ganda: Panah Keyboard dan Tombol A / D
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-14))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(14))
        self.canvas.bind('<a>', lambda _: self.paddle.move(-14))
        self.canvas.bind('<d>', lambda _: self.paddle.move(14))
        self.canvas.bind('<A>', lambda _: self.paddle.move(-14))
        self.canvas.bind('<D>', lambda _: self.paddle.move(14))

        # Kontrol Fitur Khusus: Pause [P], Restart [R], Audio Mute [M], Screenshot [F12]
        self.canvas.bind('<p>', lambda _: self.toggle_pause())
        self.canvas.bind('<P>', lambda _: self.toggle_pause())
        self.canvas.bind('<r>', lambda _: self.restart_game())
        self.canvas.bind('<R>', lambda _: self.restart_game())
        self.canvas.bind('<m>', lambda _: self.toggle_sound())
        self.canvas.bind('<M>', lambda _: self.toggle_sound())
        self.canvas.bind('<F12>', lambda _: self.capture_screenshot())

    def toggle_sound(self):
        """Menghidupkan atau mematikan efek suara retro arcade."""
        self.sound_enabled = not self.sound_enabled
        self.update_hud()

    def capture_screenshot(self):
        """Tangkapan layar instan ke folder screenshots/."""
        try:
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
        """Membuat susunan pola bata unik untuk Level 1, Level 2, dan Level 3 (Boss Level)."""
        # Bersihkan sisa bata lama
        for item_id in list(self.items.keys()):
            if isinstance(self.items[item_id], Brick):
                self.items[item_id].delete()
                del self.items[item_id]

        # Bersihkan sisa power-up
        for p in self.powerups:
            p.delete()
        self.powerups.clear()

        if level == 1:
            # Level 1: Formasi 3 Baris Klasik
            for x in range(5, self.width - 5, 75):
                self.add_brick(x + 37.5, 70, 2)
                self.add_brick(x + 37.5, 95, 1)
                self.add_brick(x + 37.5, 120, 1)
        elif level == 2:
            # Level 2: Formasi 4 Baris Rapat dengan Bata Emerald (3 Hits)
            for x in range(5, self.width - 5, 75):
                self.add_brick(x + 37.5, 65, 3)
                self.add_brick(x + 37.5, 88, 2)
                self.add_brick(x + 37.5, 111, 2)
                self.add_brick(x + 37.5, 134, 1)
        elif level == 3:
            # Level 3: Formasi Piramida Bertingkat (Challenge Mode)
            rows = [
                (60, 3, [3]),
                (82, 3, [2, 3, 4]),
                (104, 2, [1, 2, 3, 4, 5]),
                (126, 1, [0, 1, 2, 3, 4, 5, 6, 7]),
            ]
            for y_pos, hits, cols in rows:
                for col in cols:
                    x_center = 5 + col * 75 + 37.5
                    self.add_brick(x_center, y_pos, hits)

    def setup_game(self):
        """Inisialisasi posisi bola dan informasi instruksi awal permainan."""
        self.add_ball()
        self.update_hud()
        if self.text:
            self.canvas.delete(self.text)
        if self.subtext:
            self.canvas.delete(self.subtext)

        self.text = self.draw_text(self.width / 2, 215,
                                   'Press SPACE to Start', size='22', fill='#ffffff')
        self.subtext = self.draw_text(self.width / 2, 252,
                                      'Controls: [A/D] Move | [P] Pause | [R] Restart | [M] Sound',
                                      size='11', fill='#8395a7')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        base_speed = 9 + self.level
        self.ball = Ball(self.canvas, x, 355, speed=base_speed)
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
        """Menampilkan status skor, level, nyawa hati, dan status audio di HUD atas."""
        score_text = f'SCORE: {self.score}  (HIGH: {self.high_score})'
        level_text = f'LVL {self.level}/{self.max_level}'
        hearts = '❤️ ' * max(0, self.lives) if self.lives > 0 else '💔 GAME OVER'
        sound_text = '🔊 ON' if self.sound_enabled else '🔇 OFF'

        if self.hud_score is None:
            self.hud_score = self.canvas.create_text(
                110, 22, text=score_text,
                font=('Segoe UI', 11, 'bold'), fill='#feca57')
            self.hud_level = self.canvas.create_text(
                self.width / 2 - 30, 22, text=level_text,
                font=('Segoe UI', 11, 'bold'), fill='#48dbfb')
            self.hud_sound = self.canvas.create_text(
                self.width / 2 + 50, 22, text=sound_text,
                font=('Segoe UI', 9, 'bold'), fill='#a4b0be')
            self.hud_lives = self.canvas.create_text(
                self.width - 80, 22, text=hearts,
                font=('Segoe UI', 11, 'bold'), fill='#ff6b6b')
        else:
            self.canvas.itemconfig(self.hud_score, text=score_text)
            self.canvas.itemconfig(self.hud_level, text=level_text)
            self.canvas.itemconfig(self.hud_sound, text=sound_text)
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
        """Menjeda permainan sementara waktu (Pause) atau melanjutkan kembali."""
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
        """Mulai ulang total dari Level 1 dengan skor 0 dan 3 nyawa."""
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
        self.paddle.reset_width()
        self.load_level(1)
        self.setup_game()

    def spawn_powerup(self, x, y):
        """Menjatuhkan power-up secara acak (30% peluang saat bata hancur)."""
        if random.random() < 0.35:
            kind = random.choice(['EXPAND', 'LIFE', 'SLOW'])
            p = PowerUp(self.canvas, x, y, kind=kind)
            self.powerups.append(p)

    def update_powerups(self):
        """Menggerakkan item power-up jatuh ke bawah dan mengecek penangkapan oleh paddle."""
        paddle_coords = self.paddle.get_position()
        px0, py0, px1, py1 = paddle_coords

        for p in list(self.powerups):
            p.move()
            pos = p.get_position()
            # Cek jika ditangkap paddle
            if (pos[2] >= px0 and pos[0] <= px1 and pos[3] >= py0 and pos[1] <= py1):
                play_sound('powerup')
                if p.kind == 'EXPAND':
                    self.paddle.expand(250)
                    self.floating_texts.append(FloatingText(self.canvas, (pos[0]+pos[2])/2, py0 - 15, "PADDLE EXPANDED!", '#2ed573'))
                elif p.kind == 'LIFE':
                    self.lives = min(5, self.lives + 1)
                    self.floating_texts.append(FloatingText(self.canvas, (pos[0]+pos[2])/2, py0 - 15, "+1 LIFE!", '#ff4757'))
                    self.update_hud()
                elif p.kind == 'SLOW':
                    if self.ball and self.ball.speed > 7:
                        self.ball.speed = max(7, self.ball.speed - 3)
                    self.floating_texts.append(FloatingText(self.canvas, (pos[0]+pos[2])/2, py0 - 15, "BALL SLOWED!", '#1e90ff'))

                self.add_score(50)
                p.delete()
                self.powerups.remove(p)
            elif pos[1] >= self.height:
                # Terjatuh ke luar layar
                p.delete()
                self.powerups.remove(p)

    def game_loop(self):
        """Loop siklus utama game per frame animasi."""
        if not self.is_running:
            return
        if self.paused:
            self.after(100, self.game_loop)
            return

        self.paddle.tick()
        self.update_powerups()

        # Update teks skor melayang
        self.floating_texts = [ft for ft in self.floating_texts if ft.update()]

        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))

        if num_bricks == 0:
            self.is_running = False
            self.ball.speed = 0
            play_sound('win')

            if self.level < self.max_level:
                self.add_score(150 * self.level)
                self.text = self.draw_text(self.width / 2, 215, f'LEVEL {self.level} CLEARED!', size='26', fill='#1dd1a1')
                self.subtext = self.draw_text(self.width / 2, 255, f'Advancing to Level {self.level + 1}...', size='13', fill='#c8d6e5')
                self.after(2200, self.advance_level)
            else:
                self.add_score(500)
                self.text = self.draw_text(self.width / 2, 215, 'CHAMPION! ALL LEVELS CLEARED!', size='24', fill='#1dd1a1')
                self.subtext = self.draw_text(self.width / 2, 255,
                                              f'Total Score: {self.score} | Press [R] to Play Again',
                                              size='13', fill='#ffd32a')
        elif self.ball.get_position()[3] >= self.height:
            self.is_running = False
            self.lives -= 1
            self.paddle.reset_width()
            play_sound('lose')
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

    def advance_level(self):
        """Melanjutkan ke ronde level berikutnya."""
        if self.text:
            self.canvas.delete(self.text)
            self.text = None
        if self.subtext:
            self.canvas.delete(self.subtext)
            self.subtext = None
        self.level += 1
        self.paddle.reset_width()
        self.load_level(self.level)
        self.setup_game()

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        hit_anything, hit_results = self.ball.collide(objects)

        for points, destroyed, pos in hit_results:
            self.add_score(points)
            # Tampilkan animasi teks skor melayang
            pts_label = f'+{points}'
            color = '#1dd1a1' if destroyed else '#feca57'
            self.floating_texts.append(FloatingText(self.canvas, pos[0], pos[1] - 10, pts_label, color))
            if destroyed:
                self.spawn_powerup(pos[0], pos[1])


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Brick Breaker Arcade - Ilham (20240140118)')
    root.resizable(False, False)
    game = Game(root)
    game.mainloop()
