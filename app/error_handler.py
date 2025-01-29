from flask import jsonify
import requests


def handle_api_error(e):
    if isinstance(e, requests.exceptions.RequestException):
        return jsonify({'message': f'Error fetching data from external API: {e}'}), 500
    else:
      return jsonify({'message': f'An unexpected error occurred : {e}'}), 500