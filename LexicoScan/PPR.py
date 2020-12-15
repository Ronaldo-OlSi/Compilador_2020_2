from token import Token
from tipoToken import TipoToken
from erro_rastreio import Erro_rastreio
from lerArquivos import Ler_Arquivos
from criaTabela_Resultado import organizaTabela
from abc import abstractmethod

class Parser(object): # Classe abstrata

    def __init__(self, ts, lexeco, token):  # Construtor abstrato.
        self.ts = ts
        self.lexer = lexeco
        self.token = token

    @abstractmethod
    def busca_Token(self):
        pass

    @abstractmethod
    def parse(self):
        pass

    @abstractmethod
    def erro(self):
        linha = 1
        coluna = 0

        print("erro, linha" + linha + "coluna" + coluna )


class PPR:


    def parse(self):

        try:
            # Busca o nome do programa
            ind_linha = 0
            while (ind_linha < 1):

                ind_coluna = 0
                while (ind_coluna < len(self.arqLinhas[ind_linha])):

                    print("\n      --- Nome do Programa '", self.sequencia_Simbolos[0], "'---\n")

                    ind_linha = 1
                    break
        except:
            print("Erro na busca pelo nome do programa")

        # Busca Variaveis repetidas
        try:
            words = self.arqLinhas
            encontradas = set()
            dups = set()
            ind_linha = 0
            for word in words:
                ind_linha += 1
                if word in encontradas:
                    if word not in dups:
                        if word == '':  # ignorara os espaços em branco repetidos!
                            pass
                            dups.add(word)
                        else:
                            print("Variavel em duplicadade na linha", ind_linha, ", sentença =", word, "\n")
                else:
                    encontradas.add(word)
        except:
            print("Erro Sintatico. Variavel em duplicadade")

        # Percorre todos os caracteres para a analise de balanceamento
        ind_linha = 0
        while (ind_linha < len(self.arqLinhas)):
            ind_coluna = 0
            while (ind_coluna < len(self.arqLinhas[ind_linha])):

                # Salva a posição do caractere e seu valor
                caractere = self.arqLinhas[ind_linha][ind_coluna]
                ind_coluna += 1
            ind_linha += 1

            exp = str(caractere)
            abertos = 0
            for c in exp:
                if c == '(':
                    abertos += 1
                elif c == ')':
                    abertos -= 1
                    if abertos < 0:
                        break
                if abertos == 0:
                    pass
                else:
                    print('Erro, Parenteses desbalanceados. linha', ind_linha)

    def buscaToken(self):  # Busca tokens e suas posiçoes.

        ind_linha = 0
        while (ind_linha < len(self.arqLinhas)):
            ind_coluna = 0
            while (ind_coluna < len(self.arqLinhas[ind_linha])):
                # Salva a posição do caractere e seu valor
                caractere = self.arqLinhas[ind_linha][ind_coluna]

                # Testa se é um tipo de comentario ex: //bla bla bla, comentario...
                if caractere == '/':
                    if self.indice_Valid_Col(ind_linha, ind_coluna + 1):
                        chr1 = self.arqLinhas[ind_linha][ind_coluna + 1]

                        if chr1 == '/':
                            ind_linha += 1
                            ind_coluna = 0
                            continue

                # Obs: Fazer esse tipo de comentario com: enquanto não encontrar "!}" ignorar caractere...
                if caractere == '{':
                    if self.indice_Valid_Col(ind_linha, ind_coluna + 1):
                        chr1 = self.arqLinhas[ind_linha][ind_coluna + 1]
                        if chr1 == '{':
                            ind_linha += 1
                            ind_coluna = 0
                            continue

                if caractere == '{':
                    if self.indice_Valid_Col(ind_linha, ind_coluna + 1):
                        chr1 = self.arqLinhas[ind_linha][ind_coluna + 1]
                        if chr1 == '"':
                            ind_linha += 1
                            ind_coluna = 0
                            continue

                # Testa se abre e fecha parenteses corretamente
                try:
                    if caractere == '(':
                        indiceIniColuna = ind_coluna  # guarda os indices iniciais
                        indiceIniLinha = ind_linha

                        # Se o proximo indice nao for válido chegou ao fim de linha,
                        # então vá para a proxima linha
                        if self.indice_Valid_Col(ind_linha, ind_coluna + 1):
                            ind_coluna += 1
                            chr = self.arqLinhas[ind_linha][ind_coluna + 1]
                        else:
                            ind_linha += 1
                            ind_coluna = 0
                            chr = self.arqLinhas[ind_linha][ind_coluna]

                        # Enquanto não encontar um fecha parentese percorra
                        while chr != ')':
                            # Se indice é valido, percorre no arquivo
                            # Se indice não é valido, pule essa linha
                            if self.indice_Valid_Col(ind_linha, ind_coluna):
                                chr = self.arqLinhas[ind_linha][ind_coluna]
                            else:
                                ind_coluna = 0
                                ind_linha += 1
                                chr = self.arqLinhas[ind_linha][ind_coluna]
                            ind_coluna += 1
                        # Inicio da composição do lexema
                        # salva indices finais
                        indiceFinalColuna = ind_coluna
                        indiceFinalLinha = ind_linha

                        # Se o indice final é igual ao inicial, a estrutura está em uma unica linha
                        if indiceIniLinha == indiceFinalLinha:
                            lexema = self.arqLinhas[indiceFinalLinha][indiceIniColuna: indiceFinalColuna]
                            self.cria_Token(self.literal["cadeia_classe"], lexema, indiceFinalLinha, indiceFinalColuna)
                            continue

                        error = Erro_rastreio(ind_linha, ind_coluna, "sintatico", "Não fechamento de Parenteses.")

                    # Se neste ponto for 'true' é uma estrutura multi-linhas.
                    if caractere == '\'':
                        if self.indice_Valid_Col(ind_linha, ind_coluna + 1):
                            chr1 = self.arqLinhas[ind_linha][ind_coluna + 1]
                            if chr1 == '\\':
                                if self.indice_Valid_Col(ind_linha, ind_coluna + 2):
                                    chr2 = self.arqLinhas[ind_linha][ind_coluna + 2]
                                    if chr2 == 'n' or chr2 == 'r' or chr2 == 't' or chr2 == 'b' or chr2 == 'f' or chr2 == '\'' or chr2 == '\"' or chr2 == '\\':
                                        if self.indice_Valid_Col(ind_linha, ind_coluna + 3) and self.arqLinhas[ind_linha][
                                            ind_coluna + 3] == '\'':
                                            self.cria_Token(self.literal["char_classe"], caractere + chr1 + chr2, ind_linha,
                                                            ind_coluna + 2)
                                            ind_coluna += 3
                                            continue

                                        else:
                                            error = Erro_rastreio(ind_linha, ind_coluna, "sintatico", "")
                                    else:
                                        error = Erro_rastreio(ind_linha, ind_coluna, "sintatico", "")
                                else:
                                    error = Erro_rastreio(ind_linha, ind_coluna, "sintatico",
                                                          "")
                            elif chr1 != '\'' and chr1 != '\\':
                                if self.indice_Valid_Col(ind_linha, ind_coluna + 2):
                                    chr2 = self.arqLinhas[ind_linha][ind_coluna + 2]
                                    if chr2 == '\'':
                                        self.cria_Token(self.literal["char_classe"], caractere + chr1 + chr2, ind_linha,
                                                        ind_coluna + 1)
                                        ind_coluna += 2
                                        continue

                                    else:
                                        error = Erro_rastreio(ind_linha, ind_coluna, "sintatico", "não e um char classe")
                            else:
                                error = Erro_rastreio(ind_linha, ind_coluna, "sintatico", "não e um char classe")
                        else:
                            error = Erro_rastreio(ind_linha, ind_coluna, "sintatico", "não e um char classe, fim de linha")
                except:
                    print("Erro sintatico, fechamento de 'Parenteses'")
                    error = Erro_rastreio(ind_linha - 2, ind_coluna, "sintatico", "Não fechamento de Parenteses.")
                    break

                # Testa se é uma string classe, Verifica se o primeiro char tem  aspas duplas
                try:
                    if caractere == '"':
                        indiceIniColuna = ind_coluna  # guarda os indices iniciais
                        indiceIniLinha = ind_linha

                        # Se o proximo indice nao for válido chegou ao fim de linha,
                        # então vá para a proxima linha
                        if self.indice_Valid_Col(ind_linha, ind_coluna + 1):
                            ind_coluna += 1
                            chr = self.arqLinhas[ind_linha][ind_coluna + 1]
                        else:
                            ind_linha += 1
                            ind_coluna = 0
                            chr = self.arqLinhas[ind_linha][ind_coluna]

                        # Enquanto não encontar outras aspas duplas percorra
                        while chr != '"':
                            # Se indice é valido, percorre no arquivo
                            # Se indice não é valido, pule essa linha
                            if self.indice_Valid_Col(ind_linha, ind_coluna):
                                chr = self.arqLinhas[ind_linha][ind_coluna]
                            else:
                                ind_coluna = 0
                                ind_linha += 1
                                chr = self.arqLinhas[ind_linha][ind_coluna]
                            ind_coluna += 1
                        # Inicio da composição do lexema
                        # salva indices finais
                        indiceFinalColuna = ind_coluna
                        indiceFinalLinha = ind_linha

                        # Se o indice final é igual ao inicial, a string está em uma unica linha
                        if indiceIniLinha == indiceFinalLinha:
                            lexema = self.arqLinhas[indiceFinalLinha][indiceIniColuna: indiceFinalColuna]
                            self.cria_Token(self.literal["cadeia_classe"], lexema, indiceFinalLinha, indiceFinalColuna)
                            continue

                        error = Erro_rastreio(ind_linha, ind_coluna, "sintatico", "Quebra de linha dentro de uma string")

                     # Se neste ponto for 'true' é uma string multi-linhas.
                    if caractere == '\'':
                        if self.indice_Valid_Col(ind_linha, ind_coluna + 1):
                            chr1 = self.arqLinhas[ind_linha][ind_coluna + 1]
                            if chr1 == '\\':
                                if self.indice_Valid_Col(ind_linha, ind_coluna + 2):
                                    chr2 = self.arqLinhas[ind_linha][ind_coluna + 2]
                                    if chr2 == 'n' or chr2 == 'r' or chr2 == 't' or chr2 == 'b' or chr2 == 'f' or chr2 == '\'' or chr2 == '\"' or chr2 == '\\':
                                        if self.indice_Valid_Col(ind_linha, ind_coluna + 3) and self.arqLinhas[ind_linha][
                                            ind_coluna + 3] == '\'':
                                            self.cria_Token(self.literal["char_classe"], caractere + chr1 + chr2, ind_linha,
                                                            ind_coluna + 2)
                                            ind_coluna += 3
                                            continue

                                        else:  # chr3 é diferente de aspas simples (')
                                            error = Erro_rastreio(ind_linha, ind_coluna, "sintatico", "não e char classe")

                                    else:  # chr2 é diferente '\n' '\r' '\t' '\b' '\f' '\’' '\"' '\\'
                                        error = Erro_rastreio(ind_linha, ind_coluna, "sintatico", "não e char classe")
                                else:
                                    error = Erro_rastreio(ind_linha, ind_coluna, "sintatico",
                                                          "não e char classe, fim de linha")
                            elif chr1 != '\'' and chr1 != '\\':
                                if self.indice_Valid_Col(ind_linha, ind_coluna + 2):
                                    chr2 = self.arqLinhas[ind_linha][ind_coluna + 2]
                                    if chr2 == '\'':
                                        self.cria_Token(self.literal["char_classe"], caractere + chr1 + chr2, ind_linha,
                                                        ind_coluna + 1)
                                        ind_coluna += 2
                                        continue

                                    else:  # chr2 é diferente de aspas simples (')
                                        error = Erro_rastreio(ind_linha, ind_coluna, "sintatico", "não e um char classe")

                            else:  # chr1 for igual a aspas simples (') ou igual uma barra(\)
                                error = Erro_rastreio(ind_linha, ind_coluna, "sintatico", "não e um char classe")
                        else:
                            error = Erro_rastreio(ind_linha, ind_coluna, "sintatico", "não e um char classe, fim de linha")
                except:
                    print("Erro sintatico, fechamento de 'Aspas'")
                    break

                try:
                    # Analisando expressoes matematicas
                    list_expr = []
                    if caractere == '+':
                        op1 = caractere
                        num1 = caractere = self.arqLinhas[ind_linha][ind_coluna -2]
                        num2 = caractere = self.arqLinhas[ind_linha][ind_coluna +2]
                        res1 = int(num1) + int(num2)
                        list_expr = [num1, op1, num2, "=", res1]

                    if caractere == '-':
                        op2 = caractere
                        num3 = caractere = self.arqLinhas[ind_linha][ind_coluna - 2]
                        num4 = caractere = self.arqLinhas[ind_linha][ind_coluna + 2]
                        res2 = int(num3) - int(num4)
                        list_expr = [num3, op2, num4, "=", res2]

                    if caractere == '/':
                        op3 = caractere
                        num5 = caractere = self.arqLinhas[ind_linha][ind_coluna - 2]
                        num6 = caractere = self.arqLinhas[ind_linha][ind_coluna + 2]
                        res3 = int(num5) / int(num6)
                        list_expr = [num5, op3, num6, "=", res3]

                    if caractere == '*':
                        op4 = caractere
                        num7 = caractere = self.arqLinhas[ind_linha][ind_coluna - 2]
                        num8 = caractere = self.arqLinhas[ind_linha][ind_coluna + 2]
                        res4 = int(num7) * int(num8)
                        list_expr = [num7, op4, num8, "=", res4]

                    '''if list_expr != []:
                        sem_esp = list_expr
                        print(sem_esp)'''

                    # Salvando em arquivo

                    if list_expr != []:
                        sem_esp = list_expr
                        f = open("resultados_analisados/lista_expressao.txt", "a")
                        f.write(str(sem_esp))
                        f.write(str("\n"))
                        f.close()


                        for c in range(len(sem_esp)):
                                if sem_esp[c] == 1 or sem_esp[c] == 2 or sem_esp[c] == 3\
                                        or sem_esp[c] == 4 or sem_esp[c] == 5 or sem_esp[c] == 6\
                                        or sem_esp[c] == 7 or sem_esp[c] == 8 or sem_esp[c] == 9\
                                        or sem_esp[c] == 0 or sem_esp[c] == '1' or sem_esp[c] == '2'\
                                        or sem_esp[c] == '3' or sem_esp[c] == '4' or sem_esp[c] == '5' \
                                        or sem_esp[c] == '6' or sem_esp[c] == '7' or sem_esp[c] == '8' \
                                        or sem_esp[c] == '9' or sem_esp[c] == '0':pass

                                '''print("%", c + 1, '= alloca i32, align 4')
                                print("store i32", sem_esp[c], ', i32*', c + 1, ', align 4')'''


                                codigo = "%", c + 1, '= alloca i32, align 4'
                                f = open("resultados_analisados/codigo.txt", "a")
                                f.write(str(codigo))
                                f.write(str("\n"))
                                f.close()

                                codigo = "store i32", sem_esp[c], ', i32*', c + 1, ', align 4'
                                f = open("resultados_analisados/codigo.txt", "a")
                                f.write(str(codigo))
                                f.write(str("\n"))
                                f.close()


                except:
                    print("Erro semantico, fechamento de 'expressão aritimetica'")
                    error = Erro_rastreio(ind_linha - 2, ind_coluna, "semantico", "expressao.")
                    break

                # Testa se abre e fecha colchetes corretamente
                try:
                    if caractere == '[':
                        indiceIniColuna = ind_coluna  # guarda os indices iniciais
                        indiceIniLinha = ind_linha

                        # Se o proximo indice não for válido chegou ao fim de linha,
                        # então vá para a proxima linha
                        if self.indice_Valid_Col(ind_linha, ind_coluna + 1):
                            ind_coluna += 1
                            chr = self.arqLinhas[ind_linha][ind_coluna + 1]
                        else:
                            ind_linha += 1
                            ind_coluna = 0
                            chr = self.arqLinhas[ind_linha][ind_coluna]

                        # Enquanto não encontar um fecha colchete percorra
                        while chr != ']':
                            # Se indice é valido, percorre no arquivo
                            # Se indice não é valido, pule essa linha
                            if self.indice_Valid_Col(ind_linha, ind_coluna):
                                chr = self.arqLinhas[ind_linha][ind_coluna]
                            else:
                                ind_coluna = 0
                                ind_linha += 1
                                chr = self.arqLinhas[ind_linha][ind_coluna]
                            ind_coluna += 1
                        # Inicio da composição do lexema
                        # salva indices finais
                        indiceFinalColuna = ind_coluna
                        indiceFinalLinha = ind_linha

                        # Se o indice final é igual ao inicial, a estrutura está em uma unica linha
                        if indiceIniLinha == indiceFinalLinha:
                            lexema = self.arqLinhas[indiceFinalLinha][indiceIniColuna: indiceFinalColuna]
                            self.cria_Token(self.literal["cadeia_classe"], lexema, indiceFinalLinha,
                                            indiceFinalColuna)
                            continue

                        error = Erro_rastreio(ind_linha, ind_coluna, "sintatico", "Não fechamento de colchete.")

                    # Se neste ponto for 'true' é uma estrutura multi-linhas.
                    if caractere == '\'':
                        if self.indice_Valid_Col(ind_linha, ind_coluna + 1):
                            chr1 = self.arqLinhas[ind_linha][ind_coluna + 1]
                            if chr1 == '\\':
                                if self.indice_Valid_Col(ind_linha, ind_coluna + 2):
                                    chr2 = self.arqLinhas[ind_linha][ind_coluna + 2]
                                    if chr2 == 'n' or chr2 == 'r' or chr2 == 't' or chr2 == 'b' or chr2 == 'f' or chr2 == '\'' or chr2 == '\"' or chr2 == '\\':
                                        if self.indice_Valid_Col(ind_linha, ind_coluna + 3) and \
                                                self.arqLinhas[ind_linha][
                                                    ind_coluna + 3] == '\'':
                                            self.cria_Token(self.literal["char_classe"], caractere + chr1 + chr2,
                                                            ind_linha,
                                                            ind_coluna + 2)
                                            ind_coluna += 3
                                            continue

                                        else:
                                            error = Erro_rastreio(ind_linha, ind_coluna, "sintatico", "")
                                    else:
                                        error = Erro_rastreio(ind_linha, ind_coluna, "sintatico", "")
                                else:
                                    error = Erro_rastreio(ind_linha, ind_coluna, "sintatico",
                                                          "")
                            elif chr1 != '\'' and chr1 != '\\':
                                if self.indice_Valid_Col(ind_linha, ind_coluna + 2):
                                    chr2 = self.arqLinhas[ind_linha][ind_coluna + 2]
                                    if chr2 == '\'':
                                        self.cria_Token(self.literal["char_classe"], caractere + chr1 + chr2,
                                                        ind_linha,
                                                        ind_coluna + 1)
                                        ind_coluna += 2
                                        continue

                                    else:
                                        error = Erro_rastreio(ind_linha, ind_coluna, "sintatico",
                                                              "não e um char classe")
                            else:
                                error = Erro_rastreio(ind_linha, ind_coluna, "sintatico", "não e um char classe")
                        else:
                            error = Erro_rastreio(ind_linha, ind_coluna, "sintatico",
                                                  "não e um char classe, fim de linha")
                except:
                    print("Erro sintatico, fechamento de 'colchetes'")
                    error = Erro_rastreio(ind_linha - 2, ind_coluna, "semantico", "expressao.")
                    break

                # Testa se abre e fecha chaves corretamente.
                try:
                    if caractere == '{':
                        indiceIniColuna = ind_coluna  # guarda os indices iniciais
                        indiceIniLinha = ind_linha

                        # Se o proximo indice não for válido chegou ao fim de linha,
                        # então vá para a proxima linha
                        if self.indice_Valid_Col(ind_linha, ind_coluna + 1):
                            ind_coluna += 1
                            chr = self.arqLinhas[ind_linha][ind_coluna + 1]
                        else:
                            ind_linha += 1
                            ind_coluna = 0
                            chr = self.arqLinhas[ind_linha][ind_coluna]

                        # Enquanto não encontar um fecha chave percorra
                        while chr != '}':
                            # Se indice é valido, percorre no arquivo
                            # Se indice não é valido, pule essa linha
                            if self.indice_Valid_Col(ind_linha, ind_coluna):
                                chr = self.arqLinhas[ind_linha][ind_coluna]
                            else:
                                ind_coluna = 0
                                ind_linha += 1
                                chr = self.arqLinhas[ind_linha][ind_coluna]
                            ind_coluna += 1
                        # Inicio da composição do lexema
                        # salva indices finais
                        indiceFinalColuna = ind_coluna
                        indiceFinalLinha = ind_linha

                        # Se o indice final é igual ao inicial, a estrutura está em uma unica linha
                        if indiceIniLinha == indiceFinalLinha:
                            lexema = self.arqLinhas[indiceFinalLinha][indiceIniColuna: indiceFinalColuna]
                            self.cria_Token(self.literal["cadeia_classe"], lexema, indiceFinalLinha,
                                            indiceFinalColuna)
                            continue

                        error = Erro_rastreio(ind_linha, ind_coluna, "sintatico", "Não fechamento de chaves.")

                    # Se neste ponto for 'true' é uma estrutura multi-linhas.
                    if caractere == '\'':
                        if self.indice_Valid_Col(ind_linha, ind_coluna + 1):
                            chr1 = self.arqLinhas[ind_linha][ind_coluna + 1]
                            if chr1 == '\\':
                                if self.indice_Valid_Col(ind_linha, ind_coluna + 2):
                                    chr2 = self.arqLinhas[ind_linha][ind_coluna + 2]
                                    if chr2 == 'n' or chr2 == 'r' or chr2 == 't' or chr2 == 'b' or chr2 == 'f' or chr2 == '\'' or chr2 == '\"' or chr2 == '\\':
                                        if self.indice_Valid_Col(ind_linha, ind_coluna + 3) and \
                                                self.arqLinhas[ind_linha][
                                                    ind_coluna + 3] == '\'':
                                            self.cria_Token(self.literal["char_classe"], caractere + chr1 + chr2,
                                                            ind_linha,
                                                            ind_coluna + 2)
                                            ind_coluna += 3
                                            continue

                                        else:
                                            error = Erro_rastreio(ind_linha, ind_coluna, "sintatico", "")
                                    else:
                                        error = Erro_rastreio(ind_linha, ind_coluna, "sintatico", "")
                                else:
                                    error = Erro_rastreio(ind_linha, ind_coluna, "sintatico",
                                                          "")
                            elif chr1 != '\'' and chr1 != '\\':
                                if self.indice_Valid_Col(ind_linha, ind_coluna + 2):
                                    chr2 = self.arqLinhas[ind_linha][ind_coluna + 2]
                                    if chr2 == '\'':
                                        self.cria_Token(self.literal["Inteiro_classe"], caractere + chr1 + chr2,
                                                        ind_linha,
                                                        ind_coluna + 1)
                                        ind_coluna += 2
                                        continue

                                    else:
                                        error = Erro_rastreio(ind_linha, ind_coluna, "sintatico",
                                                              "não e um char classe")
                            else:
                                error = Erro_rastreio(ind_linha, ind_coluna, "sintatico", "não e um char classe")
                        else:
                            error = Erro_rastreio(ind_linha, ind_coluna, "sintatico",
                                                  "não e um char classe, fim de linha")
                except:
                    print("Erro sintatico, fechamento de 'chaves'")
                    error = Erro_rastreio(ind_linha - 2, ind_coluna, "semantico", "expressao.")
                    break

                # Testa se encontrou um identificador
                try:
                    if self.Char_Identificador(caractere):
                        ini_Lexema = ind_coluna

                        while ((self.Char_Identificador(caractere)) or (self.numero_Ident(caractere)) or (
                                caractere == '_') or (caractere == '$')):
                            ind_coluna += 1
                            caractere = self.arqLinhas[ind_linha][ind_coluna]

                        lexema = self.arqLinhas[ind_linha][ini_Lexema: (ind_coluna)]
                        if lexema not in self.reservada:
                            self.cria_Token(self.literal["variavel_classe"], lexema, ind_linha, ini_Lexema)
                            continue
                        else:
                            self.cria_Token(self.reservada[lexema], lexema, ind_linha, ini_Lexema)
                            continue
                except:
                    print("Erro Sintatico de indentificador")
                    error = Erro_rastreio(ind_linha, ind_coluna, "sintatico", "")


                # Testa se é um numero e adiciona o tipo
                try:
                    if self.numero_Ident(caractere):
                        ini_Lexema = ind_coluna
                        if caractere == "0":
                            if self.indice_Valid_Col(ind_linha, ind_coluna + 1):
                                chr1 = self.arqLinhas[ind_linha][ind_coluna + 1]

                                if ((chr1 == " ") or (self.operador_Ident(caractere, chr1)) or (chr1 in self.separador) or (
                                        chr1 == "\t") and (chr1 == "\n")):
                                    self.cria_Token(self.literal["Inteiro_classe"], caractere, ind_linha, ini_Lexema)
                                    ind_coluna += 1
                                    continue
                                else:  # Se proximo ao zero  nao houver caracter valido
                                    error = Erro_rastreio(ind_linha, ind_coluna, "sintatico", "Numero Invalido")
                            else:
                                self.cria_Token(self.literal["Inteiro_classe"], caractere, ind_linha, ini_Lexema)
                        else:
                            while self.numero_Ident(caractere):
                                ind_coluna += 1
                                if self.indice_Valid_Col(ind_linha, ind_coluna):
                                    caractere = self.arqLinhas[ind_linha][ind_coluna]
                                else:
                                    caractere = None
                            lexema = self.arqLinhas[ind_linha][ini_Lexema:ind_coluna]

                            self.cria_Token(self.literal["Inteiro_classe"], lexema, ind_linha, ini_Lexema)
                            #print(lexema)


                            continue
                except:
                    print("Erro Sintatico em teste de numeros")
                    error = Erro_rastreio(ind_linha, ind_coluna, "sintatico", "")

                # Testa se o caractere é um operador
                oper_Dup = False

                if caractere in self.operador:
                    oper_Uni = True

                    if self.indice_Valid_Col(ind_linha, ind_coluna + 1):
                        chr1 = self.arqLinhas[ind_linha][ind_coluna + 1]
                        if caractere == '=':
                            if chr1 == '=':
                                oper_Dup = True
                                oper_Uni = False
                        elif caractere == '+':
                            if chr1 == '+':
                                oper_Dup = True
                                oper_Uni = False
                            elif chr1 == '=':
                                oper_Dup = True
                                oper_Uni = False
                        elif caractere == '&':
                            if chr1 == '&':
                                oper_Dup = True
                                oper_Uni = False
                        elif caractere == '<':
                            if chr1 == '=':
                                oper_Dup = True
                                oper_Uni = False
                        elif caractere == '-':
                            if chr1 == '-':
                                oper_Dup = True
                                oper_Uni = False

                        # Criando os tokens do operador.
                        try:
                            if oper_Uni:
                                self.cria_Token(self.operador[caractere], caractere, ind_linha, ind_coluna)
                                ind_coluna += 1
                                continue
                            elif oper_Dup:
                                self.cria_Token(self.operador[caractere + chr1], caractere + chr1, ind_linha,
                                                ind_coluna)
                                ind_coluna += 2
                                continue
                        except:
                            ind_linha += 1
                            print("Erro de Operador na linha", ind_linha, "\nCaracter = ", caractere)

                # testa se o caractere é um separador.
                if caractere in self.separador:
                    self.cria_Token(self.separador[caractere], caractere, ind_linha, ind_coluna)
                    ind_coluna += 1
                    continue

                # Testa se o caractere é inválido.
                if caractere not in self.caract_Linguagem:
                    error = Erro_rastreio(ind_linha, ind_coluna, "sintatico", "Caractere não pertence a linguagem")
                    #print("Erro sintatico, caractere não pertence a linguagem")
                ind_coluna += 1

            ind_linha += 1

    def Char_Identificador(self, c):
        if ((ord('a') <= ord(c)) and (ord(c) <= ord('z'))) or (
                (ord('A') <= ord(c)) and (ord(c) <= ord('Z'))) or c == '_' or c == '\$':
            return True
        else:
            return False

    def numero_Ident(self, c):
        return c.isdigit()

    def operador_Ident(self, chr, chr1):
        if chr == '=':
            if chr1 == '=':
                return True
        elif chr == '+':
            if chr1 == '+':
                return True
        elif chr == '&':
            if chr1 == '&':
                return True
        elif chr == '<':
            if chr1 == '=':
                return True
        elif chr == '-':
            if chr1 == '-':
                return True
        elif chr == '+':
            if chr1 == '=':
                return True

        elif chr in self.operador:
            return True
        else:
            return False

    def lista_De_Caracteres(self):
        list = []
        for i in range(ord('a'), ord('z') + 1):
            list.append(chr(i))
        for i in range(ord('A'), ord('Z') + 1):
            list.append(chr(i))
        for i in range(0, 10):
            list.append(i)
        for operador in self.operador:
            list.append(operador)
        for separador in self.separador:
            list.append(separador)
        especiais = ['_', '$', '\n', '\r', '\t', '\b', '\f', '\'', '"', '\\', ' ']
        for especial in especiais:
            list.append(especial)
        return list

    def indice_Valid_Col(self, ind_Lin, ind_Col):
        if ind_Col < len(self.arqLinhas[ind_Lin]):
            return True
        else:
            return False

    def __init__(self, arqEntrada):

        self.arquivo = Ler_Arquivos(arqEntrada)
        self.arqLinhas = self.arquivo.linhasArquivo
        self.sequencia_Tokens = []
        self.sequencia_Simbolos = {}

        self.operador = {"=": TipoToken.O_ATRIBUI, "==": TipoToken.O_IGUAL, ">": TipoToken.O_MAIOR,
                         "++": TipoToken.O_INCREMENTO, "<=": TipoToken.O_MENOR_IGUAL, "!": TipoToken.O_NAO,
                         "-": TipoToken.O_MENOS, "--": TipoToken.O_DECREMENTO, "+": TipoToken.O_SOMA,
                         "+=": TipoToken.O_RECEBE_E_SOMA, "*": TipoToken.O_MULTIPLICA, "?": TipoToken.O_OU,
                         "&": TipoToken.O_E,
                         "<": TipoToken.O_MENOR, ">=": TipoToken.O_MAIOR_IGUAL, "-=": TipoToken.O_RECEBE_E_SUBTRAI}
        self.separador = {",": TipoToken.S_VIRGULA, ".": TipoToken.S_PONTO, "[": TipoToken.S_ABRE_COLCHETE,
                          "{": TipoToken.S_ABRE_CHAVES, "(": TipoToken.S_ABRE_PARENTESE,
                          ")": TipoToken.S_FECHA_PARENTESE, "}": TipoToken.S_FECHA_CHAVE,
                          "]": TipoToken.S_FECHA_COLCHETE, ";": TipoToken.S_PONTO_E_VIRGULA, "/": TipoToken.O_DIVISAO,
                          ":": TipoToken.O_DE_TIPO}
        self.reservada = {"abstrato": TipoToken.RES_ABSTRATO, "booleano": TipoToken.RES_BOOLEANO,
                          "char": TipoToken.RES_CHAR, "classe": TipoToken.RES_CLASSE, "entao": TipoToken.RES_ENTAO,
                          "herda_de": TipoToken.RES_HERDA, "falso": TipoToken.RES_FALSO,
                          "importa": TipoToken.RES_IMPORTA, "se": TipoToken.RES_SE,
                          "instancia_de": TipoToken.RES_INSTANCIA_DE,
                          "inteiro": TipoToken.RES_INTEIRO, "novo": TipoToken.RES_NOVO, "nulo": TipoToken.RES_NULO,
                          "pacote": TipoToken.RES_PACOTE, "privado": TipoToken.RES_PRIVADO,
                          "protegido": TipoToken.RES_PROTEGIDO, "publico": TipoToken.RES_PUBLICO,
                          "retorna": TipoToken.RES_RETORNA, "estatico": TipoToken.RES_ESTATICO,
                          "superior": TipoToken.RES_SUPERIOR,
                          ":=": TipoToken.O_ATRIBUICAO, "desta": TipoToken.RES_DESTA,
                          "verdadeiro": TipoToken.RES_VERDADE, "vazio": TipoToken.RES_VAZIO,
                          "enquanto": TipoToken.RES_ENQUANTO, "funcao": TipoToken.RES_FUNCAO,
                          "procedimento": TipoToken.RES_PROCEDIMENTO, "programa": TipoToken.RES_PROGRAMA,
                          "inicio": TipoToken.RES_INICIO, "escreva": TipoToken.RES_ESCREVA,
                          "erros": TipoToken.RES_ERROS, "var": TipoToken.RES_VAR_CAMPO,
                          "fim": TipoToken.RES_FIM_PROGRAMA, "faca": TipoToken.RES_FACA, "senao": TipoToken.RES_SENAO,
                          "leia": TipoToken.RES_LEIA, "esc": TipoToken.RES_ESCOPO}
        self.literal = {"Inteiro_classe": TipoToken.C_INTEIRO_CLASSE, "char_classe": TipoToken.C_CHAR_CLASSE,
                        "cadeia_classe": TipoToken.C_CADEIA_CHAR, "variavel_classe": TipoToken.C_VARIAVEL,
                        "Flutuante_classe": TipoToken.C_FLUTUANTE_CLASSE}
        self.caract_Linguagem = self.lista_De_Caracteres()

        self.comentario = False
        self.string = False

    def separador_Token(self, char):
        try:
            if str(TipoToken[char].value[1] == "separador"):
                return True
        except:
            return False

    def operador(self, char):
        try:
            if str(TipoToken[char].value[1] == "operador"):
                return True
        except:
            return False


    def cria_Token(self, tipoToken, lexema, linha, coluna):

        # Se é um desses tipos validos, será registrado na tabela de simbolos.
        if tipoToken == self.literal["Inteiro_classe"] or tipoToken == self.literal["char_classe"] or tipoToken == \
                self.literal["cadeia_classe"] or tipoToken == self.literal["variavel_classe"] or tipoToken == \
                self.literal["Flutuante_classe"]:

            # Se o lexema não existir na tabela, insere ele.
            if lexema not in self.sequencia_Simbolos.values():

                # Insere o token na tabela de simbolos, e adiciona no fluxo de tokens
                index = len(self.sequencia_Simbolos)
                self.sequencia_Simbolos[index] = lexema
                token = Token(tipoToken, lexema, linha, coluna, index)
                self.sequencia_Tokens.append(token)
                return
            else:
                # Se o token já existe, então ve como é o indice dele para inserir no fluxo de tokens

                # Obs: Tem que fazer melhor!!!.
                index = [chave for chave in self.sequencia_Simbolos if self.sequencia_Simbolos[chave] == lexema][0]
                token = Token(tipoToken, lexema, linha, coluna, index)
                self.sequencia_Tokens.append(token)
                return
        else:
            # Se o lexema não for de um tipo que requer um "Tipo", então inserir no fluxo de tokens
            token = Token(tipoToken, lexema, linha, coluna)
            self.sequencia_Tokens.append(token)
            return

    def imprime_Tabela_Analise_Sintatica(self):

        lista_Tokens = open("resultados_analisados/lista__Analise_Sintatica", 'w')
        t = organizaTabela(['Lexema', 'Lin', 'Col', 'Status Sintatico'])
        for token in self.sequencia_Tokens:
            t.add_row([str(token.getLexema()), str(token.getLinha()), str(token.getColuna()), str("Sint. Ok!")])
        lista_Tokens.write(str(t))
        lista_Tokens.close()