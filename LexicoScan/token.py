class Token:

    def __init__(self, tipo, lexema, linha, coluna, indice = None):
        self.tipoToken = tipo
        self.lexema = lexema
        self.indice = indice
        self.linha = linha
        self.coluna = coluna
    
    def toString(self):
        strTipo = str(self.tipoToken)
        if self.indice != None:
            return "<" + strTipo.split('.')[1] + "," + str(self.indice) + ">"
        else:
            return "<"+strTipo.split('.')[1]+">"
    
    def toStringTabela(self):

        return "|" + str(self.indice) + " | " + str(self.lexema) + "|";
    # Acessores.
    def getTipo(self):
        return str(self.tipoToken).split('.')[1]
    def getLexema(self):
        return self.lexema
    def getLinha(self):
        return self.linha
    def getColuna(self):
        return self.coluna