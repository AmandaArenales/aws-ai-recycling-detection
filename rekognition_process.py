import boto3
import pandas as pd

bucket = 'ai-recycling-project'
folder = 'images/'

rekognition = boto3.client('rekognition')
s3 = boto3.client('s3')

def list_images(bucket, prefix):
    objects = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    
    image_list = []
    for obj in objects.get('Contents', []):
        key = obj['Key']
        if not key.endswith('/') and key.lower().endswith(('.jpg', '.png')):
            image_list.append(key)
    return image_list

def analyze_image_bytes(bucket, key):
    obj = s3.get_object(Bucket=bucket, Key=key)
    img_bytes = obj['Body'].read()
    result = rekognition.detect_labels(
        Image={'Bytes': img_bytes},
        MaxLabels=10,
        MinConfidence=85
    )
    
    label_list = []
    top_label = None
    top_confidence = 0

    for label in result['Labels']:
        if label['Confidence'] > top_confidence:
            top_label = label['Name']
            top_confidence = label['Confidence']
    
    if top_label is not None:
        label_list.append({
            'image': key,
            'label': top_label,
            'confidence': top_confidence
        })
    
    return label_list

all_results = []
images = list_images(bucket, folder)

for image_key in images:
    print(f"Analyzing {image_key}...")
    try:
        results = analyze_image_bytes(bucket, image_key)
        for res in results:
            all_results.append(res)
    except Exception as e:
        print(f"Error analyzing {image_key}: {e}")

df = pd.DataFrame(all_results)
df.to_csv('results.csv', index=False)
print("File results.csv saved successfully!")



