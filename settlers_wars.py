"""
=============================================================
  SETTLER WARS — Dark Lord Edition
=============================================================
  CONTROLS (You = Dark Lord):
    Arrow Keys  → Move
    F           → Gather resource / Build
    G           → Attack (power boosted by Stone)

  RESOURCES:
    🪵 Wood  (Brown Circle) → Structures: Wall, House
    🪨 Stone (Gray Square)  → Weapons:    Tower, Attack Power

  BUILDINGS:
    Wall   → 2 Wood            (blocks Shadow Beasts)
    House  → 4 Wood            (increases max HP)
    Tower  → 3 Stone           (auto-shoots enemies)

  COMBAT:
    Base attack = 12 dmg
    +2 dmg per Stone collected (max +20 bonus)

  WIN:  Destroy both Shadow Beasts!
  LOSE: Your HP reaches 0.
=============================================================
"""

import pygame, math, random, sys, struct, wave, io
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

W, H    = 900, 620
UI_H    = 70
ARENA_H = H - UI_H
screen  = pygame.display.set_mode((W, H))
pygame.display.set_caption("Settler Wars — Dark Lord Edition")
clock   = pygame.time.Clock()
FPS     = 60

# ── Colours ───────────────────────────────────────────────────────────────────
BG        = (30, 55, 30)
UI_BG     = (15, 10, 30)
UI_BORDER = (100, 60, 180)
WHITE     = (255,255,255)
BLACK     = (0,  0,  0)
GRAY      = (140,140,140)
DARK_GRAY = (50, 50, 50)
RED       = (200, 40, 40)
GREEN_HP  = (50, 200, 80)
YELLOW    = (240,200, 40)
PURPLE    = (140, 0, 200)
ORANGE    = (200, 90, 20)
RES_WOOD  = (120, 75, 30)
RES_STONE = (130,130,145)
P_COLORS  = [(130, 0, 200), (180, 55, 20), (160, 80, 10)]

# ── Fonts ─────────────────────────────────────────────────────────────────────
f_sm = pygame.font.SysFont("segoeui", 14)
f_md = pygame.font.SysFont("segoeui", 17, bold=True)
f_lg = pygame.font.SysFont("segoeui", 28, bold=True)
f_xl = pygame.font.SysFont("segoeui", 52, bold=True)

def txt(surf, text, x, y, color=WHITE, font=f_sm, center=False):
    s = font.render(str(text), True, color)
    r = s.get_rect()
    if center: r.center = (x, y)
    else:      r.topleft = (x, y)
    surf.blit(s, r)

# ── Procedural Dark Music ─────────────────────────────────────────────────────
SAMPLE_RATE = 44100

def make_tone(freq, duration, vol=0.18, wave_type='sine', detune=0.0):
    n   = int(SAMPLE_RATE * duration)
    buf = []
    for i in range(n):
        t   = i / SAMPLE_RATE
        env = min(1.0, min(i, n-i) / (SAMPLE_RATE * 0.04))
        f1  = freq * (1 + detune)
        if wave_type == 'sine':
            v = math.sin(2*math.pi*f1*t)
        elif wave_type == 'square':
            v = 1.0 if math.sin(2*math.pi*f1*t) >= 0 else -1.0
        elif wave_type == 'sawtooth':
            v = 2*(t*f1 - math.floor(t*f1 + 0.5))
        else:
            v = math.sin(2*math.pi*f1*t)
        buf.append(int(v * env * vol * 32767))
    return buf

def make_silence(duration):
    return [0] * int(SAMPLE_RATE * duration)

def buf_to_sound(buf):
    raw = struct.pack(f"<{len(buf)}h", *buf)
    snd = pygame.sndarray.make_sound(
        pygame.sndarray.make_surface if False else
        __import__('numpy').frombuffer(raw, dtype='<i2') if False else
        pygame.sndarray.make_sound(
            __import__('array').array('h', buf)
        ) and None or pygame.sndarray.make_sound(
            __import__('array').array('h', buf)
        )
    )
    return snd

def build_music():
    """Build a looping dark eerie dungeon track from sine/square tones."""
    # Eerie minor-key drone notes (Hz) — D minor feel
    melody = [
        (146.83, 0.6, 'sine',    0.0),   # D2
        (146.83, 0.4, 'sine',    0.0),
        (130.81, 0.6, 'sine',   -0.002), # C2
        (123.47, 0.8, 'square',  0.001), # B1
        (110.00, 1.0, 'sine',    0.0),   # A1 (ominous hold)
        (116.54, 0.6, 'sawtooth',0.002), # Bb1
        (110.00, 0.4, 'sine',    0.0),
        (98.00,  1.2, 'sine',   -0.001), # G1 (dark resolve)
        (0,      0.3, 'sine',    0.0),   # silence
        (146.83, 0.5, 'square',  0.001),
        (155.56, 0.5, 'sine',    0.0),   # Eb2
        (146.83, 0.5, 'sine',    0.0),
        (130.81, 0.5, 'sawtooth',0.001),
        (110.00, 1.5, 'sine',    0.0),
        (0,      0.5, 'sine',    0.0),
    ]
    full = []
    for freq, dur, wt, det in melody:
        if freq == 0:
            full += make_silence(dur)
        else:
            full += make_tone(freq, dur, vol=0.14, wave_type=wt, detune=det)
    import array as arr
    snd = pygame.sndarray.make_sound(arr.array('h', full))
    return snd

def make_hit_sound():
    buf = make_tone(80, 0.12, vol=0.35, wave_type='square')
    import array as arr
    return pygame.sndarray.make_sound(arr.array('h', buf))

def make_gather_sound():
    buf = make_tone(520, 0.08, vol=0.25, wave_type='sine')
    import array as arr
    return pygame.sndarray.make_sound(arr.array('h', buf))

def make_build_sound():
    buf  = make_tone(260, 0.06, vol=0.2, wave_type='sine')
    buf += make_tone(390, 0.08, vol=0.2, wave_type='sine')
    import array as arr
    return pygame.sndarray.make_sound(arr.array('h', buf))

# Load sounds
try:
    music_snd   = build_music()
    hit_snd     = make_hit_sound()
    gather_snd  = make_gather_sound()
    build_snd   = make_build_sound()
    music_snd.play(loops=-1)
    SOUND_OK = True
except Exception:
    SOUND_OK = False

# ── Resource Node ─────────────────────────────────────────────────────────────
class ResourceNode:
    def __init__(self, x, y, kind):
        self.x, self.y = x, y
        self.kind  = kind
        self.alive = True
        self.rtimer= 0

    def update(self):
        if not self.alive:
            self.rtimer -= 1
            if self.rtimer <= 0:
                self.alive = True

    def draw(self, surf):
        if not self.alive: return
        if self.kind == 'wood':
            pygame.draw.circle(surf, (60,30,10),  (self.x+2, self.y+2), 12)
            pygame.draw.circle(surf, RES_WOOD,    (self.x,   self.y),   12)
            pygame.draw.circle(surf, (170,110,55),(self.x,   self.y),   12, 2)
            txt(surf, "W", self.x, self.y, WHITE, f_sm, center=True)
        else:
            pygame.draw.rect(surf, (50,50,60),   (self.x-13,self.y-13,26,26))
            pygame.draw.rect(surf, RES_STONE,    (self.x-12,self.y-12,24,24))
            pygame.draw.rect(surf, (190,190,205),(self.x-12,self.y-12,24,24), 2)
            txt(surf, "S", self.x, self.y, WHITE, f_sm, center=True)

    def try_gather(self, px, py):
        if self.alive and math.hypot(px-self.x, py-self.y) < 30:
            self.alive  = False
            self.rtimer = 500
            return self.kind
        return None

# ── Building ──────────────────────────────────────────────────────────────────
BUILD_DEFS = {
    'wall':  dict(cost={'wood':2,'stone':0}, hp=80,  color=(160,120,60), size=28,
                  desc="2 Wood — blocks beasts"),
    'house': dict(cost={'wood':4,'stone':0}, hp=120, color=(190,150,80), size=34,
                  desc="4 Wood — +20 max HP"),
    'tower': dict(cost={'wood':0,'stone':3}, hp=150, color=(90,50,160),  size=30,
                  desc="3 Stone — auto-attacks", atk=10, rng=150, cd=55),
}
BUILD_ORDER = ['wall','house','tower']

class Building:
    def __init__(self, x, y, btype, owner):
        self.x, self.y = x, y
        self.type  = btype
        self.owner = owner
        d = BUILD_DEFS[btype]
        self.hp     = d['hp']
        self.max_hp = d['hp']
        self.size   = d['size']
        self.atk_cd = 0

    def update(self, players):
        if self.type != 'tower': return
        if self.atk_cd > 0: self.atk_cd -= 1; return
        d = BUILD_DEFS['tower']
        for p in players:
            if p.dead or p.index == self.owner: continue
            if math.hypot(p.x-self.x, p.y-self.y) < d['rng']:
                p.take_damage(d['atk'])
                self.atk_cd = d['cd']
                break

    def take_damage(self, dmg): self.hp -= dmg

    def draw(self, surf, owner_color):
        d = BUILD_DEFS[self.type]
        s = self.size
        r = pygame.Rect(self.x-s//2, self.y-s//2, s, s)
        pygame.draw.rect(surf, DARK_GRAY, r.move(3,3), border_radius=4)
        pygame.draw.rect(surf, d['color'], r, border_radius=4)
        pygame.draw.rect(surf, owner_color, r, 3, border_radius=4)
        txt(surf, self.type[0].upper(), self.x, self.y, WHITE, f_md, center=True)
        bw = s+6
        bx, by = self.x-bw//2, self.y-s//2-9
        pygame.draw.rect(surf, RED,      (bx, by, bw, 5))
        pygame.draw.rect(surf, GREEN_HP, (bx, by, int(bw*self.hp/self.max_hp), 5))

# ── Entity base ───────────────────────────────────────────────────────────────
SPEED     = 3
ATK_RANGE = 48
BASE_DMG  = 12
ATK_CD    = 40
SPAWNS    = [(100, UI_H+80), (W-100, UI_H+80), (W//2, H-80)]

class Entity:
    def __init__(self, index):
        self.index  = index
        self.color  = P_COLORS[index]
        self.x, self.y = float(SPAWNS[index][0]), float(SPAWNS[index][1])
        self.hp     = 100
        self.max_hp = 100
        self.dead   = False
        self.resources = {'wood':0,'stone':0}
        self.buildings = []
        self.atk_cd = 0
        self.flash  = 0
        self.build_sel = 0

    @property
    def atk_dmg(self):
        """Stone boosts attack power: +2 per stone held, capped at +20."""
        return BASE_DMG + min(self.resources['stone'] * 2, 20)

    def take_damage(self, dmg):
        self.hp   -= dmg
        self.flash = 12
        if SOUND_OK:
            try: hit_snd.play()
            except: pass
        if self.hp <= 0:
            self.hp, self.dead = 0, True

    def _do_attack(self, players, buildings_all):
        if self.atk_cd > 0: return
        for p in players:
            if p.index == self.index or p.dead: continue
            if math.hypot(p.x-self.x, p.y-self.y) < ATK_RANGE:
                p.take_damage(self.atk_dmg)
                self.atk_cd = ATK_CD; return
        for b in buildings_all:
            if b.owner == self.index: continue
            if math.hypot(b.x-self.x, b.y-self.y) < ATK_RANGE+10:
                b.take_damage(self.atk_dmg)
                self.atk_cd = ATK_CD; return

    def _try_build(self, buildings_all):
        bt   = BUILD_ORDER[self.build_sel]
        cost = BUILD_DEFS[bt]['cost']
        if self.resources['wood'] < cost['wood'] or self.resources['stone'] < cost['stone']:
            for _ in range(len(BUILD_ORDER)):
                self.build_sel = (self.build_sel+1) % len(BUILD_ORDER)
                bt   = BUILD_ORDER[self.build_sel]
                cost = BUILD_DEFS[bt]['cost']
                if self.resources['wood'] >= cost['wood'] and self.resources['stone'] >= cost['stone']:
                    break
            else:
                return None
        self.resources['wood']  -= cost['wood']
        self.resources['stone'] -= cost['stone']
        b = Building(int(self.x)+random.randint(-20,20),
                     int(self.y)+random.randint(-20,20), bt, self.index)
        self.buildings.append(b)
        buildings_all.append(b)
        if bt == 'house':
            self.max_hp += 20
            self.hp = min(self.hp+20, self.max_hp)
        if SOUND_OK:
            try: build_snd.play()
            except: pass
        return bt

    def draw(self, surf, label):
        if self.dead: return
        px, py = int(self.x), int(self.y)
        flash  = self.flash % 4 < 2

        if self.index == 0:
            # Dark Lord
            cloak = (60,0,90) if not flash else WHITE
            glow  = (150,0,220)
            pts = [(px,py-22),(px+14,py+10),(px+6,py+16),(px-6,py+16),(px-14,py+10)]
            pygame.draw.polygon(surf, (30,0,50), [(x+3,y+3) for x,y in pts])
            pygame.draw.polygon(surf, cloak, pts)
            pygame.draw.circle(surf, (30,0,50),(px+2, py-14), 11)
            pygame.draw.circle(surf, cloak,    (px,   py-14), 11)
            pygame.draw.circle(surf, glow,  (px-4, py-15), 3)
            pygame.draw.circle(surf, glow,  (px+4, py-15), 3)
            pygame.draw.circle(surf, WHITE, (px-4, py-15), 1)
            pygame.draw.circle(surf, WHITE, (px+4, py-15), 1)
            # stone power aura — grows with stone count
            if self.resources['stone'] > 0:
                aura_r = 18 + min(self.resources['stone'], 10)
                pygame.draw.circle(surf, (100,0,160), (px,py), aura_r, 2)
            if self.atk_cd > 0:
                pygame.draw.circle(surf, glow, (px,py), 24, 2)
        else:
            # Shadow Beast
            bc = (180,60,20) if not flash else WHITE
            pygame.draw.circle(surf, (40,10,0), (px+3,py+3), 15)
            pygame.draw.circle(surf, bc,         (px,  py),   15)
            for angle in range(0,360,45):
                rad = math.radians(angle)
                sx  = px + int(math.cos(rad)*18)
                sy  = py + int(math.sin(rad)*18)
                pygame.draw.circle(surf, bc, (sx,sy), 4)
            pygame.draw.circle(surf, YELLOW, (px-5,py-4), 4)
            pygame.draw.circle(surf, YELLOW, (px+5,py-4), 4)
            pygame.draw.circle(surf, BLACK,  (px-5,py-4), 2)
            pygame.draw.circle(surf, BLACK,  (px+5,py-4), 2)
            if self.atk_cd > 0:
                pygame.draw.circle(surf, (255,100,0),(px,py),20,2)

        # HP bar + label
        bw = 38
        bx, by = px-bw//2, py-26
        pygame.draw.rect(surf, RED,      (bx,by,bw,5))
        pygame.draw.rect(surf, GREEN_HP, (bx,by,int(bw*self.hp/self.max_hp),5))
        txt(surf, label, px, by-13, self.color, f_sm, center=True)

# ── Human Player ──────────────────────────────────────────────────────────────
class Player(Entity):
    def handle_keys(self, keys, buildings_all):
        if self.dead: return
        dx = dy = 0
        if keys[pygame.K_LEFT]:  dx -= SPEED
        if keys[pygame.K_RIGHT]: dx += SPEED
        if keys[pygame.K_UP]:    dy -= SPEED
        if keys[pygame.K_DOWN]:  dy += SPEED
        nx = max(14, min(W-14, self.x+dx))
        ny = max(UI_H+14, min(H-14, self.y+dy))
        blocked = any(b.type=='wall' and b.owner!=self.index and
                      abs(nx-b.x)<b.size//2+12 and abs(ny-b.y)<b.size//2+12
                      for b in buildings_all)
        if not blocked: self.x, self.y = nx, ny
        if self.atk_cd > 0: self.atk_cd -= 1
        if self.flash  > 0: self.flash  -= 1

    def do_action(self, resources, players, buildings_all):
        if self.dead: return None
        for res in resources:
            k = res.try_gather(self.x, self.y)
            if k:
                self.resources[k] += 1
                if SOUND_OK:
                    try: gather_snd.play()
                    except: pass
                purpose = "→ boosts attack!" if k=='stone' else "→ use to build!"
                return f"+1 {k.upper()}  {purpose}"
        bt = self._try_build(buildings_all)
        return f"Constructed: {bt.upper()}!" if bt else "Need more resources!"

    def do_attack(self, players, buildings_all):
        if not self.dead: self._do_attack(players, buildings_all)

# ── AI Enemy ──────────────────────────────────────────────────────────────────
class AIEnemy(Entity):
    def __init__(self, index):
        super().__init__(index)
        self.resources = {'wood':4,'stone':3}
        self.state     = 'gather'
        self.state_timer = 0

    def update(self, resources, players, buildings_all):
        if self.dead: return
        if self.atk_cd > 0: self.atk_cd -= 1
        if self.flash  > 0: self.flash  -= 1
        self.state_timer += 1
        if self.state_timer % 90 == 0:
            human = next((p for p in players if p.index==0 and not p.dead), None)
            if human and math.hypot(human.x-self.x, human.y-self.y) < 170:
                self.state = 'chase'
            elif self.resources['wood'] >= 3 or self.resources['stone'] >= 3:
                self.state = random.choice(['build','gather'])
            else:
                self.state = 'gather'
        if self.state == 'gather': self._ai_gather(resources)
        elif self.state == 'chase': self._ai_chase(players, buildings_all)
        elif self.state == 'build':
            self._try_build(buildings_all)
            self.state = 'gather'
        self.x = max(14, min(W-14, self.x))
        self.y = max(UI_H+14, min(H-14, self.y))

    def _ai_gather(self, resources):
        alive = [r for r in resources if r.alive]
        if not alive: return
        t = min(alive, key=lambda r: math.hypot(r.x-self.x, r.y-self.y))
        self._move_toward(t.x, t.y, SPEED-1)
        k = t.try_gather(self.x, self.y)
        if k: self.resources[k] += 1

    def _ai_chase(self, players, buildings_all):
        human = next((p for p in players if p.index==0 and not p.dead), None)
        if not human: return
        self._move_toward(human.x, human.y, SPEED-1)
        self._do_attack(players, buildings_all)

    def _move_toward(self, tx, ty, spd):
        d = math.hypot(tx-self.x, ty-self.y)
        if d > 1:
            self.x += (tx-self.x)/d*spd
            self.y += (ty-self.y)/d*spd

# ── Notification ──────────────────────────────────────────────────────────────
class Notif:
    def __init__(self, msg, color=WHITE, life=100):
        self.msg, self.color, self.life = msg, color, life
    def draw(self, surf, y):
        s = f_sm.render(self.msg, True, self.color)
        s.set_alpha(min(255, self.life*4))
        surf.blit(s, s.get_rect(center=(W//2, y)))

# ── Resource scatter ──────────────────────────────────────────────────────────
def make_resources():
    nodes = []
    for _ in range(20):
        nodes.append(ResourceNode(random.randint(50,W-50), random.randint(UI_H+50,H-50),'wood'))
    for _ in range(14):
        nodes.append(ResourceNode(random.randint(50,W-50), random.randint(UI_H+50,H-50),'stone'))
    return nodes

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN LOOP
# ══════════════════════════════════════════════════════════════════════════════
def main():
    player    = Player(0)
    ai1       = AIEnemy(1)
    ai2       = AIEnemy(2)
    all_units = [player, ai1, ai2]
    resources = make_resources()
    buildings_all = []
    notifs    = []
    result    = None

    def add_notif(msg, color=WHITE, life=120):
        notifs.insert(0, Notif(msg, color, life))
        if len(notifs) > 5: notifs.pop()

    add_notif("⚔  SETTLER WARS — Destroy both Shadow Beasts to claim glory!", YELLOW, 300)
    add_notif("🏃 MOVE: Arrow Keys   |   ⛏ GATHER/BUILD: F   |   ⚔ ATTACK: G", WHITE, 300)
    add_notif("🪵 Wood → builds Walls & Houses  |  🪨 Stone → powers Towers & Attack!", (150,220,255), 300)

    while True:
        keys = pygame.key.get_pressed()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if result and ev.key == pygame.K_r:
                    main(); return
                if not result:
                    if ev.key == pygame.K_f:
                        msg = player.do_action(resources, all_units, buildings_all)
                        if msg: add_notif(f"⚡ {msg}", P_COLORS[0])
                    if ev.key == pygame.K_g:
                        player.do_attack(all_units, buildings_all)

        # Gather on held F
        if not result and keys[pygame.K_f] and pygame.time.get_ticks() % 20 < 2:
            for res in resources:
                k = res.try_gather(player.x, player.y)
                if k:
                    player.resources[k] += 1
                    purpose = "→ boosts attack!" if k=='stone' else "→ use to build!"
                    add_notif(f"+1 {k.upper()}  {purpose}", P_COLORS[0])
                    if SOUND_OK:
                        try: gather_snd.play()
                        except: pass
                    break

        if not result:
            player.handle_keys(keys, buildings_all)
            ai1.update(resources, all_units, buildings_all)
            ai2.update(resources, all_units, buildings_all)
            for res in resources: res.update()
            for b in list(buildings_all):
                b.update(all_units)
                if b.hp <= 0:
                    buildings_all.remove(b)
                    for u in all_units:
                        if b in u.buildings: u.buildings.remove(b)
            for n in notifs: n.life -= 1
            notifs[:] = [n for n in notifs if n.life > 0]
            if player.dead:   result = 'lose'
            elif ai1.dead and ai2.dead: result = 'win'

        # ── Draw ──────────────────────────────────────────────────────────────
        arena = pygame.Surface((W, ARENA_H))
        arena.fill(BG)
        for gx in range(0,W,40):
            pygame.draw.line(arena,(40,80,40),(gx,0),(gx,ARENA_H))
        for gy in range(0,ARENA_H,40):
            pygame.draw.line(arena,(40,80,40),(0,gy),(W,gy))

        for res in resources:      res.draw(arena)
        for b in buildings_all:    b.draw(arena, P_COLORS[b.owner])
        player.draw(arena, "DARK LORD")
        if not ai1.dead: ai1.draw(arena, "BEAST I")
        if not ai2.dead: ai2.draw(arena, "BEAST II")

        screen.fill(BLACK)
        screen.blit(arena, (0, UI_H))

        # ── UI Panel ──────────────────────────────────────────────────────────
        pygame.draw.rect(screen, UI_BG, (0,0,W,UI_H))
        pygame.draw.line(screen, UI_BORDER,(0,UI_H),(W,UI_H),2)

        # Player stats
        pygame.draw.line(screen, UI_BORDER,(W//3,4),(W//3,UI_H-4),1)
        st = "FALLEN" if player.dead else f"HP {player.hp}/{player.max_hp}"
        sc = RED if player.dead else P_COLORS[0]
        txt(screen, "⚔ DARK LORD", W//6, 8,  sc,    f_md, center=True)
        txt(screen, st,             W//6, 28, sc,    f_sm, center=True)
        txt(screen, f"🪵 Wood: {player.resources['wood']}   🪨 Stone: {player.resources['stone']}",
            W//6, 44, WHITE, f_sm, center=True)
        dmg_bonus = min(player.resources['stone']*2, 20)
        txt(screen, f"ATK: {BASE_DMG}+{dmg_bonus}  |  Next: {BUILD_ORDER[player.build_sel]}",
            W//6, 58, YELLOW, f_sm, center=True)

        # AI stats
        for i, ai in enumerate([ai1, ai2]):
            cx = W//3 + (i+1)*W//4 - 20
            if i==0: pygame.draw.line(screen,UI_BORDER,(W//3+W//4-40,4),(W//3+W//4-40,UI_H-4),1)
            label  = f"BEAST {['I','II'][i]}"
            status = "SLAIN" if ai.dead else f"HP {ai.hp}/{ai.max_hp}"
            c = DARK_GRAY if ai.dead else P_COLORS[ai.index]
            txt(screen, f"👹 {label}", cx, 14, c, f_md, center=True)
            txt(screen, status,         cx, 36, c, f_sm, center=True)
            if not ai.dead:
                txt(screen, f"State: {ai.state}", cx, 54, GRAY, f_sm, center=True)

        # Notifications
        for i,n in enumerate(notifs):
            n.draw(screen, UI_H+18+i*22)

        # How-to-play panel
        hw_lines = [
            ("HOW TO PLAY",                    YELLOW),
            ("Arrow Keys → Move",              WHITE),
            ("F → Gather Wood (W) or Stone (S)",WHITE),
            ("F → Build near base",            WHITE),
            ("G → Attack enemies",             WHITE),
            ("🪵 Wood: Wall(2W)  House(4W)",   RES_WOOD),
            ("🪨 Stone: Tower(3S) +ATK power", RES_STONE),
            ("Slay both beasts to WIN!",        GREEN_HP),
        ]
        hw_w, hw_h = 238, len(hw_lines)*17+12
        hw_x, hw_y = 8, H-hw_h-8
        hs = pygame.Surface((hw_w, hw_h), pygame.SRCALPHA)
        hs.fill((10,5,25,200))
        screen.blit(hs,(hw_x,hw_y))
        pygame.draw.rect(screen,UI_BORDER,(hw_x,hw_y,hw_w,hw_h),1,border_radius=5)
        for i,(line,col) in enumerate(hw_lines):
            txt(screen, line, hw_x+8, hw_y+6+i*17, col, f_md if i==0 else f_sm)

        # Result overlay
        if result:
            ov = pygame.Surface((W,H), pygame.SRCALPHA)
            ov.fill((0,0,0,170))
            screen.blit(ov,(0,0))
            if result == 'win':
                txt(screen,"GLORY IS YOURS!",              W//2,H//2-50,YELLOW,f_xl,center=True)
                txt(screen,"The enemies bow before your might.",W//2,H//2+10,WHITE,f_md,center=True)
            else:
                txt(screen,"THE KINGDOM FALLS!",           W//2,H//2-50,RED,   f_xl,center=True)
                txt(screen,"Your lands are conquered. Rise again.",W//2,H//2+10,GRAY,f_md,center=True)
            txt(screen,"R = Rise Again   |   ESC = Retreat",W//2,H//2+50,GRAY,f_md,center=True)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()