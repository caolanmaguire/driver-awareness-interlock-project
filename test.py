import time
import pygame

pygame = pygame.init()

scenes = {'Main': MainScene(),
          'Battle': BattleScene()} #etc

scene = scenes['Main']

class MainScene():
  ...
  def handle_event(self, event):
    if event.type == KEYUP:
      if event.key == K_a:
        scene = scenes['Battle']
  ...

class BattleScene():
  ...
  def draw(self):
    # draw your animation

  def update(self):
    # if animation is over:
    scene = scenes['Main']

...

def main_game():
  ending=False
  while not ending:
    #   clock.tick(30)
      for event in pygame.event.get():
        scene.handle_event(event)
        scene.update()
        scene.draw()