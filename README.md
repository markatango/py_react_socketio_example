# Python / gunicorn - React / javascript socket.io demo
Here is an example of two-way communication via `socket.io` between a python / gunicorn server and a react / javascript client. 
Because socket.io versions in python and node have to be coordinated closely, this code has been tested with specific node, react, and python versions. 
Accordingly, it may be necessary for the developer to modify the code and module versions to work in other environments.

## Behavior
The server emits a `message` event every two seconds with data: 
```
{
  'randomNumber': <random number between 0 and 1>,
  'boolean': <true | false>
}
```
The client displays the randomNumber in a text box, and the boolean is visualized as an indicator that changes colors in response to the boolean value.

The client has two input elements: a date/time selector and a button.  Changes made on the date/time selector are emitted via socket.io-client on a
`datetime_change` event. The server reports the event on standard output (i.e., the console) and acknowledges receipt by emitting a `datetime_ack` event.

Clicking the button emits a `toggle_button` event. The server reports this event on standard output and acknowledges receipt by emitting a `button_ack` event.

## Security

Next to nothing.  This is demo code only, so please consider hardening the server and client if contemplating using this code in a widely-deployed scenario.

TO DO:  
* Explore broader version compatibilities.
* Test production build of client and integrate into server

## Environment
Implementing socket.io communications between python and node applications requires careful coordination of python, node, react, and socket.io versions. Accordingly, this code as written requires specific module verions as follows:

* python: 3.8.10
* node: >=18.0.0
* npm: >=8.0.0
* react: ^18.2.0
* react-dom: ^18.2.0
* socket.io-client: ^4.8.1

## Start the python server:
`cd server`

__Check Python version__

`python3 --version  # Should show 3.8.10`

__Install dependencies__

`python3 -m pip install -r requirements.txt`

__Run the server...__

`python3 run_server.py`

This code asks wether the (d)evelopment or (p)roduction server is to be run.

__...or run the development server directly using flask__

`python3 server.py`

__...or run the production server directly using gunicorn__

`gunicorn -c gunicorn.conf.py server:app`

## Set up client
`cd client`

__Check Node version__

`node --version  # Should show v22.16.0`

__Setup script:__

```chmod +x setup_client.sh
./setup_client.sh
```

__Or manually:__
```npx create-react-app client
cd client
npm install socket.io-client@^4.7.5
```

__Start development server__

`npm start`
