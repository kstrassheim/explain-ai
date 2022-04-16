import React, {useState, useEffect, useContext}  from 'react';
import ExplainVisualization from '../components/ExplainVisualization'
import ExplainTextView from '../components/ExplainTextView'
import ExplainDetails from '../components/ExplainDetails'
import {useParams,Redirect}  from 'react-router-dom';
import {Button, ButtonGroup} from 'react-bootstrap';
import { toast } from 'react-toastify';
import {ArrowClockwise, PencilSquare, Lightbulb } from 'react-bootstrap-icons';
import Loading from '../Loading'
import NavMenu from '../NavMenu'
import { AuthContext } from "../App";
import './EditItem.css';
import {loadItem as apiLoadItem, explain as apiExplain} from "../api";

const defaultExplainItem = {
  id: -1,
  text:"", 
  model:"BERT",
  useAnchor:false,
  numFeatures: 6,
  precision:0.95,
  result:null
}

function EditItem(props) {
    
    const [item, setItem] = useState(null)
    const [loading, setLoading] = useState(false)
    const { state } = useContext(AuthContext);
    let { id } = useParams();
    // const id = -1

    const validateInput = () => {
      let txtText = document.getElementById("txtText")
      let txtNumFeatures = document.getElementById("txtNumFeatures")
      let txtPrecision = document.getElementById("txtPrecision")
      let valid = true;
      if (item.text && item.text.length > 0) {
        txtText.classList.remove("invalid");
      }
      else {
        txtText.classList.add("invalid");
        valid = false;
      }

      if (item.numFeatures && item.numFeatures >= 1) {
        txtNumFeatures.classList.remove("invalid");
      }
      else {
        txtNumFeatures.classList.add("invalid");
        valid = false;
      }

      if (item.precision && item.precision >= 0.0 && item.precision <= 1.0) {
        if (txtPrecision) {
          txtPrecision.classList.remove("invalid");
        }
      }
      else {
        txtPrecision.classList.add("invalid");
        valid = false;
      }

      return valid

    }

    const loadItem = async (itemId = -1) => {
      try {
        if (!itemId || itemId < 0) { 
          setItem(defaultExplainItem); 
          return; 
        }
        setLoading(true);
        const data =  await apiLoadItem(state.accessToken, itemId); 
        if (data) {
          setItem(data)
        }
        else {
          setItem(defaultExplainItem);
        }
      }
      catch(err) {}
      finally {setLoading(false)}
    }

    useEffect(() => { 
      loadItem(id);
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [id])

    const onSocketReceive = (data) => {
      //console.log(data);
      if (data.item && data.item.id === id) {
        switch (data.operation) {
          case "edit": toast.warning(`Edited by ${data.user}`); setItem(data.item); break;
          case "delete": toast.error(`Deleted by ${data.user}`); loadItem(); break;
          default: break;
        }
      }
    };
  
    useEffect(() => { 
      if (props.socket && props.socket.isInitialized()) {
        props.socket.setOnReceiveMethod(onSocketReceive);
      }
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [props.socket]);

    const explainClick = async () => {
      try {
        if (!validateInput()) { return; }
        setLoading(true);
        const data = await apiExplain(state.accessToken, item);
        if (data) {
          setItem(data)
        }
      }
      catch(err) {}
      finally {setLoading(false)}
    };

    const switchToEditModeClick = () => {
      if (!item) { return; }
      // reset result to enable edit mode
      let o = {}
      Object.assign(o, item)
      o.result = null;
      setItem(o);
    };

    const ddlModelChange = (event) => {
      let o = {}
      Object.assign(o, item)
      o.model = event.target.value
      setItem(o);
    };

    const txtNumFeaturesChanged = (event) => {
      let o = {}
      Object.assign(o, item)
      o.numFeatures = parseInt(event.target.value)
      setItem(o);
    };

    const cbAnchorChanged = (event) => {
      let o = {}
      Object.assign(o, item)
      o.useAnchor = event.target.checked
      setItem(o);
    };

    const txtPrecisionChanged = (event) => {
      let o = {}
      Object.assign(o, item)
      o.precision = parseFloat(event.target.value)
      setItem(o);
    };

    const txtTextChanged = (event) => {
      let o = {}
      Object.assign(o, item)
      o.text = event.target.value
      setItem(o);
      validateInput();
    };
    const buttonIconSize = 18

    if (!id && item && item.id && item.id !== -1) {
      return <Redirect to={`/edit/${item.id}`} />
    }

    return (
        <main className='editItem'>
          <Loading visible={loading} />
          <NavMenu>
            <ButtonGroup size="md" >
              <Button variant="success" title="Refresh" onClick={()=>{loadItem()}}><ArrowClockwise size={buttonIconSize} /></Button>
              {
                  item ? (item.result ? 
                  <Button variant="warning" title="Edit" onClick={()=>{switchToEditModeClick()}}><PencilSquare size={buttonIconSize} /></Button>
                  :
                  <Button variant="danger" title="Explain" onClick={()=>{explainClick()}}><Lightbulb size={buttonIconSize} /></Button>
                  ) : <React.Fragment />
              }
            </ButtonGroup>
          </NavMenu>
          { 
              (item ? 
                (item.result ?
                        <React.Fragment>
                          <p><ExplainTextView text={item.text} result={item.result.explainResult} anchorNames={item.result.explainAnchorNames} anchorPrecision={item.result.explainAnchorPrecision} /></p>
                          <span>Explain Duration: {item.result.durationExplainStr}</span>
                          <ExplainVisualization explainResult={item.result.explainResult} />
                          <ExplainDetails result={item.result}  item={item} />
                        </React.Fragment>
                      : <React.Fragment>
                          <br />
                          <div className="form-group">
                            <div class="mb-3">
                              <label for="ddlModel" class="form-label">ML Model:</label>
                              <select id="ddlModel" class="form-select" aria-label="Select Explain Engine" value={item.model} onChange={ddlModelChange}>
                                <option value="TfIdf">TfIdf</option>
                                <option value="LSTM">LSTM</option>
                                <option value="BERT">BERT</option>
                              </select>
                            </div>
                            <div class="mb-3">
                              <label for="txtNumFeatures" class="form-label">Lime Num Features:</label>
                              <input type="number" class="form-control" id="txtNumFeatures" placeholder="6" min="1" value={item.numFeatures} onChange={txtNumFeaturesChanged} />
                            </div>
                            <div class="mb-3 form-check">
                              <label class="cbAnchor" for="cbAnchor">Use Anchor additionaly (can be very slow):</label>
                              <input class="form-check-input" type="checkbox" checked={item.useAnchor} id="cbAnchor" onChange={cbAnchorChanged} />
                            </div>
                            { item.useAnchor ? 
                              <div class="mb-3">
                                <label for="txtPrecision" class="form-label">Anchor Precision:</label>
                                <input type="number" class="form-control" id="txtPrecision" min="0.0" max="1.0" step="0.01" value={item.precision} onChange={txtPrecisionChanged} />
                              </div> : <React.Fragment />
                            }
                            <textarea id="txtText" type="textarea" className="form-control" placeholder="Please enter some classification text" rows="20" onChange={txtTextChanged} value={item.text} />
                            <div>
                              { (item && item.text ? item.text.length : 0)} Characters, { (item && item.text ? item.text.split(' ').length : 0)} Words
                            </div>
                          </div>
                        </React.Fragment>
                )
             :  <React.Fragment />)
          }
        </main>
      );
    }
export default EditItem;