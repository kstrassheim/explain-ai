import React, { useEffect }  from 'react';
import {Accordion, Card} from 'react-bootstrap';
import './ExplainList.css';

function create_UUID(){
    let dt = new Date().getTime();
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        let r = (dt + Math.random()*16)%16 | 0;
        dt = Math.floor(dt/16);
        // eslint-disable-next-line
        return (c=='x' ? r :(r&0x3|0x8)).toString(16);
    });
    return uuid;
}

function ExplainDetails(props) {
    const spanID = create_UUID();
    const anchorNames = props.result.explainAnchorNames ? props.result.explainAnchorNames : []
    useEffect(() => { 
        if (!props.result || props.result.length < 1) { return; }
      },[props.text, props.result])

    return (
        <Accordion id={spanID}>
            <Card key={spanID}>
              <Accordion.Toggle as={Card.Header}  variant="link" eventKey={spanID}>{'Details'}</Accordion.Toggle>
              <Accordion.Collapse eventKey={spanID}>
                <Card.Body>
                    
                    <p>Model Prediction Label: {(props.result.modelPredictionLabels ? props.result.modelPredictionLabels : <React.Fragment />)}</p>
                    <p>Model Prediction: {(props.result.modelPrediction ? props.result.modelPrediction.join('  ') : <React.Fragment />)}</p>
                    
                    <p>Duration ML: {(props.result.durationInitMl ? props.result.durationInitMl : <React.Fragment />)}</p>
                    <p>Duration Lime: {(props.result.durationExplain ? props.result.durationExplain : <React.Fragment />)}</p>
                    
                    <p>Duration Total: {(props.result.durationInitMl && props.result.durationExplain ? props.result.durationExplain +  props.result.durationInitMl: <React.Fragment />)}</p>

                    <p>Local Score: {(props.result.explainer_score ? props.result.explainer_score : "-" )}</p>
                    <p>Samples: {(props.result.sample_size ? props.result.sample_size : "-" )}</p>
                    { (props.item.useAnchor) ? <React.Fragment>
                        <p>Anchor User Selected Precision: {(props.item.precision ? props.item.precision : <React.Fragment />)}</p>
                        <p>Anchor Names: {(anchorNames ? anchorNames.join(', ') : <React.Fragment />)}</p>
                        <p>Anchor Precision: {props.result.explainAnchorPrecision ? props.result.explainAnchorPrecision : ''}</p>
                        <p>Duration Anchor: {(props.result.durationExplainAnchorStr ? props.result.durationExplainAnchorStr : <React.Fragment />)}</p>
                      </React.Fragment> : <React.Fragment></React.Fragment>

                    }
                  

                </Card.Body>
              </Accordion.Collapse>
            </Card>
        </Accordion>
 );
}

export default ExplainDetails;