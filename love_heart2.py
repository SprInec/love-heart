import pygame
import numpy as np
import random
import imageio  # 导入imageio库
import os

# 获取桌面路径
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
video_path = os.path.join(desktop_path, "fireworks.mp4")  # 修改为视频文件名

# 粒子类
class Particle:
    def __init__(self, x, y, color, tail=False, is_text_particle=False):
        self.pos = np.array([x, y], dtype=np.float32)
        self.vel = np.array(
            [random.uniform(-0.5, 0.5), random.uniform(-2, -1)], dtype=np.float32)  # 随机水平漂移

        # 根据不同类型的粒子调整速度和生命周期
        if tail:
            self.vel *= random.uniform(0.1, 0.75)  # 尾迹粒子速度较慢
            self.lifespan = random.randint(300, 500)  # 尾迹粒子的生命值增加
            self.size = random.uniform(1, 2)  # 尾迹粒子更细小
        elif is_text_particle:  # 判断是否为文字粒子
            self.lifespan = 100  # 文字粒子的生命值较长
            self.size = random.uniform(2, 5)  # 文字粒子大小
        else:
            self.lifespan = random.randint(60, 100)  # 普通粒子的生命值
            self.size = random.uniform(2, 7)  # 修改为较小的粒子大小

        self.color = color

    def update(self):
        self.pos += self.vel
        self.lifespan -= 1

    def is_finished(self):
        return self.lifespan < 0


# 初始化 Pygame
def init_pygame():
    pygame.init()
    screen = pygame.display.set_mode((608, 800), pygame.RESIZABLE)
    pygame.display.set_caption("Fireworks Animation")
    return screen


# 绘制背景
def create_gradient_background(screen, background_color1, background_color2):
    gradient_surface = pygame.Surface(screen.get_size())
    for y in range(screen.get_height()):
        ratio = y / screen.get_height()
        r = int(background_color1[0] * (1 - ratio) +
                background_color2[0] * ratio)
        g = int(background_color1[1] * (1 - ratio) +
                background_color2[1] * ratio)
        b = int(background_color1[2] * (1 - ratio) +
                background_color2[2] * ratio)
        pygame.draw.line(gradient_surface, (r, g, b),
                         (0, y), (screen.get_width(), y))
    return gradient_surface


def draw_particles(screen, particles):
    for p in particles:
        if not p.is_finished():
            # 计算颜色和透明度
            alpha = max(0, 255 * (p.lifespan / 100))  # 根据生命周期调整透明度
            color_with_alpha = (*p.color, alpha)  # 添加透明度
            size_factor = (p.lifespan / 100) * p.size  # 根据生命周期调整大小
            circle_surface = pygame.Surface(
                (int(size_factor), int(size_factor)), pygame.SRCALPHA)
            circle_surface.fill((0, 0, 0, 0))  # 清空表面
            pygame.draw.circle(circle_surface, color_with_alpha, (int(
                size_factor // 2), int(size_factor // 2)), int(size_factor // 2))
            screen.blit(circle_surface, (int(
                p.pos[0] - size_factor // 2), int(p.pos[1] - size_factor // 2)))


# 绘制爱心轮廓的粒子
heart_r = 0


def draw_heart_outline(x, y, count):
    global heart_r
    particles = []
    r = random.uniform(1, 12)  # 半径范围
    heart_r = r
    for _ in range(count):
        angle = random.uniform(0, 2 * np.pi)  # 随机角度

        # 使用爱心公式计算x和y坐标
        particle_x = x + 16 * np.sin(angle)**3 * r
        particle_y = y - (13 * np.cos(angle) - 5 * np.cos(2 * angle) -
                          2 * np.cos(3 * angle) - np.cos(4 * angle)) * r

        # 生成粒子，随机大小
        color = (255, 192, 255)
        p = Particle(particle_x, particle_y, color)
        p.size = random.uniform(1, 8)  # 随机大小范围，可以调整
        particles.append(p)
    return particles


# 计算爱心尖端的位置
def heart_tip_position(x, y):
    return x, y - 10  # 尖端位置可以根据需要调整


# 绘制粒子组成的文字
def draw_text_particles(x, y, text, font_size=60, spacing=3):
    particles = []
    font = pygame.font.Font("./fonts/方正兰亭圆简体.ttf", font_size)
    text_surface = font.render(text, True, (255, 192, 255))
    text_rect = text_surface.get_rect(center=(x, y))

    for i in range(text_rect.width):
        for j in range(text_rect.height):
            if text_surface.get_at((i, j))[3] > 0 and (i % spacing == 0 and j % spacing == 0):
                particle_x = x - text_rect.width // 2 + i
                particle_y = y - text_rect.height // 2 + j
                # 创建文字粒子，传入 is_text_particle=True
                particles.append(
                    Particle(particle_x, particle_y, (255, 192, 255), is_text_particle=True))
    return particles


# 主循环
def main():
    screen = init_pygame()
    clock = pygame.time.Clock()
    particles = []
    fireworks = []

    # 创建渐变背景颜色
    background_color1 = (0, 0, 0)  # 黑色
    background_color2 = (20, 20, 50)  # 深蓝色
    gradient_surface = create_gradient_background(
        screen, background_color1, background_color2)

    # 用于保存视频帧
    frames = []
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(
                    (event.w, event.h), pygame.RESIZABLE)
                # 重新创建渐变背景
                gradient_surface = create_gradient_background(
                    screen, background_color1, background_color2)

        # 每帧生成一束烟花
        if random.random() < 0.01:  # 每100帧左右生成一次烟花
            x = random.randint(100, screen.get_width() - 100)  # 在屏幕内随机生成烟花位置
            tip_x, tip_y = heart_tip_position(
                x, screen.get_height() - 30)  # 获取爱心尖位置
            fireworks.append([tip_x, tip_y])  # 将firework变为列表

        # 更新粒子
        for firework in fireworks[:]:
            # 升起的粒子和尾迹
            p = Particle(firework[0], firework[1], (255, 192, 255))  # 粉色
            particles.append(p)

            firework[1] -= random.uniform(1.2, 2.0)  # 修改上升速度，使其更自然

            if firework[1] < screen.get_height() // 2:  # 到达中心高度
                # 清空内部粒子，添加文字粒子
                particles.extend(draw_heart_outline(
                    firework[0], firework[1], random.randint(100, 500)))  # 轮廓粒子的数量
                if heart_r >= 9:
                    particles.extend(draw_text_particles(
                        firework[0], firework[1], "love"))  # 添加文字粒子

                fireworks.remove(firework)  # 移除当前烟花

        # 更新粒子位置
        for p in particles[:]:
            p.update()
            if p.is_finished():  # 如果粒子生命周期结束，移除粒子
                particles.remove(p)

        # 绘制背景和粒子
        screen.blit(gradient_surface, (0, 0))  # 渐变背景
        draw_particles(screen, particles)

        # 保存当前帧到帧列表
        frames.append(pygame.surfarray.array3d(pygame.display.get_surface()))

        pygame.display.flip()
        clock.tick(60)

    # 创建视频
    imageio.mimsave(video_path, frames, fps=30)  # 修改为视频的保存方式和帧率

    pygame.quit()


if __name__ == "__main__":
    main()
