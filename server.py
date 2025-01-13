from flask import Flask , request
from findAns import process
app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello world"

@app.route('/question' , methods = ['POST'])
def question():
    question = request.json['question']
    content = request.json['content']
    print(question)
    solution = process(content , question)
    print(solution[0]['answer'])
    return {"response" : solution[0]['answer'] , "response_time" : solution[1] }

if __name__ == '__main__':
    app.run(debug=True)