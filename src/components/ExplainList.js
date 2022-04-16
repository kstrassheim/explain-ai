import React, { useState }  from 'react';
import {Accordion, Card,  Container, Row} from 'react-bootstrap';
import ExplainVisualization from './ExplainVisualization'
import ExplainTextView from './ExplainTextView'
import ExplainDetails from '../components/ExplainDetails'
import './ExplainList.css';

function ExplainList(props) {

  const [selectedIndex, setSelectedIndex] = useState(null)
  const onAccordeonSelect = (itemListIndexPlusOne) => {
    setSelectedIndex(itemListIndexPlusOne);
    if (props.items && props.onItemSelect) {
        props.onItemSelect(props.items[itemListIndexPlusOne-1])
    }
  }

  return (
         <Accordion onSelect={onAccordeonSelect}>
          {(props.items && props.items.length > 0 ? props.items.map((item, index) => { return (
            <Card key={index+1} id={item.id} className={
              selectedIndex && selectedIndex === (index + 1) ? 
                `selected ${item.result && item.result.modelPredictionLabels !== undefined ? (item.result.modelPredictionLabels[0] > 0 ? 'positiveLabel' : 'negativeLabel') : ''}` 
                : `${item.result && item.result.modelPredictionLabels !== undefined ? (item.result.modelPredictionLabels[0] > 0 ? 'positiveLabel' : 'negativeLabel') : ''}`
              }>
              
              <Accordion.Toggle as={Card.Header} variant="link" eventKey={index+1}>
                <Container>
                  <Row>
                    {item.name} - {item.model} - {item.explainer.name} {item.useAnchor ? ' - Anchor' : ''}
                  </Row>
                </Container>
                  
                   
              </Accordion.Toggle>
              <Accordion.Collapse eventKey={index+1}>
                <Card.Body>
                    <p><ExplainTextView text={item.text} result={item.result ? item.result : null} explain_level={1} /></p>
                      { (item.result && item.result.explainer_result ? 
                          <React.Fragment>
                            { item.explainer.name === "MultiStepLIME" ? 
                              <ExplainVisualization explainResult={Object.assign({}, ...item.result.explainer_result[1].map((x) => ({[x[0]]: x[1]})))} />
                              : <ExplainVisualization explainResult={Object.assign({}, ...item.result.explainer_result.map((x) => ({[x[0]]: x[1]})))} />
                            }
                            <ExplainDetails result={item.result} item={item} />
                          </React.Fragment>
                        :<React.Fragment />)
                      }
                </Card.Body>
              </Accordion.Collapse>
            </Card>)
            })
            : <Card><Card.Header>No Explain items available</Card.Header></Card>)}
        </Accordion>
        
  );
}

export default ExplainList;
