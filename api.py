import sqlite3
from flask import Flask, jsonify, request, make_response
import pickle
import numpy as np
from flask_restful import Resource, Api, reqparse
from sklearn.ensemble import RandomForestClassifier

from db_methods import compute_most_frequent, compute_mean_value, \
    add_to_tables, print_posts, compare_prediction_with_two_last

# creating the flask app
app = Flask(__name__)
# creating an API object
api = Api(app)

CLASS_REQUEST = 'classification_requests'
CLASS_PARAMS = 'classification_request_params'
F1 = 'f1'
F2 = 'f2'
F3 = 'f3'

DATABASE_PATH = 'data/database.db'
MODEL_PATH = 'data/tree_model.pkl'

letter_to_number = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4}
# load the model from disk
loaded_model = pickle.load(open(MODEL_PATH, 'rb'))

class Stats(Resource):
    def get(self):
        conn = sqlite3.connect(DATABASE_PATH)

        most_frequent_f3 = compute_most_frequent(conn, F3)
        mean_f1 = compute_mean_value(conn, F1)
        mean_f2 = compute_mean_value(conn, F2)

        #print_posts(conn, CLASS_REQUESTS)
        #print_posts(conn, CLASS_PARAMS)

        conn.close()
        return jsonify({"mean_f1": mean_f1, "mean_f2": mean_f2, "most_frequent_f3": most_frequent_f3})



# Define parser and request args
parser = reqparse.RequestParser()
parser.add_argument(F3, type=str, required=True)
parser.add_argument(F1, type=str, required=True)
parser.add_argument(F2, type=str, required=True)

class Classify(Resource):
    def get(self):
        try:
            args = parser.parse_args()
        except Exception as e:
            return jsonify({"status": "ERROR", "error_message": "One of arguments f1, f2, f3 is missing."})

        try:
            f1 = float(args['f1'])
        except Exception as e:
            return jsonify({"status": "ERROR", "error_message": "f1 is not a float."})

        try:
            f2 = float(args['f2'])
        except Exception as e:
            return jsonify({"status": "ERROR", "error_message": "f2 is not a float."})

        f3 = args['f3']

        # TODO: check parameter types
        if None in args.values():
            return jsonify({"status": "ERROR", "error_message": "f1 is not a float."})


        # testing version
        #pred = 1 if max(f1, f2) > 1 else 0

        # make the prediction
        if f3 not in letter_to_number.keys():
            return jsonify({"status": "ERROR", "error_message": "f3 is not in {A,B,C,D,E}."})

        data = np.array([f1, f2, letter_to_number[f3]]).reshape(1, 3)
        pred = int(loaded_model.predict(data))


        # save it into the database
        conn = sqlite3.connect(DATABASE_PATH)

        # compare prediction with two last predictions
        response_status = compare_prediction_with_two_last(conn, pred)
        add_to_tables(conn, f1, f2, f3, pred, response_status)

        conn.close()

        return jsonify({"predicted_class": pred, "status": response_status})

api.add_resource(Stats, '/stats')
api.add_resource(Classify, '/classify')

if __name__ == '__main__':

    app.run(debug=True)

