import json
import pygame
import os

imported_textures = {}

def init_textures(tileSize):
    for root_folder in ["map_elm", "characters", "UI", "projectiles"]:
        for folder in os.listdir(r"./graphics/" + root_folder):
            imported_textures[folder] = {}
            for file in os.listdir(rf"./graphics/{root_folder}/{folder}"):
                if ("." in file):
                    if (not file.endswith(".json")):
                        imported_textures[folder][file.split(".")[0]] = get_adjusted_image(fr"./graphics/{root_folder}/{folder}/{file}", tileSize)
                    else:
                        with open(rf"./graphics/{root_folder}/{folder}/{file}") as f:
                            imported_textures[folder]["options"] = json.load(f)
                else:
                    animTextures = []
                    for animTexture in sorted(os.listdir(fr"./graphics/{root_folder}/{folder}/{file}")):
                        animTextures.append(get_adjusted_image(fr"./graphics/{root_folder}/{folder}/{file}/{animTexture}", tileSize))
                    imported_textures[folder][file] = animTextures
            
            if not "options" in imported_textures[folder]:
                imported_textures[folder]["options"] = {}

    print(imported_textures)

def get_adjusted_image(path, width, height=None):
    image = pygame.image.load(path)

    if height == None:
        imageRect = image.get_rect()
        imageWidth, imageHeight = imageRect.width, imageRect.height
        height = width * imageHeight / imageWidth

    return pygame.transform.scale(image, (width, height))


def get_imported_texture(name: str, state: str = None):
    if name in imported_textures.keys() and (not state or (state and state in imported_textures[name])):
        if (state and state in imported_textures[name]):
            return imported_textures[name][state]
        elif (not state):
            return imported_textures[name]

    else:
        if (state):
            return imported_textures["default"]["idle"]
        else:
            return imported_textures["default"]

class Texture:
    def __init__(self, texturedElement, textureName, state, loop=True, endAnimFunc=None, endAnimArgs=None, animationInterval=5):
        self.texturedElement = texturedElement

        self.texture = get_imported_texture(textureName, state)
        self.isAnimated = type(self.texture) is list

        if (not self.isAnimated):
            self.flippedTexture = pygame.transform.flip(self.texture, True, False)
        else:
            self.flippedTexture = [
                pygame.transform.flip(img, True, False) for img in self.texture
            ]

        self.currentIndex = 0
        self.animationInterval = animationInterval
        self.currentTick = 0
        self.isFinished = False

        self.loop = loop
        self.endAnimFunc = endAnimFunc
        self.endAnimArgs = endAnimArgs
    
    def get_texture(self, flipped=True):
        if (not self.isAnimated):
            if (not flipped):
                return self.texture
            else:
                return self.flippedTexture
        else:
            self.currentTick += 1
            if (self.currentTick >= self.animationInterval):
                self.currentTick = 0

                if (self.loop or self.currentIndex+1 < len(self.texture)):
                    self.currentIndex += 1

                if (not self.isFinished and self.currentIndex >= len(self.texture)-1):
                    if (self.loop and self.currentIndex >= len(self.texture)):
                        self.currentIndex = 0
                    
                    elif (self.endAnimFunc):
                        if (type(self.endAnimFunc) is str):
                            getattr(self.texturedElement, self.endAnimFunc)(*self.endAnimArgs)
                        else:
                            self.endAnimFunc(*self.endAnimArgs)
                        self.isFinished = True
            
            if (not flipped):
                return self.texture[self.currentIndex]
            else:
                return self.flippedTexture[self.currentIndex]

class UIElement:
    def __init__(self, background, xpos, ypos, name, state, overLayerState=None, isPanel=True, noPanelWidth=None, noPanelHeight=None):
        self.isPanel = isPanel
        
        if (isPanel):
            self.animPanel = AnimationPanel(self, name, state)
            self.overLayer = AnimationPanel(self, name, overLayerState)
        else:
            self.surface = pygame.transform.scale(get_imported_texture(name, state), (noPanelWidth, noPanelHeight))
            self.width = noPanelWidth
            self.height = noPanelHeight
        
        self.stickedElement = None

        self.background = background
        self.xpos = xpos
        self.ypos = ypos
    
    def cropOverLayer(self, height):
        self.overLayer.set_size(None, height)
    
    def stickToElement(self, element):
        self.stickedElement = element
    
    def reload(self):
        if (self.isPanel):
            self.background.window.blit(self.animPanel.get_texture(), (self.xpos, self.ypos))
            self.background.window.blit(self.overLayer.get_texture(), (self.xpos, self.ypos))
        else:
            x, y = self.xpos, self.ypos
            if (self.stickedElement):
                x, y = self.stickedElement.xpos - self.width//2, self.stickedElement.ypos - self.height//2
            
            self.background.window.blit(self.surface, (x, y))

class AnimationPanel:
    def __init__(self, texturedElement, objName: str, state="idle"):
        self.texturedElement = texturedElement
        self.name = objName

        imported = get_imported_texture(objName)
        self.textures = {}
        self.rowTextures = {}
        
        for key in imported.keys():
            if (key != "options"):
                options = ()
                if key in imported["options"].keys():
                    options = imported["options"][key]

                self.textures[key] = Texture(texturedElement, objName, key, *options)
                self.rowTextures[key] = Texture(texturedElement, objName, key, *options)

        self.currentAnim = state
    
    def get_texture(self, *args):
        return self.textures[self.currentAnim].get_texture(args)
    
    def launch_animation(self, animation):
        if (animation in self.textures.keys()):
            self.currentAnim = animation
        else:
            print(f"Animation {animation} doesn't exist. here are the existing animations : {list(self.textures.keys())}")
    
    def get_animation(self):
        return self.currentAnim

    def set_rotation(self, rotation):
        for key in self.textures.keys():
            if type(self.textures[key].texture) is list:
                for elm in self.textures[key].texture:
                    elm = pygame.transform.rotate(elm, rotation*90)
            else:
                self.textures[key].texture = pygame.transform.rotate(self.textures[key].texture, rotation*90)
    
    def set_size(self, width, height):
        for key in self.textures.keys():
            if type(self.textures[key].texture) is list:
                for elm in self.textures[key].texture:
                    elm = pygame.transform.scale(self.rowTextures[key].texture, (width, height))
            else:
                if width == None:
                    width = self.textures[key].texture.get_width()
                if height == None:
                    height = self.textures[key].texture.get_height()

                self.textures[key].texture = pygame.transform.scale(self.rowTextures[key].texture, (width, height))

    def flip(self, x=True, y=False):
        for key in self.textures.keys():
            if type(self.textures[key].texture) is list:
                for elm in self.textures[key].texture:
                    elm = pygame.transform.flip(elm, x, y)
            else:
                self.textures[key].texture = pygame.transform.flip(self.textures[key].texture, x, y)