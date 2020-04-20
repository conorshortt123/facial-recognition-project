from FrontEnd import app

# check to see if this is the main thread of execution
if __name__ == '__main__':

    # start the flask app
    app.run(debug=True, use_reloader=False)
