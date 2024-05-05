import boto3

def login(event):
    
    email = event['email']
    password = event['password']
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Login')
    
    response = table.scan(
        FilterExpression='Email = :email AND Password = :password',
        ExpressionAttributeValues={
            ':email': email,
            ':password': password
        }
    )
        
    if response['Items']:
        
        username = response['Items'][0].get('Username', 'Unknown Username')
        
        return {
            'statusCode': 200,
            'param1': username,
            'param2' : email
        }
    else:
        return {
            'statusCode': 404,
            'body': 'Email or Password is invalid'
        }

def register(event):
    
    email = event['email']
    username = event['username']
    password = event['password']

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Login')
    
    response = table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('Email').eq(email))
    if response['Items']:
        
        return {
            'statusCode': 404,
            'body': 'The email already exists'
        }

    table.put_item(Item={'Email': email, 'Username' : username, 'Password': password})

    return {
        'statusCode': 300,
        'body': 'User registered successfully'
    }


def lambda_handler(event, context):
    
    
    if(event['request_type'] == 'login'):
        return login(event)
    elif(event['request_type'] == 'register'):
        return register(event)
    else:
        return {
            'statusCode' : 404,
            'body' : 'Invalid Request Type'
        }
    
