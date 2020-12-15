from LexicoScan.tipoToken import TipoToken
import pickle

# Usa os atributos e os acessores da classe 'token' atravez da classe 'tipo_Token',
# para exibir tipo, lexema, linha, coluna, escopo, gets e sets.

class HashTable:

    def __init__(self):
        self.size = 256
        self.hashmap = [[] for _ in range(0, self.size)]

    def hash_func(self, chave):
        hashed_chave = hash(chave) % self.size
        return hashed_chave

    def setAtributo(self, chave, token):
        hash_chave = self.hash_func(chave)
        chave_exists = False
        slot = self.hashmap[hash_chave]
        for i, kv in enumerate(slot):
            ch, v = kv
            if chave == ch:
                chave_exists = True
                break
        if chave_exists:
            slot[i] = ((chave, token))
        else:
            slot.append((chave, token))

    def getAtributo(self, chave):
        hash_chave = self.hash_func(chave)
        slot = self.hashmap[hash_chave]
        for kv in slot:
            ch, v = kv
            if chave == ch:
                return v
            else:
                raise KeyError('Chave não existe.')

    def __setitem__(self, chave, token):
        return self.setAtributo(chave, token)

    def __getitem__(self, chave):
        return self.getAtributo(chave)

HashTok = HashTable()

HashTok.setAtributo(0, TipoToken.O_ATRIBUICAO)
HashTok.setAtributo(1, TipoToken.RES_BOOLEANO)
HashTok.setAtributo(2, TipoToken.RES_INTEIRO)
HashTok.setAtributo(3, TipoToken.RES_CHAR)
HashTok.setAtributo(4, TipoToken.RES_VERDADE)
HashTok.setAtributo(5, TipoToken.RES_FALSO)
HashTok.setAtributo(6, TipoToken.RES_PROGRAMA)
HashTok.setAtributo(7, TipoToken.RES_INICIO)
HashTok.setAtributo(8, TipoToken.RES_ESCREVA)
HashTok.setAtributo(9, TipoToken.RES_LEIA)
HashTok.setAtributo(10, TipoToken.RES_ERROS)
HashTok.setAtributo(11, TipoToken.RES_SE)
HashTok.setAtributo(12, TipoToken.RES_ENTAO)
HashTok.setAtributo(13, TipoToken.RES_SENAO)
HashTok.setAtributo(14, TipoToken.RES_ENQUANTO)
HashTok.setAtributo(15, TipoToken.RES_FUNCAO)
HashTok.setAtributo(16, TipoToken.RES_PROCEDIMENTO)
HashTok.setAtributo(17, TipoToken.RES_FACA)
HashTok.setAtributo(18, TipoToken.RES_IMPORTA)
HashTok.setAtributo(19, TipoToken.RES_HERDA)
HashTok.setAtributo(20, TipoToken.RES_INSTANCIA_DE)
HashTok.setAtributo(21, TipoToken.RES_NOVO)
HashTok.setAtributo(22, TipoToken.RES_NULO)
HashTok.setAtributo(23, TipoToken.RES_CLASSE)
HashTok.setAtributo(24, TipoToken.RES_PACOTE)
HashTok.setAtributo(25, TipoToken.RES_PRIVADO)
HashTok.setAtributo(26, TipoToken.RES_PROTEGIDO)
HashTok.setAtributo(27, TipoToken.RES_PUBLICO)
HashTok.setAtributo(28, TipoToken.RES_ABSTRATO)
HashTok.setAtributo(29, TipoToken.RES_RETORNA)
HashTok.setAtributo(30, TipoToken.RES_ESTATICO)
HashTok.setAtributo(31, TipoToken.RES_SUPERIOR)
HashTok.setAtributo(32, TipoToken.RES_DESTA)
HashTok.setAtributo(33, TipoToken.RES_VAZIO)
HashTok.setAtributo(34, TipoToken.RES_VAR_CAMPO)
HashTok.setAtributo(35, TipoToken.RES_FIM_PROGRAMA)
HashTok.setAtributo(36, TipoToken.S_VIRGULA)
HashTok.setAtributo(37, TipoToken.S_PONTO)
HashTok.setAtributo(38, TipoToken.S_PONTO_E_VIRGULA)
HashTok.setAtributo(39, TipoToken.S_ABRE_PARENTESE)
HashTok.setAtributo(40, TipoToken.S_FECHA_PARENTESE)
HashTok.setAtributo(41, TipoToken.S_ABRE_CHAVES)
HashTok.setAtributo(42, TipoToken.S_FECHA_CHAVE)
HashTok.setAtributo(43, TipoToken.S_ABRE_COLCHETE)
HashTok.setAtributo(44, TipoToken.S_FECHA_COLCHETE)
HashTok.setAtributo(45, TipoToken.O_MENOS)
HashTok.setAtributo(46, TipoToken.O_SOMA)
HashTok.setAtributo(47, TipoToken.O_MULTIPLICA)
HashTok.setAtributo(48, TipoToken.O_DIVISAO)
HashTok.setAtributo(49, TipoToken.O_IGUAL)
HashTok.setAtributo(50, TipoToken.O_ATRIBUI)
HashTok.setAtributo(51, TipoToken.O_MAIOR)
HashTok.setAtributo(52, TipoToken.O_MENOR)
HashTok.setAtributo(53, TipoToken.O_INCREMENTO)
HashTok.setAtributo(54, TipoToken.O_MENOR_IGUAL)
HashTok.setAtributo(55, TipoToken.O_MAIOR_IGUAL)
HashTok.setAtributo(56, TipoToken.O_RECEBE_E_SOMA)
HashTok.setAtributo(57, TipoToken.O_RECEBE_E_SUBTRAI)
HashTok.setAtributo(58, TipoToken.O_NAO)
HashTok.setAtributo(59, TipoToken.O_DECREMENTO)
HashTok.setAtributo(60, TipoToken.O_OU)
HashTok.setAtributo(61, TipoToken.O_E)
HashTok.setAtributo(62, TipoToken.O_DE_TIPO)
HashTok.setAtributo(63, TipoToken.O_ATRIBUI)
HashTok.setAtributo(64, TipoToken.C_VARIAVEL)
HashTok.setAtributo(65, TipoToken.C_CHAR_CLASSE)
HashTok.setAtributo(66, TipoToken.C_CADEIA_CHAR)
HashTok.setAtributo(67, TipoToken.C_INTEIRO_CLASSE)
HashTok.setAtributo(68, TipoToken.C_FLUTUANTE_CLASSE)

    #Salvando o Hash em arquivo
file1 = "resultados_analisados/Hash_TS.txt"
file = open(file1, 'wb')
pickle.dump(HashTok, file)
#file = open(file1, 'rb')
#new_grades = pickle.load(file)