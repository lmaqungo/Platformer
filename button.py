
"""
Module Name: button.py

Purpose: This simple module includes a class to create buttons for pygame projects
"""

import pygame

class Button():
    """
    Represents a button object
    
    Attributes:
        image (pygame.Surface): The image of the button
        rect (pygame.Rect): Rectangle for the image, used for positioning
        clicked (bool): click status of the button
        
    """
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        
    def draw(self, surface):
        action = False
        
        # get mouse pos
        pos = pygame.mouse.get_pos()
        
        # check mouse collide and clicked
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
        
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        
        surface.blit(self.image, (self.rect.x, self.rect.y))
        
        return action
    
pygame.quit()
