from lexico import Analisa

from LexicoScan.PPR import PPR

if __name__ == "__main__":

    try:
        # Busca o arquivo de teste na pasta "exemplos_para_analise".
        analisador_Lex = Analisa("exemplos_para_analise/test_prof.lpd")
        analisador_Lex.analisa()

        # Gera os arquivos de Resultado na pasta "resultados_analisados".
        analisador_Lex.imprime_Tabela_Token()
        analisador_Lex.imprime_seq_Tokens()
        analisador_Lex.imprime_seq_Simb()
        print("\n*** Analises Lexica Salvas no diretorio /resultados_analisados ***")

    except:
        print("Erro Lexico Main")

    try:
        # Analise Sintatica e Semantica
        ppr = PPR("exemplos_para_analise/test_prof.lpd")
        ppr.buscaToken()
        ppr.parse()
        ppr.imprime_Tabela_Analise_Sintatica() # Cria arquivo de resultados Sintaticos e Semanticos.

        print("*** Codigo Intermediario Gerado e Salvo em /resultados_analisados ***")
        print("*** Analises Sintatica Salva no diretorio  /resultados_analisados ***")

    except:
        print("Erro Sintatico Main")
