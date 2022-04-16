import React from 'react';

function Loading(props) {

    return props.visible ? <div style={{
        zIndex: 9998,
        content: '',
        display:'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        background: 'radial-gradient(rgba(20, 20, 20,0.6), rgba(0, 0, 0, 0.6))',
        //background: '-webkit-radial-gradient(rgba(20, 20, 20,0.6), rgba(0, 0, 0,0.6))'
    }}> <div className="spinner-border" style={{
        zIndex: 9999,
        width: '3rem', 
        height: '3rem'
    }} role="status"><span className="sr-only"></span></div></div> : '';
}

export default Loading;