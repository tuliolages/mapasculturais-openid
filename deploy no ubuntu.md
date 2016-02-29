Deploy do ID da Cultura no Ubuntu 14.04 usando uWSGI e nginx
============================================================

Tudo foi feito como o usuário root.
### 1. Instalando os pacotes necessários para o funcionamento do sistema
```BASH
pip install uwsgi

apt-get install python-setuptools python-virtualenv python-dev build-essential postgresql python-psycopg2 libpq-dev
```

```BASH
pip install psycopg2
```

### 2. Criando um ambiente virtual e clonando o repositório

- Como root, ir para a pasta /srv/ e criar uma pasta para a instalação do ID da Cultura
```BASH
cd /srv/
mkdir openid & cd openid
```

- Clonar o projeto do repositório ID da Cultura no computado
```BASH
git clone git@github.com:hacklabr/mapasculturais-openid.git
```
Isso deve criar a pasta mapasculturais-openid

- Criar o ambiente virtual para o projeto com virtualenv
```BASH
mkdir mapasculturais-openid-env
virtualenv mapasculturais-openid-env
```
- Com o seu editor de texto predileto (ex: nano), inserir as chaves do recaptcha no fim do arquivo mapasculturais-openid-env/bin/activate
```BASH
nano mapasculturais-openid-env/bin/activate
```

- Formato das chaves (note que não há espaços antes e depois dos símbolos de igual):
```
export RECAPTCHA_PUBLIC_KEY='Chave-1'
export RECAPTCHA_PRIVATE_KEY='Chave-2'
```
### 3. Criando um banco de dados
- Nome: o mesmo que for especificado no arquivo **iddacultura/settings/rn_production.py** (neste guia, o nome será openid-staging)
- TODO: explicar como criar banco + dar permissões (provavelmente mudar a abordagem e criar um usuário openid)

### 4. Configurando a aplicação
- Criar os seguintes arquivos na pasta mapasculturais-openid:

**uwsgi_params**
```
uwsgi_param  QUERY_STRING       $query_string;
uwsgi_param  REQUEST_METHOD     $request_method;
uwsgi_param  CONTENT_TYPE       $content_type;
uwsgi_param  CONTENT_LENGTH     $content_length;

uwsgi_param  REQUEST_URI        $request_uri;
uwsgi_param  PATH_INFO          $document_uri;
uwsgi_param  DOCUMENT_ROOT      $document_root;
uwsgi_param  SERVER_PROTOCOL    $server_protocol;
uwsgi_param  REQUEST_SCHEME     $scheme;
uwsgi_param  HTTPS              $https if_not_empty;

uwsgi_param  REMOTE_ADDR        $remote_addr;
uwsgi_param  REMOTE_PORT        $remote_port;
uwsgi_param  SERVER_PORT        $server_port;
uwsgi_param  SERVER_NAME        $server_name;
```
**iddacultura.ini**
```
# ididaculltura.ini file
[uwsgi]

# Django-related settings
# the base directory (full path)
chdir           = /srv/openid/mapasculturais-openid
# Django's wsgi file
module          = iddacultura.wsgi:application
# the virtualenv (full path)
home            = /srv/openid/mapasculturais-openid-env

# process-related settings
# master
master          = true
# maximum number of worker processes
processes       = 10
# the socket (use the full path to be safe
socket          = /srv/openid/mapasculturais-openid/iddacultura.sock
# ... with appropriate permissions - may be needed
chmod-socket    = 665
# clear environment on exit
vacuum          = true
```

- Agora, para o nginx...

**/etc/nginx/sites-available/openid.conf**
```
# openid.conf

# the upstream component nginx needs to connect to
upstream django {
    server unix:///srv/openid/mapasculturais-openid/iddacultura.sock; # for a file socket
}

# configuration of the server
server {
    # the port your site will be served on
    listen      80;
    # the domain name it will serve for
    server_name url.do.servidor.de.autenticacao;
    charset     utf-8;

    # max upload size
    client_max_body_size 75M;   # adjust to taste

    # Django media
    location /media  {
        alias /srv/openid/mapasculturais-openid/media;
    }
```

- Configurar para rn_production
**iddacultura/settings/rn_production.py**
```
# coding: utf-8

from .base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'email@gmail.com'
EMAIL_HOST_PASSWORD = 'senha'
DEFAULT_FROM_EMAIL = 'email@gmail.com'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'openid-staging',
    }
}
```

- Em "iddacultura/wsgi.py" e "manage.py", mudar "iddacultura.settings" (pode ou não ter algum nome depois de settings) para "iddacultura.settings.rn_production"

### 5. Configurando um tema
- Atualmente, utilizando o default mesmo.

### 6. Conclusão

```BASH
cd mapasculturais-openid
pip install -r requirements.txt
./manage.py syncdb

service nginx restart
```

- Para o deploy ser feito:
```BASH
uwsgi --ini iddacultura.ini
```
