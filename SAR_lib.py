import json
from nltk.stem.snowball import SnowballStemmer
import os
import re


class SAR_Project:
    """
    Prototipo de la clase para realizar la indexacion y la recuperacion de noticias
        
        Preparada para todas las ampliaciones:
          parentesis + multiples indices + posicionales + stemming + permuterm + ranking de resultado

    Se deben completar los metodos que se indica.
    Se pueden añadir nuevas variables y nuevos metodos
    Los metodos que se añadan se deberan documentar en el codigo y explicar en la memoria
    """

    # lista de campos, el booleano indica si se debe tokenizar el campo
    # NECESARIO PARA LA AMPLIACION MULTIFIELD
    fields = [("title", True), ("date", False),
              ("keywords", True), ("article", True),
              ("summary", True)]
    
    
    # numero maximo de documento a mostrar cuando self.show_all es False
    SHOW_MAX = 10

 
    def __init__(self):
        """
        Constructor de la classe SAR_Indexer.
        NECESARIO PARA LA VERSION MINIMA

        Incluye todas las variables necesaria para todas las ampliaciones.
        Puedes añadir más variables si las necesitas 

        """
        self.index = {} # hash para el indice invertido de terminos --> clave: termino, valor: posting list.
                        # Si se hace la implementacion multifield, se pude hacer un segundo nivel de hashing de tal forma que:
                        # self.index['title'] seria el indice invertido del campo 'title'.
        self.sindex = {} # hash para el indice invertido de stems --> clave: stem, valor: lista con los terminos que tienen ese stem
        self.ptindex = {} # hash para el indice permuterm.
        self.docs = {} # diccionario de documentos --> clave: entero(docid),  valor: ruta del fichero.
        self.weight = {} # hash de terminos para el pesado, ranking de resultados. puede no utilizarse
        self.news = {} # hash de noticias --> clave entero (newid), valor: la info necesaria para diferenciar la noticia dentro de su fichero (doc_id y posición dentro del documento)
        #Integer : (doc_id,pos) 
        self.tokenizer = re.compile("\W+") # expresion regular para hacer la tokenizacion
        self.stemmer = SnowballStemmer('spanish') # stemmer en castellano
        self.show_all = False # valor por defecto, se cambia con self.set_showall()
        self.show_snippet = False # valor por defecto, se cambia con self.set_snippet()
        self.use_stemming = False # valor por defecto, se cambia con self.set_stemming()
        self.use_ranking = False  # valor por defecto, se cambia con self.set_ranking()


    ###############################
    ###                         ###
    ###      CONFIGURACION      ###
    ###                         ###
    ###############################


    def set_showall(self, v):
        """

        Cambia el modo de mostrar los resultados.
        
        input: "v" booleano.

        UTIL PARA TODAS LAS VERSIONES

        si self.show_all es True se mostraran todos los resultados el lugar de un maximo de self.SHOW_MAX, no aplicable a la opcion -C

        """
        self.show_all = v


    def set_snippet(self, v):
        """

        Cambia el modo de mostrar snippet.
        
        input: "v" booleano.

        UTIL PARA TODAS LAS VERSIONES

        si self.show_snippet es True se mostrara un snippet de cada noticia, no aplicable a la opcion -C

        """
        self.show_snippet = v


    def set_stemming(self, v):
        """

        Cambia el modo de stemming por defecto.
        
        input: "v" booleano.

        UTIL PARA LA VERSION CON STEMMING

        si self.use_stemming es True las consultas se resolveran aplicando stemming por defecto.

        """
        self.use_stemming = v


    def set_ranking(self, v):
        """

        Cambia el modo de ranking por defecto.
        
        input: "v" booleano.

        UTIL PARA LA VERSION CON RANKING DE NOTICIAS

        si self.use_ranking es True las consultas se mostraran ordenadas, no aplicable a la opcion -C

        """
        self.use_ranking = v




    ###############################
    ###                         ###
    ###   PARTE 1: INDEXACION   ###
    ###                         ###
    ###############################


    def index_dir(self, root, **args):
        """
        NECESARIO PARA TODAS LAS VERSIONES
        
        Recorre recursivamente el directorio "root" e indexa su contenido
        los argumentos adicionales "**args" solo son necesarios para las funcionalidades ampliadas

        """

        self.multifield = args['multifield']
        self.positional = args['positional']
        self.stemming = args['stem']
        self.permuterm = args['permuterm']

        for dir, subdirs, files in os.walk(root):
            for filename in files:
                if filename.endswith('.json'):
                    fullname = os.path.join(dir, filename)
                    self.index_file(fullname)

        ##########################################
        ## COMPLETAR PARA FUNCIONALIDADES EXTRA ##
        ##########################################
        

    def index_file(self, filename):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Indexa el contenido de un fichero.

        Para tokenizar la noticia se debe llamar a "self.tokenize"

        Dependiendo del valor de "self.multifield" y "self.positional" se debe ampliar el indexado.
        En estos casos, se recomienda crear nuevos metodos para hacer mas sencilla la implementacion

        input: "filename" es el nombre de un fichero en formato JSON Arrays (https://www.w3schools.com/js/js_json_arrays.asp).
                Una vez parseado con json.load tendremos una lista de diccionarios, cada diccionario se corresponde a una noticia

        """

        with open(filename) as fh:
            jlist = json.load(fh)
        #
        # "jlist" es una lista con tantos elementos como noticias hay en el fichero,
        # cada noticia es un diccionario con los campos:
        #      "title", "date", "keywords", "article", "summary"
        #
        # En la version basica solo se debe indexar el contenido "article"
        # "jlist" es, en definitiva, una lista con diccionario dentro con los campos enumerados arriba
        #
        #
        #Como identificador secuencial vamos a usar la longitud del diccionario + 1
        #NOTA: El índice comienza en 1 y no en 0
        self.docs[len(self.docs) + 1] = filename
        #ID del último docID
        docID = len(self.docs)
        for i in range(len(jlist)):
            #Insertanos la noticia con un clave secuencial que depende de la longitud de la lista 
            # y el valor es una tupla (docID,posición)
            #NOTA: Índice comienza en 1 y no en 0
            self.news[len(self.news) + 1] = (docID,i)
            #Noticia en formato de dict.
            new = jlist[i]

            #Recorremos los campos que tienen tuplas (campo, bool)
            for f in self.fields:
                if f[1]: content = self.tokenize(new[f[0]]) #Articulo tokenizado y separado por espacios
                else: content = [new[f[0]]] #date no se tokeniza

                for term in content: #recorremos los términos del contenido
                    aux = self.index.get(f[0], {})
                    
                    #Si el término no se encuentra en el diccionario, creamos la posting list para dicho campo
                    if term not in aux:
                        aux[term] = [len(self.news)]
                    #Si la ultima noticia añadida es diferente a la actual, añadimos
                    elif aux[term][-1] != len(self.news):
                        aux[term].append(len(self.news))
                    
                    self.index[f[0]] = aux


    def tokenize(self, text):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Tokeniza la cadena "texto" eliminando simbolos no alfanumericos y dividiendola por espacios.
        Puedes utilizar la expresion regular 'self.tokenizer'.

        params: 'text': texto a tokenizar

        return: lista de tokens

        """
        return self.tokenizer.sub(' ', text.lower()).split()



    def make_stemming(self):
        """
        NECESARIO PARA LA AMPLIACION DE STEMMING.

        Crea el indice de stemming (self.sindex) para los terminos de todos los indices.

        self.stemmer.stem(token) devuelve el stem del token

        """
        
        pass
        ####################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE STEMMING ##
        ####################################################


    
    def make_permuterm(self):
        """
        NECESARIO PARA LA AMPLIACION DE PERMUTERM

        Crea el indice permuterm (self.ptindex) para los terminos de todos los indices.

        """
        pass
        ####################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE STEMMING ##
        ####################################################




    def show_stats(self):
        """
        NECESARIO PARA TODAS LAS VERSIONES
        
        Muestra estadisticas de los indices
        
        """
        #TODO: Mirar ayuda.pdf para rellenar todo ^^ y dejarlo bonito este print que es muy chapuza
        print("="*40)
        print("Number of indexed days: ",len(self.docs))
        print("-"*40)
        print("Number of indexed news ",len(self.news))
        print("="*40)

    ###################################
    ###                             ###
    ###   PARTE 2.1: RECUPERACION   ###
    ###                             ###
    ###################################


    def solve_query(self, query, prev={}):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Resuelve una query.
        Debe realizar el parsing de consulta que sera mas o menos complicado en funcion de la ampliacion que se implementen


        param:  "query": cadena con la query
                "prev": incluido por si se quiere hacer una version recursiva. No es necesario utilizarlo.


        return: posting list con el resultado de la query

        """
        
        if query is None or len(query) == 0:
            return []

        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################
        #Le damos la vuelta porque vamos a tratar la lista como una pila
        newquery = re.split(' ', query)[::-1]
        #Pila donde almacenamos los operandos que vamos viendo
        pila = []
        #Hay que hacer todos los términos de la consulta
        while newquery != []:
            #Obtenemos el contenido, se encuentra en lo alto de la peli
            var = newquery.pop()
            #Hemos encontrado un término
            if var not in ['AND','OR','NOT']:
                #Si no hemos visto ningún operando => primer término
                if pila == []:
                    if ':' in var: #comprobamos si es de un campo específico
                        j = var.rfind(':') #obtenemos la posición de :
                        campo = var[:j] #separamos el campo
                        termino = var[j+1:] #separamos el término
                        first = self.get_posting(termino, campo)

                    else: first = self.get_posting(var)
                #Hemos encontrado operandos previamente
                else:
                    if ':' in var: #comprobamos si es de un campo específico
                        j = var.rfind(':') #obtenemos la posición de :
                        campo = var[:j] #separamos el campo
                        termino = var[j+1:] #separamos el término
                        second = self.get_posting(termino, campo)

                    else: second = self.get_posting(var)

                    #Vamos haciendo operaciones
                    while pila != []:
                        #¿Cual es el ultimo operando?
                        op = pila.pop()
                        #Es un NOT, reverse a la segunda posting list
                        if op == 'NOT':
                            second = self.reverse_posting(second)
                        #Es  un AND, hacemos and_posting
                        elif op == 'AND':
                            second = self.and_posting(first,second)
                        #Es un OR, hacemos or_posting
                        else:
                            second = self.or_posting(first,second)
                    #Guardamos el resultado para más operaciones OwO
                    first = second
            #Se trata de un operando, lo añadimos a la pila
            else:
                pila.append(var)
        #Devolvemos el resultado
        #print(first)
        return first
 
    def get_posting(self, term, field='article'):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Devuelve la posting list asociada a un termino. 
        Dependiendo de las ampliaciones implementadas "get_posting" puede llamar a:
            - self.get_positionals: para la ampliacion de posicionales
            - self.get_permuterm: para la ampliacion de permuterms
            - self.get_stemming: para la amplaicion de stemming


        param:  "term": termino del que se debe recuperar la posting list.
                "field": campo sobre el que se debe recuperar la posting list, solo necesario si se hace la ampliacion de multiples indices

        return: posting list

        """
        #print('termino: '+term + ', campo: ' + field)

        flist = self.index.get(field,{}) #Sacamos el diccionario de campo 'field'
        plist = flist.get(term,[]) #Devolvemos la posting list del término dentro del campo
        return plist


    def get_positionals(self, terms, field='article'):
        """
        NECESARIO PARA LA AMPLIACION DE POSICIONALES

        Devuelve la posting list asociada a una secuencia de terminos consecutivos.

        param:  "terms": lista con los terminos consecutivos para recuperar la posting list.
                "field": campo sobre el que se debe recuperar la posting list, solo necesario se se hace la ampliacion de multiples indices

        return: posting list

        """
        pass
        ########################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE POSICIONALES ##
        ########################################################

    def get_stemming(self, term, field='article'):
        """
        NECESARIO PARA LA AMPLIACION DE STEMMING

        Devuelve la posting list asociada al stem de un termino.

        param:  "term": termino para recuperar la posting list de su stem.
                "field": campo sobre el que se debe recuperar la posting list, solo necesario se se hace la ampliacion de multiples indices

        return: posting list

        """
        
        stem = self.stemmer.stem(term)

        ####################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE STEMMING ##
        ####################################################

    def get_permuterm(self, term, field='article'):
        """
        NECESARIO PARA LA AMPLIACION DE PERMUTERM

        Devuelve la posting list asociada a un termino utilizando el indice permuterm.

        param:  "term": termino para recuperar la posting list, "term" incluye un comodin (* o ?).
                "field": campo sobre el que se debe recuperar la posting list, solo necesario se se hace la ampliacion de multiples indices

        return: posting list

        """

        ##################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA PERMUTERM ##
        ##################################################

    def reverse_posting(self, p):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Devuelve una posting list con todas las noticias excepto las contenidas en p.
        Util para resolver las queries con NOT.


        param:  "p": posting list


        return: posting list con todos los newid exceptos los contenidos en p

        """
        #Recuperamos el nº total de noticias que hay
        allnews = [i+1 for i in range(len(self.news))]
        #Posting list resultante 
        pres = []
        i = 0
        j = 0
        while i < len(p) and j < len(allnews):
            #Si son el mismo término,incrementamos todo en 1 y no añadimos nada al resultado
            if p[i] == allnews[j]:
                i += 1
                j += 1
            #Caso alternativo: allnews[j] < p[i], entonces añadimos el término allnews[j]
            elif allnews[j] < p[i]:
                pres.append(allnews[j])
                j+=1
            #No se puede dar el caso de que p[i] > allnews[j]
        #Si quedan términos sin visitar
        while j < len(allnews):
            pres.append(allnews[j])
            j += 1
        return pres

    def and_posting(self, p1, p2):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Calcula el AND de dos posting list de forma EFICIENTE

        param:  "p1", "p2": posting lists sobre las que calcular


        return: posting list con los newid incluidos en p1 y p2

        """
        #Indice con el que recorrer la p1
        i = 0
        #Indice con el que recorrer la p2
        j = 0
        #Posting list a devolver
        plres = []
        #Iteramos en el bucle while mientras no nos salgamos de las listas
        while i < len(p1) and j < len(p2):
            #Si los punteros apuntan al mismo nº, lo añadimos a la posting list
            # e incrementamos en 1 los punteros
            if p1[i] == p2[j]:
                plres.append(p1[i])
                i += 1
                j += 1
            #Si el valor del puntero de p1 < valor puntero p2
            #incrementamos solo i
            elif p1[i] < p2[j]:
                i+=1
            #Si valor puntero p2 < valor puntero p1
            #incrementamos j
            else:
                j+=1
        #Devolvemos la posting list resultante
        return plres

    def or_posting(self, p1, p2):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Calcula el OR de dos posting list de forma EFICIENTE

        param:  "p1", "p2": posting lists sobre las que calcular


        return: posting list con los newid incluidos de p1 o p2

        """
        #Indice con el que recorrer la p1
        i = 0
        #Indice con el que recorrer la 
        j = 0
        #Posting list a devolver
        plres = []
        while i < len(p1)  and j <len(p2):
            #Si p1[i] == p2[j] añadimos solo 1
            if p1[i] == p2[j]:
                plres.append(p1[i])
                i += 1
                j += 1
            #p1[i] < p2[j] => añadimos p1[i] e incrementamos i
            elif p1[i] < p2[j]:
                plres.append(p1[i])
                i +=1
            #p1[i] > p2[j] => añadimos p2[j] e incrementamos j
            else:
                plres.append(p2[j])
                j += 1
        #Estos dos bucles son necesarios porque puede que no se haya añadido una lista entera
        while i < len(p1):
            plres.append(p1[i])
            i += 1
        while j < len(p2):
            plres.append(p2[j])
            j += 1
        return plres

    def minus_posting(self, p1, p2):
        """
        OPCIONAL PARA TODAS LAS VERSIONES

        Calcula el except de dos posting list de forma EFICIENTE.
        Esta funcion se propone por si os es util, no es necesario utilizarla.

        param:  "p1", "p2": posting lists sobre las que calcular


        return: posting list con los newid incluidos de p1 y no en p2

        """
        #A EXCEPT B se traduce como A AND NOT B, por lo tanto es tan sencillo como devolver 
        p2 = self.reverse_posting(p2)
        #A AND NOT B lo hacemos
        pres = self.and_posting(p1,p2)
        #Devolvemos el la posting list de resultado
        return pres




    #####################################
    ###                               ###
    ### PARTE 2.2: MOSTRAR RESULTADOS ###
    ###                               ###
    #####################################


    def solve_and_count(self, query):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Resuelve una consulta y la muestra junto al numero de resultados 

        param:  "query": query que se debe resolver.

        return: el numero de noticias recuperadas, para la opcion -T

        """
        result = self.solve_query(query)
        print("%s\t%d" % (query, len(result)))
        return len(result)  # para verificar los resultados (op: -T)


    def solve_and_show(self, query):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Resuelve una consulta y la muestra informacion de las noticias recuperadas.
        Consideraciones:

        - En funcion del valor de "self.show_snippet" se mostrara una informacion u otra.
        - Si se implementa la opcion de ranking y en funcion del valor de self.use_ranking debera llamar a self.rank_result

        param:  "query": query que se debe resolver.

        return: el numero de noticias recuperadas, para la opcion -T
        
        """
        result = self.solve_query(query)
        if self.use_ranking:
            result = self.rank_result(result, query)
        return result   

        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################




    def rank_result(self, result, query):
        """
        NECESARIO PARA LA AMPLIACION DE RANKING

        Ordena los resultados de una query.

        param:  "result": lista de resultados sin ordenar
                "query": query, puede ser la query original, la query procesada o una lista de terminos


        return: la lista de resultados ordenada

        """

        return []
        
        ###################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE RANKING ##
        ###################################################
