# Rem Sergey, 2024
# region Import
import random
import PysigFront as front
import pygame
import copy
import PysigExtensions as ext
import PysigMonoClasses as mono
import PysigOptions as var

c = var.core
c.mono = mono
c.ext = ext
rend = var.render
# endregion
# region Built-in Classes
class Input():
    __cursorPosition = ext.Vector(0, 0)
    __cursorWorldPosition = ext.Vector(0, 0)
    __vertical = 0
    __horizontal = 0
    __keys = None
    # region Properties
    @property
    def cursorPosition(self):
        return self.__cursorPosition
    @cursorPosition.setter
    def cursorPosition(self, value):
        self.__cursorPosition = value
    @property
    def cursorWorldPosition(self):
        return self.__cursorWorldPosition
    @cursorWorldPosition.setter
    def cursorWorldPosition(self, value):
        self.__cursorWorldPosition = value
    @property
    def vertical(self):
        return self.__vertical
    @vertical.setter
    def vertical(self, value):
        self.__vertical = value
    @property
    def horizontal(self):
        return self.__horizontal
    @horizontal.setter
    def horizontal(self, value):
        self.__horizontal = value
    @property
    def keys(self):
        return self.__keys
    @keys.setter
    def keys(self, value):
        self.__keys = value
    # endregion
    def UpdateInput(self, keys):
        pos = pygame.mouse.get_pos()
        self.keys = keys
        self.cursorPosition = ext.Vector(pos[0], pos[1])
        self.cursorWorldPosition = c.mainCamera.transform.position + self.cursorPosition
        self.vertical = 0
        self.horizontal = 0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.horizontal = 1
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.horizontal = -1
        if keys[pygame.K_UP] or keys[pygame.K_w]: self.vertical = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: self.vertical = 1
class Scene():
    __name = 'def'
    __id = 0
    __objects: []
    # region Properties
    @property
    def name(self):
        return self.__name
    @name.setter
    def name(self, value):
        self.__name = value
    @property
    def id(self):
        return self.__id
    @id.setter
    def id(self, value):
        self.__id = value
    @property
    def objects(self) -> list:
        return self.__objects
    @objects.setter
    def objects(self, value):
        self.__objects = value
    # endregion
    def __init__(self, name, id, objects: []):
        self.name = name
        self.id = id
        self.objects = []
        self.objects += objects
    def GetActive(self, recursive=False):
        active = []
        sorted = self.objects # linear
        if recursive:
            sorted = []
            trs = []
            for gm in self.objects:
                if gm.transform.parent == None:
                    trs += gm.transform.GetChilds()
            for i in trs:
                sorted.append(i.gameObject)
        for g in sorted:
            if g.selfActive: active.append(g)
        return active
    def AddLateObject(self, other):
        if not isinstance(other, GameObject) or other is None:
            return
        self.objects.append(other)
        for comp in other.components:
            if comp.enabled:
                comp.Start()
    def AddObject(self, other):
        if not isinstance(other, GameObject) or other is None:
            return
        self.objects.append(other)
    def AddObjects(self, other: list):
        for o in other:
            self.AddObject(o)
    def RemoveObject(self, other):
        if other in self.objects:
            self.objects.remove(other)
class GameObject():
    __name = ""
    __tag = ""
    __active = True
    __selfActive = __active
    __transform = None
    __components = []
    # region Properties
    @property
    def name(self):
        return self.__name
    @name.setter
    def name(self, value):
        self.__name = value
    @property
    def tag(self):
        return self.__tag
    @tag.setter
    def tag(self, value):
        self.__tag = value
    @property
    def active(self):
        return self.__active
    @active.setter
    def active(self, value):
        self.SetActive(value)
    @property
    def selfActive(self):
        return self.__selfActive
    @selfActive.setter
    def selfActive(self, value):
        self.__selfActive = value
    @property
    def transform(self):
        return self.__transform
    @transform.setter
    def transform(self, value):
        self.__transform = value
    @property
    def components(self):
        return self.__components
    @components.setter
    def components(self, value):
        self.__components = value
    # endregion
    # region Methods
    def __init__(self, name: str, tag: str, components: []):
        self.components = []
        self.transform = None
        self.name = name
        self.tag = tag
        tr = mono.Transform()
        self.transform = tr
        self.AddComponent(tr)
        self.AddComponents(components)

    def __init__(self, name: str, tag: str):
        self.components = []
        self.transform = None
        self.name = name
        self.tag = tag
        tr = mono.Transform()
        self.transform = tr
        self.AddComponent(tr)

    def AddComponent(self, component):
        self.components.append(component)
        component.InitMono(self)
        return component
    def AddComponents(self, components):
        for c in components:
            self.AddComponent(c)
        return components
    def SetActive(self, active):
        self.active = active
        if active:
            if self.transform.parent:
                self.selfActive = self.transform.parent.selfActive
            else:
                self.selfActive = True
        else:
            self.selfActive = False
        children = self.transform.GetChilds(True)
        for c in children:
             c.selfActive = c.transform.parent.selfActive
    # endregion
c.GameObject = GameObject
# endregion
# region Game-creating Methods
def rpcollection(rps, carstuck = False):
    gm = GameObject(f'RpCollection #{random.randint(0, 10**6)}', 'def')
    c.scene.AddObject(gm)
    cll = []
    for i in rps:
        cll.append(i)
        i.set_way(cll)
        gm.transform.AddChild(i.gameObject)
        i.transform.SetScale(.66, .66)
        i._RoadPoint__carscanstuck = carstuck
    return (cll, gm.transform.GetChilds())
def rp(id: str, name: str, dist: int, objs: [], pos):
    point = GameObject(name, 'def')
    point.transform.position = pos
    point.AddComponent(mono.SpriteRenderer(ext.Sprite('Graphics/road.png'), ext.Vector.zero(), -1, [0, 0, 0, 177]))
    point.AddComponent(mono.RoadPoint(id, name, dist, objs))
    return point.transform.GetComponent(mono.RoadPoint)
def trl(name, inpos, index, show=True):
    light = GameObject("traffic light ", 'def')
    if show:
        light.AddComponent(mono.SpriteRenderer(ext.Sprite('Graphics/trl.png'), ext.Vector(-10, -10), 5))
        light.AddComponent(mono.Text(ext.Font('Graphics/Fonts/Roboto-Medium.ttf', 10), "", ext.Vector(-13, -22)))
    light.transform.SetScale(.36, .36)
    cm = mono.TrafficLight(name, inpos, index)
    light.AddComponent(cm)
    light.name += cm.get_objid()
    return light.transform.GetComponent(mono.TrafficLight)
def lc(rt, gt, status:bool):
    return mono.LightController(rt, gt, status)
def bs(name, inpos, show=True):
    bus = GameObject("bus stop ", 'def')
    if show:
        bus.AddComponent(mono.SpriteRenderer(ext.Sprite('Graphics/stop.png'), ext.Vector.zero(), -5))
        bus.AddComponent(
        mono.Text(ext.Font('Graphics/Fonts/Roboto-Medium.ttf', 10), "", ext.Vector(-20, -12)))
    bus.transform.SetScale(.66, .66)
    b = mono.BusStop(name, inpos)
    bus.AddComponent(b)
    bus.name += b.get_objid()
    return bus.transform.GetComponent(mono.BusStop)
def carcolloftype(type, cars):
    for i in cars:
        i.set_cartype(type)
    return cars
def car(name, speed):
    c = mono.Car(mono.CarTypes.Passenger, name, speed)
    return c
def psgr(way) -> GameObject:
    _car = random.choice(c.cars[mono.CarTypes.Passenger])
    _car = copy.deepcopy(_car)
    obj = GameObject(_car.get_carname(), 'def')
    obj.AddComponent(mono.SpriteRenderer(ext.Sprite("Graphics/car.png")))
    obj.transform.SetPixelSize(10, 10)
    obj.AddComponent(_car)
    w0 = random.randint(0, len(way)-2)
    w1 = random.randint(w0, len(way)-1)
    obj.AddComponent(mono.Passenger(_car, mono.Car.Driver(), way[w0], way, way[w1]))
    obj.name += ' ' + str(obj.transform.GetComponent(mono.Passenger).get_uniqid())
    return obj
def bus(way, route: str, maxp, _car=None):
    if _car is None:
        _car = copy.deepcopy(c.cars[mono.CarTypes.Bus][random.randint(0, len(c.cars[mono.CarTypes.Bus])-1)])
    obj = GameObject(_car.get_carname(), 'bus')
    gr = "Graphics/car.png"
    for i in list(c.busIconDict.keys()):
        if route in i:
            gr = c.busIconDict[i]
            break
    obj.AddComponent(mono.SpriteRenderer(ext.Sprite(gr)))
    obj.transform.SetPixelSize(10, 10)
    obj.AddComponent(_car)
    w0 = way[0]  # random.randint(0, len(way) - 2)
    w1 = way[-1]  # random.randint(w0, len(way) - 1)
    color = 'White'
    for i in list(c.busColorDict.keys()):
        if route in i:
            color = c.busColorDict[i]
            break
    obj.AddComponent(mono.Text(ext.Font('Graphics/Fonts/Roboto-Medium.ttf', 10), '', ext.Vector(3, 6)))
    obj.AddComponent(mono.Text(ext.Font('Graphics/Fonts/Roboto-Medium.ttf', 10),
                               text=route,
                               offset=ext.Vector(-3, -10),
                               color=color))
    bus = obj.AddComponent(mono.Bus(_car, mono.Car.Driver(), w0, way, w1, route, maxp))
    obj.name += ' ' + str(bus.get_uniqid())
    return obj
def map(name, path, pos, size=ext.Vector(.2, .2), forceblit=False):
    gm = GameObject(name, 'def')
    gm.transform.SetScale(size.x, size.y)
    _rend = mono.SpriteRenderer(ext.Sprite(path), ext.Vector.zero(), -100, [255, 255, 255, 100])
    _rend.forceblit = forceblit
    gm.AddComponent(_rend)
    gm.transform.SetPos(pos.x, pos.y)
    c.maps.append(gm)
    return gm
def addRandBus(rootNumber:str, dir='rand'):
    if dir == 'rand':
        dir = random.randint(0, 1)
    exist = rootNumber in list(c.buswayDict.keys())
    if not exist:
        return
    obj = bus(c.buswayDict[rootNumber][dir], rootNumber, 70)
    scene.AddLateObject(obj)
def addRandCar(dir='rand'):
    if dir == 'rand':
        dir = random.randint(0, 1)
    path = c.fullway[dir]
    obj = psgr(path)
    scene.AddLateObject(obj)
# endregion
# MAIN
# region Core Initialize
pygame.init()
rend.LoadPreferences()
clock = pygame.time.Clock()
c.scene = Scene('def', 0, [])
scene = c.scene
var.render.defaults = [mono.Text, mono.SpriteRenderer]
c.iinput = Input()
# endregion
# region Initialize Cars
c.cars = {mono.CarTypes.Passenger:
         carcolloftype(mono.CarTypes.Passenger,
         [
            car("Honda", 60),
            car("Toyota", 70),
            car("Tesla", 75),
            car("BMW", 75)
         ]),
          mono.CarTypes.Bus:
          carcolloftype(mono.CarTypes.Bus,
                        [
                            car("Scania", 50),
                            car("Huananzhi", 55),
                            car("Birobijan", 60),
                            car("Moscow", 60)
                        ]),
          mono.CarTypes.Trolleybus:
          carcolloftype(mono.CarTypes.Trolleybus,
                        [
                            car("ЗиУ-10", 50)
                        ]),
          mono.CarTypes.Tram:
          carcolloftype(mono.CarTypes.Tram,
                        [
                            car("Tatra T3", 40)
                        ])}
# endregion
# region Caption and Icon
pygame.display.set_caption("Barnaul Streets Simulator")
pygame.display.set_icon(ext.Sprite('Graphics/stop.png').load)
# endregion
# region Camera Initialize
camera = GameObject("Camera", "def")
c.mainCamera = camera.AddComponent(mono.Camera(rend.windowSize, rend.framerate, rend.vsync))
camera.AddComponent(mono.PlayerController())
cam = camera.transform.GetComponent(mono.Camera)
camera.transform.position -= ext.Vector(-30, -30) # откуда этот offset я без понятия
scene.AddObject(camera)
# endregion
# region Light Controllers
c.lightsControllers.append(lc(13.0, 60.0, False))  # 0
c.lightsControllers.append(lc(60.0, 60, True))  # 1
c.lightsControllers.append(lc(60.0, 60.0, False))  # 2
# endregion
# region Map Draw
def MapDraw():
    for i in [1, 7, 13]:
        ypos = [1, 7, 13].index(i)
        for j in range(0, 6):
            vec = ext.Vector(1475 * (j-1)*1, 1475 * (ypos-1)*1)
            extra = 'low/' if rend.lowmaps else ''
            line = str((i+j)-1).zfill(2)
            mapObj = map(line, 'Graphics/map/' + extra + line + '.png', vec, ext.Vector(rend.mapsize, rend.mapsize))
            scene.AddObject(mapObj)
            sr = mapObj.transform.GetComponent(c.mono.SpriteRenderer)
            sr.enabled = rend.renderMaps
    mapEnd = map('end', f'Graphics/map/{"low/" if rend.lowmaps else ""}end.png', ext.Vector(1475 * 5, -1475), ext.Vector(rend.mapsize, rend.mapsize), True)
    mapEnd.transform.GetComponent(c.mono.SpriteRenderer).enabled = rend.renderMaps
    scene.AddObject(mapEnd)
MapDraw()
c.mapDrawFunc = MapDraw
# endregion
# region RoadPoint Collections
at1 = rpcollection([rp('10000', 'start', 240,
                       [trl('light', 240, 0, False), bs('Улица Антона Петрова', 205)],
                       ext.Vector(6416, 1242)),
                   rp('10001', 'other', 640, [], ext.Vector(6707, 1378)),
                   rp('10002', 'end', 1, [], ext.Vector(7521, 1757))
                   ], True)[0]
at0 = rpcollection([
rp('00000', 'start', 640, [], ext.Vector(7524, 1748)),
                   rp('00001', 'other', 230,
                      [trl('light', 1, 0), bs('Улица Антона Петрова', 30)],
                      ext.Vector(6714, 1368)),
    rp('00002', 'end', 82, [],
       ext.Vector(6420, 1229))
], True)[0]
asz0 = rpcollection([
rp('00100', 'start', 475, [bs('Телефонная улица', 35)], ext.Vector(6312, 1176)),
rp('00101', 'alights', 150, [bs('Северо-Западная улица', 149), trl('lineleft', 4, 1), trl('lineright', 35, 1)], ext.Vector(5663, 873)), #
rp('00102', 'end', 200,
   [],
   ext.Vector(5469, 780))
])[0]
asz1 = rpcollection([
rp('10100', 'start', 150,
   [bs('Северо-Западная улица', 2), trl('down', 121, 1)],
   ext.Vector(5431, 794)),
rp('10101', 'alights', 475, [bs('Телефонная улица', 466, False)], ext.Vector(5654, 894)),
rp('10102', 'end', 82, [], ext.Vector(6301, 1199)),
])[0]
amr0 = rpcollection([
    rp('00200', 'start', 1100,
       [bs('Стоматологическая поликлиника № 2', 1040), bs('Дворец культуры', 553),
        bs('Хозяйственный магазин', 202), trl('light', 575, 1)],
       ext.Vector(5212, 663)),
    rp('00201', 'end', 42, [], ext.Vector(3814, 9))
])[0]
amr1 = rpcollection([
    rp('10200', 'start', 1100,
       [bs('Стоматологическая поликлиника № 2', 122), bs('Дворец культуры', 553), bs('Хозяйственный магазин', 903)],
       ext.Vector(3805, 34)),
    rp('10201', 'end', 200, [], ext.Vector(5201, 684))
])[0]
mr0 = rpcollection([
    rp('00300', 'start', 42, [],
       ext.Vector(3780, -25)),
    rp('00301', '1', 46, [],
       ext.Vector(3751, -88)),
    rp('00302', '2', 51, [],
       ext.Vector(3710, -106)),
    rp('00303', '3', 114, [bs('Улица Малахова', 68)],
       ext.Vector(3626, -69)),
    rp('00304', 'end', 1,
        [],
        ext.Vector(3480, -85))
])[0]

aapr0 = rpcollection([
    rp('00400', 'start', 444,
        [trl('trl', 0, 1), bs('Улица Островского', 422)],
        ext.Vector(3480, -85)),
    rp('00401', 'ostrov', 444,
        [],
        ext.Vector(2866, -177)),
    rp('00402', 'end', 1030,
        [trl('trl', 1, 1), bs('Трактовая', 523)],
        ext.Vector(1435, -398)),
])[0]
# endregion
# region Ways Initialize
way0 = at0 + asz0 + amr0 + mr0 + aapr0
way1 = amr1 + asz1 + at1
busway0 = way0[1:]
busway1 = way1[:len(way1)-1]
c.buswayDict = {'53':[busway0, busway1],
                '144':[busway0, busway1]}
c.fullway.append(way0)
c.fullway.append(way1)
# endregion
# region Bus Dicts Initialize
c.busIconDict = {('53'): 'Graphics/longbus.png',
                 ('144'): 'Graphics/minibus.png'}
c.busColorDict = {('53'): 'Green',
                  ('144'): 'Pink'}
# endregion
camera.transform.SetPos(3127, -411)  # debug position
#rend.SavePreferences()
# region Tick Initialize
tickCar = mono.Tick.CreateObject('passenger', 2, [(addRandCar, [])]*2)
tickCarDoubleRandom = mono.Tick.CreateObject('passenger', 2, [(addRandCar, [])]*4)
tickCarDoubleRandom.transform.GetComponent(mono.Tick).SetAsRandom(1, 6)
tick53 = mono.Tick.CreateObject('53 автобус', 60, [(addRandBus, ["53"])])
tick144 = mono.Tick.CreateObject('144 автобус', 60, [(addRandBus, ["144"])])
ticklist = [tick53, tick144, tickCar, tickCarDoubleRandom] #, tickCar, tickCarDoubleRandom
for tick in ticklist:
    tick.transform.GetComponent(mono.Tick).EventsCall()
scene.AddObjects(ticklist)
# endregion
# region Debug Buses
#testway = mr0 + aapr0

#buses144 = [bus(way1, '144', 30) for i in range(0, 3)]

#scene.AddObjects(buses53)
#scene.AddObjects(buses144)
# endregion
# region Console Startup
front.__parsecommand('call startup.txt', True)
# endregion
# region Mono.Start() Initialize
for gm in scene.GetActive(True):
    for comp in gm.components:
        if comp.enabled:
            comp.Start()
# endregion
# region Runtime
scene.objects = list(set(scene.objects))
runtimeActive = True
while runtimeActive:
    # region Init Frame
    pygame.display.update()
    var.core.screen.fill('black')
    keys = pygame.key.get_pressed()
    var.core.iinput.UpdateInput(keys)
    var.core.deltaTime = clock.tick(var.core.mainCamera.targetFramerate) / 1000
    # endregion
    # region Custom Keys
    if c.iinput.keys[pygame.K_e]:
        print(c.iinput.cursorWorldPosition)
        debugstop = True
    if c.iinput.keys[pygame.K_q]:
        front.StartConsoleDialogue()
        var.core.deltaTime = clock.tick(var.core.mainCamera.targetFramerate) / 1000
        c.deltaTime = var.core.mainCamera.targetFramerate / 1000
    # endregion
    # region Console Corex
    if len(c.corex) > 0:
        for line in c.corex:
            exec(line)
            c.corex.remove(line)
    # endregion
    # region EarlyUpdate()
    for gameObject in scene.GetActive(True):
        for comp in gameObject.components:
            if (var.render.defaults.__contains__(type(comp)) == False) and comp.enabled:
                comp.EarlyUpdate()
    # endregion
    # region Update()
    for gameObject in scene.GetActive(True):
        for comp in gameObject.components:
            if (var.render.defaults.__contains__(type(comp)) == False) and comp.enabled:
                comp.Update()
    # endregion
    # region Render Update()
    for rr in var.render.defaults.__reversed__():
        rendList = []
        for gm in scene.GetActive(True):
            for comp in gm.components:
                if (type(comp) == rr)  and comp.enabled: rendList.append(comp)
        rendList.sort(key=lambda r: r.layer, reverse=False)
        for _rend in rendList:
            _rend.Update()
    # endregion
    for i in c.lightsControllers: i.Update()
    # region Quit Event
    for event in pygame.event.get():
        if event.type == pygame.QUIT or c.iinput.keys[pygame.K_ESCAPE]:
            runtimeActive = False
            pygame.quit()
    # endregion
# endregion

