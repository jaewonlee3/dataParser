from flask import Flask
from flask import request
import testParser

app = Flask(__name__)

@app.route('/')
def home():
    return 'home'

@app.route('/info/<myText>')
def info(myText):
    return 'echo: %s'%(myText)

@app.route('/postService/', methods=['POST'])
def postService():
    return request.get_json()

@app.route('/impactAnalysis', methods=['POST'])
def impactAnalysis():
    inputDto = request.get_json()
    result = testParser.myParser(inputDto)
    return result

if __name__ == "__main__":
    app.run()