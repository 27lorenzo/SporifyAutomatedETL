from flask import Flask, request

app = Flask(__name__)
auth_code = None


@app.route('/callback')
def callback():
    global auth_code
    auth_code = request.args.get('code')
    print(f"Authorization Code: {auth_code}")
    return "Authorization Code received. You can close this window."

def get_authorization_code():
    global auth_code
    return auth_code

if __name__ == '__main__':
    app.run(port=8888)
