
# classe enumerando os erros por posição e ordem.

class Erro_rastreio:
    def __init__ (self, linha, coluna, tipo = None, msg = None):
	
        tiposIdentificados = ['lexico','sintatico','semantico']
        if tipo in tiposIdentificados:
            print("erro " + tipo + " erro identificado na linha " + str(linha+1) + " e coluna " +str(coluna))
        else:
            print ("erro identificado na linha " + str(linha+1) + " e coluna " + str(coluna))
        if msg != None:
            print (msg) 
        
            
  
