import pygame
from datetime import time, datetime
from math import pi, cos, sin
import serial
import time

bg = pygame.image.load("revamped-dashboard-background.png")

try:
    # open a serial connection
    s = serial.Serial("COM3", 115200)
except:
    print('no com channel available')


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
PINK = (227, 0, 166)
NAVY = (0, 0, 53)
GRAY = (178, 170, 234)

THE_STRING = "MM" + ':' + "SS" + ':' + "MS"

WIDTH, HEIGHT = 1080, 450
center = (510, HEIGHT / 2)
clock_radius = 200
screen = pygame.display.set_mode((WIDTH, HEIGHT))#, pygame.NOFRAME)


# car states -> change based on  how you chose to read your data
speed_state = 0
rpm_state = 0
current_time = 0
best_lap = "00:00:00"
past_lap = "00:00:00"


def write_text(text, size, position):
    font = pygame.font.SysFont("copperplategothic", size, True, False)
    text = font.render(text, True, WHITE)
    text_rect = text.get_rect(center=position)
    screen.blit(text, text_rect)


def render_time(start, size, position):
    hundredth_of_a_second = int(str(start)[-2:])  # hundredth of a second
    time_in_ms = time((start // 1000) // 3600, ((start // 1000) // 60 % 60), (start // 1000) % 60)
    time_string = "{}{}{:02d}".format(time_in_ms.strftime("%M:%S"), ':', hundredth_of_a_second)
    write_text(time_string, size, position)


# theta is in degrees
def polar_to_cartesian(r, theta, width_center, height_center):
    x = r * sin(pi * theta / 180)
    y = r * cos(pi * theta / 180)
    return x + width_center, -(y - height_center)


# rg_end is non-inclusive
def clock_nums(rg_strt, rg_end, mult, size, r, angle, strt_angle, width_center, height_center):
    for number in range(rg_strt, rg_end, mult):
        write_text(str(number), size,
                   polar_to_cartesian(r, ((number / mult) * angle + strt_angle), width_center, height_center))


def ticks(rg_strt, rg_end, r, angle, strt_angle, width_center, height_center):
    for number in range(rg_strt, rg_end):
        tick_start = polar_to_cartesian(r, (number * angle + strt_angle), width_center, height_center)
        if number % 10 == 0:
            tick_end = polar_to_cartesian(r - 25, (number * angle + strt_angle), width_center, height_center)
            pygame.draw.line(screen, GRAY, tick_start, tick_end, 2)
        elif number % 5 == 0:
            tick_end = polar_to_cartesian(r - 20, (number * angle + strt_angle), width_center, height_center)
            pygame.draw.line(screen, GRAY, tick_start, tick_end, 2)
        else:
            tick_end = polar_to_cartesian(r - 15, (number * angle + strt_angle), width_center, height_center)
            pygame.draw.line(screen, GRAY, tick_start, tick_end, 2)


def pygame_task():
    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption("Dashboard")

    speed = 0
    
    while True:
        # screen.fill(NAVY)

        #INSIDE OF THE GAME LOOP
        screen.blit(bg, (0, 0))

        # SPEEDOMETER
        # gauge label
        write_text("Speedometer", 20, (WIDTH / 4, (HEIGHT / 2) - (clock_radius / 2) - 35))
        # clock numbers
        clock_nums(0, 40, 5, 40, (clock_radius - 65), 38.57143, 223.2, (WIDTH / 4), (HEIGHT / 2) + 65)
        # ticks
        ticks(0, 36, (clock_radius - 15), 7.714286, 223.2, WIDTH / 4, (HEIGHT / 2) + 65)
        # speed = speed_state
        # if speed < 0:
        #     speed = 0
        # if speed > 35:
        #     speed = 35
        # speed = 0
        
        try:
            msg = s.readline()
            if msg == b'0\r\n':
                if speed != 0:
                    speed = speed - 2
            elif msg == b'1\r\n':
                if speed >34:
                    print('woah! slow down there cowboy!')
                else:
                    speed = speed + 2
            # print(speed)
        except:
            print('no com channel available')
        theta = (speed * (270.0 / 35.0)) + (223.2 - (270.0 / 35.0))
        # draw line on gauge indicating current speed
        pygame.draw.line(screen, GRAY, ((WIDTH / 2) / 2, HEIGHT / 2 + 45),
                         polar_to_cartesian(140, theta, WIDTH / 4, (HEIGHT / 2) + 45), 4)
        # print speed below gauge
        str_speed = str(speed)
        pygame.draw.rect(screen, GRAY, [WIDTH / 4.8, HEIGHT - 55, WIDTH / 12, HEIGHT / 9], 3)
        write_text(str_speed, 50, (WIDTH / 4, (HEIGHT - 30)))

        # RPM
        # gauge label
        write_text("RPM GAUGE", 20, ((WIDTH / 4) * 3, (HEIGHT / 2) - (clock_radius / 2) - 35))
        # clock numbers
        clock_nums(0, 5500, 500, 20, (clock_radius - 65), 27, 223.2, (WIDTH / 4) * 3, (HEIGHT / 2) + 65)
        # ticks
        ticks(0, 101, (clock_radius - 15), 2.7, 223.2, (WIDTH / 4) * 3, (HEIGHT / 2) + 65)
        rpm = rpm_state
        if rpm < 0:
            rpm = 0
        if rpm > 5000:
            rpm = 5000
        theta = (rpm * (270.0 / 50.0)) + (223.2 - (270.0 / 50.0))
        # draw line on gauge indicating current RPM
        pygame.draw.line(screen, GRAY, (((WIDTH / 4) * 3), (HEIGHT / 2) + 45),
                         polar_to_cartesian(140, theta, (WIDTH / 4) * 3, (HEIGHT / 2) + 45), 4)
        # print RPM below gauge
        str_rpm = str(rpm)
        pygame.draw.rect(screen, GRAY, [(WIDTH / 2) + (WIDTH / 4.8), HEIGHT - 55, WIDTH / 12, HEIGHT / 9], 3)
        write_text(str_rpm, 50, ((WIDTH / 4) * 3, (HEIGHT - 30)))
        now = datetime.now()
        formatted = now.strftime("%H:%M:%S")
        write_text(formatted, 15, ((WIDTH - (WIDTH/2)),10))
        write_text('16% Battery', 15, ((WIDTH-70),10))

        # title
        # write_text('Digi Drive', 15, ((WIDTH - (WIDTH/2)),10))
        # # TIMER
        # # best lap
        # write_text("Best Lap", 25, (((WIDTH / 3.5) / 2) + 20, 12))
        # pygame.draw.rect(screen, PINK, [0 + 20, HEIGHT / 40 + 15, WIDTH / 3.5, HEIGHT / 8], 3)
        # write_text(best_lap, 50, (((WIDTH / 3.5) / 2) + 20, HEIGHT / 8.5))
        # # current lap
        # write_text("Current Lap", 25, (((WIDTH / 3.5) / 2) + (WIDTH / 3 + 20), 12))
        # pygame.draw.rect(screen, PINK, [WIDTH / 3 + 20, HEIGHT / 40 + 15, WIDTH / 3.5, HEIGHT / 8], 3)
        # start = pygame.time.get_ticks() - current_time
        # render_time(start, 50, (WIDTH / 2, HEIGHT / 8.5))
        # # previous lap
        # write_text("Past Lap", 25, (((WIDTH / 3.5) / 2) + ((WIDTH / 3) * 2 + 20), 12))
        # pygame.draw.rect(screen, PINK, [((WIDTH / 3) * 2) + 20, HEIGHT / 40 + 15, WIDTH / 3.5, HEIGHT / 8], 3)
        # write_text(past_lap, 50, (((WIDTH / 3.5) / 2) + ((WIDTH / 3) * 2 + 20), HEIGHT / 8.5))

        pygame.display.flip()
        clock.tick(60)


pygame_task()
