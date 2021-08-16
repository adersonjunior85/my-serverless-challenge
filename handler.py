# coding=utf-8
import os
import json
import boto3
import exifread
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")

def extractMetadata(event, context): 
    #armazenando key de event
    key, bucket = event["Records"][0]["s3"]["object"]["key"], event["Records"][0]["s3"]["bucket"]["name"]
    keybucket = {"key": key, "bucket": bucket}
    #fazendo upload da imagem usando a função getImage
    getImage(keybucket,"")
    try:       #extraindo dimensões da imagem usando exifread
        openimage = open("/tmp/imagemetadata"+key.split("/")[-1].split(".")[-1], 'rb')#tratamento para caso a imagem tenha sido diferente de jpg
        img = exifread.process_file(openimage)
        width = img['EXIF ExifImageWidth']
        height = img['EXIF ExifImageLength']
        dimension = str(width)+"x"+str(height)
    except:   #caso não consiga, armazena este resultado
        dimension = "It was not possible to find the dimensions"
    
    #preparando os dados para inserir na tabela
    item = {
        "s3objectkey":key, 
        "metadata":{
            "dimension":dimension,
            "size": str(event["Records"][0]["s3"]["object"]["size"])
            }
    }
    #inserindo os dados na tabela e gerando uma response
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    table.put_item(Item=item)
    response = {
        "statusCode": 200,
        "body": json.dumps(item)
    }   
    return response

def getMetadata(event,context):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    s3objectkey = event['pathParameters']['s3objectkey'] #tratando o event para s3objectkey
    try:  #tentando acessar o banco de dados com o {s3objectkey} informado
        data = table.get_item(Key={'s3objectkey': "upload/"+s3objectkey})#buscando no banco s3obkectkey
        #gerando uma response
        response = {
        "statusCode": 200,
        "body": json.dumps(data['Item']),
        }
        return response
    except: #response para caso não consiga encontrar o s3objectkey
        response = {
        "statusCode": 400,
        "body": "Could not find ('"+s3objectkey+"') in the database."
        }
        return response
def getImage(event,context):
    s3objectkey = event['key']
    bucket = event['bucket']
    #conectando com as credenciais
    s3 = boto3.client('s3', aws_access_key_id="<MYACESSKEY>" , aws_secret_access_key="MYSECRETACESSKEY")    #SETAR AWS KEY E AWS SECRET KEY
    #função para fazer o download e tratando o arquivo de destino pra caso seja diferente de jpg
    s3.download_file(bucket, s3objectkey, "/tmp/imagemetadata"+s3objectkey.split("/")[-1].split(".")[-1])

def infoImages(event, context):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    resultItens = table.scan() #faz a varredura e retorna todos os dados da tabela
    dictSize = {} # dicionario para separar os s3object keys e seus respectivos tamanhos
    listFileExtension = [] #lista para adicionar string com a extensão do arquivo
    dictFileExtension = {} #dicionario para contar quantas vezes repetiu a extensão
    for x in resultItens['Items']:  #inicia o laço para percorrer os itens da tabela
        dictSize[x["s3objectkey"]] = int(x["metadata"]["size"])  # separa s3objectkey e size na variavel dictSize
        extension = str(x["s3objectkey"].split("/")[-1].split(".")[-1]) #trata a string para pegar apenas o final que é a extensão do arquivo
        listFileExtension.append(extension) #adiciona à lista a extensão capturada
        dictFileExtension[extension] = 0 #adiciona um elemento ao dicionario para fazer a contagem depois
    for x in listFileExtension:
        dictFileExtension[x]+=1 #funciona como contador para contar quantas extensões continha em listFileExtension

    maxSize = max(dictSize, key=lambda i: dictSize[i]) #função max para encontrar o maior item
    minSize = min(dictSize, key=lambda i: dictSize[i]) #função min para encontrar o menor item
    response = {
        "statusCode": 200,
        "body": {
            "Larger image":maxSize,
            "Smaller image":minSize,
            "Type and number of extensions":dictFileExtension
        }
    }
    return response