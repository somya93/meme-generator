# from flask import Flask
# from flask_restful import Api, Resource
#
# app = Flask(__name__)
# api = Api(app)
#
#
# class MemeGenerator(Resource):
#     def get(self):
#         return {"data": "Get request"}
#
#     def post(self):
#         return {"data": "Posted"}
#
#
# api.add_resource(MemeGenerator, "/generatememe/")
#
# if __name__ == "__main__":
#     app.run()
