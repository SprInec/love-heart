import pygame
import numpy as np
import random
import imageio

# 粒子类
class Particle:
    def __init__(self, x, y):
        self.pos = np.array([x, y])
        angle = random.uniform(0, 2 * np.pi)
        speed = random.uniform(2, 3)
        self.vel = np.array([np.cos(angle) * speed, np.sin(angle) * speed])
        self.lifespan = 1000
        self.size = random.uniform(5, 12)

    def update(self, window_size):
        center_x = window_size[0] // 2
        center_y = window_size[1] // 2

        # 向中心移动，增加旋转效果
        angle_to_center = np.arctan2(
            center_y - self.pos[1], center_x - self.pos[0])
        rotation_speed = 0.02
        self.vel[0] += np.cos(angle_to_center + rotation_speed) * 0.05
        self.vel[1] += np.sin(angle_to_center + rotation_speed) * 0.05

        # 更新位置
        self.pos += self.vel * 0.95 + np.random.normal(0, 0.2, 2)
        self.lifespan -= 1
        self.size = max(0, self.size * 0.98)

    def is_finished(self):
        return self.lifespan < 0

# 初始化 Pygame
def init_pygame():
    pygame.init()
    screen = pygame.display.set_mode((1000, 800), pygame.RESIZABLE)
    pygame.display.set_caption("Particle Heart Animation")
    return screen


def draw_particles(screen, particles):
    for p in particles:
        if not p.is_finished():
            # 颜色渐变
            r = int(255 * (p.lifespan / 1000))
            g = int(192 * (p.lifespan / 1000))
            b = int(255 * (p.lifespan / 1000))
            color = (r, g, b)

            # 绘制粒子，大小变化
            size_factor = (p.lifespan / 1000) * p.size
            circle_surface = pygame.Surface(
                (int(size_factor), int(size_factor)), pygame.SRCALPHA)
            pygame.draw.circle(circle_surface, color, (int(
                size_factor // 2), int(size_factor // 2)), int(size_factor // 2))
            screen.blit(circle_surface, (int(
                p.pos[0] - size_factor // 2), int(p.pos[1] - size_factor // 2)))

# 绘制由粒子组成的文本
def draw_text_particles(screen, text, font, scale_factor, screen_size):
    text_surface = font.render(text, True, (255, 192, 255))
    text_rect = text_surface.get_rect(
        center=(screen_size[0] // 2, screen_size[1] // 2))
    mask = pygame.mask.from_surface(text_surface)

    particles = []
    spacing = 3  # 设置粒子间隔
    for x in range(0, text_rect.width, spacing):  # 每spacing个像素生成一个粒子
        for y in range(0, text_rect.height, spacing):  # 每spacing个像素生成一个粒子
            if mask.get_at((x, y)):
                # 如果该像素是文本的一部分，生成粒子
                size = random.uniform(3, 8)  # 动态粒子大小
                particle = Particle(text_rect.x + x + random.uniform(-2, 2),
                                    text_rect.y + y + random.uniform(-2, 2))
                particle.size = size  # 设置粒子大小
                particle.lifespan = random.randint(700, 1000)  # 随机设置粒子生命值
                particles.append(particle)

    # 绘制粒子
    for p in particles:
        if not p.is_finished():
            # 颜色渐变
            r = int(255 * (p.lifespan / 1000))
            g = int(192 * (p.lifespan / 1000))
            b = int(255 * (p.lifespan / 1000))
            color = (r, g, b)

            # 绘制粒子，动态调整大小和透明度
            size_factor = (p.lifespan / 1000) * p.size
            alpha = max(0, 255 * (p.lifespan / 1000))  # 根据生命值调整透明度
            circle_surface = pygame.Surface(
                (int(size_factor), int(size_factor)), pygame.SRCALPHA)
            circle_surface.fill((0, 0, 0, 0))  # 清空表面
            pygame.draw.circle(circle_surface, (*color, alpha),
                               (int(size_factor // 2), int(size_factor // 2)), int(size_factor // 2))
            screen.blit(circle_surface, (int(
                p.pos[0] - size_factor // 2), int(p.pos[1] - size_factor // 2)))

    return particles

# 主循环
def main():
    screen = init_pygame()
    clock = pygame.time.Clock()
    particles = []

    scale_factor = 0.8
    scale_direction = 1
    max_scale = 2  # 增加最大缩放比例
    min_scale = 0.5
    scale_step = 0.5  # 增加缩放速度
    font = pygame.font.Font("F:/Resource/Fonts/方正兰亭圆简体.ttf", 62)  # 替换为您的字体路径

    # 用于保存视频的参数
    output_file = "C:/Users/July/Desktop/particle_heart_animation.mp4"
    writer = imageio.get_writer(output_file, fps=30)  # 创建视频写入对象

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(
                    (event.w, event.h), pygame.RESIZABLE)

        # 更新粒子
        t = pygame.time.get_ticks() / 1000
        for _ in range(30):  # 每帧生成30个粒子，增加数量
            x = 16 * np.sin(t) ** 3 * 20 + screen.get_width() // 2
            y = -(13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 *
                  t) - np.cos(4 * t)) * 20 + screen.get_height() // 2
            particles.append(Particle(x, y))

        # 更新粒子位置
        for p in particles[:]:
            p.update(screen.get_size())
            if p.is_finished():
                particles.remove(p)

        # 绘制背景和粒子
        screen.fill((0, 0, 0))  # 黑色背景
        draw_particles(screen, particles)

        # 生成并绘制文本粒子
        text_particles = draw_text_particles(
            screen, "哲love颖", font, scale_factor, screen.get_size())
        draw_particles(screen, text_particles)

        # 计算缩放
        if scale_factor >= max_scale:
            scale_direction = -1
        elif scale_factor <= min_scale:
            scale_direction = 1
        scale_factor += scale_step * scale_direction

        # 捕获当前帧并写入视频
        frame = pygame.surfarray.array3d(pygame.display.get_surface())
        frame = np.rot90(frame)  # 旋转帧以匹配视频格式
        frame = np.flipud(frame)  # 翻转帧以匹配视频格式
        writer.append_data(frame)  # 将帧添加到视频

        pygame.display.flip()
        clock.tick(60)

    writer.close()  # 关闭视频写入器
    pygame.quit()


if __name__ == "__main__":
    main()
