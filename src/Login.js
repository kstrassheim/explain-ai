import React, { useState, useEffect, useContext } from "react";
import { Redirect } from "react-router-dom";
import GithubIcon from "mdi-react/GithubIcon";
import { AuthContext } from "./App";
import moment from 'moment'

// refresh access token every 1 hour
const refreshInterval = 60 * 60 * 1000;

const handleRefresh = async (csrfToken, dispatch, refreshToken, refreshExpires) => {
  if (refreshToken && refreshExpires) {
    if (moment(refreshExpires).diff(moment()) > 0) {
      const data = await (await fetch('/api/auth_refresh', {
        method: "POST",
        mode: 'same-origin', // no-cors, *cors, same-origin
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        credentials: 'same-origin', // include, *same-origin, omit
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken},
        redirect: 'follow', // manual, *follow, error
        referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
        body: JSON.stringify({refreshToken: refreshToken })
      })).json();

      if (data.accessToken && data.expires) {
        dispatch({ type: "REFRESH", payload: { accessToken:data.accessToken, expires:data.expires }});
        let refreshTimeout = setTimeout(()=>handleRefresh(csrfToken, dispatch, data.refreshToken, data.refreshExpires), refreshInterval);
        dispatch({ type: "SET_REFRESH_TIMEOUT", payload: { refreshTimeout:refreshTimeout }});
        // set refresh timeout again
      }
    }
  }
}

export default function Login(props) {
  const { state, dispatch } = useContext(AuthContext);
  const [data, setData] = useState({ errorMessage: "", isLoading: false });

  useEffect(() => {
    // After requesting Github access, Github redirects back to your app with a code parameter
    const url = window.location.href;
    const hasCode = url.includes("?code=");
    const wasUserLogout = localStorage.getItem("userLogout")
    if (!props.showloginLink && !hasCode && !wasUserLogout) {
      localStorage.removeItem("userLogout")
      const loginLink = document.getElementById('githubLoginLink')
      if (loginLink) loginLink.click();
    }

    localStorage.removeItem("userLogout")

    // If Github API returns the code parameter
    if (hasCode) {
      const newUrl = url.split("?code=");
      window.history.pushState({}, null, newUrl[0]);
      setData({ ...data, isLoading: true });
      // const local_auth_url = `${window.location.protocol}//${window.location.hostname}:${window.location.port}/api/auth`;
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      // Use code parameter and other parameters to make POST request to proxy_server
      fetch('/api/auth', {
        method: "POST",
        mode: 'same-origin', // no-cors, *cors, same-origin
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        credentials: 'same-origin', // include, *same-origin, omit
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken},
        redirect: 'follow', // manual, *follow, error
        referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
        body: JSON.stringify({authCode: newUrl[1] })
      })
        .then(response => response.json())
        .then(data => {
          if (data.user && data.accessToken && data.expires) {
            dispatch({
              type: "LOGIN",
              payload: { user: data.user, isLoggedIn: true, accessToken:data.accessToken, expires:data.expires }
            });

            // start refresh interval
            let refreshTimeout=setTimeout(async ()=>handleRefresh(csrfToken, dispatch, data.refreshToken, data.refreshExpires), refreshInterval);
            dispatch({ type: "SET_REFRESH_TIMEOUT", payload: { refreshTimeout:refreshTimeout }});
          }
          else {
            throw new Error("Login failed: Wrong login response")
          }
        })
        .catch(error => {
          setData({
            errorMessage: "Login failed"
          });
        });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  },[]);

  if (state.isLoggedIn) { 
    // save url to redirect
    let redirectUrl = "/";
    if (localStorage.getItem("loginRedirectPath") && localStorage.getItem("loginRedirectPath") !== window.location.pathname) {
      redirectUrl = localStorage.getItem("loginRedirectPath")
    }

    localStorage.removeItem("loginRedirectPath")
    
    return <Redirect to={redirectUrl} />; 
  }
  const githubLoginUrl = `https://github.com/login/oauth/authorize?scope=user&client_id=${props.clientId}&redirect_uri=${props.redirectUri}`;
  

  return (
      <section className="container">
        <div>
          <span>{data.errorMessage}</span>
          <div className="login-container">
            {data.isLoading ? (
              <div className="loader-container">
                <div className="loader"></div>
              </div>
            ) : (
              <>
                <a id='githubLoginLink'
                  className="login-link"
                  href={githubLoginUrl}
                  onClick={() => {setData({ ...data, errorMessage: "" }); }}
                >
                  <GithubIcon />
                  <span>Login with GitHub</span>
                </a>
              </>
            )}
          </div>
        </div>
      </section>
  );
};