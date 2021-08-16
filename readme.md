# Desafio Desenvolvedor Backend

## Setup

```bash
npm install -g serverless
```
```bash
sls plugin install -n serverless-python-requirements
```
Depois da instalação é preciso inserir os dados no `serverless.yml` como profile e app.

Na linha 63 do aquivo `handler.py` deve informar as chaves de acesso:
```bash
s3 = boto3.client('s3', aws_access_key_id="<MYACESSKEY>" , aws_secret_access_key="MYSECRETACESSKEY")
```


## Deploy

Estando configurado basta fazer o deploy 

```bash
serverless deploy
```

É esperado um resultado como esse:

```bash
Service Information
service: serverless-challenge
stage: dev
region: us-east-1
stack: serverless-challenge-dev
resources: 35
api keys:
  None
endpoints:
  GET - https://xxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev/images/{s3objectkey}
functions:
  extractMetadata: serverless-challenge-dev-extractMetadata
  getMetadata: serverless-challenge-dev-getMetadata
  getImage: serverless-challenge-dev-getImage
  infoImages: serverless-challenge-dev-infoImages
layers:
  None
Serverless: Invoke aws:deploy:finalize
Serverless: Removing old service artifacts from S3...
Serverless: Publishing service to the Serverless Dashboard...
Serverless: Successfully published your service to the Serverless Dashboard: https://app.serverless.com/adersonjunior85/apps/serverless-challenge/serverless-challenge/dev/us-east-1
```
## Usage

Necessita-se alterar uma pasta no seu [`amazon s3`](https://s3.console.aws.amazon.com/s3/home), no caso você precisa criar uma pasta chamada "upload" para poder enviar as suas imagens. Lembrando que necessita-se setar o seu bucket no seu `serverless.yml`

### Função extractMetadata

Basta carregar a imagem no seu bucket da [`amazon s3`](https://s3.console.aws.amazon.com/s3/home) na pasta upload que será inserido os metadados da `imagem na tabela serverless-challenge-dev` do [`dynamoDB`](https://console.aws.amazon.com/dynamodb/home).



### Usando a API /images/{s3objectkey} | Função getMetadata

Pra usar basta enviar a imagem para o [`amazon s3`](https://s3.console.aws.amazon.com/s3/home) e usar a request com o nome da sua imagem no lugar de s3objectkey.
```bash
curl --request GET
   --url https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev/images/{s3objectkey}
```

Example output:
```bash
{"s3objectkey": "upload/imagemtest3.jpg", "metadata": {"size": "336486", "dimension": "4000x2250"}}
```

### getImage

Essa função é sempre executada para baixar a imagem e fazer a leitura dos seus metadados pela função extractMetadata. Mas pode ser testada usando o serviço Lambda da AWS, o teste é feito usando como parâmetro sua s3objectkey.

```bash
{"key":"upload/{s3objectkey}","bucket":"<SEUBUCKETAQUI>"}
```

### infoImages

Essa função pode ser executada no [`lambda`](https://console.aws.amazon.com/lambda/home) da AWS indo na aba testes e executando um teste qualquer.

Example Result:
```bash
{
  "statusCode": 200,
  "body": {
    "Larger image": "upload/imagemtest4.jpg",
    "Smaller image": "upload/imagemtest1.jpg",
    "Type and number of extensions": {
      "jpg": 4
    }
  }
}
```