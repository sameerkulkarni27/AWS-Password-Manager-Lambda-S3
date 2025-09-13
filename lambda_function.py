import json
import boto3
from cryptography.fernet import Fernet

s3 = boto3.client('s3')
bucket = 'password-manager-1'

def get_key():
    key = Fernet.generate_key()
    return key



def lambda_handler(event, context):
    action = event.get('action', 'unknown')

    try:
        if (action == "test"):

            return {
                'statusCode': 200,
                'body': json.dumps('Test worked!')
            }

        elif (action == "s3"):

            response = s3.list_objects_v2(Bucket = bucket)
            count = response.get('KeyCount', 0)

            return {
                'statusCode': 200,
                'body': json.dumps(f'S3 worked! There are {count} objects in the bucket')
            }

        elif (action == "store"):

            url = event.get('url')
            username = event.get('username')
            password = event.get('password')  

            # Encrypt 
            key = get_key()
            f = Fernet(key)

            encrypted_password = f.encrypt(password).decode()

            try:

                response = s3.get_object(
                    Bucket = bucket,
                    Key = 'passwords.json'
                )

                prev_data = json.loads(response['Body'].read().decode('utf-8'))

            except:

                prev_data = {}

            prev_data[url] = {
                'username': username,
                'password': encrypted_password,
            }

            s3.put_object(
                Body = json.dumps(prev_data),
                Bucket = bucket,
                Key = 'passwords.json'
            )

            return {
                'statusCode': 200,
                'body': json.dumps(f'Store worked! Stored username/encrypted password for {url}')
            }

        elif (action == "get"):
            
            decrypt = event.get('decrypt', False)

            try:
                response = s3.get_object(
                    Bucket = bucket,
                    Key = 'passwords.json'
                )

                all_data = json.loads(response['Body'].read().decode('utf-8'))

                if decrypt:
                    # Decrypt 
                    key = get_key()
                    f = Fernet(key)

                    for url in all_data:
                        p = all_data[url]['password']

                        decrypted_password = f.decrypt(p).decode()

                        all_data[url]['password'] = decrypted_password

                return {
                    'statusCode': 200,
                    'body': json.dumps(all_data)
                }

            except:

                return {
                    'statusCode': 404,
                    'body': json.dumps('Passwords not found!')
                }

        else:

            return {
                'statusCode': 400,
                'body': json.dumps('Unknown action!')
            }
           
    except Exception as e:
        print(f"Error: {e}")
        raise e  
    
        
    

        

