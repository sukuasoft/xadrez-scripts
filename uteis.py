from mathutils import Vector

def lerp(a, b, t):
    return a + t * (b - a)
    
    
class Ponto:
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
pass

class MovePecaEvent:
    
    def __init__(self, point, target, obj):
        self.objecto = obj
        self.startPoint = point
        self.target = target
        self.isFirstDone = False
        self.motionNormalDone = False
        obj.playAction('upAction', 0, 20)
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
                    self.objecto.playAction('upAction', 20, 0)
                    self.motionNormalDone = True
                self.delta += self.stepEvent   
                return False
            else:
                if not self.objecto.isPlayingAction():
                    return True               
                    
        pass
pass