import boto3



def fetch_items(artist_name, title, release_year, table):
    
    
    filter_expression = ''
    expression_attribute_values = {}

    output = []
    statusCode = 404
    
    if artist_name and title:
        filter_expression = 'artist = :artist AND title = :title'
        expression_attribute_values = {':artist': artist_name, ':title': title}
    elif artist_name:
        filter_expression = 'artist = :artist'
        expression_attribute_values = {':artist': artist_name}
    elif title:
        filter_expression = 'title = :title'
        expression_attribute_values = {':title': title}
    
    if release_year:
        if filter_expression:
            filter_expression += ' AND release_year = :release_year'
        else:
            filter_expression = 'release_year = :release_year'
        expression_attribute_values[':release_year'] = release_year

    if filter_expression:
        response = table.scan(
            FilterExpression=filter_expression,
            ExpressionAttributeValues=expression_attribute_values)

        songs = response['Items']
        if songs:
            statusCode = 500
            for song in songs:
                url = fetch_image(song['artist'])
                output.append({'Title' : song['title'], 'Artist' : song['artist'], 'Year' : song['release_year'], 'Image' : url})
        else:
            output.append("No result is retrieved. Please query again.")
    else:
        output.append("No result is retrieved. Please query again.")

    return {
        'statusCode': statusCode,
        'body': output
    }

def fetch_image(artist):
    
    #print(artist)
    artist += '.jpg'
    s3 = boto3.client('s3')
    
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': 'a1-task2-s3806891', 'Key': artist},
        ExpiresIn=3600
        )
        
    return url

def music_query(event):
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Music')
    
    artist_name = event['artist']
    title = event['title']
    release_year = event['year']
    
    return fetch_items(artist_name, title, release_year, table)
    
def subs_query(event):
    
    statusCode = 0
    body = ''
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Subscribed')
    
    email = event['email']
    response = table.scan(
        FilterExpression = 'email = :email',
        ExpressionAttributeValues = {':email' : email}
        )
    songs = response['Items']
    print(response)
    
    if songs:
        output = []
        
        for song in songs:
            url = fetch_image(song['artist'])
            output.append({'Title' : song['title'], 'Artist' : song['artist'], 'Year' : song['release_year'], 'Image' : url})
        
        statusCode = 600
        body = output
    else:
        statusCode = 504
        body = 'You havent subscribed to any songs'
    
    return {
        'statusCode' : statusCode,
        'body' : body
    }
        

def check_music(email, title, artist, year, table):
    
    subs = title + '#' + artist + '#' + year
    response = table.scan(
        FilterExpression = 'email = :email AND subs = :subs',
        ExpressionAttributeValues = {':email' : email, ':subs' : subs}
        )
        
    if(response['Count'] == 0):
        return False
        
    else:
        return True
        
def music_unsubscribe(event):
    email = event['email']
    title = event['title']
    artist = event['artist']
    year = event['year']
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Subscribed')
    
    if(check_music(email, title, artist, year, table) == True):
        
        subs = title + '#' + artist + '#' + year
        response = table.delete_item(
            Key={
                'email': email,
                'subs': subs
            }
        )
        
        return {
            'statusCode' : 150,
            'body' : 'Music Unsubscribed Successfully'
        }
        
    else:
        return {
            'statusCode' : 404,
            'body' : 'Music doesnt exists'
        }

def music_subscribe(event):
    
    email = event['email']
    title = event['title']
    artist = event['artist']
    year = event['year']
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Subscribed')
    
    if(check_music(email, title, artist, year, table) == True):
        return {
            'statusCode' : 404,
            'body' : 'Music Already Subscribed'
        }
    else:
        
        subs = title + '#' + artist + '#' + year
        
        table.put_item(Item={'email': email, 'subs' : subs, 'title' : title, 'artist': artist, 'release_year' : year})
        return {
            'statusCode' : 100,
            'body' : 'Music Subscribed Successfully'
        }
    
    
def lambda_handler(event, context):
    
    types = event['request_type']
    
    if types == 'music_query':
        return music_query(event)
    elif types == 'subs_query':
        return subs_query(event)
    elif types == 'music_subscribe':
        print('this')
        return music_subscribe(event)
    elif types == 'music_unsubscribe':
        return music_unsubscribe(event)
    else:
        return {
            'statusCode' : 404,
            'body' : 'No/Illegal Type was Passed'
        }

