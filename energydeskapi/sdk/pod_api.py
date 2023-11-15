from flask import Flask

#for kubernetes services that do not have a rest api but need readiness and liveness prob.
def start_pod_api(port: int, callback_readiness = None, callback_liveness = None):
    app = Flask(__name__)

    @app.route('/liveness')
    def liveness():
        if not callback_liveness is None:
            callback_liveness()
        return "OK"

    @app.route('/readiness')
    def readiness():
        if not callback_readiness is None:
            callback_readiness()
        return "OK"

    app.run(host='0.0.0.0', port=port)
