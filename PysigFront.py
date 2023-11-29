from os import system, name
from PysigOptions import core as c, render as rend
import random

__version = 'demo 1123'

def StartConsoleDialogue():
    greetings = [
        '\nСимулятор улицы Антона Петрова',
        f'Версия: {__version}',
        'Автор: Сергей Рем, 1ИСП-21',
        'Введите help для списка доступных команд, clear для очистки консоли или ~ для выхода из консоли\n'
    ]
    for i in greetings:
        print(i)
    __entercommand()
def __entercommand():
    comm = input('Команда: ')
    __parsecommand(comm)
def __parsecommand(comm:str) -> None:
    name = comm.split()[0]
    args = comm.split()
    args.pop(0)
    match name:
        case '~':
            return
        case 'help':
            __help(args)
        case 'clear':
            __clear()
        case 'carlist':
            __carlist(args)
        case 'robjlist':
            __robjlist(args)
        case 'follow':
            __follow(args)
        case 'map':
            __map(args)
        case _:
            print(f"Команда {name} не найдена!")

    __entercommand()
def __clear():
    if name == 'nt':  # windows
        _ = system('cls')
    else:  # mac & linux
        _ = system('clear')
def __help(args):
    show = 1 if len(args) == 1 and not args[0].isdigit() else 0  # if len(args) == 0
    manual = {
        'h':"HELP.\n"
            "h -> список всех команд.\n"
            "h @команда@ -> описание заданной команды.\n",
        'clear':"CLEAR CONSOLE.\n"
                "clear -> команда для очистки консоли.",
        'carlist':"CAR LIST.\n"
                  "carlist -> список всех машин, упорядоченных по уникальному идентификатору.\n"
                  "carlist @тип_машины@ -> список машин определённого типа,"
                  " упорядоченных по номеру маршрута по возрастанию, если это общ. транспорт,"
                  " или по уникальному идентификатору.\n"
                  "Типы машин: passenger, bus, trolleybus, tram.\n"
    }
    if show == 1:
        target = args[0]
        for c in manual:
            if c == target:
                found = True
                print(manual[c])
                break
        if not found:
            print('Не удалось найти команду!')
    else:
        for c in manual:
                print(manual[c])
def __carlist(args):
    if len(args) == 1:
        args[0] = args[0].capitalize()
    showtype = True if len(args) == 0 else False
    objs = c.scene.GetActive(True)
    cars = [gameObject for gameObject in objs if gameObject.transform.HasComponent(c.mono.Car)]
    if not showtype:
        cars = [gm for gm in cars if gm.transform.GetComponent(c.mono.Car).get_cartype().name ==args[0]]
        if c.mono.CarTypes(args[0]) in [c.mono.CarTypes.Bus, c.mono.CarTypes.Trolleybus, c.mono.CarTypes.Tram]:
            cars.sort(key=lambda car: car.transform.GetComponent(c.mono.Bus).get_route())
            cars.reverse()
        else:
            cars.sort(key=lambda car: car.transform.GetComponent(c.mono.CarObjectLogic).get_uniqid())
    else:
        cars.sort(key=lambda car: car.transform.GetComponent(c.mono.Car).get_cartype().value)
    for gameObject in cars:
        car = gameObject.transform.GetComponent(c.mono.Car)
        i = gameObject.transform.GetComponent(c.mono.CarObjectLogic).get_uniqid()
        t = str(car.get_cartype()).split('.')[1]
        n = car.get_carname()
        o = ''
        if car.get_cartype() in [c.mono.CarTypes.Bus, c.mono.CarTypes.Trolleybus, c.mono.CarTypes.Tram]:
            l = car.transform.GetComponent(c.mono.Bus)
            o = f'{l._Bus__route} маршрут, {l._Bus__passengers}/{l._Bus__maxpassengers} пс.'
        if showtype:
            print(f"{t}, id {i}, {n}, {o}")
        else:
            print(f"id {i}, {n}, {o}")
def __robjlist(args):
    if len(args) == 1:
        showall = False
        match args[0]:
            case 'trafficlight':
                args[0] = 'TrafficLight'
            case 'busstop':
                args[0] = 'BusStop'
            case 'crossing':
                args[0] = args[0].capitalize()
    else:
        showall = True
    all = c.scene.GetActive(True)
    objs = [gameObject for gameObject in all if gameObject.transform.HasComponent(c.mono.RoadObject)]
    if not showall:
        objs = [obj for obj in objs if obj.transform.GetComponent(c.mono.RoadObject).objType.name == args[0]]
        objs.sort(key=lambda x: x.transform.GetComponent(c.mono.RoadObject).objId)
    else:
        objs.sort(key=lambda x: x.transform.GetComponent(c.mono.RoadObject).objType.value)
    for i in objs:
        r = i.transform.GetComponent(c.mono.RoadObject).ReturnAsString()
        print(r)
def __follow(args):
    rand = len(args) != 1
    objs = c.scene.GetActive(True)
    cars = [gameObject for gameObject in objs if gameObject.transform.HasComponent(c.mono.Car)]
    if rand:
        target = random.choice(cars)
    else:
        for i in cars:
            if i.transform.GetComponent(c.mono.CarObjectLogic).uniqId == args[0]:
                target = i
                break
        else:
            target = random.choice(cars)
    c.mainCamera.followAt = target
    print("Чтобы выйти нажмите '~'")
def __map(args):
    if len(args) == 0:
        for map in c.maps:
            sr = map.transform.GetComponent(c.mono.SpriteRenderer)
            sr.enabled = not sr.enabled
        return
    match args[0]:
        case 'low':
            for map in c.maps:
                rend.lowmaps = True
                rend.mapsize = float(args[1])
                map.transform.SetScale(rend.mapsize, rend.mapsize)
                map.transform.GetComponent(c.mono.SpriteRenderer).image = c.ext.Sprite(
                    "Graphics/map/low/" + map.name + '.png')
        case 'high':
            for map in c.maps:
                rend.lowmaps = False
                rend.mapsize = 1
                map.transform.SetScale(rend.mapsize, rend.mapsize)
                map.transform.GetComponent(c.mono.SpriteRenderer).image = c.ext.Sprite(
                    "Graphics/map/" + map.name + '.png')
