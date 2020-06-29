import requests
from bs4 import BeautifulSoup
import re
import csv

#Variaveis globais do sistema
cargo = 'programador python'      #Cargo a ser buscado
pagina = 0               #indice da pagina em que sera extraida os links de vagas
lista = [0]              #esse vetor armazena a quantidade de paginas que esta sendo lida no rodapé das vagas pesquisadas
count = 0                #Contador de links extraidos, ainda serão limpos
links = []               #Links das vagas que estão sendo extraidos pelo sistema
dadosbrutos = {}         #Dicionario de dados que ira armazenar Titulo : Requisitos

def infojobs_scrapper_links():


    def conectar():
        response = requests.get(
            f'https://www.infojobs.com.br/vagas-de-emprego-{cargo}-em-sao-paulo.aspx?Page={lista[pagina]}')
        html_doc = response.content
        soup = BeautifulSoup(html_doc, 'html.parser')
        return soup

    def converterstrint(strings): #Converte STR em INT
        inteiros = []
        for r in strings:
            inteiros.append(int(r))

        global lista
        lista = inteiros

    def remove_repetidos(lista2): #Remove itens repetidos da lista
        l = [] # Lista que ira armazenar os links ja limpos
        for i in lista2:
            if i not in l:
                l.append(i)
        l.sort()     # Ordena a Lista de links
        return l #Retorna a lista limpa de itens duplicados

    def contarpaginas(soup2):  # conta a quantidade de paginas disponivel no rodapé
        paginasdisp = soup2.find('div', attrs={'id': 'ctl00_phMasterPage_cGrid_Paginator1_divPaginator'}) #Localiza o local no codigo do site responsavel pelo rodapé
        paginas = paginasdisp.get_text() #Lê as STR no campo de rodapé do site
        for r in (("\n", " "), ("<", ""), ('>', ''), ('Anterior', ''), ('Próxima', '')): #Faz a limpeza dos dados desnecessários do rodapé
            paginas = paginas.replace(*r)
        index = paginas.split() #Junta tudo em uma list
        global lista
        global pagina #Variaveis globais a serem alteradas, são necessarias para ativar a repetição e o indice da pagina a ser lida aberta
        lista2 = lista + index #Adiciona os dados do rodapé em um lista só
        converterstrint(lista2) #converte para STR
        lista = remove_repetidos(lista) #Remove os dados repetidos
        pagina = pagina + 1 #adiciona mais um ao indice para abrir a pagina

    def gravar_txt(link):
        with open('dados\links.txt', 'w') as file:
            for r in link:
                #print(r)
                file.write(f'{r}\n')
            


    def copiarlinks(soup2):  # seleciona os links para ser analisados ja limpos
        global count
        global links
        for link in soup2.find_all('a', attrs={'href': re.compile("^https?://www.infojobs.com.br/vaga-")}): # Site do Infojobs possui um URL de busca padrão
            #print(link.get('href'))
            links.append(link.get('href')) #salva os links na variavel
            count = count + 1 #contador dos links armazenados
        links = remove_repetidos(links) #Função remove itens repetidos da lista
        #print(links)
        #print(len(links))


    dados = conectar() #primeira conexao para fazer a leitura da primeira pagina e iniciar a contagem
    contarpaginas(dados) #Primeira contagem de paginas para ativar o laço de repetição
    copiarlinks(dados)
    maxpage = max(lista) #primeira contagem de valor maximo


    while maxpage > lista[pagina]:        #O laço ira girar comparando o rodape com o maximo do rodapé mudando de pagina ate chegar ao final das paginas disponiveis.
        dados = conectar()                #Salva os dados da pesquisa na variavel
        copiarlinks(dados)                #Copia o link das paginas
        contarpaginas(dados)              #Conta a QTD de paginas disponivel no rodapé
        print(f'Pagina: {pagina - 1}')    #-1 pois as paginas são analisadas apos a primeira contagem de dados.
        print(f'Quantidade de vagas encontradas ate o momento: {len(links)}')
        #print(f'Lista : {lista}')
        maxpage = max(lista)
    gravar_txt(links)
    print(f'Total de vagas encontradas: {len(links)}')#QTD de vagas

def infojobs_read_links():   #Lê os links e extrai os dados ja relativamente tratados sobre as vagas.


    def conectar(link):
        response = requests.get(link)
        html_doc = response.content
        soup = BeautifulSoup(html_doc, 'html.parser')
        return soup


    def gravar_csv():
        with open('dados/dicionariodedados.csv', mode='w', newline='', encoding='UTF-8') as csv_file:
            for key in dadosbrutos.keys():
                csv_file.write(f'{key}, {dadosbrutos[key]}\n')


    def capturar_dados(soup):
        requisitos = []

        for tag in soup.find_all('h1', attrs={'class': re.compile("vacancy-title")}): #para cada tag no codigo aberto procure H1
            titulos = tag.get_text()



        for tag in soup.find_all('ol', attrs={'class': re.compile("descriptionItems")}): #para cada tag no codigo aberto procure OL
            texto = ';'
            for r in tag.find_all('li'):               #para cada LI dentro do OL procure LI
                requisitos.append(r.get_text('|', strip=True))



            requisitosbruto = texto.join(requisitos) #transforma a lista de requisitos em uma string
            dadosbrutos[titulos] = requisitosbruto #Cria um dicionario titulos: requisitos



    for r in links:
        soup = conectar(r)
        capturar_dados(soup)
        gravar_csv()


infojobs_scrapper_links()
infojobs_read_links()