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
                        # TODO : Find a better way to do this... (in Options ?)
                        if root_folder != "UI":
                            imported_textures[folder][file.split(".")[0]] = get_adjusted_image(fr"./graphics/{root_folder}/{folder}/{file}", tileSize)
                        else:
                            imported_textures[folder][file.split(".")[0]] = pygame.image.load(fr"./graphics/{root_folder}/{folder}/{file}")
                    else:
                        with open(rf"./graphics/{root_folder}/{folder}/{file}") as f:
                            imported_textures[folder]["options"] = json.load(f)

                else:
                    animTextures = []
                    for animTexture in sorted(os.listdir(fr"./graphics/{root_folder}/{folder}/{file}")):
                        if root_folder != "UI":
                            animTextures.append(get_adjusted_image(fr"./graphics/{root_folder}/{folder}/{file}/{animTexture}", tileSize))
                        else:
                            animTextures.append(pygame.image.load(fr"./graphics/{root_folder}/{folder}/{file}/{animTexture}"))

                    imported_textures[folder][file] = animTextures
            
            if not "options" in imported_textures[folder]:
                imported_textures[folder]["options"] = {}

def get_adjusted_image(path, width, height=None):
    image = pygame.image.load(path)

    if height == None or width == None:
        imageRect = image.get_rect()
        imageWidth, imageHeight = imageRect.width, imageRect.height
        
        if height == None:
            height = width * imageHeight / imageWidth
        elif width == None:
            width = height * imageWidth / imageHeight

    return pygame.transform.scale(image, (width, height))


def get_imported_texture(name: str, state: str = None):
    if name in imported_textures.keys():
        if (state):
            if (state in imported_textures[name]):
                return imported_textures[name][state]
            else:
                return None
        elif (not state):
            return imported_textures[name]

    else:
        if (state):
            return imported_textures["default"]["idle"]
        else:
            return imported_textures["default"]

class Texture:
    def __init__(self, texturedElement, textureName, state, loop=True, endAnimFunc=None, endAnimArgs=None, animationInterval=5, autoLaunchAnimation=None, relaunchable=True):
        self.texturedElement = texturedElement

        self.texture = get_imported_texture(textureName, state)
        if not self.texture:
            self.texture = get_imported_texture(textureName, "idle")
            state = "idle"

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
        self.autoLaunchAnimation = autoLaunchAnimation
        self.relaunchable = relaunchable

        self.loop = loop
        self.endAnimFunc = endAnimFunc
        self.endAnimArgs = endAnimArgs
    
    def get_loop_time(self):
        if not self.isAnimated:
            return self.animationInterval
        else:
            return self.animationInterval * len(self.texture)
    
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

                if (not self.isFinished):
                    self.currentIndex += 1
                    
                    if self.currentIndex >= len(self.texture):
                        if self.loop:
                            self.currentIndex = 0
                        
                        else:
                            self.isFinished = True
                            self.currentIndex = len(self.texture) - 1
                        
                        if (self.endAnimFunc):
                            if (type(self.endAnimFunc) is str):
                                getattr(self.texturedElement, self.endAnimFunc)(*self.endAnimArgs)
                            else:
                                self.endAnimFunc(*self.endAnimArgs)
            
            if (not flipped):
                return self.texture[self.currentIndex]
            else:
                return self.flippedTexture[self.currentIndex]

class UIElement:
    def __init__(self, background, xpos, ypos, name, state, overLayerState=None, width=None, height=None):
        self.surface = AnimationPanel(self, name, state)
        self.surface.set_size(width, height)
        
        self.width = width
        self.height = height

        self.overLayer = None
        if overLayerState:
            self.overLayer = AnimationPanel(self, name, overLayerState)
            self.overLayer.set_size(width, height)
        
        self.stickedElement = None

        self.background = background
        self.xpos = xpos
        self.ypos = ypos
    
    def cropOverLayer(self, height):
        self.overLayer.set_size(None, height)
    
    def stickToElement(self, element):
        self.stickedElement = element
    
    def reload(self):
        x, y = self.xpos, self.ypos
        if (self.stickedElement):
            x, y = self.stickedElement.xpos - self.width//2, self.stickedElement.ypos - self.height//2
        
        self.background.window.blit(self.surface.get_texture(), (x, y))

        if self.overLayer:
            self.background.window.blit(self.overLayer.get_texture(), (x, y))

class AnimationPanel:
    def __init__(self, texturedElement, objName: str, state="idle"):
        self.texturedElement = texturedElement
        self.name = objName

        imported = get_imported_texture(objName)

        self.textures: dict[str, Texture] = {}
        self.rowTextures = {}
        
        for key in imported.keys():
            if (key != "options"):
                options = ()
                if key in imported["options"].keys():
                    options = imported["options"][key]

                self.textures[key] = Texture(texturedElement, objName, key, *options)
                self.rowTextures[key] = Texture(texturedElement, objName, key, *options)

        self.currentAnim = state
    
    def get_loop_time(self, state):
        if self.does_state_exist(state):
            return self.textures[state].get_loop_time()
        else:
            return 0
    
    def does_state_exist(self, state):
        return state in self.textures.keys()
    
    def get_texture(self, *args):
        if not self.currentAnim in self.textures.keys():
            self.currentAnim = "idle"

        if self.textures[self.currentAnim].autoLaunchAnimation and self.textures[self.currentAnim].isFinished and not self.textures[self.currentAnim].loop:
            self.launch_animation(self.textures[self.currentAnim].autoLaunchAnimation)

        return self.textures[self.currentAnim].get_texture(args)
    
    def launch_animation(self, animation):
        if (animation in self.textures.keys() and self.textures[self.currentAnim].relaunchable):
            self.currentAnim = animation

            if self.textures[self.currentAnim].relaunchable:
                self.textures[self.currentAnim].isFinished = False
                self.textures[self.currentAnim].currentIndex = 0
        else:
            pass
            # print(f"Animation {animation} doesn't exist. here are the existing animations : {list(self.textures.keys())}")
    
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

    def set_opacity(self, alpha=255):
        for key in self.textures.keys():
            if type(self.textures[key].texture) is list:
                for elm in self.textures[key].texture:
                    elm.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
            else:
                self.textures[key].texture.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)