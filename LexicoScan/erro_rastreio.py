
# classe enumerando os erros por posição e ordem.

class Erro_rastreio:
    def __init__(self, linha, coluna, tipo = None, msg = None):
	
        tipos_Identificados = ['lexico','sintatico','semantico']
        if tipo in tipos_Identificados:
            print("Erro " + tipo + " identificado na linha " + str(linha+1) + " e coluna " +str(coluna+1))
        else:
            print ("Erro identificado na linha " + str(linha+1) + " e coluna " + str(coluna+1))
        if msg != None:
            print (msg) 
        
            
  
