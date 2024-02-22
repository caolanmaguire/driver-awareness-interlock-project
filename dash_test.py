import pygame


pygame.init()


display_width = 800
display_height = 600

gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('DigiDrive | Car Dashboard')

black = (0,0,0)
white = (255,255,255)

clock = pygame.time.Clock()
crashed = False

closedEyeImg = pygame.image.load('icons/eye_closed.png')
DEFAULT_IMAGE_SIZE = (150,150)
closedEyeImg = pygame.transform.scale(closedEyeImg, DEFAULT_IMAGE_SIZE)

carImg = pygame.image.load('icons/attention_alert.png')
DEFAULT_IMAGE_SIZE = (150,150)
carImg = pygame.transform.scale(carImg, DEFAULT_IMAGE_SIZE)

def write_text(text, size, position):
    font = pygame.font.SysFont("Arial", size, True, False)
    text = font.render(text, True, white)
    text_rect = text.get_rect(center=position)
    gameDisplay.blit(text, text_rect)

def car(x,y):
    gameDisplay.blit(carImg, (x,y))
    gameDisplay.blit(closedEyeImg, (150,y))

x =  (0)
y = (display_height - DEFAULT_IMAGE_SIZE[1])

while not crashed:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True

    gameDisplay.fill(black)
    car(x,y)
    write_text("Speedometer", 30, (display_width / 4, (display_height / 2) - (100 / 2) - 35))
    write_text("RPM", 30, (display_width / 2, (display_height / 2) - (100 / 2) - 35))
    write_text("Message", 40, (80, 20))
        
    pygame.display.update()
    clock.tick(60)

pygame.quit()
quit()