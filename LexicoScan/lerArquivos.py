from pathlib import Path
import sys

class Ler_Arquivos:

    def __init__ (self, nomeArquivo):
        arquivo = Path(nomeArquivo)
        self.linhasArquivo = []
        self.linha = 0
        self.coluna = 0
        self.indice = 0

        if arquivo.exists():
            arquivo = open(nomeArquivo, "r")
            self.linhasArquivo = arquivo.read().splitlines()
            arquivo.close()
        else:
            print("Não encontrado")
            sys.exit()

if __name__ == "__main__":
    leitor = Ler_Arquivos("exemplo.lpd")