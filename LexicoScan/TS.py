from token import Token
from tipoToken import TipoToken
from erro_rastreio import Erro_rastreio
from lerArquivos import Ler_Arquivos
from criaTabela_Resultado import organizaTabela

class Analisa_Sint:

    # Aponta Erros sintaticos
    def analisa(self):

        # Testa os caracteres em suas posiçoes.
        ind_linha = 0
        while (ind_linha < len(self.arqLinhas)):
            ind_coluna = 0
            while (ind_coluna < len(self.arqLinhas[ind_linha])):
                caractere = self.arqLinhas[ind_linha][ind_coluna]

                # Testa se o caractere é inválido.
                if caractere not in self.caract_Linguagem:
                    error = Erro_rastreio(ind_linha, ind_coluna, "lexico", "caractere não pertence a linguagem")
                ind_coluna += 1
            ind_linha += 1

