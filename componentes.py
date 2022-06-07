from random import random, randrange
import bge
from collections import OrderedDict
from mathutils import Vector
from uteis import Ponto
from uteis import MovePecaEvent

class peca(bge.types.KX_PythonComponent):
   
    args =  OrderedDict([
        ('tipoPeca', 0) 
        
    ])

    def start(self, args):
        self.selected = False
        self.casaTarget = None
        self.isMove = False
        self.moveEvent = None
        
        ## Armazena informação se essa peca ja foi jogada ou não
        self.first = True
        
        self.tipoPeca = args['tipoPeca']
        
        self.ponto = self.getPonto()
        
        self.gc = bge.logic.getCurrentScene().objects['Quadro']
        self.gc_cp = self.gc.components['GC']
        pass
    
    def getPonto(self):
        return Ponto(self.object['coluna']
        , self.object['linha'])
        
    def update(self):
        if self.selected:
            self.gc_cp.marcarCasa(self, self.ponto, self.object['jogador'], self.tipoPeca, self.first)
            self.selected = False
        
        if self.isMove:
            if self.moveEvent == None:
                self.moveEvent = MovePecaEvent(self.object.localPosition, self.casaTarget.localPosition, self.object) 
                if self.casaTarget['tipoMarca'] == 2:
                    self.gc_cp.eliminar_peca(self.casaTarget['namePeca'])

            
            if self.moveEvent.done():
                self.isMove = False
                self.moveEvent = None
                
               
                c = self.gc_cp.getCasa(self.ponto)
                
                c['isPeca'] = False
                c['namePeca'] = ''

                self.casaTarget['isPeca'] = True
                self.casaTarget['jgPeca'] = self.object['jogador']
                self.casaTarget['namePeca'] = self.object.name
                p = self.gc_cp.getPontoPorCasa(self.casaTarget.name)
            
                
                self.object['coluna'] = p.x
                self.object['linha'] = p.y
                
                self.ponto = self.getPonto()

                if p.y == 7 and self.object['jogador'] == 1 and self.tipoPeca == 0:
                    self.gc_cp.promocao(self)
        
                elif p.y == 0 and self.object['jogador'] == 0 and self.tipoPeca == 0:
                    self.gc_cp.promocao(self)

                self.first = False
                
                self.casaTarget = None
                self.gc_cp.changeJogador()
                self.gc_cp.wait = False
                self.gc_cp.lastPecaSelected = None
        pass


class GC (bge.types.KX_PythonComponent):
    
    def start(self, args):
        self.wait = False
        self.jg_atual = 0
        self.casasMarcadas = []
        objs = bge.logic.getCurrentScene().objects
        self.casas = []
        self.lastPecaSelected = None
    
        cols = 'ABCDEFGH'
        
       # self.painelPromocao = objs['PainelPromocao']

        #self.changeVisiblePainel(False)
        for i in range(1, 9):
            c = []
            
            for x in range(8):
                c.append(objs[str(cols[x] + str(i))])
                
            self.casas.append(c)
        
        #print(self.casas)
        pass


    #def changeVisiblePainel(self, state):
     #   self.painelPromocao.setVisible(state)

      #  for ch in self.painelPromocao.children:
       #     ch.setVisible(state)
        #    for c in ch.children:
         #       c.setVisible(state)

    def update(self):
        pass
    
    from random import randrange
    def promocao(self, peca):
        self.wait = True
       # self.changeVisiblePainel(True)
        self.lastPecaSelected = peca

        self.PromocaoSelecionada(randrange(1, 5, 1))

    def PromocaoSelecionada(self, id):
        self.lastPecaSelected.tipoPeca = id 

        obj = self.lastPecaSelected.object.children[0]

        if id == 1:
            obj.replaceMesh('Torre')
        elif id == 2:
            obj.replaceMesh('Cavalo')
        elif id == 3:
            obj.replaceMesh('Bispo')
        elif id == 4:
             obj.replaceMesh('Rainha')
        
        #self.changeVisiblePainel(False)

        self.wait = False
        pass

    def eliminar_peca(self, name):
        print(name)
        bge.logic.getCurrentScene().objects[name].endObject()
    
    def changeJogador(self):
        if self.jg_atual == 0:
            self.jg_atual = 1
        else:
            self.jg_atual  = 0
    
    def getPontoPorCasa(self, nameCasa):
        x = 0
        y = 0
        p = None
      #  print(nameCasa)
        for l in self.casas:
            x = 0
            for c in l:
                if c.name == nameCasa:
                    p = Ponto(x, y)
                    break
                x += 1
            y += 1
         
        return p
    
    def marcarCasa(self, pecaComponent, ponto, jg, peca, first):
        
        if len(self.casasMarcadas) != 0:
            self.desmarcarCasas()
        
        casaPeca = self.getCasa(ponto)
     
        casaPeca.color = [0.03, 0.87, 1, 1]
        casaPeca['marcado'] = True
        casaPeca['tipoMarca'] = 0
        self.casasMarcadas.append(casaPeca)
        dir = 1
        if jg == 0:
            dir = -1
            
        pontos = None
        
        if peca == 0:
            pontos = self.getPeao(ponto, dir, first)
        elif peca == 1:
            pontos = self.getTorre(ponto)
        elif peca == 2:
            pontos = self.getCavalo(ponto)
        elif peca == 3:
            pontos = self.getBispo(ponto)
        
        elif peca == 4:
            pontos = self.getBispo(ponto)
            pontos.extend(self.getTorre(ponto))
            
        elif peca == 5:
            pontos = self.getRei(ponto)
            print(pontos)
        
        
        for p in pontos:
            c = self.getCasa(p)
            
            if c['isPeca']: 
                if c['jgPeca'] != jg:
                    c.color = [0.78, 0, 0, 1]   
                    c['marcado'] = True
                    c['tipoMarca'] = 2
                    self.casasMarcadas.append(c)
                    
            else:
                c.color = [0, 0.78, 0.49, 1]
                c['marcado'] = True
                c['tipoMarca'] = 1
                self.casasMarcadas.append(c)
            
        self.lastPecaSelected = pecaComponent
        pass
    
    
    def moverPeca(self, toCasa):
        self.wait = True
        self.lastPecaSelected.isMove =True
        self.lastPecaSelected.casaTarget = toCasa
        self.desmarcarCasas()
        pass
        
    def desmarcarCasas(self):
        
        for cm in self.casasMarcadas:
            if cm['normalColor'] == 'black':
                cm.color = [0, 0, 0, 1]
            else:
                cm.color = [1, 1, 1, 1]
            
            cm['marcado'] = False
        
    
    def getCasa(self, ponto):
        return self.casas[ponto.y][ponto.x]
    
    def getPeao(self, ponto, dir, first):
        ls_pontos = []
        
        qtd_casa = 2
        if not first:
            qtd_casa = 1
        
        for y in range(1, qtd_casa+1):
            if self.casas[ponto.y + (y * dir)][ponto.x]['isPeca']:
                break
            ls_pontos.append(Ponto(ponto.x, ponto.y + (y * dir)))
        
        if self.isLimite(ponto.y + dir) and self.isLimite(ponto.x + 1):
            if self.casas[ponto.y + dir][ponto.x + 1]['isPeca']:
                ls_pontos.append(Ponto(ponto.x + 1, ponto.y + dir))
                
        if self.isLimite(ponto.y + dir) and self.isLimite(ponto.x - 1):
            if self.casas[ponto.y + dir][ponto.x - 1]['isPeca']:
                ls_pontos.append(Ponto(ponto.x - 1, ponto.y + dir))
        
        return ls_pontos
    
    def getTorre(self, ponto):
        ls_pontos = []
        
        for x in range(ponto.x + 1, 8):
            ls_pontos.append(Ponto(x, ponto.y))
            if self.casas[ponto.y][x]['isPeca']:
                break
            
        for x in range(ponto.x - 1, -1, -1):
            ls_pontos.append(Ponto(x, ponto.y))
            if self.casas[ponto.y][x]['isPeca']:
                break
            
        for y in range(ponto.y + 1, 8):
            ls_pontos.append(Ponto(ponto.x, y))
            if self.casas[y][ponto.x]['isPeca']:
                break
        
        for y in range(ponto.y - 1, -1, -1):
            ls_pontos.append(Ponto(ponto.x, y))
            if self.casas[y][ponto.x]['isPeca']:
                break
        
        return ls_pontos
    
    def getCavalo(self, ponto):
        ls_pontos = []
        
        lines = [ponto.y - 2, ponto.y + 2]
        cols = [ponto.x - 2, ponto.x + 2]
        
        for l in lines:
            if not self.isLimite(l):
                continue
            
            if self.isLimite(ponto.x-1):
                ls_pontos.append(Ponto(ponto.x -1, l))
            
            if self.isLimite(ponto.x + 1):
                ls_pontos.append(Ponto(ponto.x + 1, l))
        
        for c in cols:
            if not self.isLimite(c):
                continue
            
            if self.isLimite(ponto.y - 1):
                ls_pontos.append(Ponto(c, ponto.y - 1))
            
            if self.isLimite(ponto.y + 1):
                ls_pontos.append(Ponto(c, ponto.y + 1))
        
        return ls_pontos

    
    def getBispo(self, ponto):
        ls_pontos = []
        
        #armazena as direções diagonais que o bispo se move
        dirs = [[1, 1], [-1, 1], [1, -1], [-1, -1]] 
        
        for dir in dirs:
            
            done = False
            x = 1
            y = 1
            
            while not done:
                if self.isLimite(ponto.x + (dir[0] * x)) and self.isLimite(ponto.y + (dir[1] * y)):
                        ls_pontos.append(Ponto(ponto.x + (dir[0] * x), ponto.y + (dir[1] * y)))
                        if self.casas[ponto.y + (dir[1] * y)][ponto.x + (dir[0] * x)]['isPeca']:
                            done = True
                        else:
                            x += 1
                            y += 1
                else:
                    done = True    
        
        return ls_pontos    
    
    def getRei(self, ponto):
        ls_pontos = []
        
        cols = [ponto.x - 1, ponto.x + 1]
        
        for col in cols:
            
            for l in range(ponto.y - 1, ponto.y + 2):
                if not self.isLimite(l):
                    continue
                ls_pontos.append(Ponto(col, l))
                
        if self.isLimite(ponto.y - 1):
            ls_pontos.append(Ponto(ponto.x, ponto.y - 1))
        
        if self.isLimite(ponto.y + 1):
            ls_pontos.append(Ponto(ponto.x, ponto.y + 1))
        
        return ls_pontos
                
    def isLimite(self, valor):
        return valor <= 7 and valor >= 0
pass