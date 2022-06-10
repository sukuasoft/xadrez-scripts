from mathutils import Vector

def lerp(a, b, t):
    return a + t * (b - a)
    
    
class Ponto:
    def mostrar(self):
        return f'(X={self.x}, Y={self.y})'
    
    def __str__(self) -> str:
        return self.mostrar()
        
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def igual(self, ponto):
        return self.x == ponto.x and self.y == ponto.y
    def __eq__(self, __o: object) -> bool:

        if hasattr(__o, 'x') and hasattr(__o, 'y'):
            return  self.igual(__o)
        else:
            return False
    
pass

class MovePecaEvent:
    
    def __init__(self, point, target, obj):
        self.objecto = obj
        self.startPoint = point
        self.target = target
        self.isFirstDone = False
        self.motionNormalDone = False
        obj.playAction('upAction', 0, 10)
        self.delta = 0.0
        self.stepEvent = ((1000 / 60) / 1000) * 0.5
        pass
    
    def done(self):
        
        
        if  not self.isFirstDone  and not self.objecto.isPlayingAction():
            self.isFirstDone = True
            return False
        
        if self.isFirstDone:
            if not self.motionNormalDone:
                if self.delta < 1:
                     vet =  Vector((lerp(self.startPoint.x, self.target.x, self.delta), lerp(self.startPoint.y, self.target.y, self.delta), self.startPoint.z))
                     self.objecto.localPosition = vet
                      
                else:
                    self.objecto.stopAction()
                    self.objecto.playAction('upAction', 10, 0)
                    self.motionNormalDone = True
                self.delta += self.stepEvent   
                return False
            else:
                if not self.objecto.isPlayingAction():
                    return True               
                    
        pass
pass


class XequeData:
    def __init__(self):
        self.pecaMovimentos = []
        self.isXeque = False
        self.isDone = False
        pass
    def add(self, data):

        index = self.getIndex(data[0])
        if  index == -1:
            self.pecaMovimentos.append(data)
        else:
            self.pecaMovimentos[index][1].extend(data[1])

        #for p in self.pecaMovimentos:
       #     print(p[1].mostrar())
            
    
    def getIndex(self, key):
        index = 0
        for c in self.pecaMovimentos:
            if c[0] == key:
                return index
            
            index += 1

        return -1

    def limpar(self):
        self.pecaMovimentos = []
        self.isXeque = False
    pass


def print_array(lista):
    for li in lista:
        print(str(li) + ', ' , end="")
    
    print('')