from enum import Enum
from copy import deepcopy
import json
class flag_names(Enum):
    # region Log
    log_end_reach_message = 'log_end_reach_message'
    # endregion
    # region Console
    comma_break = 'comma_break'
    comma_auto_revert_break = 'comma_auto_revert_break'
    # endregion
class Flags:
    # region Flags
    __ff = flag_names
    __flags: dict[str:bool]
    __flags = {
        __ff.log_end_reach_message: False,
        __ff.comma_break: False,
        __ff.comma_auto_revert_break: True,

    }
    # endregion
    # region Methods
    def get(self, name) -> bool:
        if name in list(self.__flags.keys()):
            return self.__flags[name]
        else:
            raise NameError
    def set(self, name, value:bool):
        if name in list(self.__flags.keys()):
            self.__flags[name] = value
        else:
            raise NameError
    def switch(self, name):
        if name in list(self.__flags.keys()):
            self.__flags[name] = not self.__flags[name]
        else:
            raise NameError
    def get_copy(self):
        return deepcopy(self.__flags)
    # endregion
class Args:
    # region Arguments
    __args = {
        "version": 1,
    }
    # endregion
    # region Methods
    def get(self, key:str) -> object:
        if key in self.__args:
            if f'${key}' == self.__args[key]:
                print('args key and value is the same (recursion problem)')
                return f'@r${key}'
            return self.__args[key]
        else:
            print(f'{key} is not in dict!')
    def set(self, key:str, value, create=False):
        if key in self.__args or create:
            self.__args[key] = value
        else:
            print(f'{key} is not in dict!')
    def delete(self, key:str):
        if key in self.__args:
            del self.__args[key]
        else:
            print(f'{key} is not in dict!')
    def get_copy(self) -> dict:
        return deepcopy(self.__args)
    # endregion
class Render():
    windowSize = (600, 600)
    framerate = 60
    vsync = 1
    renderMaps = True
    lowmaps = False
    mapsize = 1.0
    defaults = []
    def __iter__(self):
        yield 'windowSize', self.windowSize
        yield 'framerate', self.framerate
        yield 'vsync', self.vsync
        yield 'renderMaps', self.renderMaps
        yield 'lowmaps', self.lowmaps
        yield 'mapsize', self.mapsize

    def SavePreferences(self):
        with open("preferences.json", "w") as pref:
            json.dump(dict(self), pref, indent=4)
        end = 'Preferences saved successfully!'
        print(end)
    def LoadPreferences(self):
        with open("preferences.json", "r") as pref:
            a = json.load(pref)
            for key, value in a.items():
                setattr(self, key, value)
        end = 'Preferences loaded successfully!'
        print(end)
    def ResetVisuals(self):
        camera = core.mainCamera
        camera.__init__(self.windowSize, self.framerate, self.vsync)
        camera.Start()
        for map in core.maps:
            core.scene.RemoveObject(map)
            del map
        core.mapDrawFunc()
        end = 'Preferences restarted successfully!'
        print(end)

class Core():
    __dev = True
    __version = 'beta 0.9.9a'
    @property
    def version(self):
        return self.__version
    @property
    def dev(self):
        return self.__dev
    mono = None
    GameObject = None
    ext = None
    scene = None
    screen = None
    iinput = None
    deltaTime = 0
    mainCamera = None
    lightsControllers = []
    maps = []
    mapDrawFunc = None
    buswayDict = {}  # номер маршрута: [путь0, путь1]
    busIconDict = {}  # (номера маршрутов): путь к спрайту
    busColorDict = {}  # (номера маршрутов): цвет
    fullway = []
    corex = []
render = Render()
core = Core()
flags = Flags()
args = Args()
args.set('version', core.version)
