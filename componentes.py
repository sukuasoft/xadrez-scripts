from random import random, randrange
import bge
from collections import OrderedDict
from mathutils import Vector
from uteis import Ponto, XequeData
from uteis import MovePecaEvent
from uteis import print_array

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
    
    def __str__(self) -> str:
        return self.object.name
    def update(self):
        
        if self.selected and self.gc_cp.xequeData.isXeque:
            data = self.gc_cp.xequeData

            index = data.getIndex(self.object.name)
            
            if index != -1:
                 
                pontos = data.pecaMovimentos[index][1]
                if len(self.gc_cp.casasMarcadas) != 0:
                     self.gc_cp.desmarcarCasas()

                for p in pontos:
                    c = self.gc_cp.getCasa(p)
                    
                    if c['isPeca']: 
                        if c['jgPeca'] != self.object['jogador']:
                            c.color = [0.78, 0, 0, 1]   
                            c['marcado'] = True
                            c['tipoMarca'] = 2
                            self.gc_cp.casasMarcadas.append(c)
                            
                    else:
                        c.color = [0, 0.78, 0.49, 1]
                        c['marcado'] = True
                        c['tipoMarca'] = 1
                        self.gc_cp.casasMarcadas.append(c)
                    
                self.gc_cp.lastPecaSelected = self

                self.selected  = False
                    
            pass

        elif self.selected:
            self.gc_cp.marcarCasa(self, self.ponto, self.object['jogador'], self.tipoPeca, self.first)
            self.selected = False
        
        if self.isMove:
            self.gc_cp.xequeData.limpar()
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

                self.gc_cp.checarXeque(self)
        pass


class GC (bge.types.KX_PythonComponent):
    
    args = {'reiPreto': '', 'reiBranco': ''}
    def start(self, args):
        self.wait = False
        self.jg_atual = 0
        self.casasMarcadas = []
        objs = bge.logic.getCurrentScene().objects
        self.casas = []
        self.lastPecaSelected = None
        self.reiPreto = objs[args['reiPreto']]
        self.reiBranco = objs[args['reiBranco']]
        self.xequeData = XequeData()

    
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

    def checarXeque(self, peca):
        rei = None
        if peca.object['jogador'] == 0:
            rei = self.reiPreto
        else:
            rei = self.reiBranco

       
        pontos = None 
        if peca.tipoPeca == 0:
            dir = 1
            if peca.object['jogador'] == 0:
                 dir = -1

            pontos = self.getPeao(peca.ponto, dir, peca.first)
        elif peca.tipoPeca == 1:
            pontos = self.getTorre(peca.ponto)
        elif peca.tipoPeca == 2:
            pontos = self.getCavalo(peca.ponto)
        elif peca.tipoPeca == 3:
            pontos = self.getBispo(peca.ponto)
        
        elif peca.tipoPeca == 4:
            pontos = self.getBispo(peca.ponto)
            pontos.extend(self.getTorre(peca.ponto))
            
        else:
            pontos = self.getRei(peca.ponto)

        isXeque = False
        #Verificar se a peca jogada xekou o rei oponente
        for p in pontos:
           if p.igual(rei.components['peca'].ponto):
               isXeque = True
               break
        
        if isXeque:
            
            #marca o rei que foi xequado
            self.xequeData.isXeque = True
            c = self.getCasa(rei.components['peca'].ponto)
            c.color = [0.62, 0.18, 0.73, 1]
            self.casasMarcadas.append(c)

            #pega os pontos onde o rei pode andar
            pts = self.getRei(rei.components['peca'].ponto)
            
            index = 0
            done = False

            #tirando onde tem pecas amigas ou mesma equipa
            while not done:
                if not (index == len(pts)):
                    c = self.getCasa(pts[index])

                    if  c['isPeca'] and c['jgPeca'] == rei['jogador']:
                        pts.remove(pts[index])
                        index -= 1
                    else:
                        index += 1 
                else:
                    done = True
         
            #remove os perigos de andamento do rei
            pts = self.removendoPerigos(pts, rei['jogador'])
            
            #mostrar os pontos onde rei pode andar
            print(str(pts)) 

            ##testa se o rei pode comer
            for pt in pts:
                if pt.igual(peca.ponto):
                    isXeque = isXeque and False
                    self.xequeData.add((rei.name, [pt]))
                    #print('Rei pode comer o oponente')
                    break
            
            ##testa se o rei pode andar para fugir o xeque 
           

            if len(pts) == 0:
                print('Usuario nao pode mover-se')
            else:
                #print(pts)

                self.xequeData.add((rei.name, pts))
                isXeque = isXeque and False
               # isXeque = True
            

            #Pecas disponiveis do rei atacado
            jgs =  self.getJogadorEquipa(rei['jogador'])

           # print_array(jgs)

            #verifica se alguma peca pode eliminar o atacante
            for jg in jgs:
                pontos = None
                if jg.tipoPeca == 0:
                    dir = 1
                    if rei['jogador'] == 0:
                        dir = -1

                    pontos = self.getPeao(jg.ponto, dir, jg.first)
         
                        
                elif jg.tipoPeca == 1:
                    pontos = self.getTorre(jg.ponto)
                elif jg.tipoPeca == 2:
                    pontos = self.getCavalo(jg.ponto)
                elif jg.tipoPeca == 3:
                    pontos = self.getBispo(jg.ponto)
                
                elif jg.tipoPeca == 4:
                    pontos = self.getBispo(jg.ponto)
                    pontos.extend(self.getTorre(peca.ponto))

                else:
                    continue
                
                for pt in pontos:
                    if peca.ponto.igual(pt):
                        self.xequeData.add((jg.object.name, [pt]))
                        isXeque = isXeque and False
                      #  print('Uma peca pode eliminar!')
                        break
            

            ## Calculo da interpolacao

            if peca.tipoPeca == 1 or peca.tipoPeca == 3 or peca.tipoPeca == 4:

                #print('hello')
                pontosInter = []
                pontoRei = rei.components['peca'].ponto
                
                #analisa qual tipo de movimentação a peca fez
                if peca.ponto.x == pontoRei.x or peca.ponto.y == pontoRei.y:

                    #torre
                    #print('torre')
                    if  peca.ponto.x != pontoRei.x:
                        dirX = -1
                        if pontoRei.x > peca.ponto.x:
                            dirX = 1
                            
                        done = False
                        x = peca.ponto.x + dirX
                        y = peca.ponto.y

                        while not done:
                            if pontoRei.x == x:
                                done = True   
                            else:
                                pontosInter.append(Ponto(x, y))
                                print(f'({x}, {y})')
                                
                            x += dirX

                    else:
                       
                        dirY = -1

                        if pontoRei.y > peca.ponto.y:
                            dirY = 1

                        done = False 
                        x = peca.ponto.x 
                        y = peca.ponto.y + dirY

                        while not done:
                            if pontoRei.y == y:
                                done = True   
                            else:
                                pontosInter.append(Ponto(x, y))
                                print(f'({x}, {y})')
                                
                            y += dirY   

                           
                    pass
                else:
                    #bispo
                    print('bispo')
                    dirX = -1
                    if pontoRei.x > peca.ponto.x:
                        dirX = 1 

                    dirY = -1

                    if pontoRei.y > peca.ponto.y:
                        dirY = 1
                    
                    done = False
                    x = peca.ponto.x + dirX
                    y = peca.ponto.y + dirY

                    while not done:
                        if pontoRei.x == x and pontoRei.y == y:
                            done = True   
                        else:
                            pontosInter.append(Ponto(x, y))
                            print(f'({x}, {y})')
                        
                        x += dirX
                        y += dirY

                #print_array(pontosInter)
                if  len(pontosInter) != 0:
                  #  print_array(pontosInter)
            
                    for jg in jgs:
                        pontos = None
                        if jg.tipoPeca == 0:
                            dir = 1
                            if rei['jogador'] == 0:
                                dir = -1

                            pontos = self.getPeao(jg.ponto, dir, jg.first)
                        elif jg.tipoPeca == 1:
                            pontos = self.getTorre(jg.ponto)
                        elif jg.tipoPeca == 2:
                            pontos = self.getCavalo(jg.ponto)
                        elif jg.tipoPeca == 3:
                            pontos = self.getBispo(jg.ponto)
                        
                        elif peca.tipoPeca == 4:
                            pontos = self.getBispo(jg.ponto)
                            pontos.extend(self.getTorre(jg.ponto))
                        
                        else:
                            continue

                        for ptIn in pontosInter:
                            for pt in pontos:
                                if ptIn.igual(pt):
                                    self.xequeData.add((jg.object.name, [ptIn]))
            
                                    isXeque = isXeque and False
                                    break
            #print('Checado!')
            
            if isXeque:
                self.xequeData.isDone = True
                print('Xeque-Mate')
            else:
                print('Saiu do xeque!')
            
        else:
           # print('Não checado!')
           pass
        pass
    
    
    def removendoPerigos(self, pontos, jg):
        oposto = 0
        if jg == 0:
            oposto = 1

        opostos = self.getJogadorEquipa(oposto)

        novoPontos = pontos

        for op in opostos:
            
            pontos = novoPontos.copy()

            if len (novoPontos) == 0:
                break

            pts = None
            if op.tipoPeca == 0:
                dir = 1
                if op.object['jogador'] == 0:
                    dir = -1

                pts = self.getPeao(op.ponto, dir, op.first)
            elif op.tipoPeca == 1:
                pts = self.getTorre(op.ponto)
            elif op.tipoPeca == 2:
                pts = self.getCavalo(op.ponto)
            elif op.tipoPeca == 3:
                pts = self.getBispo(op.ponto)
            elif op.tipoPeca == 4:
                pts = self.getBispo(op.ponto)
                pts.extend(self.getTorre(op.ponto))
            else:
                pts = self.getRei(op.ponto)
            
            for p in pontos:
                for pt in pts:
                    if p.igual(pt):
                        novoPontos.remove(pt)
                        break
        
        if len(novoPontos) == 0:
            return []
        return novoPontos

    
    def getJogadorEquipa(self, jg):
    
        jgs = []
        for l in self.casas:
            for c in l:
                if c['isPeca'] and c['jgPeca'] == jg:
                    obj = bge.logic.getCurrentScene().objects[c['namePeca']]
                    if obj.components['peca'].tipoPeca != 5: 
                        jgs.append(obj.components['peca'])

        return jgs



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
            pontos = self.removendoPerigos(pontos, pecaComponent.object['jogador'])
         
        
        
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