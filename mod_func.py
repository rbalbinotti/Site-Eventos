

# Functions

# Padronização nome das colunas
col_padrao = {
    'resp_evento': 'resp',
    'data_contato': 'data_contato',
    'etapa': 'etapa',
    'situação': 'situação',
    'data_evento': 'data_evento',
    'horário_início': 'horário_início',
    'tipo': 'tipo',
    'empresa': 'empresa',
    'contato': 'contato',
    'telefone': 'telefone',
    'email': 'email',
    'qtde_convidados': 'qtde_convidados',
    'cardápio': 'cardápio',
    'preço': 'preço',
    'kids': 'kids',
    'preço_kids': 'preço_kids',
    'sinal': 'sinal',
    'valor_extra': 'valor_extra',
    'forma_de_pagamento': 'forma_de_pagamento',
    'observação': 'observação',
    'convidados_presentes': 'convidados_presentes',
    'kids_presentes': 'kids_presentes',
    'total_convidados_previsto': 'total_convidados_previsto',
    'valor_total_previsto': 'valor_total_previsto',
    'total_convidados_presentes': 'total_convidados_presentes',
    'valor_total_realizado': 'valor_total_realizado',
    }


# Tratando colunas
def colunas_lower_replace(x):
    '''
    This function organize strings and replace name columns.
    Create col_padrao with names to replace.
    '''
    # x.rename(columns=col_padrao, inplace=True)
    x.columns = x.columns.str.strip().str.lower().str.replace(' ', '_')
    return


# Tratando espaços em branco
def whitespace_remover(dataframe):
    '''
    Remove whitespaces if columns is object.
    '''
    # iterating over the columns
    for i in dataframe.columns.tolist():

        # checking datatype of each columns
        if dataframe[i].dtypes == 'object':

            # applying strip function on column
            return dataframe[i].str.strip()

        else:

        # if condn. is False then it will do nothing.
            pass



