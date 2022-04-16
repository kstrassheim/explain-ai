export const initialState = {
    // isLoggedIn: JSON.parse(localStorage.getItem("isLoggedIn")) || false,
    // user: JSON.parse(localStorage.getItem("user")) || null,
    // authCode: JSON.parse(localStorage.getItem("accessToken")) || null
    isLoggedIn: false,
    user: null,
    accessToken:  null,
    expires:null,
    refreshTimeout:null
    // client_id: process.env.REACT_APP_CLIENT_ID,
    // redirect_uri: process.env.REACT_APP_REDIRECT_URI,
    // client_secret: process.env.REACT_APP_CLIENT_SECRET,
    // proxy_url: process.env.REACT_APP_PROXY_URL
  };
  
  export const reducer = (state, action) => {
    switch (action.type) {
      case "LOGIN": {
        // localStorage.setItem("isLoggedIn", JSON.stringify(action.payload.isLoggedIn))
        // localStorage.setItem("user", JSON.stringify(action.payload.user))
        // localStorage.setItem("accessToken", JSON.stringify(action.payload.accessToken))
        return {
          ...state,
          isLoggedIn: action.payload.isLoggedIn,
          user: action.payload.user,
          accessToken: action.payload.accessToken,
          expires:action.payload.expires
        };
      }
      case "REFRESH": {
        // localStorage.setItem("isLoggedIn", JSON.stringify(action.payload.isLoggedIn))
        // localStorage.setItem("user", JSON.stringify(action.payload.user))
        // localStorage.setItem("accessToken", JSON.stringify(action.payload.accessToken))
        return {
          ...state,
          accessToken: action.payload.accessToken,
          expires:action.payload.expires
        };
      }

      case "SET_REFRESH_TIMEOUT": {
        return {
          ...state,
          refreshTimeout: action.payload.refreshTimeout
        };
      }
      case "LOGOUT": {
        // clear token refresh timeout
        if(state.refreshTimeout) {
          clearTimeout(state.refreshTimeout);
        }
        return {
          ...state,
          isLoggedIn: false,
          user: null,
          accessToken:null,
          expires:null,
          refreshTimeout:null
        };
      }
      default:
        return state;
    }
  };