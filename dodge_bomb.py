import os
import random
import sys
import pygame as pg
import time
import math


WIDTH, HEIGHT = 1100, 650
DELTA = {  # 移動量辞書
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))
blackout = pg.Surface((WIDTH, HEIGHT))

def write_gameover(screen: pg.Surface) -> None:#ゲームオーバー画面
    blackout = pg.Surface((WIDTH, HEIGHT))    
    blackout.set_alpha(150)
    pg.draw.rect(blackout, (0, 0, 0), (0, 0, WIDTH, HEIGHT))    
    screen.blit(blackout, (0, 0))
    go_img = pg.image.load("fig/8.png")
    go_img = pg.transform.rotozoom(go_img, 0, 0.9)
    go_rct_left = go_img.get_rect()
    go_rct_right = go_img.get_rect()
    go_rct_left.midright = (WIDTH // 2 - 200, HEIGHT // 2)
    go_rct_right.midleft = (WIDTH // 2 + 200, HEIGHT // 2)
    screen.blit(go_img, go_rct_left)
    screen.blit(go_img, go_rct_right)
    font = pg.font.SysFont(None, 100)
    text = font.render("Game Over", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)
    pg.display.update()
    time.sleep(5)

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    bb_imgs = []
    bb_accs = [a for a in range(1, 11)]
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)
    return bb_imgs, bb_accs

def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRectまたは爆弾Rect
    戻り値：横方向，縦方向の画面内外判定結果
    画面内ならTrue，画面外ならFalse
    """
    yoko, tate = True, True  # 初期値：画面内
    if rct.left < 0 or WIDTH < rct.right:  # 横方向の画面外判定
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom: # 縦方向の画面外判定
        tate = False
    return yoko, tate  # 横方向，縦方向の画面内判定結果を返す



def get_kk_img(sum_mv: tuple[int, int], base_img: pg.Surface) -> pg.Surface:
    direction_map = {
        (0, -5): 90,
        (5, -5): 45,
        (5, 0): 0,
        (5, 5): 315,
        (0, 5): 270,
        (-5, 5): 225,
        (-5, 0): 180,
        (-5, -5): 135,
    }
    dx, dy = sum_mv
    if (dx, dy) == (0, 0):
        return base_img
    dx = max(-5, min(5, dx))
    dy = max(-5, min(5, dy))
    key = (int(dx / abs(dx)) * 5 if dx != 0 else 0,
           int(dy / abs(dy)) * 5 if dy != 0 else 0)
    angle = direction_map.get(key, 0)  # 該当しない場合は右（0度）
    return pg.transform.rotate(base_img, angle)


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    kk_img_base = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_img = kk_img_base.copy()
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_imgs, sbb_accs = init_bb_imgs()
    bb_rct = bb_imgs[0].get_rect()
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    bb_img = pg.Surface((20, 20))  # 空のSurfaceを作る（爆弾用）
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)  # 赤い円を描く
    bb_img.set_colorkey((0, 0, 0))  # 黒を透明色に設定
    bb_rct = bb_img.get_rect()  # 爆弾Rectを取得
    bb_rct.centerx = random.randint(0, WIDTH)  # 横座標用の乱数
    bb_rct.centery = random.randint(0, HEIGHT)  # 縦座標用の乱数
    vx, vy = +5, +5  # 爆弾の移動速度
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        if kk_rct.colliderect(bb_rct) and tmr > 150:
            write_gameover(screen)            
            return
        screen.blit(bg_img, [0, 0]) 
        screen.blit(kk_img, kk_rct)
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        kk_img = get_kk_img(tuple(sum_mv), kk_img_base)
        kk_rct = kk_img.get_rect(center=kk_rct.center)  # 回転後の画像でRect更新
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        # if key_lst[pg.K_UP]:
        #     sum_mv[1] -= 5
        # if key_lst[pg.K_DOWN]:
        #     sum_mv[1] += 5
        # if key_lst[pg.K_LEFT]:
        #     sum_mv[0] -= 5
        # if key_lst[pg.K_RIGHT]:
        #     sum_mv[0] += 5
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])  # 移動をなかったことにする
        idx = min(tmr // 500, 9)
        bb_img = bb_imgs[idx]
        avx = vx * sbb_accs[idx]
        avy = vy * sbb_accs[idx]
        screen.blit(bb_img, bb_rct)
        bb_rct = bb_img.get_rect(center=bb_rct.center)
        bb_rct.move_ip(avx, avy)  # 爆弾の移動
        yoko,tate=check_bound(bb_rct)
        if not yoko:#横方向にはみ出ていたら
            vx *= -1
        if not tate:
            vy *= -1
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()