import json
from os import system, name
from PysigOptions import core as c, render as rend, flags, flag_names as ff, args as cargs
import random

__started = False
def StartConsoleDialogue():
    greetings = f'''
Симулятор улицы Антона Петрова
Версия: {cargs.get('version')}
Автор: Сергей Рем, 1ИСП-21
Введите help для списка доступных команд, clear для очистки консоли или q для выхода из консоли
    '''

    print(greetings)
    __entercommand()
def __entercommand():
    if flags.get(ff.comma_break):
        if flags.get(ff.comma_auto_revert_break):
            flags.switch(ff.comma_break)
        return
    comm = input('Команда: ')
    __parsecommand(comm)
def first_props_replace(args:list) -> tuple:
    indExcludes = []
    propsExcludes = []
    for i in range(len(args)):
        arg: str
        arg = args[i]
        props = []
        for ch in range(len(arg)):
            if arg[ch] == '@':
                props.append(ch)
        unprop = arg
        for propi in props:
            symb = arg[propi+1]
            match symb:
                case 's':
                    unprop = unprop.replace('@s', '', 1)
                    unprop = '"' + unprop + '"'
                case 'c':
                    unprop = unprop.replace('@c', '', 1)
                    unprop = "'" + unprop + "'"
                case 'r':
                    unprop = unprop.replace('@r', '', 1)
                    indExcludes.append(i)
                    break
        args[i] = unprop
    for i in indExcludes:
        propsExcludes.append(args[i])
    return (args, propsExcludes)



def __replace_props(args:list) -> list:
    # region Hints
    # $ - replace element by core.args dictionary value (literally variable);
    #       > by default, doesn't put the value in quotes if type of the value is str;
    #       > ex. $version (output will be: release 1.0);
    # @ - property symbol, which is used together with the key that is written after the @;
    #       > it is always placed to the left of the other symbols;
    #       @s - puts the element in "" quotes;
    #       @c - puts the element in '' quotes;
    #       @r - prevents the use of other characters after it as pointers;
    #       > ex. @sTrue, @r$version;
    # endregion
    _args, exs = first_props_replace(args)
    args = _args
    pointerExcludes = exs
    createStack = lambda: ''.join([arg for arg in args if arg not in pointerExcludes])
    stack = createStack()
    while '$' in stack:
        stack = createStack()
        for i in range(len(args)):
            arg: str
            arg = args[i]
            if arg in pointerExcludes: continue
            if '$' in arg:
                j = arg.index('$')
                unprop = arg[j+1:]
                unprop = cargs.get(unprop)
                unprop = str(unprop)
                args[i] = arg.replace(arg[j:], unprop, 1)
                args, pointerExcludes = first_props_replace(args)
                continue

    return args
def __parsecommand(comm:str, single=False) -> None:
    if len(comm) == 0: __entercommand()
    name = comm.split()[0]
    args = comm.split()
    args.pop(0)
    args = __replace_props(args)
    # region Cases
    match name:
        case 'q':
            return
        case 'exit':
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
        case 'unfollow':
            __unfollow(args)
        case 'flags':  # dev
            __flags(args)
        case 'corex':  # dev
            __corex(args)
        case 'render':  # dev
            __render(args)
        case 'echo':
            __echo(args)
        case 'call':  # dev
            __call(args)
        case 'cargs':  # dev
            __cargs(args)
        case 'if':  # dev
            __if(args)
        case 'dev':  # dev
            c._Core__dev = False
            if len(args) > 0:
                c._Core__dev = True if args[0] == '1983' else False
        case _:
            print(f"Команда {name} не найдена!")
    # endregion
    if not single:
        __entercommand()
def __dev_check():
    return c.dev
def __clear():
    if name == 'nt':  # windows
        _ = system('cls')
    else:  # mac & linux
        _ = system('clear')
def __echo(args):
    line = ''.join([i+' ' for i in args])
    line = line[:-1]
    print(line)
def __cargs(args): # DEV
    if not __dev_check(): return
    pr = lambda _k, _g: print(f'${_k}: {_g} (type {type(_g)})')
    match len(args):
        case 0:
            for k,v in cargs.get_copy().items():
                pr(k,v)
        case 2:
            if not args[1] in cargs.get_copy(): return
            key = args[1]
            args[0] = 'del' if args[0] == 'delete' else args[0]
            match args[0]:
                case 'get':
                    get = cargs.get(key)
                    pr(key, get)
                case 'del':
                    cargs.delete(key)
                    print(f'${key} deleted.')
    if len(args) >= 3:
        if not args[0] == 'set': return
        key = args[1]
        value = args[2]
        _type = args[-1] if len(args)>=4 and '"' not in value else 'str'
        if '"' in value and '"' not in args[-1]:
            args[-1] = ''
            print('uee')
        if '"' in value:
            value = args[2:]
            value = [i for i in value if i != '']
            value = ''.join([i + ' ' for i in value])
            value = value[:-1]
            value = value.replace('"', '')
        value = eval(f'{_type}("{value}")')
        cargs.set(key, value, True)
        get = cargs.get(key)
        pr(key, get)


def __call(args): # DEV
    if not __dev_check() or len(args) == 0: return
    file = open(args[0], encoding='utf-8')
    flags.set(ff.comma_break, True)
    flags.set(ff.comma_auto_revert_break, False)
    for row in file:
        __parsecommand(row, True)
    flags.switch(ff.comma_break)
    flags.switch(ff.comma_auto_revert_break)
def __help(args):
    manual = ['help', 'carlist', 'robjlist', 'follow', 'unfollow', 'map']
    if len(args) > 0 and args[0] not in manual:
        print(f'Справочная информация к команде {args[0]} не найдена. Проверьте правильность написания и попробуйте ещё раз.')
        return
    show = 1 if len(args) > 0 else 0  # if len(args) == 0
    targets = []
    if show == 1:
        targets.append(args[0])
    else:
        targets = manual
    for command in targets:
        with open(f'Manual/{command}.txt', 'r', encoding='utf-8') as file:
            print('>>>', end='')
            for row in file:
                print('    ' + row, end='')
            print('')
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
        objs = [obj for obj in objs if obj.transform.GetComponent(c.mono.RoadObject).get_objtype().name == args[0]]
        objs.sort(key=lambda x: x.transform.GetComponent(c.mono.RoadObject).get_objid())
    else:
        objs.sort(key=lambda x: x.transform.GetComponent(c.mono.RoadObject).get_objtype().value)
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
            if i.transform.GetComponent(c.mono.CarObjectLogic).get_uniqid() == args[0]:
                target = i
                break
        else:
            target = random.choice(cars)
    c.mainCamera.followAt = target
    flags.set(ff.comma_break, True)
    #print("Чтобы выйти нажмите '~'")
def __unfollow(args):
    c.mainCamera.followAt = None
    flags.set(ff.comma_break, True)
    #print("Чтобы выйти нажмите '~'")
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
def __flags(args): # DEV
    if not __dev_check(): return
    copies = flags.get_copy()
    keys = list(copies.keys())
    keynames = [key.name for key in keys]
    if len(args) == 0:
        for key in keys:
            print(f'{key.name}: {copies[key]}')
    if len(args) == 3:
        if args[0] == 'set' and args[1] in keynames and args[2].capitalize() in ['True', 'False']:
            args[1] = ff(args[1])
            args[2] = '' if args[2].capitalize() == 'False' else args[2]
            flags.set(args[1], bool(args[2].capitalize()))
            print(f'{args[1].name}: {flags.get(args[1])}')
def __corex(args): # DEV
    if not __dev_check(): return
    line = ''.join([f'{i} ' for i in args])
    c.corex.append(line)
    print('Line added in Corex.')
def __render(args): # DEV
    if not __dev_check(): return
    if len(args) > 0:
        match args[0]:
            case 'save':
                rend.SavePreferences()
            case 'load':
                rend.LoadPreferences()
                rend.ResetVisuals()
    else:
        for key, value in dict(rend).items():
            print(f'{key}: {value}')
def __if(args:list):
    full = ''.join([i + ' ' for i in args])[:-1]
    cond = full.split('then')[0]
    act = args[args.index('then')+1:]
    act = ''.join([i + ' ' for i in act])[:-1]
    b = eval(cond)
    if b:
        __parsecommand(act)

