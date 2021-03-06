from base64 import b64encode
import httplib2
import json

http = httplib2.Http()

base_url = 'https://vision.googleapis.com/v1/images:annotate?key='


def encode_image(image_path, charset):
    with open(image_path, 'rb') as image:
        b64_img = b64encode(image.read())

    return b64_img.decode(charset)


def get_response(b64encoded_image):
    with open('key.json', 'r') as jsonFile:    # local API key store
        key = json.load(jsonFile)
        req_url = base_url + key['api-key']

    req_body = {
      "requests": [
        {
          "image": {
            "content": b64encoded_image
          },
          "features": [
            {
                "type": "LABEL_DETECTION",
                "maxResults": 15
            },
            {
                "type" : "TEXT_DETECTION",
                "maxResults": 1
            },
            {
                "type" : "WEB_DETECTION",
                "maxResults": 1
            }
          ]
        }
      ]
    }

    req_headers = {"Content-Type": "application/json; charset=utf-8"}

    (headers, body) = http.request(req_url, 'POST', body=json.dumps(req_body), headers=req_headers)
    return headers, body


def image_label_detection(data_path):
    with open('./test.json') as data_file:
        data = json.load(data_file)
    label = []
    score = []
    length = len(data["responses"][0]["labelAnnotations"])

    for i in range(length):  # label과 그에 대응하는 score 저장
        if(data["responses"][0]["labelAnnotations"][i]["score"] > 0.6):
            label.append(data["responses"][0]["labelAnnotations"][i]["description"])
            score.append(data["responses"][0]["labelAnnotations"][i]["score"])
            if(label[len(label)-1] == "product" or label[len(label)-1] == "produce"):
                label.pop()
                label.append(data["responses"][0]["webDetection"]["webEntities"][0]["description"])

    length = len(label)

    # 조건에 맞게 label 잘라내기
    if(score[0] > 0.95):
        while(score[length-1] < 0.95):
            label.pop()
            length = len(label)
    elif(sum(score)/length > 0.75):
        while(score[length-1] < 80):
            label.pop()
            length = len(label)
    else:
        while(score[length -1] < 70):
            label.pop()
            length = len(label)

    return label


def image_text_detection(data_path):
    with open('./test.json') as data_file:
        data = json.load(data_file)

    return data["responses"][0]["textAnnotations"][0]["description"]


if __name__ == '__main__':
    local_image_path = "./orange.jpg"    # You have to fix the image path here.
    (headers, body) = get_response(encode_image(local_image_path, 'ascii'))

    # 이렇게 하면 파일을 따로 저장해야하고
    f = open("./test.json", 'w')
    f.write(body.decode('utf-8'))
    f.close()

    print(image_label_detection("./test.json"))
    """
    with open('./test.json') as data_file:
        data = json.load(data_file)
    size = len(data["responses"][0]["labelAnnotations"])
    print(data["responses"][0]["webDetection"]["webEntities"][0]["description"])  # 값 하나하나 접근하기
    """

    """ 이렇게 하면 문자 하나하나씩 접근해야돼요
    str = body.decode('utf-8')
    print(str)
    """
