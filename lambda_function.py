import json
import boto3
import base64

s3 = boto3.client('s3')
bucket = 'password-manager-1'

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

            # Encode using base64
            password_bytes = password.encode()
            base64_bytes = base64.b64encode(password_bytes)

            encoded_password = base64_bytes.decode()

            try:
                response = s3.get_object(
                    Bucket = bucket,
                    Key = 'passwords.json'
                )

                # Store previous data and add onto it
                prev_data = json.loads(response['Body'].read().decode('utf-8'))

            except:

                prev_data = {}

            prev_data[url] = {
                'username': username,
                'password': encoded_password,
            }

            # Update the password.json file in S3 bucket with updated data
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
            # Optional parameter to decrypt all encrypted passwords when getting
            decrypt = event.get('decrypt', False)

            try:
                response = s3.get_object(
                    Bucket = bucket,
                    Key = 'passwords.json'
                )

                all_data = json.loads(response['Body'].read().decode('utf-8'))

                if decrypt:
                    # Decrypt (if existing password was never encrypted in the first place, just keep it in place)
                    for urls in all_data:
                        p = all_data[urls]['password']

                        try:
                            base64_bytes = p.encode()
                            password_bytes = base64.b64decode(base64_bytes)
                            decoded_password = password_bytes.decode()
                        except:
                            decoded_password = p

                        all_data[urls]['password'] = decoded_password

                return {
                    'statusCode': 200,
                    'body': json.dumps(all_data)
                }

            except Exception as e:
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
    
        
    

        

