# IT WAS ALL CREATED BY REM
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
class Input():
    cursorPosition = ext.Vector(0, 0)
    cursorWorldPosition = ext.Vector(0, 0)
    vertical = 0
    horizontal = 0
    keys = None
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
    name = 'def'
    id = 0
    objects = []
    def __init__(self, objects: []):
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
    def AddObject(self, other):
        self.objects.append(other)
    def AddObjects(self, other: []):
        for o in other:
            self.AddObject(o)
class GameObject():
    name = ""
    tag = ""
    active = True
    selfActive = active
    transform = None
    components = []

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
    def AddComponents(self, components = []):
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
            childs = self.transform.GetChilds(True)
        for c in childs:
             c.selfActive = c.transform.parent.selfActive
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
    point = GameObject("name", 'def')
    point.transform.position = pos
    point.AddComponent(mono.SpriteRenderer(ext.Sprite('Graphics/road.png'), ext.Vector.Zero(), -1, [0, 0, 0, 177]))
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
        bus.AddComponent(mono.SpriteRenderer(ext.Sprite('Graphics/stop.png'), ext.Vector.Zero(), -5))
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
def psgr(way, _car=None) -> GameObject:
    if _car is None:
        _car = copy.deepcopy(c.cars[mono.CarTypes.Passenger][random.randint(0, len(c.cars[mono.CarTypes.Bus])-1)])
    obj = GameObject(_car.get_carname(), 'def')
    obj.AddComponent(mono.SpriteRenderer(ext.Sprite("Graphics/car.png")))
    obj.transform.SetPixelSize(10, 10)
    obj.AddComponent(_car)
    w0 = random.randint(0, len(way)-2)
    w1 = random.randint(w0, len(way)-1)
    obj.AddComponent(mono.Passenger(_car, mono.Car.Driver(), way[w0], way, way[w1]))
    obj.name += ' ' + str(obj.transform.GetComponent(mono.Passenger).__uniqId)
    return obj
def bus(way, route: str, maxp, _car=None):
    if _car is None:
        _car = copy.deepcopy(c.cars[mono.CarTypes.Bus][random.randint(0, len(c.cars[mono.CarTypes.Bus])-1)])
    obj = GameObject(_car.get_carname(), 'def')
    obj.AddComponent(mono.SpriteRenderer(ext.Sprite("Graphics/car.png")))
    obj.transform.SetPixelSize(10, 10)
    obj.AddComponent(_car)
    w0 = way[0] #random.randint(0, len(way) - 2)
    w1 = way[-1] #random.randint(w0, len(way)-1)
    obj.AddComponent(mono.Text(ext.Font('Graphics/Fonts/Roboto-Medium.ttf', 10), '', ext.Vector(3, 6)))
    bus = obj.AddComponent(mono.Bus(_car, mono.Car.Driver(), w0, way, w1, route, maxp))
    obj.name += ' ' + str(bus.get_uniqid())
    return obj
def map(name, path, pos, size=ext.Vector(.2, .2), forceblit=False):
    gm = GameObject(name, 'def')
    gm.transform.SetScale(size.x, size.y)
    rend = mono.SpriteRenderer(ext.Sprite(path), ext.Vector.Zero(), -100, [255, 255, 255, 100])
    rend.forceblit = forceblit
    gm.AddComponent(rend)
    gm.transform.SetPos(pos.x, pos.y)
    c.maps.append(gm)
    return gm
# MAIN
pygame.init()

clock = pygame.time.Clock()
c.scene = Scene([])
scene = c.scene
var.render.defaults = [mono.Text, mono.SpriteRenderer]
c.iinput = Input()
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
                        ])}

pygame.display.set_caption("Barnaul Streets Simulator")
pygame.display.set_icon(ext.Sprite('Graphics/stop.png').load)

camera = GameObject("Camera", "def")
c.mainCamera = camera.AddComponent(mono.Camera((1280, 720), 60, 1))
camera.AddComponent(mono.PlayerController())
cam = camera.transform.GetComponent(mono.Camera)
camera.transform.SetPos(3127, -411)
camera.transform.position -= ext.Vector(-30, -30) # откуда этот offset я без понятия

c.lightsControllers.append(lc(13.0, 60.0, False))  # 0
c.lightsControllers.append(lc(60.0, 60.0, True))  # 1
c.lightsControllers.append(lc(60.0, 60.0, False))  # 2

rend.lowmaps = True
rend.mapsize = 2
for i in [1, 7, 13]:
    ypos = [1, 7, 13].index(i)
    for j in range(0, 6):
        vec = ext.Vector(1475 * (j-1)*1, 1475 * (ypos-1)*1)
        extra = 'low/' if rend.lowmaps else ''
        line = str((i+j)-1).zfill(2)
        scene.AddObject(map(line, 'Graphics/map/' + extra + line + '.png', vec, ext.Vector(rend.mapsize, rend.mapsize)))
scene.AddObject(map('end', f'Graphics/map/{"low/" if rend.lowmaps else ""}end.png', ext.Vector(1475 * 5, -1475), ext.Vector(rend.mapsize, rend.mapsize), True))

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
rp('00102', 'start', 475, [bs('Телефонная улица', 35)], ext.Vector(6312, 1176)),
rp('00101', 'alights', 150, [bs('Северо-Западная улица', 149), trl('lineleft', 4, 1), trl('lineright', 35, 1)], ext.Vector(5663, 873)),
rp('00100', 'end', 200,
   [],
   ext.Vector(5469, 780))
])[0]
asz1 = rpcollection([
rp('10100', 'start', 150,
   [bs('Северо-Западная улица', 2), trl('down', 121, 1)],
   ext.Vector(5431, 794)),
rp('10101', 'alights', 475, [bs('Телефонная улица', 466, False)], ext.Vector(5654, 894)),
rp('10102', 'end', 1, [], ext.Vector(6301, 1199)),
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

testway = mr0 + aapr0

cc = 0
buses53 = [bus(testway, '53', 70) for i in range(0, 5)]
buses144 = [bus(testway, '144', 30) for i in range(0, 3)]
scene.AddObjects([camera])
scene.AddObjects(buses53)
scene.AddObjects(buses144)
for gm in scene.GetActive(True):
    for comp in gm.components:
        if comp.enabled:
            comp.Start()
runtimeActive = True
while runtimeActive:
    pygame.display.update()
    keys = pygame.key.get_pressed()
    var.core.iinput.UpdateInput(keys)
    var.core.deltaTime = clock.tick(var.core.mainCamera.targetFramerate) / 1000
    var.core.screen.fill('black')
    #var.core.screen.blit(pygame.Surface([1000, 1000]), (0, 0))
    if c.iinput.keys[pygame.K_e]:
        print(c.iinput.cursorWorldPosition)
        debugstop = True
    if c.iinput.keys[pygame.K_q]:
        front.StartConsoleDialogue()
        var.core.deltaTime = clock.tick(var.core.mainCamera.targetFramerate) / 1000
        c.deltaTime = var.core.mainCamera.targetFramerate / 1000
        #comm = input('command: ')
    # print(player.transform.TryGetComponent(mono.SpriteRenderer).layer, bcg.transform.TryGetComponent(mono.SpriteRenderer).layer)
    for gameObject in scene.GetActive(True):
        for comp in gameObject.components:
            if (var.render.defaults.__contains__(type(comp)) == False) and comp.enabled:
                comp.Update()


    for rr in var.render.defaults.__reversed__():
        rendList = []
        for gm in scene.GetActive(True):
            for comp in gm.components:
                if (type(comp) == rr)  and comp.enabled: rendList.append(comp)
        rendList.sort(key=lambda r: r.layer, reverse=False)
        for rend in rendList: 
            rend.Update()

    for i in c.lightsControllers:
        i.Update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            runtimeActive = False
            pygame.quit()
