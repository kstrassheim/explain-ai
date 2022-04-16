import 'bootstrap/dist/css/bootstrap.min.css';
import React, {createContext, useRef, useEffect, useReducer}  from 'react';
import { Switch,  Route } from 'react-router';
import NotFound from './NotFound'
import Login from './Login'
import Home from './pages/Home'
import EditItem from './pages/EditItem'
import About from './pages/About'
import Toastr from './Toastr'
import { initialState, reducer } from "./store/reducer";
import {ApiItemSocket} from "./api";
export const AuthContext = createContext();

function App(props) {
  const [state, dispatch] = useReducer(reducer, initialState)
  const socket = useRef(new ApiItemSocket(window.location.protocol === 'https:' ? 'wss:' : 'ws:',  window.location.host, 'socket/itemsocket'));

  const initSocket = () => {
    if (!state.accessToken) { return; }
      socket.current.init(state.accessToken);
    };

    // const closeSocket = () => {
    //   if (socket && (socket.readyState === WebSocket.CONNECTING || socket.readyState === WebSocket.OPEN)) {
    //     socket.close();
    //     socket.current = null;
    //   }
    // }

    useEffect(() => { 
      initSocket();
      // eslint-disable-next-line react-hooks/exhaustive-deps
    },[state.accessToken]);

  return (
    <AuthContext.Provider
      value={{
        state,
        dispatch
      }}
    >
      <div className="App">
        <Toastr />  
        <Switch>
          <Route exact path='/login' component={() => <Login showloginLink={false} clientId={document.getElementById('authClientId').value} redirectUri={`${window.location.protocol}//${window.location.hostname}:${window.location.port}/login`} />} />
          <Route exact path='/' component={() => <Home socket={socket ? socket.current: null}  />} />
          <Route exact path='/edit/:id' component={() => <EditItem socket={socket ? socket.current: null} />} />
          <Route exact path='/new' component={() => <EditItem socket={socket ? socket.current: null} />} />
          <Route exact path='/about' component={() => <About />} />
          <Route component={() => <NotFound  />} />
        </Switch>
      </div>
    </AuthContext.Provider>
  );
}

export default App;
