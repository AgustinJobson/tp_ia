from simpleai.search import (
    SearchProblem, 
    breadth_first, 
    depth_first, 
    uniform_cost,
    astar
)

from simpleai.search.viewers import WebViewer, BaseViewer


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
    'san_vicente': [('angelica',18)]
}

class mercadoArtificialProblem(SearchProblem):

    def is_goal(self, state):
        camiones_estado, paquetes_estado = state
        lista = []
        for cam in camiones_estado:
            lista.append(cam[0])
        return (set(lista) == ('rafaela','santa_fe') or set(lista) == ('santa_fe','rafaela')) and (len(paquetes_estado) == 0)

    def actions(self, state):
        acciones_disponibles = []
        camiones_estado, paquetes_estado = state
        for index_camion, camion in enumerate(camiones_estado):
            for ciudad_a_ir in CONEXIONES[camion[0]]:
                nafta_necesaria = ciudad_a_ir[1] / 100
                if (camion[1] >= nafta_necesaria):
                    acciones_disponibles.append((index_camion,ciudad_a_ir[0]))
        return acciones_disponibles
    

    #((('Sunchales',1.5,()), ('Sunchales',2,()), ('Rafaela',2,())), ('p1','p2','p3', 'p4')
    def result(self, state, action):
        camiones_estado, paquetes_estado = state
        camiones_estado = list(camiones_estado)
        paquetes_estado = list(paquetes_estado)

        for index_camion, cam in enumerate(camiones_estado):
            cam = list(cam)
            ciudad_del_camion = cam[0]
            nafta_restante_camion = cam[1]
            paquetes_del_camion = list(cam[2]) 
            #cam[2] = list(cam[2])
            if index_camion == action[0]:
                #PRIMERO NOS MOVEMOS A LA CIUDAD DE LA ACCIÓN Y RESTAMOS EL COMBUSTIBLE
                for ciudad in CONEXIONES[cam[0]]:
                    if ciudad[0] == action[1]:
                        nafta_necesaria = ciudad[1] / 100
                nafta_restante_camion -= nafta_necesaria
                ciudad_del_camion = action[1]              

                #ACA CARGAMOS COMBUSTIBLE SI SE ENCUENTRA EN RAFAELA O SANTA FE
                if action[1] == 'rafaela' or action[1] == 'santa_fe':
                    nafta_restante_camion = camiones[index_camion][2]
                    #camiones_estado[index_camion][1] = camiones[index_camion][2]
            
                #ACÁ DEJAMOS UN PAQUETE CUANDO SE ENCUENTRA EN LA CIUDAD DEL PAQUETE (SI TIENE)
                if len(paquetes_del_camion) != 0:
                    for paq in paquetes_del_camion:
                        for paq_2 in paquetes:
                            if paq == paq_2[0] and ciudad_del_camion == paq_2[2]:
                                paquetes_del_camion.remove(paq)

                #ACÁ JUNTAMOS PAQUETES SI ES NECESARIO JUNTAR
                for paq in paquetes_estado:
                    for paq_2 in paquetes:
                        if paq == paq_2[0] and ciudad_del_camion == paq_2[1]:
                            paquetes_estado.remove(paq)
                            paquetes_del_camion.append(paq)

            cam = tuple((ciudad_del_camion, nafta_restante_camion, tuple(paquetes_del_camion)))

        state = tuple((tuple(camiones_estado), tuple(paquetes_estado)))
        return state

    def cost(self, state_ini, action, state_fin):
        indice_camion_accion, ciudad_a_ir = action
        camiones_estado, paquetes_estado = state_ini
        for index_camion_estado, cam in enumerate(camiones_estado):
            if index_camion_estado == indice_camion_accion:
                for ciudad in CONEXIONES[cam[0]]:
                    if ciudad[0] == ciudad_a_ir:
                        return ciudad[1] / 100


def planear_camiones(metodo, camiones, paquetes):
    lista = []
    for camion in camiones:
        lista.append((camion[1], camion[2],()))
    
    lista2 = []
    for paquete in paquetes:
        lista2.append(paquete[0])
            
    INITIAL_STATE = (tuple(lista), tuple(lista2))
    problema = mercadoArtificialProblem(INITIAL_STATE)
    
    resultado = metodo(problema)
    itinerario = []
    for action,state in resultado.path():
        #aca sacamos ('c1',..)
        index_camion = action[0] 
        camion = camiones[index_camion][0]
        
        #ahora sacamos la ciudad a la que va
        camiones_estado, paquetes_estado = state
        ciudad = camiones_estado[index_camion][0]
        
        #sacamos la nafta que le cuesta llegar de un lugar a otro
        for ciudad_conexion in CONEXIONES[ciudad]:
            if ciudad_conexion[0] == action[1]:
                nafta = ciudad_conexion[1] / 100
                break
            
        #faltan los paquetes de ese camion, que lo tenemos en el camiones_estado[index_camion][2] . e.g ('Sunchales',2,('p1','p2')),
        paquetes_del_camion = camiones_estado[index_camion][2]
        
        #agregamos todo al itinerario
        itinerario.append(camion,ciudad,nafta,tuple(paquetes_del_camion))
        
    return tuple(itinerario)

if __name__ == '__main__':   
    camiones=[
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
        breadth_first,camiones,paquetes
    )

    print(itinerario)