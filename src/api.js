const postJSON = async (url, accessToken, params = {}) => {
    params["accessToken"] = accessToken
    return await (await fetch(url, {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        mode: 'same-origin', // no-cors, *cors, same-origin
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        credentials: 'same-origin', // include, *same-origin, omit
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value},
        redirect: 'follow', // manual, *follow, error
        referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
        body: JSON.stringify(params)
      })).json()
}

const loadItems = async (accessToken) => {
    return postJSON(`/api/items`, accessToken);
}

const loadItem = async (accessToken, id) => {
    return postJSON(`/api/item`, accessToken, {id:id});
}

const deleteItem = async (accessToken, item) => {
    return postJSON(`/api/deleteitem`, accessToken, {item:item});
}

const explain = async (accessToken, item) => {
    return postJSON(`/api/explain`, accessToken, {item:item});
}

class ApiItemSocket {
    _protocol = null;
    _host = null;
    _path = null;

    _socket = null;
    _onreceive = null

    constructor(protocol, host, path) {
        this._protocol = protocol;
        this._host = host;
        this._path = path;
    }

    isOpen() {  return this._socket.readyState === WebSocket.OPEN; }
    isInitialized() { return this._socket !== null;}

    init(accessToken) {
        if (!this._socket || this._socket.readyState === WebSocket.CLOSING || this._socket.readyState === WebSocket.CLOSED)
        {
            if (this.socket) { this.close(); }
            this._socket = new WebSocket(`${this._protocol}//${this._host}/${this._path}`,accessToken);
            this._socket.onclose = (e) => { 
                console.log("Closed websocket connection: restarting"); 
                this.init(accessToken); 
                this.setOnReceiveMethod(this._onreceive); 
            };
        }
    }

    setOnReceiveMethod(onreceive) {
        if (!this._socket) { return; }
        this.__onreceive = onreceive;
        this._socket.onmessage = (e) => {
            if (this.__onreceive) {
                this.__onreceive(JSON.parse(e.data));
            }
        };
    }

    send(data) {
        if (this._socket.isOpen()) {
            this._socket.send(JSON.stringify(data));
        }
    }

    close() {
        this._socket.onclose = () => {};
        if (this._socket && (this._socket.readyState === WebSocket.CONNECTING || this._socket.readyState === WebSocket.OPEN)) {
            this._socket.close();
        }
    }
}


export {postJSON, loadItems, loadItem, deleteItem, explain, ApiItemSocket};