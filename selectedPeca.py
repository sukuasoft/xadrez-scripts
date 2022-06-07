import bge

from uteis import Ponto 

co = bge.logic.getCurrentController()
own = co.owner
over  = co.sensors['em_cima']
click = co.sensors['clicado']

if over.positive and click.positive:
    game_controller = bge.logic.getCurrentScene().objects['Quadro'].components['GC']
    

    if not game_controller.wait:
        if own['jogador'] == game_controller.jg_atual:
            own.components['peca'].selected = True 
            
        else:
            c = game_controller.getCasa(Ponto(own['coluna'], own['linha']))
            if  not game_controller.wait and c['marcado'] and c['tipoMarca'] != 0:
                    game_controller.moverPeca(c)
            
    