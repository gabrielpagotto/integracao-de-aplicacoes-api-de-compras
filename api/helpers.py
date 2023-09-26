import re

def create_url_path(string_formatada):
    padroes = string_formatada.split(',')
    regex_padroes = []
    for padrao in padroes:
        padrao = padrao.strip()
        padrao_regex = re.sub(r':(\w+)', r'(?P<\1>.+)', padrao)
        regex_padroes.append(padrao_regex)
    return ','.join(regex_padroes)
