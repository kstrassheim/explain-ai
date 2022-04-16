import React, {useState, useEffect, useContext}  from 'react';
import ExplainVisualization from '../components/ExplainVisualization'
import ExplainTextView from '../components/ExplainTextView'
import ExplainDetails from '../components/ExplainDetails'
import {useHistory, useParams,Redirect}  from 'react-router-dom';

import {Container, Row, Col, Button, Form} from 'react-bootstrap';
import { toast } from 'react-toastify';
import {PencilSquare} from 'react-bootstrap-icons';
import Loading from '../Loading'
import NavMenu from '../NavMenu'
import { AuthContext } from "../App";
import './EditItem.css';
import {loadItem as apiLoadItem, explain as apiExplain} from "../api";


const defaultExplainItem = {
  id: -1,
  text:"", 
  model:"BERT",
  explainer: {
    name: "LIME",
    num_features: 10,
    num_samples: 100
  }
}

const defaultExplainItemLIME = {
  name: "LIME",
  num_features: 10,
  num_samples: 100
}


const defaultExplainItemIterativeLIME = {
  name: "IterativeLIME",
  num_features: 10,
  min_samples: 10,
  max_samples: 1000,
  step_size: 100,
  distance_metric: "MSE",
  error_cutoff: 0.001
}
const defaultExplainItemMultiStepLIME = {
  name: "MultiStepLIME",
  select: 'Combined',
  num_features: 10,
  min_samples: [10, 10],
  max_samples: [1000, 1000],
  step_size: [100, 100],
  distance_metric: ['MAE', 'MAE'],
  error_cutoff: [0.001, 0.001]
}
const defaultAnchor = {
  name: "Anchor",
  num_features: 10,
  precision: 0.95
}


const default_explainer = {
  'LIME' : defaultExplainItemLIME,
  'IterativeLIME': defaultExplainItemIterativeLIME,
  'Anchor' : defaultAnchor,
  'MultiStepLIME' : defaultExplainItemMultiStepLIME
}

function getDefaultExplainer(explainer){
  if(default_explainer[explainer]){
    return {...default_explainer[explainer]}
  }else{
    return {...default_explainer['LIME']}
  }
}

function EditItem(props) {
    const history = useHistory()
    const [item, setItem] = useState(null)
    const [loading, setLoading] = useState(false)
    const [edit] = useState(false)
    const { state } = useContext(AuthContext);
    const [explainLevel, setExplainLevel] = useState(0)
    let { id } = useParams();
 
    const validateInput = () => {
      return true;
      // let txtText = document.getElementById("txtText")

      // let valid = true;
      // if (item.text && item.text.length > 0) {
      //   txtText.classList.remove("invalid");
      // }
      // else {
      //   txtText.classList.add("invalid");
      //   valid = false;
      // }

      // return valid

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

    
    if (!id && item && item.id && item.id !== -1) {
      return <Redirect to={`/edit/${item.id}`} />
    }

    const changeExplainerParameter = (event, target, parse=null, index=null) => {
      let o = {}
      Object.assign(o, item)
      if(index==null) {
        o.explainer[target] = parse == null ? event.target.value : parse(event.target.value)
      } else {
        console.log("changeExplainerParameter")
        console.log(o.explainer[target][index])
        o.explainer[target][index] = parse == null ? event.target.value : parse(event.target.value)
      }
      
      setItem(o);
    }
    const explainerForms = (explainer) => {
      switch(explainer){
        case 'LIME':
          return (
            <React.Fragment>
            <h4>LIME settings:</h4>
            <Form.Group>
              <Form.Label>Number of features</Form.Label>
              <Form.Control disabled={item.result ? true : false} as="input" type="number" min="2" step="1.0" value={item.explainer.num_features ? item.explainer.num_features : 100} onChange={(event) => changeExplainerParameter(event, "num_features", parseInt)}/>
            </Form.Group>
            <Form.Group>
              <Form.Label>Number of samples</Form.Label>
              <Form.Control disabled={item.result ? true : false} as="input" type="number" min="2" step="1.0" value={ item.explainer.num_samples ? item.explainer.num_samples : 100} onChange={(event) => changeExplainerParameter(event, "num_samples", parseInt)}/>
            </Form.Group>
            </React.Fragment>
          )
        case 'IterativeLIME':
          return (
            <React.Fragment>
            <h4>IterativeLIME settings:</h4>
            <Form.Group>
              <Form.Label>Number of features</Form.Label>
              <Form.Control disabled={item.result ? true : false} id="num_features" as="input" type="number" min="2" step="1.0" value={item.explainer.num_features ? item.explainer.num_features : 100} onChange={(event) => changeExplainerParameter(event, "num_features", parseInt)}/>
            </Form.Group>
            <Form.Group>
              <Form.Label>Minimum number of samples</Form.Label>
              <Form.Control disabled={item.result ? true : false} id="min_samples" as="input" type="number" min="2" step="1.0" value={item.explainer.min_samples ? item.explainer.min_samples : 10} onChange={(event) => changeExplainerParameter(event, "min_samples", parseInt)}/>
            </Form.Group>
            <Form.Group>
              <Form.Label>Maximum number of samples</Form.Label>
              <Form.Control disabled={item.result ? true : false} id="max_samples" as="input" type="number" min="2" step="1.0" value={item.explainer.max_samples ? item.explainer.max_samples : 1000} onChange={(event) => changeExplainerParameter(event, "max_samples", parseInt)}/>
            </Form.Group>
            <Form.Group>
              <Form.Label>Sample Step Size</Form.Label>
              <Form.Control disabled={item.result ? true : false} id="step_size" as="input" type="number" min="1" step="1.0" value={item.explainer.step_size ? item.explainer.step_size : 100} onChange={(event) => changeExplainerParameter(event, "step_size", parseInt)}/>
            </Form.Group>
            <Form.Group>
              <Form.Label>Distance Metric</Form.Label>
              <Form.Control disabled={item.result ? true : false} id="distance_metric" as="select" value={item.explainer.distance_metric ? item.explainer.distance_metric : "MAE"} onChange={(event) => changeExplainerParameter(event, "distance_metric")}>
                  <option>MAE</option>
                  <option>MSE</option>
              </Form.Control>
            </Form.Group>
            <Form.Group>
              <Form.Label>Error Cutoff</Form.Label>
              <Form.Control disabled={item.result ? true : false} id="error_cutoff" as="input" type="number" min="0" step="1.0" value={item.explainer.error_cutoff ? item.explainer.error_cutoff : 0.001} onChange={(event) => changeExplainerParameter(event, "error_cutoff", parseFloat)}/>
            </Form.Group>
            </React.Fragment>
          )
          case 'MultiStepLIME':
            return (
              <React.Fragment>
                <h4>MultiStepLIME</h4>
                <Form.Group>
                  <Form.Label>Combination Setting</Form.Label>
                  <Form.Control disabled={item.result ? true : false} as="select"  value={item.explainer.select ? item.explainer.select : "Combined"} onChange={(event) => changeExplainerParameter(event, "select")}>
                      <option>Combined</option>
                      <option>Individual</option>
                  </Form.Control>
                </Form.Group>
                <h5>Sentence Level</h5>
                <Form.Group>
                  <Form.Label>Minimum number of samples</Form.Label>
                  <Form.Control disabled={item.result ? true : false} as="input" type="number" min="2" step="1.0" value={item.explainer.min_samples ? item.explainer.min_samples[0] : 10} onChange={(event) => changeExplainerParameter(event, "min_samples", parseInt, 0)}/>
                </Form.Group>
                <Form.Group>
                  <Form.Label>Maximum number of samples</Form.Label>
                  <Form.Control disabled={item.result ? true : false} as="input" type="number" min="2" step="1.0" value={item.explainer.max_samples ? item.explainer.max_samples[0] : 100} onChange={(event) => changeExplainerParameter(event, "max_samples", parseInt, 0)}/>
                </Form.Group>
                <Form.Group>
                  <Form.Label>Distance Metric</Form.Label >
                  <Form.Control disabled={item.result ? true : false} as="select" value={item.explainer.distance_metric ? item.explainer.distance_metric[0] : 'MAE'} onChange={(event) => changeExplainerParameter(event, "distance_metric", null, 0)}>
                      <option>MAE</option>
                      <option>MSE</option>
                  </Form.Control>
                </Form.Group>
                <Form.Group>
                  <Form.Label>Error Cutoff</Form.Label>
                  <Form.Control disabled={item.result ? true : false} as="input" type="number" min="0" step="0.005" value={item.explainer.error_cutoff ? item.explainer.error_cutoff[0] : 0.001} onChange={(event) => changeExplainerParameter(event, "error_cutoff", parseFloat, 0)}/>
                </Form.Group>
                <br/>
                <h5>Word Level</h5>
                    <Form.Group>
                  <Form.Label>Minimum number of samples</Form.Label>
                  <Form.Control disabled={item.result ? true : false} as="input" type="number" min="2" step="1.0" value={item.explainer.min_samples ? item.explainer.min_samples[1] : 10} onChange={(event) => changeExplainerParameter(event, "min_samples", parseInt, 1)}/>
                </Form.Group>
                <Form.Group>
                  <Form.Label>Maximum number of samples</Form.Label>
                  <Form.Control disabled={item.result ? true : false} as="input" type="number" min="2" step="1.0" value={item.explainer.max_samples ? item.explainer.max_samples[1] : 100} onChange={(event) => changeExplainerParameter(event, "max_samples", parseInt, 1)}/>
                </Form.Group>
                <Form.Group>
                  <Form.Label>Distance Metric</Form.Label>
                  <Form.Control disabled={item.result ? true : false} as="select"  value={item.explainer.distance_metric ? item.explainer.distance_metric[1] : 'MAE'} onChange={(event) => changeExplainerParameter(event, "distance_metric", null, 1)}>
                      <option>MAE</option>
                      <option>MSE</option>
                  </Form.Control>
                </Form.Group>
                <Form.Group>
                  <Form.Label>Error Cutoff</Form.Label>
                  <Form.Control disabled={item.result ? true : false} as="input" type="number" min="0" step="0.005" value={item.explainer.error_cutoff ? item.explainer.error_cutoff[1] : 0.001} onChange={(event) => changeExplainerParameter(event, "error_cutoff", parseFloat, 1)}/>
                </Form.Group>
              </React.Fragment>
            )
          case 'Anchor':
              return (
                <React.Fragment>
                  <h4>Anchor</h4>
                  <Form.Group>
                  <Form.Label>Number of Features</Form.Label>
                  <Form.Control disabled={item.result ? true : false} as="input" type="number" min="1" step="1.0" value={item.explainer.num_features ? item.explainer.num_features : 0.001} onChange={(event) => changeExplainerParameter(event, "num_features", parseInt)}/>
                  </Form.Group>

                  <Form.Group>
                  <Form.Label>Precision</Form.Label>
                  <Form.Control disabled={item.result ? true : false} id="precision" as="input" type="number" min="0" max="1" step="0.05" value={item.explainer.precision ? item.explainer.precision : 0.001} onChange={(event) => changeExplainerParameter(event, "precision", parseFloat)}/>
                  </Form.Group>
                </React.Fragment>
              )
          default:
            return (
              <React.Fragment>
                Not implemented
              </React.Fragment>
            )
      }
    }

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

    const cancelClick = () => {
      if(item.id !== -1){
        loadItem(item.id)
      }else{
        console.log("Redirect")
        
        history.push("/")
      }
    }

    const ddlModelChange = (event) => {
      let o = {}
      Object.assign(o, item)
      o.model = event.target.value
      setItem(o);
    };

    const explainerChanged = (event) => {
      let o = {...item}
      let d = getDefaultExplainer(event.target.value)
      o.explainer = d
      setItem(o);
    }
    const changeExplainLevel = (event) => {
      if(event.target.value === "Sentence Level"){
        setExplainLevel(0)
      } else {
        setExplainLevel(1)
      }
    }

    const txtTextChanged = (event) => {
      let o = {}
      Object.assign(o, item)
      o.text = event.target.value
      setItem(o);
      validateInput();
    };
    const buttonIconSize = 18



    return (
        <main className='editItem'>
          <Loading visible={loading} />
          <NavMenu />
          <Container>
          { 
              (item ? 
                <React.Fragment>
                  <Form>
                    <Row>
                      <Col sm="9">
                        <Container>
                        <h2>Text</h2>
                        {(!edit && item.result ? 
                        <React.Fragment>
                  
                        <Container>
                        <Row>
                        <ExplainTextView text={item.text} result={item.result} explain_level={explainLevel}/>
                        </Row>
                        
                        <Row>
                        <br/>
                        <Button as="div" type="button" variant="warning" title="Edit" onClick={switchToEditModeClick}>Edit Text <PencilSquare size={buttonIconSize} /></Button>
                        </Row>
                        </Container>
                        </React.Fragment> 
                        
                        : 
                        
                        <React.Fragment>
                        <Form.Group className="mb-3">
                          <Form.Control 
                            id="txtText"
                            as="textarea" 
                            size="lg" 
                            rows={20} 
                            placeholder= {item.text ? "" : "Write your text here."}
                            defaultValue = {item.text ? item.text : ""}
                            onChange = {txtTextChanged}
                          />
                        </Form.Group>
                        <Button as="div" type="submit" onClick={() => explainClick()}>Explain Instance</Button>
                        {' '}
                        <Button as="div" type="submit" variant="danger" onClick={() => cancelClick()}>Cancel</Button>
                        </React.Fragment>
                        )}

                        </Container>
                      </Col>
                      <Col>
                        <Row>
                        <Container>
                        <h3>Machine Learning Model</h3>
                        <Form.Group onChange={(event) => ddlModelChange(event)}>
                        <Form.Control disabled={item.result ? true : false} id="model" as="select" value={item.model}>
                          <option>TfIdf</option>
                          <option>LSTM</option>
                          <option>BERT</option>
                        </Form.Control>
                        </Form.Group>
                        </Container>
                        </Row>
                        <br/>
                        <Row>
                          <Container>
                        <h3>Explaining Method</h3>
                        <Form.Group >
                        <Form.Control disabled={item.result ? true : false} id="explainer" as="select" onChange={explainerChanged} value={item.explainer.name}>
                          <option>LIME</option>
                          <option disabled>Anchor</option>
                          <option>IterativeLIME</option>
                          <option>MultiStepLIME</option>
                        </Form.Control>
                        </Form.Group>
                        
                        
                        </Container>
                        </Row>
                        <br/>
                        <Row>
                        {explainerForms(item.explainer.name)}
                        </Row>
                      </Col>
                      
                    </Row>
                  </Form>
                </React.Fragment>

             :  <React.Fragment />)

            //print explanation if item was explained before

          }
          {
            item && item.result ? 
            <React.Fragment>
              <h2>Explanation</h2>
              <ExplainDetails result={item.result}  item={item} />
              <br/>
              {
                item.explainer.name === "MultiStepLIME" ? 
                 <React.Fragment>
                        
                        <Form.Group onChange={(event) => changeExplainLevel(event)}>
                        <Form.Control id="model" as="select">
                          <option>Sentence Level</option>
                          <option>Word Level</option>
                        </Form.Control>
                        </Form.Group>
                        <ExplainVisualization explainResult={Object.assign({}, ...item.result.explainer_result[explainLevel].map((x) => ({[x[0]]: x[1]})))} />
                </React.Fragment>
                :
                <ExplainVisualization explainResult={Object.assign({}, ...item.result.explainer_result.map((x) => ({[x[0]]: x[1]})))} />
              }
            
            </React.Fragment>
            :
            <React.Fragment/>
          }
          
          

          </Container>
        </main>
      );
    }
export default EditItem;