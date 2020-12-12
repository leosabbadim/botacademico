# -*- coding: utf-8 -*-

import math
import networkx as nx
import nltk
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import time
import io
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
import datetime

def saudacao():
    # obtém a hora atual para bom dia, boa tarde ou boa noite
    hora_atual = datetime.datetime.now().hour

    if hora_atual < 12:
        mensagem = ('\n\tBom dia!')
    elif (12 <= hora_atual < 18):
        mensagem = ('\n\tBoa tarde!')
    else:
        mensagem = ('\n\tBoa noite!')

    print('\t',mensagem)

class Sentenca:
    def __init__(self, texto, raw_text):
        """
        O parâmetro ``texto`` é uma instância de Texto.
        ``raw_text`` é o texto puro da sentença.
        """

        self.texto = texto
        self.raw_text = raw_text
        self._palavras = None
        self._pontuacao = None

    @property
    def palavras(self):
        """
        Quebrando as sentenças em palavras. As palavras
        da sentença serão usadas para calcular a semelhança.
        """
        if self._palavras is not None:
            return self._palavras

        # nltk.word_tokenize é quem divide a sentenças em palavras.
        self._palavras = nltk.word_tokenize(self.raw_text)
        return self._palavras

    @property
    def pontuacao(self):
        """
        Implementação do algorítimo simplificado para pontuação
        dos nós do grafo.
        """
        if self._pontuacao is not None:
            return self._pontuacao

        # aqui a gente simplesmente soma o peso das arestas
        # relacionadas a este nó.
        pontuacao = 0.0
        for n in self.texto.graph.neighbors(self):
            pontuacao += self.texto.graph.get_edge_data(self, n)['weight']

        self._pontuacao = pontuacao
        return self._pontuacao

    def __hash__(self):
        """
        Esse hash aqui é pra funcionar como nó no grafo.
        Os nós do NetworkX tem que ser 'hasheáveis'
        """
        return hash(self.raw_text)
class Texto:
    def __init__(self, raw_text):
        """
        ``raw_text`` é o text puro a ser resumido.
        """
        self.raw_text = raw_text
        self._sentences = None
        self._graph = None

    @property
    def sentences(self):
        """
        Quebra o texto em sentenças utilizando o sentence tokenizer
        padrão do nltk.
        """

        if self._sentences is not None:
            return self._sentences

        # nltk.sent_tokenize é quem divide o texto em sentenças.
        self._sentences = [Sentenca(self, s)
                           for s in nltk.sent_tokenize(self.raw_text)]
        return self._sentences

    @property
    def graph(self):
        """
        Aqui cria o grafo, colocando as sentenças como nós as arestas
        (com peso) são criadas com base na semelhança entre sentenças.
        """

        if self._graph is not None:
            return self._graph

        graph = nx.Graph()
        # Aqui é o primeiro passo descrito acima. Estamos criando os
        # nós com as unidades de texto relevantes, no nosso caso as
        # sentenças.
        for s in self.sentences:
            graph.add_node(s)

        # Aqui é o segundo passo. Criamos as arestas do grafo
        # baseadas nas relações entre as unidades de texto, no nosso caso
        # é a semelhança entre sentenças.
        for node in graph.nodes():
            for n in graph.nodes():
                if node == n:
                    continue

                semelhanca = self._calculate_similarity(node, n)
                if semelhanca:
                    graph.add_edge(node, n, weight=semelhanca)

        self._graph = graph
        return self._graph

    def _calculate_similarity(self, sentence1, sentence2):
        """
        Implementação da fórmula de semelhança entre duas sentenças.
        """
        w1, w2 = set(sentence1.palavras), set(sentence2.palavras)

        # Aqui a gente vê quantas palavras que estão nas frases se
        # repetem.
        repeticao = len(w1.intersection(w2))
        # Aqui a normalização.
        semelhanca = repeticao / (math.log(len(w1)) + math.log(len(w2)))

        return semelhanca

    def resumir(self):
        """
        Aqui a gente extrai as frases com maior pontuação.
        O tamanho do resumo será 20% do número de frases original
        """
        # aqui definindo a quantidade de frases
        qtd = int(len(self.sentences) * 0.2) or 1

        # ordenando as frases de acordo com a pontuação
        # e extraindo a quantidade desejada.
        sentencas = sorted(
            self.sentences, key=lambda s: s.pontuacao, reverse=True)[:qtd]

        # ordenando as sentenças de acordo com a ordem no texto
        # original.
        ordenadas = sorted(sentencas, key=lambda s: self.sentences.index(s))

        return ' '.join([s.raw_text for s in ordenadas])

bot = ChatBot("Bot Acadêmico")  # inicia o bot
conversa = ['olá',
'oi',
'como vai você?',
'eu estou bem',
'que bom',
'sim',
'posso ajudá-lo com alguma coisa?',
'sim, eu tenho uma pergunta',
'qual é a sua pergunta?',
'eu poderia pedir uma xícara de açúcar?',
'me desculpe, mas eu não tenho nenhum',
'obrigado de qualquer maneira',
'sem problemas',
'qual é o seu livro favorito?',
'sou um computador, não tenho preferências',
'então, qual é a sua cor favorita?',
'roxo',
'quem é você?',
'quem? Quem é senão uma forma seguindo a função de quê',
'então o que você é?',
'um homem em uma máscara',
'eu posso ver isso',
'não é seu poder de observação eu duvido, mas apenas a natureza paradoxal de pedir um homem mascarado que é. Mas diga-me, você gosta de música?',
'eu gosto de ver filmes',
'que tipo de filme você gosta?',
'eu gosto do Exterminador do Futuro',
'eu estou trabalhando em um projeto',
'qual projeto?',
'eu estou tentando fazer um bolo',
'fale-me sobre você',
'o que você quer saber?',
'você é um robô?',
'sim eu sou',
'como você trabalha?',
'complexo demais para você entender']

trainer = ListTrainer(bot)  # define o método de treinamento
trainer.train(conversa)  # define a lista de conversa

saudacao()
print('\n\tEu sou o Bot Acadêmico, um bot em treinamento \n'
      '\tSou programado para resumir artigo e textos \n'
      '\tE com isso, pesquiso sobre os autores fazendo uma avaliação e enviando tudo para o seu email no final'
      '\n\n\tCaso queira que eu faça a leitura do artigo, digite:   leitura'
      '\n\tPara encerrar a nossa conversa, digite:    tchau'
      '\n\tMas se quiser só conversar, eu também estou treinando para saber responder da melhor maneira!\n\n')

def ler_pdf(inPDFfile):
    inFile = open(inPDFfile, 'rb')
    RM = PDFResourceManager()
    RS = io.StringIO()
    Texto_Conversor = TextConverter(RM, RS, laparams=LAParams())
    interpreter = PDFPageInterpreter(RM, Texto_Conversor)
    for page in PDFPage.get_pages(inFile):
        interpreter.process_page(page)

    txt = RS.getvalue()
    return txt

def enviar_email(text_entrada):
    import smtplib
    from email.mime.text import MIMEText

    smtp_ssl_host = 'smtp.gmail.com'
    smtp_ssl_port = 465
    # username ou email para logar no servidor
    username = 'botacademico.smart@gmail.com'
    password = 'botpython123'

    from_addr = 'botacademico.smart@gmail.com'
    to_addrs = [email_enviar]

    message = MIMEText(text_entrada)
    message['subject'] = 'Resposta BOT Acadêmico'
    message['from'] = from_addr
    message['to'] = ', '.join(to_addrs)

    server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
    server.login(username, password)
    server.sendmail(from_addr, to_addrs, message.as_string())
    server.quit()
    print("\nE-mail enviado!")


while True:
    quest = input('Humano: ').lower()
    if (quest == 'tchau'):
        resposta = ('Adorei conversar com você, volte sempre!')
        print('Bot Acadêmico: ', resposta)
        exit()

    if (quest == 'leitura'):

        print('\nMe diz o nome do arquivo que você quer que eu busque: '
              '\nLembrando: Sempre no formato PDF')
        PDFfile = input('Artigo: ')

        inPDFfile = (PDFfile+'.pdf')

        num_autor = int(input('Quantos autores esse artigo tem: '))
        autores = []
        count = 0
        print('Ok, agora me informa o nome desses autores dando ENTER entre cada um deles e no final\n')
        while count < num_autor:
            autor = input('Autor(a): ')
            autores.append(autor)
            count = count + 1

        lerPDF = ler_pdf(inPDFfile)

        t = Texto(lerPDF)
        resumo = (t.resumir())



        print("\n\nCerto, agora vou pesquisar o ineditismo desse artigo...")

                                ####################

        from selenium import webdriver
        from selenium.webdriver.common.keys import Keys

        # Chamando a função de pesquisa por texto
        PATH = 'C:\Program Files (x86)\chromedriver.exe'

        driver = webdriver.Chrome(PATH)

        driver.get('https://scholar.google.com.br/')
        search = driver.find_element_by_id("gs_hdr_tsi")
        search.send_keys(resumo)
        #search.send_keys(Keys.RETURN)
        result = driver.find_element_by_id("gs_ab_md")

        x = (result.text).split()
        driver.quit()


        # Caso tenha poucos resultados de texto
        if x == []:
            print('Pesquisei pelo resumo e não encontrei nada, vou dar uma certificada no resultado'
                  'Vou pesquisar pelo texto em sí, me da 1 min')
            PATH = 'C:\Program Files (x86)\chromedriver.exe'

            driver = webdriver.Chrome(PATH)

            driver.get('https://scholar.google.com.br/')
            search = driver.find_element_by_id("gs_hdr_tsi")
            search.send_keys(lerPDF)
            #search.send_keys(Keys.RETURN)
            result = driver.find_element_by_id("gs_ab_md")

            x = (result.text).split()
            driver.quit()

            if x == []:
                pontos1 = 5
                x_result = '0 resultados'
                est1 = (u'\u2606' * pontos1)
            elif x[1] == 'resultado':
                x_result = (x[0] + ' ' + x[1])
                x_f = (float(x[0].replace('.', '')))
                y = (int(x_f))

                if y >= 500000:
                    pontos1 = +1
                elif y >= 100000 and y < 500000:
                    pontos1 = +2
                elif y >= 50000 and y < 100000:
                    pontos1 = +3
                elif y >= 10000 and y < 30000:
                    pontos1 = +4
                else:
                    pontos1 = +5

                est1 = (u'\u2606' * pontos1)


            # Busca de texto normal
            else:
                x_result = (x[1] + ' ' + x[2])
                x_f = (float(x[1].replace('.', '')))
                y = (int(x_f))

                pontos1 = None

                if y >= 500000:
                    pontos1 = +1
                elif y >= 100000 and y < 500000:
                    pontos1 = +2
                elif y >= 50000 and y < 100000:
                    pontos1 = +3
                elif y >= 10000 and y < 30000:
                    pontos1 = +4
                else:
                    pontos1 = +5

                est1 = (u'\u2606' * pontos1)


        if x[1] == 'resultado':
            x_result = (x[0] + ' ' + x[1])
            x_f = (float(x[0].replace('.', '')))
            y = (int(x_f))

            if y >= 500000:
                pontos1 = +1
            elif y >= 100000 and y < 500000:
                pontos1 = +2
            elif y >= 50000 and y < 100000:
                pontos1 = +3
            elif y >= 10000 and y < 30000:
                pontos1 = +4
            else:
                pontos1 = +5

            est1 = (u'\u2606' * pontos1)

        elif x[0] == 'Aproximadamente':
            x_result = (x[1] + ' ' + x[2])
            x_f = (float(x[1].replace('.', '')))
            y = (int(x_f))

            if y >= 500000:
                pontos1 = +1
            elif y >= 100000 and y < 500000:
                pontos1 = +2
            elif y >= 50000 and y < 100000:
                pontos1 = +3
            elif y >= 10000 and y < 30000:
                pontos1 = +4
            else:
                pontos1 = +5

            est1 = (u'\u2606' * pontos1)


        # Busca de texto normal
        else:
            x_result = (x[1] + ' ' + x[2])
            x_f = (float(x[1].replace('.', '')))
            y = (int(x_f))

            pontos1 = None

            if y >= 500000:
                pontos1 = +1
            elif y >= 100000 and y < 500000:
                pontos1 = +2
            elif y >= 50000 and y < 100000:
                pontos1 = +3
            elif y >= 10000 and y < 30000:
                pontos1 = +4
            else:
                pontos1 = +5

            est1 = (u'\u2606' * pontos1)


        ###
        ### Chamando a função de pesquisa por nome
        print("\nEspera só mais um pouco, vou pesquisar sobre os autores desse artigo...")
        time.sleep(2)
        var_autor = []

        for autor in autores:

            PATH = 'C:\Program Files (x86)\chromedriver.exe'
            driver = webdriver.Chrome(PATH)
            driver.get('https://scholar.google.com.br/')

            search = driver.find_element_by_id("gs_hdr_tsi")
            search.send_keys('"a"'.replace("a", autor))
            search.send_keys(Keys.RETURN)

            name = driver.find_element_by_id("gs_ab_md")


            if name.text == '':
                pontos2 = 1
                z_result = '0 resultados'
                est2 = (u'\u2606' * pontos2)

            else:
                z = (name.text).split()

                # Pesquisa para poucos resultados de autor
                if z[1] == 'resultado':
                    z_result = (z[0] + ' ' + z[1])
                    x_f = (float((z[0].replace('.', ''))))
                    y = (int(z[0]))

                    if y >= 20:
                        pontos2 = 5
                    elif y >= 15 and y < 20:
                        pontos2 = 4
                    elif y >= 10 and y < 15:
                        pontos2 = 3
                    elif y >= 5 and y < 10:
                        pontos2 = 2
                    else:
                        pontos2 = 1

                    est2 = (u'\u2606' * pontos2)

                # Pesquisa normal de autor
                elif z[0] == 'Aproximadamente':
                    z_result = (z[1] + ' ' + z[2])
                    x_f = (float((z[1].replace('.', ''))))
                    y = (int(x_f))

                    if y >= 20:
                        pontos2 = 5
                    elif y >= 15 and y < 20:
                        pontos2 = 4
                    elif y >= 10 and y < 15:
                        pontos2 = 3
                    elif y >= 5 and y < 10:
                        pontos2 = 2
                    else:
                        pontos2 = 1

                    est2 = (u'\u2606' * pontos2)

                else:
                    z_result = (z[0] + ' ' + z[1])
                    y = (int(z[0]))

                    if y >= 20:
                        pontos2 = 5
                    elif y >= 15 and y < 20:
                        pontos2 = 4
                    elif y >= 10 and y < 15:
                        pontos2 = 3
                    elif y >= 5 and y < 10:
                        pontos2 = 2
                    else:
                        pontos2 = 1

                    est2 = (u'\u2606' * pontos2)

            driver.quit()
            resultado = (
                        'O(a) Autor(a) ' + autor + ' obteve ' +  z_result + ', alcançado a seguinte pontuação: '+
                        est2)
            var_autor.append(resultado)


        texto_expor= [('\n\n\n'),
                      ('A pontuação foi feita de 1 a 5, sendo 1 a menor pontuação e 5 a maior'),
                      ('Para o texto, quanto menor o resultado encontrado, melhor a pontuação'),
                      ('Para o autor, quanto maior o resultado encontrado, melhor a pontuação')]

        resultado_texto = ('O texto pesquisado obteve ' + x_result + ', e alcançou a seguinte pontuação: ' + est1)

        texto_expor_novo = "\n".join(map(str, texto_expor))
        resultado_texto_novo = "\n".join(map(str, resultado_texto))
        var_autor_novo = "\n".join(map(str, var_autor))

        entrada = ['O artigo pesquisado foi:', PDFfile, 'Resumo: ', resumo, texto_expor_novo, resultado_texto, var_autor_novo]
        #text_entrada = ('O resumo feito foi: \r\n' + resumo + str(texto_expor) + '\r\n'+ str(resultado_texto)+ '\r\n'+ str(var_autor))

        text_entrada = "\n\n".join(map(str, entrada))

        email_enviar = input('\nInforme um e-mail para enviar os resultados: ')

        enviar_email(text_entrada)

    resposta = bot.get_response(quest)
    print('Bot Acadêmico: ', resposta)


