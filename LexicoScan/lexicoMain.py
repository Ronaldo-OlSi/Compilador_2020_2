from lexico import Analisa

if __name__ == "__main__":

    #Busca o arquivo de teste.
    analisador_Lex = Analisa("exemplos/exemplo.lpd")
    analisador_Lex.analisa()
    analisador_Lex.imprime_seq_Tokens()
    analisador_Lex.imprime_seq_Simb()
    analisador_Lex.imprime_Tabela_Token()
