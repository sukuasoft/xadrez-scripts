import bpy
import os

os.system('cls')


objs = bpy.context.selected_objects

def criar_game_propriedade():
    for obj in objs:
        bpy.context.scene.objects.active = obj
        #bpy.ops.object.game_property_new(type='INT', name='idade')
        bpy.ops.object.game_property_new(type='BOOL', name='isPeca')
        bpy.ops.object.game_property_new(type='STRING', name='normalColor')
        bpy.ops.object.game_property_new(type='INT', name='tipoMarca')
        bpy.ops.object.game_property_new(type='BOOL', name='marcado')
        bpy.ops.object.game_property_new(type='INT', name='jgPeca')
        
def criar_game_propriedade_peao():
      for obj in objs:
        bpy.context.scene.objects.active = obj
        #bpy.ops.object.game_property_new(type='INT', name='idade')
        bpy.ops.object.game_property_new(type='INT', name='coluna')
        bpy.ops.object.game_property_new(type='INT', name='linha')
        bpy.ops.object.game_property_new(type='INT', name='jogador')

def criar_sensores_and_controller():
     for obj in objs:
        bpy.context.scene.objects.active = obj 
        
        bpy.ops.logic.controller_add(type='PYTHON')
        control = obj.game.controllers['Python']
        control.text = bpy.data.texts['casaSelected.py']
       
        bpy.ops.logic.sensor_add(type='MOUSE', name='em_cima')
        obj.game.sensors['em_cima'].mouse_event =  'MOUSEOVER'
        obj.game.sensors['em_cima'].link(control)
        
        bpy.ops.logic.sensor_add(type='MOUSE', name='clicado')  
        obj.game.sensors['clicado'].mouse_event =  'LEFTCLICK'
        obj.game.sensors['clicado'].link(control)
        

### Colocara as peças do jogaddor como valores nas casas iniciais
def colocarCasaJogador():
    for obj in objs:
        obj.game.properties['isPeca'].value = True
        #obj.game.properties['jgPeca'].value = 0
        obj.game.properties['jgPeca'].value = 1

def criar_game_propriedade():
    for obj in objs:
        bpy.context.scene.objects.active = obj
        bpy.ops.object.game_property_new(type='STRING', name='namePeca') 
#criar_sensores_and_controller()       
#criar_game_propriedade_peao()
#colocarCasaJogador()