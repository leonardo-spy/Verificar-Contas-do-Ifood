# Examinador automatizado para contas do Ifood

## Cupom & Banner Finder

Aplicação que lista todos os seus cupons e banners da sua conta! Acessa de formar automatizada uma lista de contas do Ifood (entrando através da autentificarão por e-mail no método IMAP) e realiza o Scrapping de seus banners e cupons, enviando o resultado em forma de lista para um chat no Telegram.

## O que o projeto contém
- Scrapping em Python
- Selenium
- Integração com a API do Telegram
- Integração com IMAP

## Instalação
Para rodar o projeto faça essas configurações:
- Clone o projeto (utilizando comando git ou baixando em zip)
- Instale o Python (recomendado versão 3.8)
- Instale um WebDriver (recomendamos o driver do Google Chrome)
- Instale a biblioteca que se encontra em requirements
```
python -m pip install -U pip setuptools
python -m pip install --upgrade pip
pip install -r requirements.txt
```
Configure uma lista de contas no arquivo 'login.txt', os e-mails precisa ter o acesso IMAP liberado e para isto você pode acessar estes links para liberar em cada provedores:
- [Google IMAP](https://mail.google.com/mail/u/0/#settings/fwdandpop) e [Aplicações de LessSecure do Google](https://myaccount.google.com/lesssecureapps) (caso esteja habilitado a autentificarão de dois fatores, você precisará gerar uma senha única para esta aplicação em [AppsPassword](https://myaccount.google.com/apppasswords))
- [Yahoo](https://login.yahoo.com/myaccount/security/app-password/)
- [Outlook e Hotmail](https://outlook.live.com/mail/0/options/mail/accounts)
```
email@teste.com
senhaTeste123
email2@teste.com.br
senhateste2
```
Crie um Bot no Telegram e adicione ele em uma conversar onde será imprimido o resultado, para isso basta realizar esses passos:
- No Telegram, abra uma conversa com @Botfather
- Envie /newbot
- Em seguida escolha um Nome e Username para seu Bot (o Username deve finalizar com 'bot', exemplo: Testebot)
- O BotFather irar te retornar seu token, então basta enviar um 'Olá' para seu Bot na DM (mensagem privada) caso você queira receber o resultado da aplicação na DM, ou adicione o bot em um grupo e envie um 'Olá' no grupo para receber o resultado da aplicação no grupo
- Acesse https://api.telegram.org/bot{token}/getUpdates e substitua {Token} pelo seu código de Token sem as chaves {}
- Caso você opte por receber o resultado pela DM, pegue o id (representado por 1111111111) abaixo
```
{"ok":true,"result":[{"update_id":613808168,
"message":{"message_id":579,"from":{"id":1111111111,"is_bot":false,"first_name":"teste","username":"usuarioteste","language_code":"pt-br"},"chat":{"id":1111111111,"first_name":"teste","username":"usuarioteste","type":"private"},"date":1650481674,"text":"teste"}]}
```
- Caso opite por receber em grupo, pegue o id (representado por -9999999999999) abaixo
```
{"ok":true,"result":[{"update_id":613808167,
"message":{"message_id":8461,"from":{"id":1111111111,"is_bot":true,"first_name":"Group","username":"GroupAnonymousBot"},"sender_chat":{"id":-9999999999999,"title":"Grupo teste","type":"supergroup"},"chat":{"id":-9999999999999,"title":"Grupo teste","type":"supergroup"},"date":1650481382}}]}
```
- Configure o main.py substituindo o my_token e chat_id pelo token do seu bot e o id da conversa respectivamente
```
my_token = '123123123:XXXXXXXXXxxxxxxxxxxxxxx'
chat_id = "-9999999999999"
```

## Endpoints
Lista de Banners e Cupons gerados a partir dos resultados das contas do Ifood, o resultado da consulta será imprimido no Chat integrado do Telegram!<br>
<img src="https://user-images.githubusercontent.com/19514153/164307691-db76e73a-90de-4b86-ae28-a5809f35967f.jpeg" width="300" height="600">
<br>

## Nota
A aplicação não realiza nenhuma ação ilegal, as consultar de múltiplas contas não significa que as contas sejam suas, você pode adicionar contas únicas de parentes e amigos seus (com a autorização deles) ... A aplicação somente automatiza a consulta, e não a criar de outras contas no qual inflija diretamente nos Termos de Uso do ifood.
