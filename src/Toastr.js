import React, { Component } from 'react';    
import { ToastContainer } from 'react-toastify';    
import 'react-toastify/dist/ReactToastify.css';    
import './Toastr.css';    
class Toastr extends Component {    
  render(){    
    return (  
      <ToastContainer autoClose="1000"  />    
    );    
  }    
}    
export default Toastr 