import React, { useState, useContext } from 'react';
import { Collapse, Navbar, NavbarBrand, NavbarToggler, NavItem, NavLink } from 'reactstrap';
import { Link, Redirect } from 'react-router-dom';
import './NavMenu.css';
import { AuthContext } from "./App";
import moment from 'moment'

function NavMenu(props) {
    const title = document.getElementById('websiteTitle') ? document.getElementById('websiteTitle').value : 'Explain-AI'
    // NAVIGATION
    const [collapsed, setCollapsed] = useState(true);
    const toggleNavbar = () => { setCollapsed(!collapsed)  }

    // LOGIN 
    const { state, dispatch } = useContext(AuthContext);
    // check if whether user is not logged in or token is expired
    if (!state.isLoggedIn || moment(state.expires).isBefore(moment())) { 
        // save url to redirect
        localStorage.setItem("loginRedirectPath", window.location.pathname)
        return <Redirect to="/login" />; 
    }
    const { avatar_url, login } = state.user
    const handleLogout = () => { 
        localStorage.setItem("userLogout", true)
        dispatch({ type: "LOGOUT" }); 
    } 

    return (
        <header>
            <Navbar className={"navbar-expand-sm fixed-top navbar-toggleable-sm"} light={true}>
                <div className="container-fluid">
                    <NavbarBrand>
                        <img src="static/logo-light-57x57.png" width="32" height="32" alt="Logo" style={{ marginTop: '-4px', marginRight:'7px'}} />
                        <span style={{marginRight:'50px'}} className='d-none d-sm-inline pr-3'>{title}</span>
                        { props.children ? props.children : <React.Fragment /> }
                        <img src={avatar_url} className='ms-1 ms-sm-3' width="32" height="32" alt={login} style={{borderRadius:'5px'}} onDoubleClick={()=> handleLogout()} title={login}/>
                    </NavbarBrand>
                    
                    <NavbarToggler onClick={toggleNavbar} className="mr-2 navbar-toggler navbar-toggler-right" />
                    <Collapse className="d-sm-inline-flex flex-sm-row-reverse" isOpen={!collapsed} navbar>
                    
                    <ul className="navbar-nav flex-grow">
                        <NavItem><NavLink tag={Link} to="/">Home</NavLink></NavItem>
                        <NavItem><NavLink tag={Link} to="/about">About</NavLink></NavItem>
                    </ul>
                    
                    </Collapse>
                    
                </div>
            </Navbar>
        </header>
    );
}

export default NavMenu;
