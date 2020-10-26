from simpleai.search import (
    SearchProblem, 
    breadth_first, 
    depth_first, 
    uniform_cost,
    astar,
    iterative_limited_depth_first
)

from simpleai.search.viewers import WebViewer, BaseViewer

CARGAS = ['rafaela','santa_fe'] 
CONEXIONES = {
    'sunchales': [('lehmann', 32)],
    'lehmann': [('rafaela', 8),('sunchales',32)],
    'rafaela': [('susana', 10),('esperanza', 70),('lehmann',8)],
    'susana': [('angelica', 25),('rafaela',10)],
    'angelica': [('san_vicente', 18),('sc_de_saguier', 60),('susana',25),('santo_tome',85)],
    'esperanza': [('recreo', 20),('rafaela',70)],
    'recreo': [('santa_fe', 10),('esperanza',20)],
    'santa_fe': [('santo_tome', 5),('recreo',10)],
    'santo_tome': [('angelica', 85),('sauce_viejo', 15),('santa_fe',5)],
    'sauce_viejo': [('santo_tome',15)],
    'san_vicente': [('angelica',18)],
    'sc_de_saguier': [('angelica',60)]
}

class mercadoArtificialProblem(SearchProblem):
    def is_goal(self, state):
        camiones_estado, paquetes_estado = state
        lista = []
        if len(paquetes_estado) != 0:
            return False
        
        for cam in camiones_estado:
            if (len(cam[2]) > 0):
                paquetes_del_camion = cam[2]
                for paq in paquetes_del_camion:
                    for paq_2 in PAQUETES:
                        if paq == paq_2[0] and paq_2[2] != cam[0]:
                            return False
                lista.append(cam[0])
            else:
                lista.append(cam[0])     
            
        for camion in lista:
            if camion not in CARGAS:
                return False
            
        return True

    def actions(self, state):
        acciones_disponibles = []
        camiones_estado, paquetes_estado = state
        for index_camion, camion in enumerate(camiones_estado):            
            #ACCIONES DE MOVER EL CAMION
            for ciudad_a_ir in CONEXIONES[camion[0]]:
                nafta_necesaria = round((ciudad_a_ir[1] / 100),2)
                if (camion[1] >= nafta_necesaria):
                    acciones_disponibles.append((index_camion,ciudad_a_ir[0], nafta_necesaria))
                            
        return acciones_disponibles
    

    #estado: ((('Sunchales',1.5,()), ('Sunchales',2,()), ('Rafaela',2,())), ('p1','p2','p3', 'p4')
    #accion: (0,'Rafaela', nafta_necesaria)
    def result(self, state, action):
        camiones_estado, paquetes_estado = state
        camiones_estado = list(camiones_estado)
        paquetes_estado = list(paquetes_estado)
        
        cam = camiones_estado[action[0]]
        cam = list(cam)
        ciudad_del_camion = cam[0]
        nafta_restante_camion = cam[1]
        paquetes_del_camion = list(cam[2]) 
      
        #ACÁ JUNTAMOS PAQUETES SI ES NECESARIO JUNTAR
        for paquete in paquetes_estado:
            for paquete_lista in PAQUETES:
                if paquete == paquete_lista[0] and ciudad_del_camion == paquete_lista[1]:                    
                    paquetes_del_camion.append(paquete) 
        
        for paq in paquetes_del_camion:
            for paq2 in paquetes_estado:
                if paq == paq2:
                    paquetes_estado.remove(paq)

        #ACÁ DEJAMOS UN PAQUETE CUANDO SE ENCUENTRA EN LA CIUDAD DEL PAQUETE (SI TIENE)
        if len(paquetes_del_camion) != 0:
            item_list = []
            for paq in paquetes_del_camion:
                for paq_2 in PAQUETES:
                    if paq == paq_2[0] and ciudad_del_camion == paq_2[2]:
                        item_list.append(paq)
            if len(item_list) != 0:
                paquetes_del_camion = [e for e in paquetes_del_camion if e not in item_list]

        #PRIMERO NOS MOVEMOS A LA CIUDAD DE LA ACCIÓN Y RESTAMOS EL COMBUSTIBLE
        ciudad_del_camion = action[1]  
        nafta_necesaria = action[2]
        
        #ACA CARGAMOS COMBUSTIBLE SI SE ENCUENTRA EN RAFAELA O SANTA FE
        if ciudad_del_camion == 'rafaela' or ciudad_del_camion == 'santa_fe':
            nafta_restante_camion = CAMIONES[action[0]][2]
        else:
            nafta_restante_camion = round((nafta_restante_camion - nafta_necesaria),2)   


        cam = tuple((ciudad_del_camion, nafta_restante_camion, tuple(paquetes_del_camion)))
        camiones_estado[action[0]] = cam
        state = tuple((tuple(camiones_estado), tuple(paquetes_estado)))

        return state

    def cost(self, state_ini, action, state_fin):
        return action[2]
    
    def heuristic(self, state):
        camiones_estado, paquetes_estado = state
        lista = []
        #Por cada paquete del estado, obtenemos el minimo recorrido que debe hacer en ese momento. Despues retornamos el máximo de esos minimos / 100. (Es decir, el costo de nasta)
        #Ejemplo: ((('Sunchales',1.5,()), ('Sunchales',2,()), ('Rafaela',2,())), ('p1','p2','p3', 'p4') 

        if paquetes_estado:
            for paquete_estado in paquetes_estado:
                for paquete_global in PAQUETES:
                    if paquete_estado == paquete_global[0]:
                        x = 0
                        for ciudad in CONEXIONES[paquete_global[1]]:
                            if x == 0:
                                menor = ciudad[1]
                                x = 1
                            else:
                                if ciudad[1]<menor:
                                    menor = ciudad[1]
                        lista.append(menor)
            return round((max(lista) / 100),2)
        return 0

def planear_camiones(metodo, camiones, paquetes):
    lista = []
    for camion in camiones:
        lista.append((camion[1], camion[2],()))
    
    lista2 = []
    for paquete in paquetes:
        lista2.append(paquete[0])

    global CAMIONES 
    CAMIONES = list(camiones)
    global PAQUETES 
    PAQUETES = list(paquetes)

    METODOS = {
        'breadth_first': breadth_first,
        'depth_first': depth_first,
        'iterative_limited_depth_first': iterative_limited_depth_first,
        'uniform_cost': uniform_cost,
        'astar': astar,
    }

    INITIAL_STATE = (tuple(lista), tuple(lista2))
    problema = mercadoArtificialProblem(INITIAL_STATE) 
    result = METODOS[metodo](problema)
    
    itinerario = []
    for action,state in result.path():
        #aca sacamos ('c1',..)
        if action == None:
            pass
        else:            
            index_camion = action[0] 
            camion = camiones[index_camion][0]
            
            #ahora sacamos la ciudad a la que va
            camiones_estado, paquetes_estado = state
            ciudad = camiones_estado[index_camion][0]
            
            #sacamos la nafta que le cuesta llegar de un lugar a otro
            nafta = action[2]
                
            #faltan los paquetes de ese camion, que lo tenemos en el camiones_estado[index_camion][2] . e.g ('Sunchales',2,('p1','p2')),
            paquetes_del_camion = camiones_estado[index_camion][2]
            
            #agregamos todo al itinerario
            itinerario.append((camion,ciudad,nafta,list(paquetes_del_camion)))

    return itinerario

if __name__ == '__main__':   
    """camiones=[
        # id, ciudad de origen, y capacidad de combustible máxima (litros)
        ('c1', 'rafaela', 1.5),
        ('c2', 'rafaela', 2),
        ('c3', 'santa_fe', 2),
    ]

    paquetes=[
        # id, ciudad de origen, y ciudad de destino
        ('p1', 'rafaela', 'angelica'),
        ('p2', 'rafaela', 'santa_fe'),
        ('p3', 'esperanza', 'susana'),
        ('p4', 'recreo', 'san_vicente'),
    ]

    itinerario = planear_camiones(
        # método de búsqueda a utilizar. Puede ser: astar, breadth_first, depth_first, uniform_cost o greedy
        "breadth_first",camiones,paquetes
    )"""
