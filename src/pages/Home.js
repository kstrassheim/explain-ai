import React, {useState, useEffect, useContext}  from 'react';
import { useHistory } from "react-router-dom";
import NavMenu from '../NavMenu';
import {Button, ButtonGroup, Modal, Container} from 'react-bootstrap';
import { toast } from 'react-toastify';
import {ArrowClockwise, PlusCircle, PencilSquare, Trash } from 'react-bootstrap-icons';
import Loading from '../Loading';
import './Home.css';
import ExplainList from '../components/ExplainList'
import { AuthContext } from "../App";
import {loadItems as apiLoadItems, deleteItem as apiDeleteItem} from "../api";

function Home(props) {
  const [selectedItem, setSelectedItem] = useState(undefined)
  const [items, setItems] = useState(null);
  const [loading, setLoading] = useState(false)
  const [deleteModalShow, setDeleteModalShow] = useState(false)

  const { state } = useContext(AuthContext);
  const history = useHistory();
  

  const deleteItem = async () => {
    try {
      if (!selectedItem) {return;}
      setLoading(true);
      let data = await apiDeleteItem(state.accessToken, selectedItem);
      
      if (data && data.id === selectedItem.id) {
        let newItems = items.filter(o=>o.id!==data.id);
        setItems(newItems)
        setSelectedItem(null);
        setLoading(false);
        // $(`#${data.id}`).animate({left:"-=2000", height:'0.5em', opacity:0.1}, 300, ()=>{ });
      }
    }
    catch(err) {}
    finally {
      setLoading(false);
    }
  }
  const selectAndDelete = (item) => {
    setSelectedItem(item);
    deleteClick()
  }
  const loadItems = async () => {
    if (!state.accessToken) { return; }
    setLoading(true);
    try {
      let data = await apiLoadItems(state.accessToken);
      if (data) {
        setItems(data)
        //toast.success("Loading items complete");
      }
      else {
        setItems(null)
      }
    }
    catch(err) {}
    finally {
      setLoading(false);
    }
  }

  /// dont use async here because it causes trouble with routing
  useEffect(() => { 
    loadItems();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [props]);

  const onSocketReceive = (data) => {
    //console.log(data);

    switch (data.operation) {
      case "add": toast.info(`Item ${data.item.name} added by ${data.user}`); loadItems(); break;
      case "edit": toast.warning(`Item ${data.item.name} edited by ${data.user}`); loadItems(); break;
      case "delete": toast.error(`Item ${data.item.name} deleted by ${data.user}`); loadItems(); break;
      default: break;
    }
  };

  useEffect(() => { 
    if (props.socket && props.socket.isInitialized()) {
      props.socket.setOnReceiveMethod(onSocketReceive);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [props.socket]);


    const newClick = () => {
      history.push(`/new`)
    }

    const editClick = () => {
      history.push(`/edit/${selectedItem.id}`)
    };

    const deleteClick = () => {
      setDeleteModalShow(true);
    };

    const deleteModalClick = () => {
      deleteItem();
      setDeleteModalShow(false);
    };

    const onItemSelect = (item) => {
      setSelectedItem(item)
    }

    const handleDeleteModalClose = () => setDeleteModalShow(false);

    const buttonIconSize = 18
    return (
        <React.Fragment>
          <Loading visible={loading} />
          <NavMenu>
            <ButtonGroup size="md" >
              <Button variant="success" title="Refresh" onClick={()=>{loadItems()}}><ArrowClockwise size={buttonIconSize} /></Button>
              <Button variant="info" title="New" disabled={selectedItem} onClick={()=>{newClick()}}><PlusCircle size={buttonIconSize} /></Button>
              <Button variant="warning" title="Edit" disabled={!selectedItem} onClick={()=>{editClick()}}><PencilSquare size={buttonIconSize} /></Button>
              <Button variant="danger" title="Delete" disabled={!selectedItem} onClick={()=>{deleteClick()}}><Trash size={buttonIconSize} /></Button>
            </ButtonGroup>
          </NavMenu>
          <div className="d-none d-md-block d-lg-block d-xl-block" style={{height: '8px'}} />
          <main className='homePage'>
            <Container>
            <ExplainList items={items} onItemSelect={onItemSelect} onItemDelete={selectAndDelete}/>
            </Container>
            
          </main>
          <Modal show={deleteModalShow} onHide={handleDeleteModalClose} backdrop="static" keyboard={false} >
            <Modal.Header>
              <Modal.Title>Delete</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              Are you sure to delete the item {"\""}{selectedItem ? selectedItem.name : ''}{"\""} ?
            </Modal.Body>
            <Modal.Footer>
              <ButtonGroup size="lg" >
                <Button variant="success" onClick={handleDeleteModalClose}>No</Button>
                <Button variant="danger" onClick={deleteModalClick}>Yes</Button>
              </ButtonGroup>
            </Modal.Footer>
          </Modal>
        </React.Fragment>
      );
    }
export default Home;