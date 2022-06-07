import bge 

co = bge.logic.getCurrentController()
casa = co.owner

over  = co.sensors['em_cima']
click = co.sensors['clicado']

game_controller = bge.logic.getCurrentScene().objects['Quadro'].components['GC']


if over.positive and click.positive and not game_controller.wait:
    
    if casa['marcado'] and casa['tipoMarca'] != 0:
        game_controller.moverPeca(casa)
    
    else:
        print('Casa invalida')