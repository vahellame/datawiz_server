import json

from flask import Flask, request, json, Response

from psycopg2.extras import Json

from utils.sql import execute_sql, str_to_binary, binary_to_str
from config import *

app = Flask(__name__)
app.json_encoder.ensure_ascii = False
app.config['JSON_AS_ASCII'] = False


@app.route('/barcodes', methods=['GET'])
def handle_barcodes():
    barcodes = execute_sql(
        "SELECT * "
        "FROM barcodes "
        "ORDER BY id",
        POSTGRES_CONNECTION_PARAMS
    )
    barcodes_len = len(barcodes)
    for i in range(barcodes_len):
        barcodes[i]['code'] = binary_to_str(barcodes[i]['code'])
        barcodes[i]['text'] = binary_to_str(barcodes[i]['text'])
        barcodes[i]['email'] = binary_to_str(barcodes[i]['email'])
        barcodes[i]['display_name'] = binary_to_str(barcodes[i]['display_name'])

    response_dict = {
        'status': 'ok',
        'barcodes': barcodes
    }
    response_json = json.dumps(response_dict, ensure_ascii=False)
    response = Response(response_json, content_type="application/json; charset=utf-8")
    return response


@app.route('/add_barcode', methods=['POST'])
def handle_add_barcode():
    data = json.loads(request.data.decode())
    print(data)
    code = str_to_binary(str(data['code']))
    text = str_to_binary(data['text'])
    email = str_to_binary(data['email'])
    display_name = str_to_binary(data['display_name'])
    reviews = Json([])
    barcode_id = execute_sql(
        f"INSERT INTO barcodes(code, text, email, display_name, reviews) "
        f"VALUES ({code}, {text}, {email}, {display_name}, {reviews}) "
        f"RETURNING id",
        POSTGRES_CONNECTION_PARAMS,
    )[0]['id']

    response_dict = {
        'status': 'ok',
        'barcode_id': barcode_id
    }
    response_json = json.dumps(response_dict, ensure_ascii=False)
    response = Response(response_json, content_type="application/json; charset=utf-8")
    return response


@app.route('/add_review', methods=['POST'])
def handle_add_review():
    data = json.loads(request.data.decode())
    barcode_id = data['barcode_id']
    barcode_reviews = execute_sql(
        f"SELECT reviews "
        f"FROM barcodes "
        f"WHERE id={barcode_id}",
        POSTGRES_CONNECTION_PARAMS
    )[0]['reviews']
    barcode_reviews.append(
        {
            'text': data['text'],
            'email': data['email'],
            'display_name': data['display_name'],
        }
    )
    execute_sql(
        f"UPDATE barcodes "
        f"SET reviews={Json(barcode_reviews)} "
        f"WHERE id={barcode_id}",
        POSTGRES_CONNECTION_PARAMS
    )

    response_dict = {
        'status': 'ok',
    }
    response_json = json.dumps(response_dict, ensure_ascii=False)
    response = Response(response_json, content_type="application/json; charset=utf-8")
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)


