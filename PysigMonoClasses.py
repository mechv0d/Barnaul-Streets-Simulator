import random
from PysigExtensions import Sprite, Font, Vector, clamp, lerp
import pygame
import random as rd
import enum
from PysigOptions import core
from abc import ABC
class Mono(ABC):
    enabled = True
    # game object:
    gameObject = None
    transform = None
    def Start(self):
        pass
    def Update(self):
        pass
    def LongUpdate(self):
        pass
    def InitMono(self, gm):
        self.gameObject = gm
        self.transform = gm.transform

class Transform(Mono):
    position = Vector.Zero()
    rotation = 0
    scale = Vector(1, 1)
    parent = None
    childs = []
    def __init__(self, pos: Vector, rot: float, scale: Vector):
        self.parent = None
        self.childs = []
        self.position = pos
        self.rotation = rot
        self.scale = scale
    def __init__(self):
        self.parent = None
        self.childs = []
        self.position = Vector.Zero()
        self.rotation = 0
        self.scale = Vector(1, 1)
    def AddChild(self, child): # CHILD IS GAME OBJECT!!!!
        self.childs.append(child)
        child.transform.parent = self.gameObject
    def SetParent(self, other): # PARENT IS GAME OBJECT!!!!
        other.transform.childs.append(self.gameObject)
        self.parent = other
        self.position = self.position - other.transform.position
    def RemoveParent(self):
        self.parent.childs.remove(self)
        self.parent = None
    def SetPos(self, x, y):
        self.position = Vector(x, y)
    def SetRot(self, z):
        self.rotation = z
    def SetScale(self, x, y):
        self.scale = Vector(x, y)
    def SetPixelSize(self, wight, height):
        rend = self.GetComponent(SpriteRenderer)
        if rend != False:
            load = rend.Load()
            self.SetScale(wight / load.get_width(), height / load.get_height())
    def HasComponent(self, _type):
        for comp in self.gameObject.components:
            if isinstance(comp, _type):  # type(comp) == _type:
                return True
        return False
    def GetComponent(self, _type):
        for comp in self.gameObject.components:
            if isinstance(comp, _type):
                return comp
        return False
    def GetComponents(self, _type):
        comps = []
        for comp in self.gameObject.components:
            if isinstance(comp, _type):
                comps.append(comp)
        return comps
    def GetComponentsInChilds(self, _type, includeInactive = False):
        childs = self.GetChilds(includeInactive)
        comps = []
        for child in childs:
            comps += child.transform.GetComponents(_type)
        return comps

    def GetChilds(self, includeInactive = False):
        childs = []
        self.GetRecursive(childs, includeInactive)
        return childs
    def GetRecursive(self, array, inactive):
        array.append(self)
        for child in self.childs:
            if child.selfActive or inactive:
                child.transform.GetRecursive(array, inactive)
class SpriteRenderer(Mono):
    image = Sprite("Graphics/def.png")
    offseted = False
    offset = Vector.Zero()
    color = [0, 0, 0, 255]
    layer = 0
    forceblit = False
    def __init__(self, image: Sprite, offset=Vector.Zero(), layer=0, color=[255, 255, 255, 255.0]):
        self.image = image
        self.color = color
        self.layer = layer
        self.offset = offset
    def Start(self):
        if self.offseted:
            self.offset = Vector(-self.image.wight/2, -self.image.height/2)
    def Load(self):
        return pygame.image.load(self.image.path)
    def Update(self):
        if not self.CanBlit():
            return
        blitpos = self.transform.position + self.offset
        if (self.transform.parent != None):
            blitpos += self.transform.parent.transform.position
        if core.mainCamera.gameObject.transform.parent:
            blitpos -= core.mainCamera.gameObject.transform.parent.transform.position
        blitpos -= core.mainCamera.gameObject.transform.position

        img = pygame.transform.scale(self.image.load, (self.image.wight * self.transform.scale.x, self.image.height * self.transform.scale.y))
        img = pygame.transform.rotate(img, self.transform.rotation)
        img.convert_alpha()
        if isinstance(self.color, list):
            img.set_alpha(self.color[3])
        core.screen.blit(img, (blitpos.x, blitpos.y))

    def CanBlit(self) -> bool:
        if self.forceblit:
            return True
        blitpos = Vector.Zero()
        if core.mainCamera.gameObject.transform.parent:
            blitpos += core.mainCamera.gameObject.transform.parent.transform.position
        blitpos += core.mainCamera.gameObject.transform.position
        blitrange = [
            Vector(blitpos.x - core.mainCamera.screenSize.x / 1.2, blitpos.x + core.mainCamera.screenSize.x / 1),
            Vector(blitpos.y - core.mainCamera.screenSize.y / 1.2, blitpos.y + core.mainCamera.screenSize.y / 1)
                    ]
        #print(core.mainCamera.gameObject.transform.position)
        pos = self.transform.position + self.offset
        endpos = pos + Vector(self.image.wight, self.image.height)
        centpos = pos + Vector(self.image.wight, self.image.height)/2
        inx = blitrange[0].x < pos.x < blitrange[0].y
        iny = blitrange[1].x < pos.y < blitrange[1].y
        endx = blitrange[0].x < endpos.x < blitrange[0].y
        endy = blitrange[1].x < endpos.y < blitrange[1].y
        ctrx = blitrange[0].x < centpos.x < blitrange[0].y
        ctry = blitrange[1].x < centpos.y < blitrange[1].y
        start = inx and iny
        end = endx and endy
        center = ctrx and ctry
        down = inx and endy
        up = endx and iny
        return start or end or center or down or up


class Text(Mono):
    font = None  # Font()
    offset = Vector.Zero()
    layer = 0
    text = ''
    antialias = False
    color = [255, 255, 255, 255]
    bcg = None
    def __init__(self, font: Font, text, offset = Vector.Zero(), layer=0, antialias=True, color='White', bcg=None):
        self.font = font
        self.text = text
        self.offset = offset
        self.layer = layer
        self.antialias = antialias
        self.color = color
        self.bcg = bcg
    def load(self):
        return self.font.font.render(self.text, self.antialias, self.color, self.bcg)
    def Update(self):
        blitpos = self.transform.position + self.offset
        if (self.transform.parent != None):
            blitpos += self.transform.parent.transform.position
        if core.mainCamera.gameObject.transform.parent:
            blitpos -= core.mainCamera.gameObject.transform.parent.transform.position
        blitpos -= core.mainCamera.gameObject.transform.position
        txt = self.load() #pygame.transform.scale(self.load(), (self.image.wight * self.transform.scale.x, self.image.height * self.transform.scale.y))
        txt = pygame.transform.rotate(txt, self.transform.rotation)
        txt.convert_alpha()
        #self.colorize(img, self.color)
        if isinstance(self.color, list):
            txt.set_alpha(self.color[3])
        core.screen.blit(txt, (blitpos.x, blitpos.y))

class PlayerController(Mono):
    lerpTime = .0
    strength = 2
    baseSpeed = 400*3
    def Update(self):
        totalSpeed = self.baseSpeed * self.lerpTime
        if core.iinput.horizontal != 0 and core.iinput.vertical != 0: totalSpeed *= .54**.5
        v = Vector(core.iinput.horizontal, core.iinput.vertical)
        if v != Vector.Zero():
            self.lerpTime += core.deltaTime * self.strength
        else:
            self.lerpTime = 0
        self.lerpTime = clamp(self.lerpTime, 0, 1)

        self.transform.position += v * totalSpeed * core.deltaTime
      #  self.transform.position.x += core.iinput.horizontal * totalSpeed * core.deltaTime
       # self.transform.position.y += core.iinput.vertical * totalSpeed * core.deltaTime
class Camera(Mono):
    followAt = None
    screenSize = Vector(800, 600)
    targetFramerate = 60
    vsync = 0
    def __init__(self, size=(800, 600), framerate=60, vsync = 0):
        self.screenSize = Vector(size[0], size[1])
        self.targetFramerate = framerate
        self.vsync = vsync
    def Start(self):
        core.screen = pygame.display.set_mode((self.screenSize.x, self.screenSize.y), vsync=self.vsync)
    def Update(self):
        if self.followAt:
            x = self.followAt.transform.position.x
            y = self.followAt.transform.position.y
            self.transform.SetPos(x - self.screenSize.x/2, y - self.screenSize.y/2)
class RoadPoint(Mono):
    __id = '00000' # 0-направление движения (0 - налево, 1 - направо, 2 - в обе), 00-отрезок трассы, 00-маленькая часть отрезка
    __name = 'default'
    __distance = 1
    __objects = [][:]
    __cars = [][:]
    __way = None  # []
    __carscanstuck = False
    def __init__(self, id: str, name, distance, objects):
        self.__id = id.zfill(5)
        self.__name = name
        self.__distance = distance
        self.__objects = objects
    def Start(self):
        for i in self.__objects:
            if not self == self.__way[-1]:
                i.transform.position = Vector.Lerp(self.transform.position,
                                            self.__way[self.__way.index(self)+1].transform.position,
                                            i.get_position() / self.__distance)
            else:
                i.transform.position = Vector.Lerp(self.transform.position,
                                            self.__way[self.__way.index(self)-1].transform.position,
                                            i.get_position() / self.__distance)
            #i.transform.SetParent(self.gameObject)
            core.scene.AddObject(i.gameObject)
            for j in i.gameObject.components:
                j.Start()
    def get_cars(self):
        return self.__cars
    def set_way(self, way):
        self.__way = way
    def get_objects(self):
        return self.__objects
    def get_distance(self):
        return self.__distance
    def get_stuck(self):
        return self.__carscanstuck


class RoadObjectTypes(enum.Enum):
    TrafficLight = 'TrafficLight'
    BusStop = 'BusStop'
    Crossing = 'Crossing'
class CarTypes(enum.Enum):
    Passenger = 'Passenger'
    Bus = 'Bus'
    Trolleybus = 'Trolleybus'
    Tram = 'Tram'
class LightController:
    __canPass = False
    __time = 0.0
    __redTime = 30.0
    __greenTime = 60.0
    def Update(self):
        self.__time -= core.deltaTime
        if self.__time <= 0:
            if self.__canPass:
                self.__time = self.__redTime
            else:
                self.__time = self.__greenTime
            self.__canPass = not self.__canPass
    def __init__(self, rt, gt, status:bool):
        self.__redTime = rt
        self.__greenTime = gt
        self.__canPass = not status
        self.Update()
    def canPass(self):
        return self.__canPass
    def get_time(self):
        return self.__time
class RoadObject(Mono):
    __name = 'default'
    __objId = str(random.randint(0, 10**4)).zfill(4)
    __objType = RoadObjectTypes.TrafficLight
    __position = 0
    def AllowStream(self, car):
        pass
    def ReturnAsString(self) -> str:
        pass
    def get_objid(self):
        return self.__objId
    def get_position(self):
        return self.__position
    def get_objtype(self):
        return self.__objType

class TrafficLight(RoadObject):
    __canPass = False
    __controllerIndex = 0 # есть массив с bool переменными, и каждый светофор будет ссылаться на определённый объект в массив
    def ReturnAsString(self) -> str:
        return f"{str(self.__objType).split('.')[1]}, {self.__objId}, {self.__name}, {self.__position} м. от начала отрезка, " \
               f"{'Зеленый' if self.__canPass else 'Красный'} ещё {round(core.lightsControllers[self.__controllerIndex].time, 1)} сек."
    def Update(self):
        self.__canPass = core.lightsControllers[self.__controllerIndex].canPass()
        txt = self.transform.GetComponent(Text)
        if txt != False:
            #txt.text = 'Зеленый' if self.canPass else 'Красный'
            txt.text = str(round(core.lightsControllers[self.__controllerIndex].get_time(), 1))
            cl = 'Green' if self.__canPass else 'Red'
            txt.color = cl
    def AllowStream(self, car):
        return self.__canPass
    def __init__(self, name, pos, index):
        self._RoadObject__name = name
        self._RoadObject__objType = RoadObjectTypes.TrafficLight
        self._RoadObject__objId = str(random.randint(0, 10**4)).zfill(4)
        self._RoadObject__position = pos
        self.__controllerIndex = index
class BusStop(RoadObject):
    __canAdd = True
    __passengers = 0
    __time = 7.0
    __coeff = int(__time) // 3
    def Start(self):
        self.__passengers = random.randint(1, 14)
    def ReturnAsString(self) -> str:
        return f"{str(self.__objType).split('.')[1]}, {self.__objId}, {self.__name}, {self.__position} м. от начала отрезка, {self.__passengers} " \
               f"{'пассажир' if self.__passengers % 10 == 1 and self.__passengers != 11 else 'пассажира' if self.__passengers % 10 in [2, 3, 4] and self.__passengers not in [12, 13, 14] else 'пассажиров'}"
    def RemovePassengers(self, max:int):
        p = self.__passengers
        count = clamp(random.randint(0, p), 0, max)
        self.__passengers = clamp(p - count, 0, p)
        return count
    def AddPassengers(self):
        self.__passengers += random.randint(0, self.__coeff)
        self.__time = random.uniform(7, 17)
        self.__coeff = int(self.__time) // 3
    def Update(self):
        if self.__canAdd:
            self.__time -= core.deltaTime
        if self.__time <= 0:
            self.AddPassengers()

        txt = self.transform.GetComponent(Text)
        if txt is not False:
            txt.text = f"{self._RoadObject__name}\n{self.__passengers} пс."
    def AllowStream(self, car):
        return True
    def __init__(self, name, pos):
        self._RoadObject__name = name
        self._RoadObject__objType = RoadObjectTypes.BusStop
        self._RoadObject__objId = str(random.randint(0, 10**4)).zfill(4)
        self._RoadObject__position = pos
class Car(Mono):
    class Driver():
        __defNames = ['Сергей', 'Пётр', 'Стас', 'Кирилл', 'Александр', 'Михаил', 'Максим', 'Иван', 'Дмитрий', 'Олег']
        __defSurnames = ['Худяков', 'Попов', 'Васильев', 'Моисеев', 'Николаев', 'Безруков', 'Смирнов', 'Кузнецов', 'Новиков', 'Трофимов']
        name = ""
        baseRush = 1
        def __init__(self):
            self.__name = rd.choice(self.__defNames) + ' ' + rd.choice(self.__defSurnames)
            self.__baseRush = rd.uniform(.95, 1.1)
    __carId = str(rd.randint(0, 10**4)).zfill(4)
    __carType = CarTypes.Passenger
    __carName = 'default'
    __baseSpeed = 170
    #color = [255, 255, 255, 255]
    def __init__(self, type, name, speed=150):
        self.__carType = type
        self.__carName = name
        self.__baseSpeed = speed
        #self.color = color
        self.__carId = str(rd.randint(0, 10**4)).zfill(4)
    def Start(self):
        s = self.transform.GetComponent(SpriteRenderer)
        #s.color = self.color
    def get_carname(self):
        return self.__carName
    def get_cartype(self):
        return self.__carType
    def set_cartype(self, type):
        self.__carType = type
    def get_speed(self):
        return self.__baseSpeed
class CarObjectLogic(Mono):
    __uniqId = '0'
    __car = None
    __driver = None # Car.Driver()
    __canDrive = True
    __lerpspeed = .4  # in range btw 0 and 1
    __speed = 1  # car.baseSpeed
    __currentDistance = 0  # from 0 to currentPoint.distance
    __startPos = Vector.Zero()
    __currentPoint = None
    __path = [][:]
    __endPoint = None
    def __init__(self, car, driver, currentPoint, path:[], endPoint):
        self.__uniqId = str(rd.randint(0, 10**4)).zfill(4)
        self.__car = car
        self.__driver = driver
        self.__speed = car.get_speed() * driver.baseRush
        self.__currentPoint = currentPoint
        self.__currentPoint.cars.append(self)
        self.__path = path
        self.__endPoint = endPoint
    def Start(self):
        self.__startPos = self.__currentPoint.transform.position
    def ReturnAsString(self) -> str:
        pass

    def Check(self):
        d = self.__currentDistance
        for obj in self.__currentPoint.get_objects():
            if not d < obj.get_position() < d + 10:
                continue
            if obj.AllowStream(self) is False:
                self.__canDrive = False
                self.__lerpspeed = 0

                return
        if self.__currentPoint.get_stuck():
            for car in self.__currentPoint.get_cars():
                if d < car.__currentDistance < d + 8:
                    if car.__canDrive is False:
                        self.__canDrive = False
                        self.__lerpspeed = 0

                        return
                    else:
                        if car.__car.get_cartype() == CarTypes.Bus or car.__car.get_cartype() == CarTypes.Trolleybus:
                            if car.transform.GetComponent(Bus)._Bus__stoptime <= 0:
                                self.__lerpspeed = clamp(self.__lerpspeed - .1, 0, 1)

        self.__canDrive = True
    def Drive(self):
        if self.__canDrive:
            self.__lerpspeed = clamp(self.__lerpspeed + core.deltaTime * .8, 0, 1)
        secspeed = self.__speed / 3.6
        self.__currentDistance += core.deltaTime * (secspeed * self.__lerpspeed)
        self.transform.position = Vector.Lerp(self.__startPos,
                                              self.__path[self.__path.index(self.__currentPoint)+1].transform.position,
                                              self.__currentDistance / self.__currentPoint.get_distance())
        if self.__currentDistance > self.__currentPoint.get_distance():
            self.__currentPoint.get_cars().remove(self)
            if self.__currentPoint == self.__endPoint:
                self.__remove()
                return
            if self.__endPoint == self.__path[self.__path.index(self.__currentPoint) + 1]:
                self.__remove()
                return
            self.__currentPoint = self.__path[self.__path.index(self.__currentPoint) + 1]
            self.__currentPoint.get_cars().append(self)
            self.__currentDistance = 0
            self.__startPos = self.transform.position
    def __remove(self):
        core.scene.objects.remove(self.gameObject)
        print(f'{self.__car.get_cartype().value} #{self.__uniqId} has reached the end!')
        if self.transform.parent:
            self.transform.RemoveParent()
        cam = core.mainCamera
        if cam.followAt == self.gameObject:
            cam.followAt = None

class Passenger(CarObjectLogic):
    def Update(self):
        self.Check()
        if self.__canDrive:
            self.Drive()
class Bus(CarObjectLogic):
    __route = '0'
    __passengers = 0
    __maxpassengers = 30
    __stoptime = 0
    __reachedstops = None

    def __init__(self, car, driver, currentPoint, path:[], endPoint, route: str, maxpass: int):
        rd.seed(rd.randint(-(10**8), 10**8))
        self._CarObjectLogic__uniqId = str(rd.randint(0, 10**4)).zfill(4)
        self._CarObjectLogic__car = car
        self._CarObjectLogic__driver = driver
        self._CarObjectLogic__speed = car._Car__baseSpeed * driver._Driver__baseRush
        self._CarObjectLogic__currentPoint = currentPoint
        self._CarObjectLogic__currentPoint.get_cars().append(self)
        self._CarObjectLogic__path = path
        self._CarObjectLogic__endPoint = endPoint
        self.__route = route
        self.__maxpassengers = maxpass
    def Start(self):
        self.__reachedstops = []
        self._CarObjectLogic__startPos = self._CarObjectLogic__currentPoint.transform.position
    def Update(self):
        self.Check()
        self.BusStopCheck()
        if self.__stoptime > 0:
            self.__stoptime -= core.deltaTime
        else:
            if self._CarObjectLogic__canDrive:
                self.Drive()

        txt = self.transform.GetComponent(Text)
        if txt != False:
            txt.text = f"{self.__passengers}/{self.__maxpassengers}"
    def BusStopCheck(self):
        d = self._CarObjectLogic__currentDistance
        for obj in self._CarObjectLogic__currentPoint.get_objects():
            if not d < obj.get_position() < d + 4.5:
                if obj.get_objid() in self.__reachedstops:
                    obj.canAdd = True
                    if self.__maxpassengers - self.__passengers > 0:
                        self.__passengers = clamp(self.__passengers - random.randint(0, 4), 0, self.__maxpassengers)
                        self.__passengers += obj.RemovePassengers(self.__maxpassengers - self.__passengers)
                    self.__reachedstops.remove(obj.get_objid())
                continue
            if obj.get_objtype() != RoadObjectTypes.BusStop:
                continue
            if obj.get_objid() not in self.__reachedstops:
                obj.canAdd = False
                self.__lerpspeed = 0
                self.__stoptime = random.uniform(3, 7)
                self.__reachedstops.append(obj.get_objid())
    def get_uniqid(self):
        return self._CarObjectLogic__uniqId
    def get_route(self):
        return self.__route