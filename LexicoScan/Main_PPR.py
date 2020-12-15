from lexico import Analisa

from LexicoScan.HashTable_Token import HashTok
from LexicoScan.TS import PPR

if __name__ == "__main__":

    try:
        # Busca o arquivo de teste na pasta "exemplos_para_analise".

        #analisador_Lex = Analisa("exemplos_para_analise/test_prof.lpd")
        #analisador_Lex = Analisa("exemplos_para_analise/exemplo.lpd")
        analisador_Lex = Analisa("exemplos_para_analise/car.lpd")
        #analisador_Lex = Analisa("exemplos_para_analise/teste_de_erros.lpd")
        analisador_Lex.analisa()

        # Gera os arquivos de Resultado na pasta "resultados_analisados".

        analisador_Lex.imprime_Tabela_Token()
        analisador_Lex.imprime_seq_Tokens()
        analisador_Lex.imprime_seq_Simb()

        print("\n Analises de Tokens Salvas no diretorio /resultados_analisados")
        # Exibindo o HashMap. Tambem pode ser visto na pasta "resultados_analisados".
        #print("Tokens: ", HashTok.hashmap)
    except:
        print("Erro Lexico Main")

    try:
        analisador_Sint = PPR("exemplos_para_analise/car.lpd")
        #analisador_Sint = Analisa_Sint("exemplos_para_analise/test_prof.lpd")
        #analisador_Sint = Analisa_Sint("exemplos_para_analise/exemplo.lpd")
        analisador_Sint.buscaToken()
        analisador_Sint.imprime_Tabela_Analise_Sintatica()

        print(" Analises Sintatica Salva no diretorio /resultados_analisados")
    except:
        print("Erro Sintatico Main")
